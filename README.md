# Astra Voice AI Assistant

Astra is Dan's personal AI voice assistant built for macOS. It combines voice control, local AI models, system awareness, computer vision, music control, automation, and network intelligence.

## Features

### Voice Assistant

* Wake word activation
* Speech-to-text command processing
* Text-to-speech responses
* Conversational AI fallback

### AI Integration

* Local LLM support using Ollama
* Vision analysis using LLaVA / Moondream
* Image-based object identification
* Screen analysis

### macOS Awareness

* CPU monitoring
* RAM usage
* Storage monitoring
* Battery status
* Wi-Fi information
* Docker status
* External drive detection

### Network Awareness

* Local network device discovery
* MAC address detection
* Manufacturer lookup
* mDNS device discovery
* Device classification
* Network bandwidth monitoring
* New device detection

### Automation

* Spotify control
* Timers
* Alarms
* Notes
* Morning briefing
* Application launching

# Requirements

## Hardware

Recommended:

* macOS computer (Apple Silicon recommended)
* 8GB+ RAM
* Microphone
* Webcam (for computer vision features)

## Software

Install:

* Python 3.12+
* Homebrew
* Ollama
* Git

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>

cd voice-assistant
```

## 2. Create Virtual Environment

```bash
python3 -m venv venv
```

Activate:

### macOS/Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If requirements.txt does not exist:

```bash
pip install \
opencv-python \
mediapipe \
psutil \
zeroconf \
mac-vendor-lookup \
requests \
pillow \
pyttsx3
```

# Ollama Setup

Astra uses local AI models through Ollama.

## Install Ollama

Download:

https://ollama.com

Verify:

```bash
ollama --version
```

## Download Models

General conversation:

```bash
ollama pull llama3.2:3b
```

Computer vision:

```bash
ollama pull moondream
```

Optional:

```bash
ollama pull llava:7b
```

Check installed models:

```bash
ollama list
```

Start Ollama:

```bash
ollama serve
```

# macOS Permissions

Astra requires permissions for certain features.

## Microphone

System Settings:

```
Privacy & Security
    >
Microphone
    >
Enable Terminal / VS Code
```

## Camera

For computer vision:

```
Privacy & Security
    >
Camera
    >
Enable Terminal / VS Code
```

## Screen Recording

For screen analysis:

```
Privacy & Security
    >
Screen Recording
    >
Enable Terminal / VS Code
```

## Location

For weather features:

```
Privacy & Security
    >
Location Services
    >
Enable Terminal / VS Code
```

# Running Astra

Activate environment:

```bash
source venv/bin/activate
```

Run:

```bash
python main.py
```

Example commands:

```
Good morning Astra

What's the weather?

Play my workout playlist

Set a timer for 5 minutes

Check my Mac

Scan my network

Read my notes

Analyze my screen

What am I holding?
```

# Network Awareness Setup

Install:

```bash
pip install zeroconf mac-vendor-lookup
```

Astra scans only the local network it is connected to.

Example:

```
Home Wi-Fi

Router
 |
 +-- MacBook
 +-- iPhone
 +-- Smart TV
 +-- Alexa
```

It cannot scan devices on the internet or other private networks.

# Computer Vision Setup

Install:

```bash
pip install opencv-python mediapipe pillow
```

Features:

* Hand tracking
* Object capture
* Screen selection
* Image analysis

Camera test:

```bash
python test_object.py
```

# Project Structure

```
voice-assistant/

├── assistant/
│   ├── assistant.py
│   └── router.py
│
├── services/
│   ├── weather.py
│   ├── spotify.py
│   ├── llm.py
│   ├── vision.py
│   ├── network_awareness.py
│   ├── mdns_discovery.py
│   ├── mac_status.py
│   └── timer.py
│
├── speech/
│   ├── speech.py
│   ├── tts.py
│   └── wakeword.py
│
├── tools/
│   ├── system.py
│   └── network.py
│
├── main.py
└── README.md
```

# Troubleshooting

## Ollama timeout

Check running models:

```bash
ollama ps
```

Stop unused models:

```bash
ollama stop <model>
```

## Camera not detected

Check permissions:

```
System Settings
>
Privacy & Security
>
Camera
```

## Network scan permission error

Scapy/network tools may require administrator access.

Astra's current network scanner uses ARP, mDNS, and system tools that work without full packet capture.

## NumPy / MediaPipe conflicts

If dependencies break:

```bash
pip uninstall numpy

pip install numpy==1.26.4
```

# Future Features

Planned Astra upgrades:

* Advanced object recognition
* Face recognition
* Personal device trust system
* Network threat detection
* Smart home integration
* Calendar integration
* More autonomous AI actions

# License

Personal project.
