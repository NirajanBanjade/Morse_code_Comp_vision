#!/usr/bin/env python3
"""
Webcam Processor Module
Handles webcam/camera feed processing for Morse code decoding.
"""

import cv2


def process_webcam(decoder, camera_id=0, display=True):
    """Process webcam feed and decode Morse code."""
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Error: Cannot open camera {camera_id}")
        return None
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30  # Default fallback
    
    print(f"Processing webcam at {fps:.1f} FPS")
    print("Press 'q' to quit")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get timestamp
        timestamp = frame_count / fps
        
        # Select ROI on first frame
        if decoder.roi is None:
            decoder.select_roi(frame)
            decoder.state_start_time = timestamp
        
        # Extract and process intensity
        intensity = decoder.extract_intensity(frame)
        new_state = decoder.detect_state(intensity)
        
        if decoder.debug and frame_count % 10 == 0:
            print(f"Frame {frame_count}: intensity={intensity:.3f}, state={'ON' if new_state else 'OFF'}")
        
        # Handle state changes
        if new_state != decoder.current_state:
            decoder.process_state_change(new_state, timestamp)
        
        # Draw overlay
        if display:
            display_frame = decoder.draw_overlay(frame.copy(), intensity, timestamp)
            cv2.imshow('Morse Decoder', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        frame_count += 1
    
    # Process final state change if needed
    if decoder.current_state:
        # Light was still ON - process it
        decoder.process_state_change(False, timestamp + 1.0)
    elif decoder.current_symbol:
        # OFF but have accumulated symbols - emit letter
        char = decoder.decode_symbol()
        if char:
            decoder.decoded_text += char
            print(f"Decoded: {char} (final) → '{decoder.decoded_text}'")
    
    cap.release()
    cv2.destroyAllWindows()
    
    return decoder.decoded_text