#!/usr/bin/env python3
"""
Generate test videos with Morse code blinking light.
"""

import cv2
import numpy as np
import argparse


# Morse code encoding
MORSE_ENCODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.'
}


def text_to_morse(text):
    """Convert text to Morse code pattern."""
    morse_list = []
    
    for char in text.upper():
        if char == ' ':
            morse_list.append('/')  # Word separator
        elif char in MORSE_ENCODE:
            morse_list.append(MORSE_ENCODE[char])
    
    return ' '.join(morse_list)


def generate_timing_pattern(morse_code, unit_duration):
    """
    Generate list of (state, duration) tuples from Morse code string.
    
    Timing rules:
    - dot: 1 unit ON
    - dash: 3 units ON
    - gap between symbols: 1 unit OFF
    - gap between letters: 3 units OFF
    - gap between words: 7 units OFF
    """
    pattern = []
    
    letters = morse_code.split(' ')
    
    for i, letter in enumerate(letters):
        if letter == '/':  # Word separator
            pattern.append((False, 7 * unit_duration))
        else:
            # Process each dot/dash
            for j, symbol in enumerate(letter):
                if symbol == '.':
                    pattern.append((True, 1 * unit_duration))
                elif symbol == '-':
                    pattern.append((True, 3 * unit_duration))
                
                # Gap between symbols (except last)
                if j < len(letter) - 1:
                    pattern.append((False, 1 * unit_duration))
            
            # Gap between letters (except last)
            if i < len(letters) - 1 and letters[i + 1] != '/':
                pattern.append((False, 3 * unit_duration))
    
    return pattern


def create_morse_video(text, output_path, wpm=12, fps=30, width=640, height=480):
    """Create a video with blinking Morse code."""
    
    # Calculate unit duration from WPM
    # Standard: PARIS = 50 units, WPM = 50 units per minute
    unit_duration = 1.2 / wpm  # seconds per unit
    
    print(f"Generating Morse video:")
    print(f"  Text: {text}")
    print(f"  WPM: {wpm}")
    print(f"  Unit duration: {unit_duration:.3f}s")
    print(f"  FPS: {fps}")
    
    # Convert text to Morse
    morse_code = text_to_morse(text)
    print(f"  Morse: {morse_code}")
    
    # Generate timing pattern
    pattern = generate_timing_pattern(morse_code, unit_duration)
    
    # Calculate total duration
    total_duration = sum(duration for _, duration in pattern)
    total_frames = int(total_duration * fps)
    
    print(f"  Total duration: {total_duration:.1f}s ({total_frames} frames)")
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Light properties
    center = (width // 2, height // 2)
    radius = 50
    
    frame_count = 0
    
    for state, duration in pattern:
        num_frames = int(duration * fps)
        
        for _ in range(num_frames):
            # Create black frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Draw light if ON
            if state:
                cv2.circle(frame, center, radius, (255, 255, 255), -1)
            
            out.write(frame)
            frame_count += 1
    
    # Add a final pause (letter gap duration) to ensure last symbol is decoded
    pause_frames = int(3 * unit_duration * fps)
    black_frame = np.zeros((height, width, 3), dtype=np.uint8)
    for _ in range(pause_frames):
        out.write(black_frame)
        frame_count += 1
    
    out.release()
    print(f"Video saved to {output_path} ({frame_count} frames)")


def main():
    parser = argparse.ArgumentParser(description='Generate Morse code test video')
    parser.add_argument('--text', default='HELLO WORLD', help='Text to encode')
    parser.add_argument('--output', default='morse_test.mp4', help='Output video path')
    parser.add_argument('--wpm', type=int, default=12, help='Words per minute')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    parser.add_argument('--width', type=int, default=640, help='Video width')
    parser.add_argument('--height', type=int, default=480, help='Video height')
    
    args = parser.parse_args()
    
    create_morse_video(
        text=args.text,
        output_path=args.output,
        wpm=args.wpm,
        fps=args.fps,
        width=args.width,
        height=args.height
    )


if __name__ == '__main__':
    main()