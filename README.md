<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=40&pause=1000&color=F54703&center=true&vCenter=true&width=600&lines=J.A.R.V.I.S.;Just+A+Rather+Very+Intelligent+System;Your+Personal+AI+Assistant" alt="JARVIS" />

### *Just A Rather Very Intelligent System*

> *"At ease, Mr. Stark."* — Your personal AI assistant, built for the real world.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F54703?style=for-the-badge&logo=meta&logoColor=white)](https://console.groq.com)
[![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-blueviolet?style=for-the-badge)](https://github.com/your-username/mega_project1-JARVIS/pulls)

<br/>

[🚀 Quick Start](#-quick-start) &nbsp;·&nbsp; [✨ Features](#-features) &nbsp;·&nbsp; [🗂️ Architecture](#%EF%B8%8F-project-structure) &nbsp;·&nbsp; [💬 Commands](#-example-commands) &nbsp;·&nbsp; [🤝 Contributing](#-contributing)

</div>

---

## 🔥 What is J.A.R.V.I.S.?

**JARVIS** is a full-stack, browser-based AI personal assistant inspired by Tony Stark's iconic AI — built with **Python + Flask** on the backend and powered by **Groq's ultra-fast LLaMA 3.3 70B** model.

It understands natural language, remembers your conversation context, and can do everything from launching apps on your PC to fetching live weather, news, and Wikipedia summaries — all from a sleek **Iron Man–themed web interface**.

It also ships with a **CLI voice mode** (`main.py`) for true hands-free control via microphone.

```
You  : "What's the weather in Tokyo?"
JARVIS: "Current weather in Tokyo, Japan: Sunny, 29°C.
         Humidity is 63% and wind speed is 14 km/h, Sir."
```

---

## ✨ Features

| &nbsp; | Feature | Description | How It Works |
|:---:|---|---|---|
| 🧠 | **AI Chat** | Multi-turn conversation with memory | Groq API → LLaMA 3.3 70B. Retains last 10 message turns for full context. |
| 🌤️ | **Live Weather** | Real-time weather for any city | wttr.in JSON API — temp, humidity, wind speed, feels-like. No key required. |
| 📰 | **News Feed** | Top 6 latest headlines | Google News RSS parsed live with title, source, date & article link. |
| 🎵 | **Music Player** | Play songs on YouTube | Built-in library → YouTube URL. Falls back to YouTube search automatically. |
| 📖 | **Wikipedia** | 3-sentence article summaries | MediaWiki REST API — searches by topic, fetches clean intro excerpt. |
| 😂 | **Jokes** | Safe programming & pun jokes | JokeAPI v2 with safe-mode filter. Includes offline fallback jokes. |
| 🖥️ | **Launch Apps** | Open local PC applications | `subprocess.Popen` — Notepad, Calculator, Paint, VS Code, Chrome & more. |
| 🌐 | **Open Websites** | Navigate to popular sites | Google, YouTube, GitHub, LinkedIn, Instagram, Twitter, Maps & more. |
| 🔍 | **Google Search** | Web search on demand | Parses query from command, opens Google results in a new tab. |
| 🕐 | **Date & Time** | Current time, date & day of week | Python `datetime` — formatted 12h time, full date, day name. |
| 🎙️ | **Voice Mode** | Full speech I/O via CLI | SpeechRecognition (Google STT) + pyttsx3 TTS. Wake word: **"Jarvis"**. |
| 🔄 | **Dual AI Backend** | Swap Groq ↔ Gemini | Switch between LLaMA 3.3 and Gemini 1.5 Flash with a few commented lines. |

---

## 🗂️ Project Structure

```
mega_project1-JARVIS/
│
├── 🚀  app.py                 # Main Flask app — routes, AI logic, command handling
├── 🎙️  main.py                # Standalone CLI voice assistant (mic input + TTS)
├── 🎵  musicLibrary.py        # Song name → YouTube URL mapping dictionary
│
├── templates/
│   └── 🎨  index.html         # Iron Man–themed single-page web UI
│
├── static/
│   ├── css/
│   │   └── 💅  style.css      # Arc reactor animations, glassmorphism, dark UI
│   └── js/
│       └── ⚡  script.js       # Voice recognition, command dispatch, UI updates
│
├── 🔐  .env                   # Your API keys — NEVER commit this!
├── ✅  .env.example            # Safe template for collaborators
├── 📦  requirements.txt        # Python dependencies
├── 🚫  .gitignore              # Files excluded from version control
└── 📖  README.md               # You are here
```

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                     Browser (Web UI)                      │
│   script.js ──[POST /api/command]──► Flask (app.py)      │
│              ◄──[JSON response]──────                     │
└───────────────────────┬──────────────────────────────────┘
                        │  Routes to one of:
         ┌──────────────┼───────────────────┐
         ▼              ▼                   ▼
  Groq / Gemini    External APIs      Local System
  (AI fallback)  (wttr.in, News,   (subprocess.Popen
                  Wiki, JokeAPI)     → open apps)
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+** installed
- A free **[Groq API key](https://console.groq.com/keys)** *(takes under a minute)*
- For voice mode: a working **microphone** + PyAudio

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/mega_project1-JARVIS.git
cd mega_project1-JARVIS
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure your API key

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your key:

```env
# Required — powers the LLaMA 3.3 AI chat
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — only needed if you switch backend to Gemini
# GEMINI_API_KEY=your_gemini_key_here
```

> 🔑 Get your **free Groq key** at [console.groq.com/keys](https://console.groq.com/keys)

### Step 5 — Launch JARVIS 🚀

```bash
python app.py
```

JARVIS will **automatically open your browser** at `http://127.0.0.1:5000`. Done!

---

## 🎙️ Voice Assistant Mode (CLI)

For a true voice-command experience, run:

```bash
python main.py
```

Say **"Jarvis"** to wake it up, then speak any command:

| Say... | JARVIS does... |
|--------|----------------|
| *"Jarvis, open YouTube"* | Opens youtube.com in browser |
| *"Jarvis, play Zaalima"* | Plays the YouTube video |
| *"Jarvis, open Google"* | Opens google.com |

> ⚠️ **PyAudio on Windows failing?**
> ```bash
> pip install pipwin && pipwin install pyaudio
> ```

---

## 💬 Example Commands (Web UI)

| You say… | JARVIS responds… | Action |
|---|---|:---:|
| `Hello Jarvis` | "Hello. All systems are fully operational." | 💬 |
| `What's the weather in Mumbai?` | Live weather card — temp, humidity, wind | 🌤️ |
| `Tell me the news` | Top 6 headlines with links & sources | 📰 |
| `Play Zaalima` | Opens the YouTube video directly | 🎵 |
| `Search Wikipedia for black holes` | 3-sentence Wikipedia summary | 📖 |
| `Tell me a joke` | Safe programming pun | 😂 |
| `What time is it?` | "The current time is 08:42 PM, Sir." | 🕐 |
| `Open Notepad` | Launches Notepad on your PC | 🖥️ |
| `Open GitHub` | Opens github.com in a new tab | 🌐 |
| `Who created you?` | Stark-level wit via LLaMA 3.3 AI | 🧠 |

---

## 🔐 Environment Variables

| Variable | Required | Description | Get it here |
|---|:---:|---|---|
| `GROQ_API_KEY` | ✅ **Yes** | Powers LLaMA 3.3 70B AI | [console.groq.com/keys](https://console.groq.com/keys) |
| `GEMINI_API_KEY` | ❌ Optional | Google Gemini 1.5 Flash fallback | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

> ⚠️ **Security:** `.env` is listed in `.gitignore`. **Never commit it.** Use `.env.example` for collaborators.

---

## 🔄 Switching AI Backend: Groq ↔ Gemini

JARVIS ships with **Groq (LLaMA 3.3)** active. To switch to **Google Gemini 1.5 Flash**:

1. Add your key to `.env`: `GEMINI_API_KEY=your_key`
2. In `app.py`, **uncomment** the Gemini setup block and `init_gemini()` call
3. **Uncomment** the `ask_gemini()` function
4. In `process_command()`, replace `ask_groq(c)` → `ask_gemini(c)`
5. **Comment out** the Groq block

> 📝 Step-by-step comments are already in `app.py` — just follow them.

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+, Flask 3.1 | HTTP server, routing, business logic |
| **AI (Primary)** | Groq Cloud — LLaMA 3.3 70B Versatile | Natural language AI with multi-turn memory |
| **AI (Fallback)** | Google Gemini 1.5 Flash | Optional swap-in AI backend |
| **Frontend** | HTML5, CSS3, Vanilla JS | Iron Man–themed responsive single-page app |
| **Weather** | [wttr.in](https://wttr.in) JSON API | Live weather — no key needed |
| **News** | Google News RSS | Real-time headlines |
| **Knowledge** | MediaWiki REST API | Wikipedia 3-sentence summaries |
| **Humor** | [JokeAPI v2](https://jokeapi.dev) | Safe, curated jokes |
| **Voice (CLI)** | SpeechRecognition + pyttsx3 + PyAudio | Mic input + TTS output |

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|:---:|---|
| `/` | `GET` | Serves the Iron Man web UI |
| `/api/command` | `POST` | Main command handler — `{ "command": "..." }` |
| `/api/weather?city=Delhi` | `GET` | Returns raw weather JSON for any city |
| `/api/music` | `GET` | Returns the full music library as JSON |

**Sample `POST /api/command` response:**
```json
{
  "speak":            "Current weather in Delhi, India: Sunny, 36°C. Humidity 42%.",
  "action":           "show_weather",
  "target":           { "city": "Delhi, India", "temp_c": "36", "humidity": "42", ... },
  "original_command": "what's the weather in Delhi"
}
```

---

## 🎵 Music Library

The built-in library contains curated Bollywood hits. Add your own in [`musicLibrary.py`](musicLibrary.py):

```python
music = {
    "zaalima":        "https://www.youtube.com/watch?v=hnCsD8jlp2E",
    "o maahi":        "https://www.youtube.com/watch?v=3YxEAEY8vB4",
    "tu jaane na":    "https://www.youtube.com/watch?v=Jne9t8sHpUc",
    "pehla pyaar":    "https://www.youtube.com/watch?v=0Gxr9nE9YYA",
    # ↓ Add your songs here
    "your song":      "https://youtube.com/watch?v=YOUR_VIDEO_ID",
}
```

> If a song isn't in the library, JARVIS automatically falls back to a **YouTube search**.

---

## ❓ Troubleshooting

<details>
<summary><strong>🔴 PyAudio installation fails on Windows</strong></summary>
<br/>

```bash
pip install pipwin
pipwin install pyaudio
```

Or download a pre-built wheel from [Christoph Gohlke's page](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).
</details>

<details>
<summary><strong>🔴 JARVIS says "My AI core is offline"</strong></summary>
<br/>

1. Confirm `.env` exists and contains `GROQ_API_KEY=gsk_...`
2. Verify the key is valid at [console.groq.com](https://console.groq.com)
3. Check your internet connection
</details>

<details>
<summary><strong>🔴 Weather always defaults to Delhi</strong></summary>
<br/>

Your command must include a preposition:
- ✅ `"weather in Mumbai"`
- ✅ `"weather for Paris"`
- ❌ `"Mumbai weather"` — city not extracted
</details>

<details>
<summary><strong>🔴 Voice mode says "Could not understand audio"</strong></summary>
<br/>

- Check microphone permissions: **Windows Settings → Privacy → Microphone**
- Speak clearly in a quiet environment
- Verify PyAudio works: `python -c "import pyaudio; print('OK')"`
</details>

---

## 🤝 Contributing

Contributions make open source amazing. Any improvements are **greatly appreciated**!

1. **Fork** the repository
2. **Create** your feature branch: `git checkout -b feature/AmazingFeature`
3. **Commit** your changes: `git commit -m "Add: AmazingFeature"`
4. **Push** to your branch: `git push origin feature/AmazingFeature`
5. **Open** a Pull Request

### 💡 Ideas for Contributions

- 🗺️ Google Maps / directions integration
- 📅 Calendar & reminders via Google Calendar API
- 🌍 Multi-language voice support
- 🔔 Desktop push notifications
- 🎵 Spotify / local music playback
- 🧩 Plugin system for custom commands

---

## 📄 License

Distributed under the **MIT License** — use it, build on it, ship it. Just give credit. 😊

See [`LICENSE`](LICENSE) for full details.

---

<div align="center">

<br/>

**Made with ❤️ and a little bit of Stark technology**

*"Sometimes you gotta run before you can walk."* — Tony Stark

<br/>

⭐ **If JARVIS helped you, give it a star!** ⭐

</div>
