# HoloAssistant (not-a-project)

**Experimental / proof-of-concept repository**  
This is not a polished or packaged project — it’s a proof of concept for a university course.
Things may be messy. The code that controls the servos are on the pi, not on this repository. therefore functions are incomplete.

---

## What this is

HoloAssistant combines:

- **Computer vision**
  - Face tracking using OpenCV + MediaPipe to detect where your nose is and outputs an x and y coordinate.
- **Speech recognition**
  - Microphone input via python's `SpeechRecognition` library (failed me on stage)
- **AI responses**
  - Google's gemini API (key not included this time)
- **Text-to-speech**
  - Audio output via google's text to speech api, which turns gemini's output into real speech
- **3D application layer**
  - Panda3D model that rotates based on where your nose is, creating a real time 3D holographic effect
  - (ratios are wrong and need to be manually tuned to each webcam's fov)

All glued together in Python with some multithreading.

---

## Structure

```text
├── main.py                 # Entry point (Panda3D app)
├── main.py2                # same as main, but with working servo code (incomplete)
├── tracker.py              # Face / vision tracking logic
├── talkassistant.py        # Voice + AI assistant logic
├── .vscode/                # Editor config / stubs
└── README.md               # .

```

## Setup
```
0. Make sure you have a functional webcam and microphone, microphone sensitivity 30-60% or stt library will fail
1. Install Python 3.12.12 (with pyenv for example)
2. Create a virtual environment (pyenv/venv)
3. Go into the virtual environment and clone this repository
4. cd into the repository
```

```bash
pip install opencv-python mediapipe panda3d SpeechRecognition google-generativeai gTTS
# note: some packages may be missing! install what isnt there
```
```
python3 main.py
```
