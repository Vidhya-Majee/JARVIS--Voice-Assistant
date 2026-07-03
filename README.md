<div align="center">

# 🤖 J.A.R.V.I.S.
### *Just A Rather Very Intelligent System*

> *"At ease, Mr. Stark."* — Your personal AI assistant, inspired by Iron Man

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F54703?style=for-the-badge&logo=meta&logoColor=white)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## ✨ What is JARVIS?

**JARVIS** is a full-stack AI assistant built with **Flask + Groq AI (LLaMA 3.3 70B)**. It runs in your browser with a sleek Iron Man–themed UI and understands natural language commands — from checking the weather to cracking a joke to opening apps on your PC.

Think of it as your personal Friday — but smarter.

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🧠 **AI Chat** | Powered by Groq's LLaMA 3.3 70B — multi-turn memory, witty like Stark's JARVIS |
| 🌤️ **Live Weather** | Real-time weather for any city via wttr.in (no API key needed) |
| 📰 **News Feed** | Latest headlines from Google News RSS |
| 🎵 **Music Player** | Play your favorite songs directly on YouTube |
| 📖 **Wikipedia Search** | Get 3-sentence summaries from Wikipedia instantly |
| 😂 **Joke Generator** | Safe programming and pun jokes via JokeAPI |
| 🖥️ **Open PC Apps** | Launch Notepad, Calculator, VS Code, Chrome, and more by voice |
| 🕐 **Date & Time** | Ask JARVIS what time or date it is |
| 🌐 **Open Websites** | "Open YouTube", "Open GitHub" — JARVIS handles it |
| 🎙️ **Voice Mode (CLI)** | Full speech recognition + text-to-speech via `main.py` |

---

## 🗂️ Project Structure

```
mega_project1-JARVIS/
│
├── app.py               # 🚀 Main Flask application (all routes + AI logic)
├── main.py              # 🎙️  CLI voice assistant (speech recognition)
├── musicLibrary.py      # 🎵 Song name → YouTube URL mapping
│
├── templates/
│   └── index.html       # 🎨 Iron Man–themed web UI
│
├── static/
│   ├── css/style.css    # 💅 UI styles
│   └── js/script.js     # ⚡ Frontend logic
│
├── .env                 # 🔐 Your secret API keys (NEVER commit this!)
├── .env.example         # ✅ Safe template for collaborators
├── requirements.txt     # 📦 Python dependencies
├── .gitignore           # 🚫 Files excluded from Git
└── README.md            # 📖 You are here
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mega_project1-JARVIS.git
cd mega_project1-JARVIS
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
# Copy the example file
cp .env.example .env
```

Now open `.env` and add your **Groq API key**:

```env
GROK_API_KEY=your_groq_api_key_here
```

> 🔑 Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys)

### 5. Run JARVIS

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000** 🎉

---

## 🎙️ Voice Assistant Mode (CLI)

Want JARVIS to listen to your voice directly? Run:

```bash
python main.py
```

Then say **"Jarvis"** to wake it up and give commands like:
- *"Open YouTube"*
- *"Play Zaalima"*
- *"Open Google"*

> ⚠️ Requires a working **microphone** and PyAudio installed.

---

## 💬 Example Commands (Web UI)

| You say... | JARVIS does... |
|---|---|
| `"What's the weather in Mumbai?"` | Shows live weather card |
| `"Tell me a joke"` | Cracks a programming pun |
| `"Search Wikipedia for quantum computing"` | Returns a 3-sentence summary |
| `"What time is it?"` | Tells the current time |
| `"Open Notepad"` | Launches Notepad on your PC |
| `"Play Zaalima"` | Opens the song on YouTube |
| `"Who are you?"` | JARVIS introduces himself 😎 |

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROK_API_KEY` | ✅ Yes | Your Groq API key for LLaMA 3.3 AI |
| `GEMINI_API_KEY` | ❌ Optional | Google Gemini key (future use) |

> **Never commit your `.env` file.** Use `.env.example` as the template for collaborators.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1 |
| **AI Engine** | Groq Cloud API — LLaMA 3.3 70B Versatile |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Weather API** | wttr.in (free, no key needed) |
| **News** | Google News RSS |
| **Wikipedia** | MediaWiki REST API |
| **Jokes** | JokeAPI v2 |
| **Voice (CLI)** | SpeechRecognition + pyttsx3 |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** your changes: `git commit -m "Add: your feature"`
4. **Push** to the branch: `git push origin feature/your-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — do whatever you want, just give credit. 😊

---

<div align="center">

Made with ❤️ and a little bit of Stark technology

*"Sometimes you gotta run before you can walk."* — Tony Stark

</div>
