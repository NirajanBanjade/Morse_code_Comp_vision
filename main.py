#!/usr/bin/env python3
"""
Morse Code Video Decoder
Detects and decodes Morse code from blinking lights in video files or webcam feeds.
"""

import argparse
import sys
from morse_decoder import MorseVideoDecoder
from video_processor import process_video
from webcam_processor import process_webcam


def main():
    parser = argparse.ArgumentParser(description='Decode Morse code from video')
    parser.add_argument('video', help='Path to video file (or 0 for webcam)')
    parser.add_argument('--no-display', action='store_true', help='Run without visual display')
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    parser.add_argument('--roi-size', type=int, default=64, help='ROI size in pixels')
    parser.add_argument('--interactive', action='store_true', help='Manually select ROI (recommended for webcam)')
    parser.add_argument('--no-adaptive', action='store_true', help='Disable adaptive thresholds')
    
    args = parser.parse_args()
    
    # Handle webcam
    video_source = 0 if args.video == '0' else args.video
    is_webcam = args.video == '0'
    
    # Create decoder with appropriate settings
    decoder = MorseVideoDecoder(
        roi_size=args.roi_size,
        debug=args.debug,
        interactive_roi=args.interactive or is_webcam,  # Enable interactive for webcam by default
        adaptive_threshold=not args.no_adaptive
    )
    
    # Process video or webcam
    if is_webcam:
        result = process_webcam(decoder, camera_id=0, display=not args.no_display)
    else:
        result = process_video(decoder, video_source, display=not args.no_display)
    
    print("\n" + "="*50)
    print("DECODED TEXT:")
    print(result)
    print("="*50)


if __name__ == '__main__':
    main()