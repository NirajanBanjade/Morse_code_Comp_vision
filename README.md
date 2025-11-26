Project Proposal: Real-Time Morse Code Detection Using Light Intensity
Team Member: Nirajan Banjade

Problem Statement
Morse code remains one of the simplest and most reliable ways to transmit messages using light, especially in emergency or low-bandwidth scenarios such as SOS signaling, survival situations, and long-distance visual communication. However, there is currently no widely available computer-vision tool that can automatically decode Morse code from blinking lights in real time.
This project aims to build a system that detects changes in light intensity from video or a webcam feed and translates them into English text by analyzing temporal patterns of short and long flashes.

Dataset
No public dataset exists for Morse code light-intensity signals, and sample videos on stock platforms (e.g., Getty Images) are very expensive and not suitable for academic use.
Therefore, I made a python script which generate white light and black background sample morse code videos to test them with the app.
Since no benchmark dataset was available for testing, I used a mobile app called “Morse Code” to generate encoded text messages. These outputs were then used to test and validate my own application’s decoding accuracy.
This approach allowed me to create diverse, controlled examples for tuning the detection of dots (·), dashes (—), and timing gaps.


Proposed Method
The system will perform visual Morse code detection using light-intensity analysis. The method combines signal processing and computer vision techniques covered in the course:
1. Preprocessing and ROI Extraction
Use OpenCV to read video frames.


Apply Gaussian smoothing to reduce noise.


Optionally detect and track the bright light source using:


Thresholding


Contour detection


Centroid tracking (object tracking)


2. Light Intensity Signal Extraction
Convert frames to grayscale.


Compute average pixel intensity within the detected ROI for each frame.


Build a 1D intensity-over-time signal.


3. Temporal Signal Analysis (Key CV Techniques)
Use course techniques such as:
Thresholding & Binarization (convert intensity curve to ON/OFF).


Temporal smoothing (moving average filter).


Dynamic time segmentation to classify:


short flash → dot


long flash → dash


short pause → letter boundary


long pause → word boundary


4. Morse Code Decoding
Map dot–dash patterns to characters using Morse code lookup tables.


Return decoded text in real time.


5. Evaluation
Test across different:


light intensities


distances


background noise


blinking speeds


Report accuracy of dot/dash segmentation and character decoding.



Potential Applications
SOS or emergency rescue signaling


Communication in low-visibility environments


Amateur radio and hobbyist tools


Assistive technology for people who use visual signaling



python main.py 0 --interactive --roi-size 100
