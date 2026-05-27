# 🌌 J.A.R.V.I.S. (Just A Rather Very Intelligent System) — Web HUD Assistant

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-3.0%2B-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Web Speech API](https://img.shields.io/badge/Web%20Speech-API-cyan?logo=javascript&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
[![HUD Style](https://img.shields.io/badge/UI-Stark%20HUD-orange)](#)

An advanced digital assistant dashboard inspired by Stark Industries' iconic tech. JARVIS features a dual-mode interaction model: a beautiful, responsive cybernetic **Web HUD** with voice processing, and a classic offline **Voice Console** running directly inside your terminal.

---

## ⚡ Key Features

* **Interactive Arc Reactor Core:** Pulsing, segmented SVG-based reactor that triggers voice command modes when clicked.
* **Dual Execution Modes:**
  * **Web HUD (`app.py`):** Runs a Flask server with client-side Speech Recognition (Web Speech API) and customized Robotic TTS (Speech Synthesis).
  * **Voice Console (`main.py`):** Operates offline using `speech_recognition` and Python's native `pyttsx3` text-to-speech package.
* **Interactive Terminal Logger:** Real-time log monitoring panel tracking system state and commands on the webpage.
* **Live Widgets:**
  * **Music Controller:** Click to play music library tracks directly.
  * **News Feed:** Dynamically pulls the top articles and headlines from Google News RSS.
* **Web Automation:** Automatically opens the localhost browser window on startup and runs command-triggered URL links.

---

## 📂 Project Architecture

```txt
mega_project1-JARVIS/
├── .venv/                  # Python Virtual Environment
├── static/
│   ├── css/
│   │   └── style.css       # Stark Industries Cyber-HUD Stylesheet
│   └── js/
│       └── script.js       # Core Frontend Speech Controller & UI Logic
├── templates/
│   └── index.html          # Web HUD Dashboard HTML Layout
├── app.py                  # Flask Web Server Backend
├── main.py                 # Offline Voice Assistant Script
├── musicLibrary.py         # Static Music Playback Registry
├── README.md               # Documentation (You are here)
└── .gitignore              # Repository Ignored File List
```

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.10+** installed on your system.

### 1. Clone & Enter Directory
```bash
git clone https://github.com/Vidhya-Majee/JARVIS--Voice-Assistant.git
cd JARVIS--Voice-Assistant
```

### 2. Activate Virtual Environment
* **On PowerShell (Windows Default):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
* **On Command Prompt (CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```
* **On Unix/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install flask speechRecognition pyttsx3
```

---

## 🚀 Running the Assistant

### Mode A: Interactive Web HUD (Recommended)
This starts the Web server on `localhost` and automatically launches your browser:
```bash
python app.py
```
* **Web address:** Open [http://127.0.0.1:5000](http://127.0.0.1:5000) if it doesn't open automatically.
* **Interaction:** Click the spinning **Arc Reactor** or tap the `Spacebar` to speak, or use the **System Console** at the bottom-left to type manual commands.

### Mode B: Offline Voice Console
Run the command-line assistant using system-level audio capture:
```bash
python main.py
```
* Say **"Jarvis"** to wake the assistant up. 
* Wait for the wake confirmation sound/text, then give your command (e.g. *"Play song name"*).

---

## ⚙️ Configured Commands

| Command | Action / Behavior |
| :--- | :--- |
| **"hello" / "hi jarvis"** | Plays a polite welcome greeting |
| **"open google"** | Opens `google.com` in a new tab |
| **"open youtube"** | Opens `youtube.com` in a new tab |
| **"open github"** | Opens `github.com` in a new tab |
| **"play [song_name]"** | Plays track from your custom library (or falls back to YouTube search) |
| **"news"** | Queries and displays Google RSS feed headlines |
| **"search [query]"** | Searches Google for the requested query |

---

## 🛸 Future Roadmaps
See [jarvis_upgrade_roadmap.md](.gemini/antigravity-ide/brain/88d2c39d-5a08-432a-85e3-9573e63d7de8/jarvis_upgrade_roadmap.md) for step-by-step instructions on implementing:
1. **Gemini LLM Brain** for advanced conversation.
2. **System CPU & RAM Monitors** directly on the dashboard.
3. **Circular Audio Wave Visualizer** around the Arc Reactor.
