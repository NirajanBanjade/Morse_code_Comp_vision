#!/usr/bin/env python3
"""
Morse Code Decoder Module
Core decoder class for detecting and decoding Morse code from video frames.
"""

import cv2
import numpy as np
from collections import deque

# Morse code lookup table
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
    '----.': '9'
}


class MorseVideoDecoder:
    """Decodes Morse code from video by tracking light intensity changes."""
    
    def __init__(self, roi_size=64, smooth_window=5, debug=False, interactive_roi=False, adaptive_threshold=True):
        self.roi_size = roi_size
        self.smooth_window = smooth_window
        self.debug = debug
        self.interactive_roi = interactive_roi      # ← NEW: enables manual ROI selection
        self.adaptive_threshold = adaptive_threshold # ← NEW: enables adaptive thresholds
        
        # Signal processing parameters
        self.threshold_high = 0.4  # Intensity above this = ON
        self.threshold_low = 0.1   # Intensity below this = OFF
        self.baseline_alpha = 0.02  # Slow baseline adaptation
        self.max_intensity = 0.5 
        
        # Timing parameters
        self.unit_duration = 0.1  # Initial guess (in seconds)
        self.unit_min = 0.02
        self.unit_max = 0.25
        self.unit_alpha = 0.1  # Unit duration adaptation rate
        
        # State tracking
        self.roi = None
        self.baseline = None
        self.intensity_buffer = deque(maxlen=smooth_window)
        self.current_state = False  # False = OFF, True = ON
        self.state_start_time = 0
        self.durations_on = deque(maxlen=20)
        self.durations_off = deque(maxlen=20)
        
        # Decoding state
        self.current_symbol = []
        self.decoded_text = ""
        
    def select_roi(self, frame):
        """Find the brightest region in the frame as ROI or let user select."""
        # ↓↓↓ NEW SECTION: Interactive selection ↓↓↓
        if self.interactive_roi:
            print("\n" + "="*50)
            print("INTERACTIVE ROI SELECTION")
            print("="*50)
            print("1. Turn your flashlight ON")
            print("2. Click and drag to select the flashlight area")
            print("3. Press ENTER to confirm, or ESC to auto-select")
            print("="*50 + "\n")
            
            roi = cv2.selectROI("Select Flashlight ROI", frame, fromCenter=False, showCrosshair=True)
            cv2.destroyWindow("Select Flashlight ROI")
            
            if roi[2] > 0 and roi[3] > 0:  # Valid selection
                self.roi = roi
                print(f"✓ ROI manually selected at ({roi[0]}, {roi[1]}, size: {roi[2]}x{roi[3]})")
                return self.roi
        # ↑↑↑ END NEW SECTION ↑↑↑
        
        # Auto-select brightest region (ORIGINAL CODE with minor improvements)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        
        # Find brightest point
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blurred)
        
        print(f"Auto-detecting brightest point: intensity={max_val:.1f}/255")  # ← NEW: show what it found
        
        # Center ROI around brightest point
        x = max(0, max_loc[0] - self.roi_size // 2)
        y = max(0, max_loc[1] - self.roi_size // 2)
        x = min(x, frame.shape[1] - self.roi_size)
        y = min(y, frame.shape[0] - self.roi_size)
        
        self.roi = (x, y, self.roi_size, self.roi_size)
        print(f"✓ ROI auto-selected at ({x}, {y})")  # ← NEW: better message
        return self.roi
    
    def extract_intensity(self, frame):
        """Extract mean intensity from ROI."""
        if self.roi is None:
            return 0
        
        x, y, w, h = self.roi
        roi_frame = frame[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        
        intensity = np.mean(gray) / 255.0  # Normalize to 0-1
        
        # Update baseline (slow-moving average for dark/background level)
        if self.baseline is None:
            self.baseline = intensity
        else:
            # Only update baseline when light is OFF (low intensity)
            if intensity < 0.5:
                self.baseline = (1 - self.baseline_alpha) * self.baseline + self.baseline_alpha * intensity
        
        # ↓↓↓ NEW SECTION: Adaptive thresholds ↓↓↓
        # Track maximum intensity for adaptive thresholding
        if intensity > self.max_intensity:
            self.max_intensity = intensity
            
            # Adaptively update thresholds if enabled
            if self.adaptive_threshold and self.baseline is not None:
                intensity_range = self.max_intensity - self.baseline
                if intensity_range > 0.2:  # Sufficient dynamic range
                    # Set thresholds as percentages of the range
                    self.threshold_low = self.baseline + 0.2 * intensity_range
                    self.threshold_high = self.baseline + 0.6 * intensity_range
                    
                    if self.debug:
                        print(f"Adaptive thresholds: LOW={self.threshold_low:.3f}, HIGH={self.threshold_high:.3f}")
        # ↑↑↑ END NEW SECTION ↑↑↑
        
        # Smooth with buffer
        self.intensity_buffer.append(intensity)
        smoothed = np.median(list(self.intensity_buffer))
        
        return smoothed
    
    def detect_state(self, intensity):
        """Detect ON/OFF state using hysteresis thresholding."""
        if intensity > self.threshold_high:
            return True
        elif intensity < self.threshold_low:
            return False
        else:
            return self.current_state  # Keep previous state
    
    def update_unit_estimate(self):
        """Estimate unit duration from collected ON/OFF durations."""
        all_durations = list(self.durations_on) + list(self.durations_off)
        
        if len(all_durations) < 5:
            return
        
        # Use median divided by ~1.5 as heuristic (dots are ~1 unit)
        median_duration = np.median(all_durations)
        new_unit = np.clip(median_duration / 1.5, self.unit_min, self.unit_max)
        
        # Smooth update
        self.unit_duration = (1 - self.unit_alpha) * self.unit_duration + self.unit_alpha * new_unit
    
    def classify_duration(self, duration, is_on):
        """Classify duration as dot/dash (ON) or gap type (OFF)."""
        units = duration / self.unit_duration
        
        if is_on:
            # Dot = ~1 unit, Dash = ~3 units
            if units < 1.8:
                return 'dot'
            else:
                return 'dash'
        else:
            # Intra-letter = ~1 unit, Letter gap = ~3 units, Word gap = ~7 units
            if units < 1.8:
                return 'intra'
            elif units < 4.5:
                return 'letter'
            else:
                return 'word'
    
    def decode_symbol(self):
        """Decode accumulated dots/dashes to a character."""
        if not self.current_symbol:
            return None
        
        symbol_str = ''.join(self.current_symbol)
        char = MORSE_CODE.get(symbol_str, '?')
        self.current_symbol = []
        return char
    
    def process_state_change(self, new_state, timestamp):
        """Handle state transitions and decode Morse."""
        duration = timestamp - self.state_start_time
        
        # Ignore very short blips (< 0.02 seconds)
        if duration < 0.02:
            return
        
        if self.current_state:  # Was ON, now OFF
            self.durations_on.append(duration)
            symbol = self.classify_duration(duration, True)
            
            if symbol == 'dot':
                self.current_symbol.append('.')
            elif symbol == 'dash':
                self.current_symbol.append('-')
            
            if self.debug:
                print(f"ON: {duration:.3f}s → {symbol}")
        
        else:  # Was OFF, now ON
            if duration > 0.02:  # Only count meaningful gaps
                self.durations_off.append(duration)
                gap_type = self.classify_duration(duration, False)
                
                if gap_type == 'letter':
                    char = self.decode_symbol()
                    if char:
                        self.decoded_text += char
                        print(f"Decoded: {char} → '{self.decoded_text}'")
                
                elif gap_type == 'word':
                    char = self.decode_symbol()
                    if char:
                        self.decoded_text += char
                    self.decoded_text += ' '
                    print(f"Word gap → '{self.decoded_text}'")
                
                if self.debug:
                    print(f"OFF: {duration:.3f}s → {gap_type}")
        
        # Update unit estimate
        self.update_unit_estimate()
        
        # Update state
        self.current_state = new_state
        self.state_start_time = timestamp
    
    def draw_overlay(self, frame, intensity, timestamp):
        """Draw debug overlay on frame."""
        h, w = frame.shape[:2]
        
        # Draw ROI rectangle
        if self.roi:
            x, y, rw, rh = self.roi
            color = (0, 255, 0) if self.current_state else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + rw, y + rh), color, 2)
        
        # Info panel
        cv2.rectangle(frame, (10, 10), (w - 10, 120), (0, 0, 0), -1)
        
        cv2.putText(frame, f"Unit: {self.unit_duration*1000:.0f}ms", 
                   (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        state_text = "ON " if self.current_state else "OFF"
        cv2.putText(frame, f"State: {state_text}", 
                   (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Intensity: {intensity:.2f}", 
                   (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Decoded text
        display_text = self.decoded_text[-40:] if len(self.decoded_text) > 40 else self.decoded_text
        cv2.putText(frame, f"Text: {display_text}", 
                   (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame