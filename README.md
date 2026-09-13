<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=40&pause=1000&color=00F0FF&center=true&vCenter=true&width=600&lines=J.A.R.V.I.S.;Just+A+Rather+Very+Intelligent+System;Your+Personal+AI+Assistant" alt="JARVIS" />

### *Just A Rather Very Intelligent System*

> *"At ease, Mr. Stark."* — Your personal AI assistant, built for the real world.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-Qwen3--27B-00F0FF?style=for-the-badge&logo=groq&logoColor=white)](https://console.groq.com)
[![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-blueviolet?style=for-the-badge)](https://github.com/your-username/mega_project1-JARVIS/pulls)

<br/>

[🚀 Quick Start](#-quick-start) &nbsp;·&nbsp; [✨ Features](#-features) &nbsp;·&nbsp; [🗂️ Architecture](#%EF%B8%8F-project-structure) &nbsp;·&nbsp; [💬 Commands](#-example-commands) &nbsp;·&nbsp; [🎵 Music Library](#-music-library) &nbsp;·&nbsp; [🤝 Contributing](#-contributing)

</div>

---

## 🔥 What is J.A.R.V.I.S.?

**JARVIS** is a full-stack, browser-based AI personal assistant inspired by Tony Stark's iconic AI — built with **Python + Flask** on the backend and powered by **Groq's ultra-fast Qwen3-27B** model.

It understands natural language, **remembers your conversations across sessions** (SQLite), responds as **Sir or Ma'am** based on your name, and can do everything from launching apps on your PC to fetching live weather, news, Wikipedia summaries, cracking jokes, flipping coins, rolling dice, and controlling system volume — all from a sleek **Stark Industries holographic web interface**.

It also ships with a **CLI voice mode** (`main.py`) for true hands-free control via microphone.

```
You   : "What's the weather in Tokyo?"
JARVIS: "Current conditions in Tokyo, Japan, Sir: Sunny, 29°C — feels like 31°C.
         Humidity 63%, wind 14 km/h, visibility 10 km."
```

---

## ✨ Features

| &nbsp; | Feature | Description |
|:---:|---|---|
| 🧠 | **AI Chat (Qwen3-27B)** | Multi-turn conversation with **persistent SQLite memory** across restarts |
| 🎭 | **JARVIS Personality** | Stays in character — never breaks, addresses you as Sir/Ma'am, dry Stark wit |
| 👤 | **Sir / Ma'am Detection** | Auto-detects gender from name introduction; explicit override supported |
| 🌤️ | **Live Weather** | Real-time weather for any city — temp, feels-like, humidity, wind, visibility |
| 📰 | **News Feed** | Top headlines with category routing (tech, sports, business, health, entertainment) |
| 🎵 | **Music Library (148 tracks)** | Arijit Singh, Atif Aslam, Taylor Swift, BTS, Justin Bieber, Dua Lipa + more |
| 📖 | **Wikipedia** | 3-sentence article summaries on any topic |
| 😂 | **Jokes** | Safe jokes with JARVIS quips via JokeAPI + offline fallbacks |
| 🖥️ | **Launch Apps** | Open Notepad, Calculator, VS Code, Chrome, Word, Excel & more |
| 🌐 | **Open Websites** | Google, YouTube, GitHub, LinkedIn, Instagram, Twitter, Maps & more |
| 🔍 | **Google Search** | Voice/text search — opens results in a new tab |
| 🕐 | **Date & Time** | Current time, date, day of week |
| 🎲 | **Fun Commands** | Coin flip, dice roll (any sides), random number in custom range |
| 💻 | **System Commands** | Lock PC, shutdown, restart, battery status, volume up/down/mute, screenshot |
| 🔢 | **Math Evaluator** | Spoken math — "calculate 18 percent of 5000", "what is 15 squared" |
| 🌐 | **IP Address** | "What's my IP?" — reads your local network address |
| 🎙️ | **Voice Mode** | Full speech I/O via CLI — wake word: **"Jarvis"** |
| 🔄 | **Dual AI Backend** | Swap Groq ↔ Gemini with a few commented lines in `app.py` |
| 🧠 | **Persistent Memory** | Chat history saved to `jarvis_memory.db` — survives server restarts |

---

## 🗂️ Project Structure

```
mega_project1-JARVIS/
│
├── 🚀  app.py                 # Flask app — routes, AI, SQLite memory, all commands
├── 🎙️  main.py                # Standalone CLI voice assistant (mic input + TTS)
├── 🎵  musicLibrary.py        # 148 songs — Arijit, Atif, Taylor Swift, BTS & more
├── 💾  jarvis_memory.db       # Auto-created — SQLite chat history (persistent)
│
├── templates/
│   └── 🎨  index.html         # Stark Industries holographic HUD — single-page UI
│
├── static/
│   ├── css/
│   │   └── 💅  style.css      # Arc reactor, particle canvas, glassmorphism, scanlines
│   └── js/
│       └── ⚡  script.js       # Waveform viz, particle BG, voice recognition, UI
│
├── 🔐  .env                   # Your API keys — NEVER commit this!
├── ✅  .env.example            # Safe template for collaborators
├── 📦  requirements.txt        # Python dependencies
├── 🚫  .gitignore              # Excludes .env, DB, venv, cache
└── 📖  README.md               # You are here
```

### Architecture Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Browser (Holographic HUD)                   │
│  script.js ──[POST /api/command]──► Flask (app.py)            │
│             ◄──[JSON response]──────                           │
│  Particle canvas · Waveform viz · Sir/Ma'am · Quick commands  │
└──────────────────────────┬────────────────────────────────────┘
                            │  Routes to one of:
         ┌──────────────────┼────────────────────┬─────────────┐
         ▼                  ▼                    ▼             ▼
  Groq / Gemini       External APIs        Local System    SQLite DB
  (Qwen3-27B AI)   (wttr.in, Google      (subprocess    (persistent
  + SQLite memory   News, Wiki, Jokes)    → open apps)    memory)
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+** installed
- A free **[Groq API key](https://console.groq.com/keys)** *(under 1 minute to get)*
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
# Required — powers the Qwen3-27B AI chat
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

Say **"Jarvis"** to wake it up, then speak any command.

> ⚠️ **PyAudio on Windows failing?**
> ```bash
> pip install pipwin && pipwin install pyaudio
> ```

---

## 💬 Example Commands

| You say… | JARVIS responds… |
|---|---|
| `Hello Jarvis` | "Hello, Sir. All systems are fully operational." |
| `My name is Priya` | Switches to **Ma'am** for the rest of the session |
| `What's the weather in Tokyo?` | Live card — temp, feels-like, humidity, wind, visibility |
| `Tech news` | Top technology headlines with sources & links |
| `Play anti hero` | Opens Taylor Swift — Anti-Hero on YouTube |
| `Play kesariya` | Opens Arijit Singh — Kesariya on YouTube |
| `Play dynamite` | Opens BTS — Dynamite on YouTube |
| `Tell me about black holes` | 3-sentence Wikipedia summary |
| `Tell me a joke` | Safe joke + JARVIS quip |
| `Calculate 18 percent of 5000` | "The answer is 900, Sir." |
| `Flip a coin` | "It's Heads, Sir. The arc reactor chose this one." |
| `Roll a 20-sided die` | "You rolled a 14 on a 20-sided die, Sir." |
| `Random number between 50 and 200` | "Your random number between 50 and 200 is 137, Sir." |
| `What's my IP address?` | Reads your local IP |
| `Lock my screen` | Instantly locks Windows workstation |
| `Volume up` | Increases system volume |
| `Battery status` | Reports % and charging state |
| `Open VS Code` | Launches Visual Studio Code |
| `What time is it?` | "The current time is 08:42 PM, Sir." |
| `Who created you?` | Stark-level wit via Qwen3 AI |
| `Clear your memory` | Wipes the SQLite conversation history |

---

## 🎵 Music Library

**148 tracks** across 7 artist sections + genres. Just say `"play <song name>"`:

| Artist | Popular Songs You Can Play |
|---|---|
| 🎤 **Arijit Singh** | Kesariya, Channa Mereya, Khairiyat, Tum Hi Ho, Bekhayali, Kabira + 14 more |
| 🎤 **Atif Aslam** | Teri Galliyan, Aadat, Doorie, Tajdar-e-Haram, Woh Lamhe + 9 more |
| 🎤 **Taylor Swift** | Anti Hero, Cruel Summer, Cardigan, Lavender Haze, Blank Space + 9 more |
| 🎤 **BTS** | Dynamite, Butter, Boy With Luv, Spring Day, Fake Love + 7 more |
| 🎤 **Justin Bieber** | Baby, Sorry, Love Yourself, Peaches, Ghost + 6 more |
| 🎤 **Dua Lipa** | New Rules, Don't Start Now, Levitating, Physical, Cold Heart + 6 more |
| 🎧 **Bollywood** | Chaiyya Chaiyya, Kun Faya Kun, Bulleya, Ghungroo + 18 more |
| 🎧 **Lofi / Chill** | Lofi Hip Hop, Study Music, Deep Focus, Night Lofi |
| 🦾 **Marvel OST** | Iron Man Theme, Avengers Theme, Endgame Theme |

> If a song isn't in the library, JARVIS automatically falls back to a **YouTube search**.

Add your own in [`musicLibrary.py`](musicLibrary.py):
```python
"your song name": "https://www.youtube.com/watch?v=VIDEO_ID",
```

---

## 🔐 Environment Variables

| Variable | Required | Description | Get it here |
|---|:---:|---|---|
| `GROQ_API_KEY` | ✅ **Yes** | Powers Qwen3-27B AI chat | [console.groq.com/keys](https://console.groq.com/keys) |
| `GEMINI_API_KEY` | ❌ Optional | Google Gemini 1.5 Flash fallback | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

> ⚠️ **Security:** `.env` is listed in `.gitignore`. **Never commit it.** Use `.env.example` for collaborators.

---

## 🔄 Switching AI Backend: Groq ↔ Gemini

JARVIS ships with **Groq (Qwen3-27B)** active. To switch to **Google Gemini 1.5 Flash**:

1. Add your key to `.env`: `GEMINI_API_KEY=your_key`
2. In `app.py`, **uncomment** the Gemini setup block and `init_gemini()` call
3. **Uncomment** the `ask_gemini()` function
4. In `process_command()`, replace `ask_groq(c)` → `ask_gemini(c)`
5. **Comment out** the Groq block

> 📝 Step-by-step comments are already in `app.py` — just follow them.

---

## 🧠 Persistent Memory

JARVIS uses **SQLite** to remember your conversations across server restarts:

- History stored in `jarvis_memory.db` (auto-created on first run)
- Last **10 turns** are loaded as context with every AI request
- To clear memory: say `"clear your memory"` or `POST /api/clear-memory`

```bash
# Manually wipe memory
curl -X POST http://localhost:5000/api/clear-memory
```

---

## 📦 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.10+, Flask 3.1 | HTTP server, routing, business logic |
| **AI (Primary)** | Groq Cloud — Qwen3-27B | Ultra-fast AI chat with persistent multi-turn memory |
| **AI (Fallback)** | Google Gemini 1.5 Flash | Optional swap-in AI backend |
| **Memory** | SQLite (built-in) | Persistent conversation history across restarts |
| **Frontend** | HTML5, CSS3, Vanilla JS | Holographic HUD with particle canvas + waveform |
| **Weather** | [wttr.in](https://wttr.in) JSON API | Live weather — no key needed |
| **News** | Google News RSS | Real-time categorized headlines |
| **Knowledge** | MediaWiki REST API | Wikipedia 3-sentence summaries |
| **Humor** | [JokeAPI v2](https://jokeapi.dev) | Safe curated jokes |
| **Voice (CLI)** | SpeechRecognition + pyttsx3 + PyAudio | Mic input + TTS output |

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|:---:|---|
| `/` | `GET` | Serves the Stark Industries holographic HUD |
| `/api/command` | `POST` | Main command handler — `{ "command": "..." }` |
| `/api/weather?city=Delhi` | `GET` | Returns raw weather JSON for any city |
| `/api/music` | `GET` | Returns the full music library as JSON |
| `/api/clear-memory` | `POST` | Wipes the SQLite conversation history |

**Sample `POST /api/command` response:**
```json
{
  "speak":            "Current conditions in Delhi, India, Sir: Sunny, 36°C — feels like 39°C.",
  "action":           "show_weather",
  "target":           { "city": "Delhi, India", "temp_c": "36", "humidity": "42", ... },
  "original_command": "what's the weather in Delhi"
}
```

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
4. Run `python -c "from groq import Groq; print('OK')"` to test the package
</details>

<details>
<summary><strong>🔴 Groq model error — model not found</strong></summary>
<br/>

Groq rotates their model catalogue. Check what's available on your account:
```bash
python -c "from groq import Groq; import os; [print(m.id) for m in Groq(api_key=os.getenv('GROQ_API_KEY')).models.list().data]"
```
Then update `GROQ_MODEL` in `app.py` line ~112.
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

<details>
<summary><strong>🔴 JARVIS still says "Sir" after I gave my name</strong></summary>
<br/>

Say it clearly as a full sentence:
- ✅ `"My name is Priya"` — switches to Ma'am
- ✅ `"Call me Ma'am"` — explicit override
- ✅ `"I am a girl"` — switches to Ma'am
- The title persists for the current session only (until Flask restarts)
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

- 🔊 ElevenLabs TTS — real JARVIS movie voice
- 📸 Screenshot + Gemini Vision — "what's on my screen?"
- 📅 Google Calendar integration
- 📈 Stock prices via Yahoo Finance API
- 🌍 Multi-language voice support
- 📱 PWA — install JARVIS as a desktop app
- 🔔 Desktop push notifications / reminders
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
