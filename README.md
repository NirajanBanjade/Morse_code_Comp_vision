# 🔦 Morse Code Video Decoder

A real-time Morse code decoder that detects and translates blinking lights from video files or webcam feeds into text. Perfect for decoding light-based Morse code signals, historical recordings, or creating interactive Morse code communication systems.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- **Real-time decoding** from webcam feeds
- **Video file processing** for recorded Morse code signals
- **Automatic ROI detection** - finds the brightest light source
- **Adaptive timing** - automatically adjusts to different transmission speeds
- **Visual feedback** - live display with intensity monitoring and decoded text
- **Robust signal processing** - handles noise and varying light conditions
- **Debug mode** - detailed logging for troubleshooting

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Webcam (optional, for live decoding)

### Python Dependencies
```
opencv-python>=4.0.0
numpy>=1.19.0
```

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/morse-video-decoder.git
cd Morse_code_Comp_vision
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install opencv-python numpy
```

## 📖 Usage

## 🎯 How It Works

This project supports three main workflows:
1. Generating synthetic Morse videos (for testing)
2. Decoding Morse code from a video file
3. Real-time decoding from webcam feed

Each section below includes code or commands to help you reproduce results.

### 🎥 1. Generate Test Videos (Synthetic Morse Code Video Creator)

You can create your own blinking-light Morse videos using the included video generation script.

**Example: Generate a video for "SOS"**
```bash
python generate_morse_video.py --text "SOS" --output sos.mp4
```

#### Key Options

| Argument | Description | Default |
|----------|-------------|---------|
| `--message` | The text message to encode in Morse | Required |
| `--dot-duration` | Duration (seconds) of a dot | 0.1 |
| `--fps` | Frames per second in output video | 30 |
| `--output` | Output filename | output.mp4 |

**Output:** A blinking white circle simulating Morse code, ideal for testing the decoder.

### 🔎 2. Decode Morse Code from Video Files

Use the main decoder to process any video containing a blinking light source.

**Basic decoding:**
```bash
python main.py video.mp4
```

**Example with debug logs enabled:**
```bash
python main.py sos.mp4 --debug
```

**Example with custom ROI size:**
```bash
python main.py video.mp4 --roi-size 128
```

#### What happens internally:
- The system auto-detects the brightest object
- Tracks intensity changes frame-by-frame
- Extracts ON/OFF durations
- Classifies durations as dot, dash, letter gap, or word gap
- Translates final Morse code sequence into text

#### Expected Output Example:
```
Processing video at 30.0 FPS

Auto-detecting brightest point...
✓ ROI auto-selected at (281, 166)

Decoded: S → 'S'
Decoded: O → 'SO'
Decoded: S → 'SOS'

==================================================
DECODED TEXT:
SOS
==================================================
```

### 🎦 3. Real-Time Decoding from Webcam

You can also decode live Morse signals with your webcam.

**Start webcam decoding:**
```bash
python main.py 0
```

#### Features during real-time mode:
- Live ROI detection
- Light intensity overlay
- Frame-by-frame ON/OFF classification
- Real-time decoded characters appearing as you blink a flashlight

This mode is great for interactive demos, presentations, and live signaling.

### 🧠 How to Know Which Mode to Use

| Task | Command | Purpose |
|------|---------|---------|
| Generate your own Morse video | `generate_morse_video.py` | Testing & reproducibility |
| Decode from an existing file | `main.py video.mp4` | Analyze recordings |
| Decode in real time | `main.py 0` | Demo or live communication |

---

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `video` | Path to video file or `0` for webcam | Required |
| `--no-display` | Run without visual display | False |
| `--debug` | Print debug information | False |
| `--roi-size` | ROI size in pixels | 64 |

### Help
```bash
python main.py --help
```

## 🎯 How It Works

1. **ROI Selection**: Automatically detects the brightest region in the frame
2. **Intensity Extraction**: Monitors light intensity changes in the ROI
3. **State Detection**: Uses hysteresis thresholding to determine ON/OFF states
4. **Timing Analysis**: Classifies durations as dots, dashes, or gaps
5. **Adaptive Learning**: Adjusts unit duration based on signal patterns
6. **Character Decoding**: Translates Morse patterns to text using standard ITU alphabet

### Morse Code Timing
- **Dot**: 1 unit
- **Dash**: 3 units
- **Intra-character gap**: 1 unit
- **Character gap**: 3 units
- **Word gap**: 7 units

## 📁 Project Structure

```
morse-video-decoder/
│
├── main.py                 # Main entry point
├── morse_decoder.py        # Core decoder class and logic
├── video_processor.py      # Video file processing
├── webcam_processor.py     # Webcam feed processing
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎬 Example

### Creating a Test Video
Flash a light in Morse code pattern for "SOS":
- `...` (S) - 3 short flashes
- `---` (O) - 3 long flashes
- `...` (S) - 3 short flashes

Record this with your phone or webcam, then decode:
```bash
python main.py sos_video.mp4
```

Expected output:
```
ROI selected at (320, 240)
Processing video at 30.0 FPS
Decoded: S → 'S'
Decoded: O → 'SO'
Decoded: S → 'SOS'

==================================================
DECODED TEXT:
SOS
==================================================
```

## 🔧 Current Capabilities

### ✅ Implemented
- [x] Video file processing
- [x] Webcam real-time decoding
- [x] Automatic bright spot detection
- [x] Adaptive timing estimation
- [x] Hysteresis-based state detection
- [x] Visual overlay with stats
- [x] Full Morse alphabet (A-Z, 0-9)
- [x] Signal smoothing and noise reduction
- [x] Debug logging

### 🚧 Limitations
- Requires consistent lighting conditions
- Works best with single, isolated light source
- Manual ROI selection not yet supported
- No support for punctuation marks
- Assumes standard International Morse Code timing

## 🔮 Future Plans

### Planned Features
- [ ] **Manual ROI selection** - Click to select light source
- [ ] **Multiple light sources** - Track and decode multiple signals simultaneously
- [ ] **Punctuation support** - Add common punctuation marks
- [ ] **Audio Morse decoding** - Decode from sound (beeps/tones)
- [ ] **Recording mode** - Save decoded messages to file
- [ ] **Playback controls** - Pause, rewind, speed adjustment for video files
- [ ] **Calibration mode** - Interactive setup for optimal parameters
- [ ] **Advanced filtering** - Better noise rejection and signal processing
- [ ] **GUI application** - User-friendly interface with visualization
- [ ] **Configuration file** - Save/load custom settings
- [ ] **Statistics dashboard** - Accuracy metrics, timing analysis
- [ ] **Training mode** - Learn Morse code with feedback
- [ ] **Mobile app** - Android/iOS version

### Enhancement Ideas
- [ ] Machine learning for better signal classification
- [ ] Support for non-standard Morse variants
- [ ] Historical accuracy mode for vintage recordings
- [ ] Two-way communication system
- [ ] Integration with amateur radio applications
- [ ] Batch processing for multiple videos
- [ ] Export decoded text with timestamps
- [ ] Color-coded signal visualization

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution
- Improving signal processing algorithms
- Adding new features from the roadmap
- Writing tests and documentation
- Reporting bugs and issues
- Creating example videos and tutorials

## 🐛 Known Issues

- ROI selection may fail in very dark environments
- Very fast or very slow transmission speeds may require parameter tuning
- Webcam frame rate variations can affect timing accuracy

Please report issues on the [GitHub Issues](https://github.com/yourusername/morse-video-decoder/issues) page.


⭐ **Star this repository if you find it helpful!**
Made by Nirajan Banjade
