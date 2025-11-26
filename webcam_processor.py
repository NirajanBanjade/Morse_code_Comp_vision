
"""
Webcam Processor Module - Enhanced with Calibration
"""
import cv2
import time

def calibrate_timing(decoder, cap, display=True):
    """Calibrate by having user blink 5 dots."""
    print("\n" + "="*50)
    print("CALIBRATION MODE")
    print("="*50)
    print("Blink your flashlight ON and OFF 5 times")
    print("(short blinks, like: blink-pause-blink-pause...)")
    print("Press SPACE when ready...")
    print("="*50 + "\n")
    
    # Wait for user
    while True:
        ret, frame = cap.read()
        if not ret:
            return False
        
        if decoder.roi is None:
            decoder.select_roi(frame)
        
        intensity = decoder.extract_intensity(frame)
        display_frame = decoder.draw_overlay(frame.copy(), intensity, 0)
        cv2.putText(display_frame, "Press SPACE to start calibration", 
                   (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        cv2.imshow('Morse Decoder', display_frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    
    # Collect ON durations (when light is ON)
    print("Calibrating... START BLINKING NOW!")
    on_durations = []
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = 0
    
    prev_state = False
    on_start_time = None
    timeout_time = time.time() + 20  # 20 second timeout
    
    while len(on_durations) < 5 and time.time() < timeout_time:
        ret, frame = cap.read()
        if not ret:
            break
        
        timestamp = frame_count / fps
        intensity = decoder.extract_intensity(frame)
        current_state = intensity > decoder.threshold_high  # Simple ON/OFF
        
        # Detect ON->OFF transition (end of blink)
        if prev_state and not current_state:
            if on_start_time is not None:
                duration = timestamp - on_start_time
                if duration > 0.05:  # At least 50ms
                    on_durations.append(duration)
                    print(f"  Blink {len(on_durations)}: {duration*1000:.0f}ms")
        
        # Detect OFF->ON transition (start of blink)
        elif not prev_state and current_state:
            on_start_time = timestamp
        
        prev_state = current_state
        
        if display:
            display_frame = decoder.draw_overlay(frame.copy(), intensity, timestamp)
            cv2.putText(display_frame, f"Blinks detected: {len(on_durations)}/5", 
                       (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Morse Decoder', display_frame)
            cv2.waitKey(1)
        
        frame_count += 1
    
    if len(on_durations) >= 3:
        avg = sum(on_durations) / len(on_durations)
        decoder.unit_duration = avg
        print(f"\n✓ Calibration complete!")
        print(f"  Your dot duration: {avg*1000:.0f}ms")
        print(f"  Dash should be: ~{avg*3*1000:.0f}ms (3x longer)")
        print(f"  Letter gap: ~{avg*3*1000:.0f}ms pause")
        print(f"\nNow you can send Morse code!")
        time.sleep(2)  # Give user time to read
        return True
    else:
        print(f"\n✗ Only detected {len(on_durations)} blinks - need at least 3")
        print("Using default timing (may not work well)")
        decoder.unit_duration = 0.3  # Slower default
        time.sleep(2)
        return False


def process_webcam(decoder, camera_id=0, display=True):
    """Process webcam feed and decode Morse code."""
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Cannot open camera {camera_id}")
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30
    
    print(f"\n{'='*50}")
    print(f"WEBCAM MORSE CODE DECODER")
    print(f"{'='*50}")
    
    # Run calibration with pattern
    calibrate_with_pattern(decoder, cap, display)
    
    print(f"\nInstructions:")
    print("  - Start blinking Morse code")
    print("  - 'q' to quit")
    print("  - 'r' to reselect ROI")
    print("  - 'c' to recalibrate timing")
    print(f"{'='*50}\n")
    
    frame_count = 0
    decoder.state_start_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        timestamp = frame_count / fps
        
        if decoder.roi is None:
            decoder.select_roi(frame)
            decoder.state_start_time = timestamp
        
        intensity = decoder.extract_intensity(frame)
        new_state = decoder.detect_state(intensity)
        
        if new_state != decoder.current_state:
            decoder.process_state_change(new_state, timestamp)
        
        # ↓↓↓ ADD THIS NEW SECTION HERE ↓↓↓
        # Auto-decode if user pauses for too long (5 seconds)
        if decoder.current_symbol and not decoder.current_state:
            time_since_last_blink = timestamp - decoder.state_start_time
            if time_since_last_blink > 5.0:  # 5 second timeout
                char = decoder.decode_symbol()
                if char:
                    decoder.decoded_text += char
                    print(f"Auto-decoded after pause: {char}")
        # ↑↑↑ END NEW SECTION ↑↑↑
        
        if display:
            display_frame = decoder.draw_overlay(frame.copy(), intensity, timestamp)
            cv2.imshow('Morse Decoder', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("\nReselecting ROI...")
                decoder.roi = None
                decoder.baseline = None
                decoder.max_intensity = 0.5
            elif key == ord('c'):
                print("\nRecalibrating...")
                calibrate_timing(decoder, cap, display)
                decoder.decoded_text = ""
                decoder.current_symbol = []
        
        frame_count += 1
    
    # ↓↓↓ ALSO IMPROVE THIS FINALIZATION SECTION ↓↓↓
    # Finalize - force decode any remaining symbol
    if decoder.current_state:
        # If light is still ON, turn it OFF first
        decoder.process_state_change(False, timestamp + 1.0)
    
    # Always try to decode remaining symbols
    if decoder.current_symbol:
        char = decoder.decode_symbol()
        if char:
            decoder.decoded_text += char
            print(f"\nFinal character decoded: {char}")
    
    print(f"\nFinal decoded text: '{decoder.decoded_text}'")
    # ↑↑↑ END IMPROVED FINALIZATION ↑↑↑
    
    cap.release()
    cv2.destroyAllWindows()
    
    return decoder.decoded_text
def calibrate_with_pattern(decoder, cap, display=True):
    """Calibrate by having user send 'EEEEE' (5 dots)."""
    print("\n" + "="*50)
    print("CALIBRATION MODE")
    print("="*50)
    print("Send the letter 'E' five times: E E E E E")
    print("(E = one short blink)")
    print("")
    print("Blink pattern:")
    print("  SHORT-blink ... pause ... SHORT-blink ... pause ... (5 times)")
    print("")
    print("Press SPACE when ready...")
    print("="*50 + "\n")
    
    # Wait for user
    while True:
        ret, frame = cap.read()
        if not ret:
            return False
        
        if decoder.roi is None:
            decoder.select_roi(frame)
        
        intensity = decoder.extract_intensity(frame)
        display_frame = decoder.draw_overlay(frame.copy(), intensity, 0)
        cv2.putText(display_frame, "Press SPACE to start calibration", 
                   (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        cv2.imshow('Morse Decoder', display_frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    
    print("Calibrating... Send 'EEEEE' now!")
    print("(5 short blinks with pauses between)")
    
    on_durations = []
    off_durations = []
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = 0
    
    prev_state = False
    state_start_time = None
    timeout_time = time.time() + 25
    
    while (len(on_durations) < 5 or len(off_durations) < 4) and time.time() < timeout_time:
        ret, frame = cap.read()
        if not ret:
            break
        
        timestamp = frame_count / fps
        intensity = decoder.extract_intensity(frame)
        current_state = intensity > decoder.threshold_high
        
        # State change detected
        if current_state != prev_state:
            if state_start_time is not None:
                duration = timestamp - state_start_time
                
                # Collect ON durations (dots)
                if prev_state and duration > 0.05:
                    on_durations.append(duration)
                    print(f"  Dot {len(on_durations)}: {duration*1000:.0f}ms")
                
                # Collect OFF durations (letter gaps)
                elif not prev_state and duration > 0.05 and len(on_durations) > 0:
                    off_durations.append(duration)
                    print(f"    Gap: {duration*1000:.0f}ms")
            
            state_start_time = timestamp
            prev_state = current_state
        
        if display:
            display_frame = decoder.draw_overlay(frame.copy(), intensity, timestamp)
            status = f"Dots: {len(on_durations)}/5, Gaps: {len(off_durations)}/4"
            cv2.putText(display_frame, status, 
                       (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Morse Decoder', display_frame)
            cv2.waitKey(1)
        
        frame_count += 1
    
    # Calculate unit from dots
    if len(on_durations) >= 3:
        import statistics
        
        # Use median of ON durations as unit (dots should be ~1 unit)
        median_dot = statistics.median(on_durations)
        
        # Validate by checking letter gaps (should be ~3x dot)
        if len(off_durations) >= 2:
            median_gap = statistics.median(off_durations)
            ratio = median_gap / median_dot
            print(f"\n  Analysis:")
            print(f"    Median dot: {median_dot*1000:.0f}ms")
            print(f"    Median gap: {median_gap*1000:.0f}ms")
            print(f"    Ratio: {ratio:.1f}x (should be ~3x)")
            
            # If ratio is reasonable, use dot duration
            if 1.5 < ratio < 6.0:
                decoder.unit_duration = median_dot
                print(f"\n✓ Calibration successful!")
                print(f"  Your unit: {median_dot*1000:.0f}ms")
                print(f"  Dot: ~{median_dot*1000:.0f}ms")
                print(f"  Dash: ~{median_dot*3*1000:.0f}ms")
                time.sleep(2)
                return True
        else:
            # Just use dots
            decoder.unit_duration = median_dot
            print(f"\n✓ Calibration complete!")
            print(f"  Your unit: {median_dot*1000:.0f}ms")
            time.sleep(2)
            return True
    
    print(f"\n✗ Calibration failed")
    print("Using default timing (300ms)")
    decoder.unit_duration = 0.3
    time.sleep(2)
    return False