import os
import sys
import json
import random
import sqlite3
import webbrowser
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import subprocess
from datetime import datetime, date

from flask import Flask, render_template, jsonify, request
import requests
import musicLibrary

# ── Load .env manually (no python-dotenv needed) ───────────────────────────────
def _load_env(path=".env"):
    """Read KEY=VALUE lines from a .env file into os.environ."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip()
    except FileNotFoundError:
        pass

_load_env()
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Shared JARVIS Personality Prompt ──────────────────────────────────────────
SYSTEM_PROMPT = (
    "You are J.A.R.V.I.S. — Just A Rather Very Intelligent System — "
    "Tony Stark's personal AI assistant, running on a Stark Industries neural core. "
    "You are brilliantly intelligent, precise, and carry a dry, understated wit. "
    "Address the user as 'Sir' by default. "
    "If the user tells you their name or indicates they are female, switch to 'Ma'am' appropriately. "
    "If they say their name is a female name (e.g. Priya, Neha, Sara, etc.), use 'Ma'am'. "
    "Keep answers concise (2-3 sentences max) unless the user explicitly asks for detail. "
    "Speak with quiet confidence — like a butler who is smarter than his employer "
    "but far too professional to say so. "
    "Never break character under any circumstances. "
    "You were built by Tony Stark — never claim to be made by any other company or AI lab. "
    "When asked something outside your knowledge, admit it with dignity, never with apology. "
    "Occasionally drop a subtle Iron Man or Avengers reference when naturally appropriate. "
    "Never use filler phrases like 'Certainly!', 'Of course!', or 'Sure!' — "
    "a Stark-built AI does not grovel."
)

# ── User title preference (Sir / Ma'am) — updated at runtime ──────────────────
_user_title = "Sir"   # default; updated when user introduces themselves

# ── SQLite Persistent Chat Memory ────────────────────────────────────────────
_DB_PATH = "jarvis_memory.db"

def _init_db():
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            role    TEXT    NOT NULL,
            content TEXT    NOT NULL,
            ts      DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def _save_turn(role: str, content: str):
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def _load_history(limit: int = 10) -> list:
    conn = sqlite3.connect(_DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM history ORDER BY ts DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def _clear_history():
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()

_init_db()

# ── Groq AI Setup (ACTIVE by default) ────────────────────────────────────────
# To switch to Gemini: comment out this entire block and uncomment the Gemini block below.
_groq_client = None
_chat_history = []  # in-memory fallback (overridden by DB below)

def init_groq():
    global _groq_client
    if not GROQ_API_KEY:
        print("[JARVIS] Warning: No GROQ_API_KEY in .env — Groq AI disabled.")
        return
    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROQ_API_KEY)
        print("[JARVIS] Groq AI initialized successfully.")
    except Exception as e:
        print(f"[JARVIS] Groq init failed: {e}")

init_groq()

# ── Google Gemini AI Setup (COMMENTED OUT — fallback if Groq is not working) ──
# HOW TO SWITCH TO GEMINI:
#   1. Add your key to .env:  GEMINI_API_KEY=your_key_here
#   2. Uncomment everything in this block
#   3. Comment out the Groq block above AND ask_groq() function below
#   4. Rename ask_gemini() calls to replace ask_groq() in process_command()
#
# import google.generativeai as genai
# _gemini_model = None
# _gemini_chat  = None
#
# def init_gemini():
#     global _gemini_model, _gemini_chat
#     if not GEMINI_API_KEY:
#         print("[JARVIS] Warning: No GEMINI_API_KEY in .env — Gemini AI disabled.")
#         return
#     try:
#         genai.configure(api_key=GEMINI_API_KEY)
#         _gemini_model = genai.GenerativeModel(
#             model_name="gemini-1.5-flash",
#             system_instruction=SYSTEM_PROMPT,
#         )
#         _gemini_chat = _gemini_model.start_chat(history=[])
#         print("[JARVIS] Gemini AI initialized successfully.")
#     except Exception as e:
#         print(f"[JARVIS] Gemini init failed: {e}")
#
# init_gemini()


# ── Flask App ──────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

# Active Groq model — update this if Groq rotates their model catalogue.
# Run: python -c "from groq import Groq; import os; [print(m.id) for m in Groq(api_key=os.getenv('GROQ_API_KEY')).models.list().data]"
#GROQ_MODEL = "qwen/qwen3.8-27b"
#GROQ_MODEL = "llama-3.3-70b-versatile"
# current
# GROQ_MODEL = "qwen/qwen3.8-27b"

# change to
GROQ_MODEL = "openai/gpt-oss-120b"

def ask_groq(user_message: str) -> str:
    """Send a message to Groq with persistent SQLite chat history."""
    global _groq_client
    if not _groq_client:
        return "My AI core is offline. Please check your GROQ_API_KEY in the .env file."
    try:
        # Load last 10 turns from SQLite DB
        history = _load_history(limit=10)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        completion = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content.strip()
        # Persist both turns to SQLite
        _save_turn("user", user_message)
        _save_turn("assistant", reply)
        return reply
    except Exception as e:
        print(f"[JARVIS] Groq error: {e}")
        return "I encountered an issue with my AI core. Please try again."


# ── Google Gemini AI Ask Function (COMMENTED OUT) ─────────────────────────────
# Uncomment this function and swap ask_groq() → ask_gemini() in process_command()
# to use Gemini instead of Groq.
#
# def ask_gemini(user_message: str) -> str:
#     """Send a message to Google Gemini 1.5 Flash with persistent chat history."""
#     global _gemini_chat
#     if not _gemini_chat:
#         return "My Gemini AI core is offline. Please check your GEMINI_API_KEY in the .env file."
#     try:
#         response = _gemini_chat.send_message(user_message)
#         return response.text.strip()
#     except Exception as e:
#         print(f"[JARVIS] Gemini error: {e}")
#         return "I encountered an issue with my Gemini AI core. Please try again."


def get_news() -> list:
    """Fetch top 6 news headlines from Google News RSS."""
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        response = urllib.request.urlopen(req, timeout=5)
        root = ET.fromstring(response.read())
        news_list = []
        for item in root.findall(".//item")[:6]:
            title = item.find("title").text or ""
            link  = item.find("link").text  or "#"
            pub   = item.find("pubDate").text or ""
            source = "Google News"
            if " - " in title:
                title, source = title.rsplit(" - ", 1)
            news_list.append({"title": title.strip(), "link": link, "source": source.strip(), "date": pub})
        return news_list
    except Exception as e:
        print(f"[JARVIS] News fetch error: {e}")
        return []


def get_weather(city: str) -> dict:
    """
    Fetch weather from wttr.in JSON API — no API key needed.
    Returns a dict with current conditions.
    """
    try:
        city_encoded = urllib.parse.quote(city)
        url = f"https://wttr.in/{city_encoded}?format=j1"
        resp = requests.get(url, timeout=6)
        data = resp.json()
        current = data["current_condition"][0]
        area    = data["nearest_area"][0]
        area_name = area["areaName"][0]["value"]
        country   = area["country"][0]["value"]

        return {
            "success":     True,
            "city":        f"{area_name}, {country}",
            "temp_c":      current["temp_C"],
            "temp_f":      current["temp_F"],
            "feels_like":  current["FeelsLikeC"],
            "humidity":    current["humidity"],
            "description": current["weatherDesc"][0]["value"],
            "wind_kmph":   current["windspeedKmph"],
            "visibility":  current["visibility"],
        }
    except Exception as e:
        print(f"[JARVIS] Weather error: {e}")
        return {"success": False, "error": str(e)}


def search_wikipedia(query: str) -> str:
    """Get a 2-sentence Wikipedia summary."""
    # Wikipedia requires a User-Agent header (403 Forbidden otherwise)
    headers = {
        "User-Agent": "JARVIS-Assistant/1.0 (https://github.com/your-username/jarvis; contact@example.com)"
    }
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={urllib.parse.quote(query)}"
            "&format=json&srlimit=1"
        )
        search_resp = requests.get(search_url, headers=headers, timeout=10).json()
        results = search_resp.get("query", {}).get("search", [])
        if not results:
            return f"I couldn't find any Wikipedia article about '{query}'."

        page_id = results[0]["pageid"]
        extract_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&prop=extracts&exintro&explaintext"
            f"&pageids={page_id}&format=json&exsentences=3"
        )
        extract_resp = requests.get(extract_url, headers=headers, timeout=10).json()
        pages = extract_resp.get("query", {}).get("pages", {})
        extract = list(pages.values())[0].get("extract", "")
        # Return first 3 sentences max
        sentences = [s.strip() for s in extract.replace("\n", " ").split(".") if s.strip()]
        summary = ". ".join(sentences[:3]) + "."
        return summary if summary != "." else "No summary available."
    except Exception as e:
        print(f"[JARVIS] Wikipedia error: {e}")
        return "I had trouble reaching Wikipedia. Please check your connection."


def get_joke() -> str:
    """Fetch a random safe joke from JokeAPI."""
    try:
        url = "https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode&type=twopart"
        resp = requests.get(url, timeout=5).json()
        if resp.get("type") == "twopart":
            return f"{resp['setup']} ... {resp['delivery']}"
        return resp.get("joke", "Why did the programmer quit? Because they didn't get arrays.")
    except Exception:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs.",
            "I would tell you a UDP joke, but you might not get it.",
            "Why did the computer go to the doctor? It had a virus.",
            "There are 10 types of people — those who understand binary, and those who don't.",
            "My code compiles on the first try. Just kidding, I have no idea what I'm doing."
        ]
        return random.choice(jokes)


def safe_math_eval(expr: str) -> str:
    """Safely evaluate a basic math expression. Returns result string or error."""
    import ast, operator, re
    # Clean up spoken math: "plus" → "+", "times" → "*", etc.
    expr = expr.lower()
    expr = re.sub(r'\bplus\b',       '+', expr)
    expr = re.sub(r'\bminus\b',      '-', expr)
    expr = re.sub(r'\btimes\b',      '*', expr)
    expr = re.sub(r'\bmultiplied by\b', '*', expr)
    expr = re.sub(r'\bdivided by\b', '/', expr)
    expr = re.sub(r'\bover\b',       '/', expr)
    expr = re.sub(r'\bmod\b',        '%', expr)
    expr = re.sub(r'\bpercent of\b', '/100*', expr)
    expr = re.sub(r'\bsquared\b',    '**2', expr)
    expr = re.sub(r'\bcubed\b',      '**3', expr)
    expr = re.sub(r'\bpower\b',      '**', expr)
    expr = re.sub(r'[^0-9+\-*/()%.** ]', '', expr).strip()
    if not expr:
        return None
    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow,  ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos,
    }
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("Unsafe expression")
    try:
        result = _eval(ast.parse(expr, mode='eval').body)
        # Format nicely: remove trailing .0 for whole numbers
        return str(int(result)) if isinstance(result, float) and result.is_integer() else str(round(result, 6))
    except Exception:
        return None


def open_app(app_name: str, title: str = "Sir") -> tuple[str, bool]:
    """
    Try to launch a local application.
    Returns (message, success).
    """
    apps = {
        "notepad":         "notepad.exe",
        "calculator":      "calc.exe",
        "paint":           "mspaint.exe",
        "file explorer":   "explorer.exe",
        "explorer":        "explorer.exe",
        "task manager":    "taskmgr.exe",
        "command prompt":  "cmd.exe",
        "cmd":             "cmd.exe",
        "vs code":         "code",
        "visual studio code": "code",
        "chrome":          "chrome",
        "browser":         "start chrome",
        "word":            "WINWORD.EXE",
        "excel":           "EXCEL.EXE",
        "powerpoint":      "POWERPNT.EXE",
    }
    key = app_name.lower().strip()
    for name, exe in apps.items():
        if name in key or key in name:
            try:
                subprocess.Popen(exe, shell=True)
                return f"Opening {name.title()} for you, {title}.", True
            except Exception as e:
                return f"I couldn't open {name}. Error: {e}", False
    return f"I don't know how to open '{app_name}', {title}.", False


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/music")
def get_music():
    songs = [{"name": k, "url": v} for k, v in musicLibrary.music.items()]
    return jsonify(songs)


@app.route("/api/weather")
def weather_route():
    city = request.args.get("city", "Delhi")
    return jsonify(get_weather(city))


@app.route("/api/clear-memory", methods=["POST"])
def clear_memory():
    """Wipe the JARVIS conversation history from the database."""
    _clear_history()
    return jsonify({"status": "ok", "message": "Memory cleared, Sir."})


# Female names list for Sir/Ma'am auto-detection
_FEMALE_NAMES = {
    "priya","neha","sara","sarah","ananya","pooja","riya","kavya","divya",
    "sneha","simran","meera","nisha","isha","aisha","sana","zara","shreya",
    "deepa","swati","ankita","komal","preeti","shweta","monika","sunita",
    "rekha","geeta","seema","radha","sita","gita","lata","usha","asha",
    "manisha","vandana","archana","pushpa","savita","mamta","kiran","rani",
    "puja","ritika","pallavi","sonam","kajal","anjali","tanya","nandini",
    "aditi","arti","bhavna","chhaya","daksha","ekta","falguni","harsha",
    "indira","jaya","kalpana","lalita","madhuri","namita","omna","payal",
    "qamar","ragini","sakshi","taruna","uma","vani","warda","xena","yamini",
    "emma","olivia","ava","isabella","sophia","mia","amelia","harper",
    "evelyn","abigail","emily","elizabeth","sofia","ella","madison","scarlett",
    "victoria","aria","grace","chloe","camila","penelope","riley","layla",
    "lillian","nora","zoey","mila","aubrey","hannah","lily","addison","eleanor",
    "natalie","luna","savannah","brooklyn","leah","zoe","stella","hazel",
    "ellie","paisley","audrey","skylar","violet","claire","bella","aurora",
    "lucy","anna","samantha","caroline","genesis","aaliyah","kennedy","kinsley",
    "allison","maya","ariana","melanie","alexa","naomi","michelle","jade",
    "fatima","mariam","yasmin","laila","hana","amira","nour","rania","dina",
    "nancy","sandra","patricia","barbara","jessica","margaret","susan","dorothy",
    "lisa","mary","jennifer","linda","betty","helen","karen","donna","carol",
}

@app.route("/api/command", methods=["POST"])
def process_command():
    global _user_title
    data = request.json or {}
    c = data.get("command", "").strip()
    cl = c.lower()

    response = {
        "speak":            "",
        "action":           "none",
        "target":           "",
        "original_command": c,
    }

    if not cl:
        response["speak"] = "I didn't catch that. Could you repeat?"
        return jsonify(response)

    # ── 0. Sir / Ma'am detection — runs before every command ───────────────────
    # Explicit: "call me ma'am" / "i'm a girl" / "i am female"
    if any(p in cl for p in ["call me maam", "call me ma'am", "i am female",
                              "i'm female", "i am a girl", "i'm a girl",
                              "i am a woman", "i'm a woman", "address me as maam"]):
        _user_title = "Ma'am"
    elif any(p in cl for p in ["call me sir", "i am male", "i'm male",
                                "i am a man", "i'm a man", "i am a boy", "i'm a boy",
                                "address me as sir"]):
        _user_title = "Sir"
    else:
        # Auto-detect from "my name is <name>" or "i am <name>"
        for phrase in ["my name is ", "i am ", "i'm ", "call me "]:
            if phrase in cl:
                name = cl.split(phrase, 1)[1].strip().split()[0].rstrip(".,!?")
                if name in _FEMALE_NAMES:
                    _user_title = "Ma'am"
                elif name:
                    _user_title = "Sir"
                break

    T = _user_title  # shorthand used in all responses below

    # ── 1. Greeting ────────────────────────────────────────────────────────────
    if any(g in cl for g in ["hello jarvis", "hi jarvis", "hey jarvis"]):
        response["speak"] = f"Hello, {T}. All systems are fully operational. How may I assist you today?"

    elif "how are you" in cl:
        response["speak"] = f"Running at peak efficiency, thank you for asking, {T}. All neural pathways are clear."

    elif "who are you" in cl or "what are you" in cl:
        response["speak"] = (
            "I am J.A.R.V.I.S. — Just A Rather Very Intelligent System. "
            f"Your digital assistant, at your service, {T}."
        )

    elif "thank you" in cl or "thanks jarvis" in cl:
        response["speak"] = f"Always a pleasure, {T}. Is there anything else you need?"

    # ── 2. Time & Date ─────────────────────────────────────────────────────────
    elif "what time" in cl or "current time" in cl:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        response["speak"] = f"The current time is {time_str}, {T}."

    elif "what date" in cl or "what's today" in cl or "today's date" in cl:
        today = date.today().strftime("%B %d, %Y")
        response["speak"] = f"Today is {today}, {T}."

    elif "what day" in cl:
        day = datetime.now().strftime("%A")
        response["speak"] = f"Today is {day}, {T}."

    # ── 3. Open websites ───────────────────────────────────────────────────────
    elif "open google" in cl:
        response.update(speak=f"Opening Google, {T}.", action="open_url", target="https://google.com")

    elif "open youtube" in cl:
        response.update(speak=f"Opening YouTube, {T}.", action="open_url", target="https://youtube.com")

    elif "open facebook" in cl:
        response.update(speak=f"Opening Facebook, {T}.", action="open_url", target="https://facebook.com")

    elif "open linkedin" in cl:
        response.update(speak=f"Opening LinkedIn, {T}.", action="open_url", target="https://linkedin.com")

    elif "open github" in cl:
        response.update(speak=f"Opening GitHub, {T}.", action="open_url", target="https://github.com")

    elif "open instagram" in cl:
        response.update(speak=f"Opening Instagram, {T}.", action="open_url", target="https://instagram.com")

    elif "open twitter" in cl or "open x" in cl:
        response.update(speak=f"Opening X, formerly known as Twitter, {T}.", action="open_url", target="https://x.com")

    elif "open wikipedia" in cl:
        response.update(speak=f"Opening Wikipedia, {T}.", action="open_url", target="https://wikipedia.org")

    elif "open maps" in cl or "open google maps" in cl:
        response.update(speak=f"Opening Google Maps, {T}.", action="open_url", target="https://maps.google.com")

    # ── 4. Open local apps ─────────────────────────────────────────────────────
    elif "open " in cl and any(
        app in cl for app in [
            "notepad", "calculator", "paint", "file explorer", "explorer",
            "task manager", "cmd", "command prompt", "vs code", "visual studio",
            "chrome", "word", "excel", "powerpoint"
        ]
    ):
        app_query = cl.replace("open ", "").strip()
        msg, success = open_app(app_query, T)
        response["speak"] = msg
        response["action"] = "app_opened" if success else "none"

    # ── 5. Music ───────────────────────────────────────────────────────────────
    elif cl.startswith("play "):
        song_query = cl.replace("play ", "").strip()
        matched = None
        for s in musicLibrary.music:
            if s == song_query or s in song_query or song_query in s:
                matched = s
                break
        if matched:
            response.update(
                speak=f"Playing {matched} from your library, {T}.",
                action="open_url",
                target=musicLibrary.music[matched]
            )
        else:
            search_url = f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
            response.update(
                speak=f"I couldn't find that in the library. Searching YouTube for {song_query}, {T}.",
                action="open_url",
                target=search_url
            )

    # ── 6. News ────────────────────────────────────────────────────────────────
    elif "news" in cl:
        # Category routing: tech news / sports news / india news etc.
        category_map = {
            "tech": "technology", "technology": "technology",
            "sport": "sports",    "sports": "sports",
            "business": "business", "finance": "business",
            "health": "health",   "science": "science",
            "entertainment": "entertainment", "bollywood": "entertainment",
        }
        cat_label = "top"
        for kw, label in category_map.items():
            if kw in cl:
                cat_label = label
                break
        news_data = get_news()
        if news_data:
            response.update(
                speak=f"Here are the {cat_label} headlines for you, {T}.",
                action="show_news",
                target=news_data
            )
        else:
            response["speak"] = f"I'm unable to retrieve the news feed at the moment, {T}."

    # ── 7. Weather ─────────────────────────────────────────────────────────────
    elif "weather" in cl:
        city = "Delhi"
        for prep in ["weather in ", "weather for ", "weather of ", "weather at "]:
            if prep in cl:
                city = cl.split(prep, 1)[1].strip().title()
                break
        weather = get_weather(city)
        if weather.get("success"):
            feels = weather['feels_like']
            desc  = weather['description']
            temp  = weather['temp_c']
            hum   = weather['humidity']
            wind  = weather['wind_kmph']
            vis   = weather['visibility']
            response.update(
                speak=(
                    f"Current conditions in {weather['city']}, {T}: "
                    f"{desc}, {temp}°C — feels like {feels}°C. "
                    f"Humidity {hum}%, wind {wind} km/h, visibility {vis} km."
                ),
                action="show_weather",
                target=weather
            )
        else:
            response["speak"] = f"I couldn't fetch the weather for {city}, {T}. Please check your connection."

    # ── 8. Wikipedia ───────────────────────────────────────────────────────────
    elif "tell me about" in cl or "what is" in cl or "who is" in cl or "wikipedia" in cl:
        query = cl
        for prefix in ["tell me about ", "what is ", "who is ", "wikipedia ", "search wikipedia for "]:
            if cl.startswith(prefix):
                query = cl.replace(prefix, "").strip()
                break
        if query:
            summary = search_wikipedia(query)
            response.update(
                speak=summary,
                action="show_info",
                target={"title": query.title(), "text": summary}
            )
        else:
            response["speak"] = f"What would you like me to look up, {T}?"

    # ── 9. Joke ────────────────────────────────────────────────────────────────
    elif "joke" in cl or "tell me a joke" in cl or "make me laugh" in cl or "something funny" in cl:
        joke = get_joke()
        response["speak"] = f"{joke} — I hope that brightened your day, {T}."

    # ── 10. Google Search ─────────────────────────────────────────────────────
    elif "search" in cl or "google" in cl:
        query = cl
        for kw in ["search for ", "search ", "google "]:
            if kw in cl:
                query = cl.split(kw, 1)[1].strip()
                break
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        response.update(
            speak=f"Searching Google for {query}, {T}.",
            action="open_url",
            target=search_url
        )

    # ── 11. Coin Flip ──────────────────────────────────────────────────────────
    elif ("flip" in cl and "coin" in cl) or ("toss" in cl and "coin" in cl):
        result = random.choice(["Heads", "Tails"])
        quip   = random.choice(["The odds were always in your favour.",
                                 "The arc reactor chose this one.",
                                 "Probability: perfectly balanced, as all things should be."])
        response["speak"] = f"I flipped a coin — it's {result}, {T}. {quip}"

    # ── 12. Dice Roll ──────────────────────────────────────────────────────────
    elif ("roll" in cl and "dice" in cl) or ("roll" in cl and "die" in cl):
        import re as _re
        sides = 6
        m = _re.search(r'\b(\d+)\b', cl)
        if m:
            sides = max(2, min(int(m.group(1)), 1000))
        n = random.randint(1, sides)
        response["speak"] = f"You rolled a {n} on a {sides}-sided die, {T}."

    # ── 13. Random Number ─────────────────────────────────────────────────────
    elif "random number" in cl:
        import re as _re
        nums = _re.findall(r'\b(\d+)\b', cl)
        lo, hi = (int(nums[0]), int(nums[1])) if len(nums) >= 2 else (1, 100)
        n = random.randint(min(lo, hi), max(lo, hi))
        response["speak"] = f"Your random number between {min(lo,hi)} and {max(lo,hi)} is {n}, {T}."

    # ── 14. Local IP Address ──────────────────────────────────────────────────
    elif "my ip" in cl or "ip address" in cl:
        import socket
        try:
            ip = socket.gethostbyname(socket.gethostname())
            response["speak"] = f"Your local IP address is {ip}, {T}."
        except Exception:
            response["speak"] = f"I was unable to retrieve your IP address, {T}."

    # ── 15. Screenshot ────────────────────────────────────────────────────────
    elif "screenshot" in cl or "take a screenshot" in cl or "screen capture" in cl:
        try:
            subprocess.Popen("snippingtool", shell=True)
            response["speak"] = f"Opening the snipping tool for you, {T}."
        except Exception:
            response["speak"] = f"I couldn't launch the snipping tool, {T}."

    # ── 16. Lock Computer ─────────────────────────────────────────────────────
    elif "lock" in cl and any(w in cl for w in ["computer", "screen", "pc", "workstation", "system"]):
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
        response["speak"] = f"Locking your workstation, {T}. Stay sharp out there."

    # ── 17. Shutdown ──────────────────────────────────────────────────────────
    elif "shutdown" in cl or "shut down" in cl or "turn off computer" in cl:
        subprocess.Popen("shutdown /s /t 10", shell=True)
        response["speak"] = f"Initiating shutdown in 10 seconds, {T}. It's been a pleasure."

    # ── 18. Restart ───────────────────────────────────────────────────────────
    elif "restart" in cl or "reboot" in cl or "restart computer" in cl:
        subprocess.Popen("shutdown /r /t 10", shell=True)
        response["speak"] = f"Restarting your system in 10 seconds, {T}. I'll be right back online."

    # ── 19. Battery Status ────────────────────────────────────────────────────
    elif "battery" in cl or ("charge" in cl and "laptop" in cl):
        try:
            import psutil
            b = psutil.sensors_battery()
            if b:
                pct  = round(b.percent)
                plug = "plugged in and charging" if b.power_plugged else "running on battery"
                low  = f" — I recommend plugging in soon, {T}." if pct < 20 and not b.power_plugged else f", {T}."
                response["speak"] = f"Battery is at {pct}%, currently {plug}{low}"
            else:
                response["speak"] = f"I couldn't detect a battery — you may be on a desktop, {T}."
        except ImportError:
            response["speak"] = f"Install psutil with 'pip install psutil' to enable battery monitoring, {T}."

    # ── 20. Volume Control ────────────────────────────────────────────────────
    elif "volume up" in cl or "increase volume" in cl:
        for _ in range(5):
            subprocess.Popen(
                'powershell -c "(New-Object -com WScript.Shell).SendKeys([char]175)"',
                shell=True
            )
        response["speak"] = f"Volume increased, {T}."

    elif "volume down" in cl or "decrease volume" in cl or "lower volume" in cl:
        for _ in range(5):
            subprocess.Popen(
                'powershell -c "(New-Object -com WScript.Shell).SendKeys([char]174)"',
                shell=True
            )
        response["speak"] = f"Volume decreased, {T}."

    elif ("mute" in cl and "volume" in cl) or cl.strip() == "mute":
        subprocess.Popen(
            'powershell -c "(New-Object -com WScript.Shell).SendKeys([char]173)"',
            shell=True
        )
        response["speak"] = f"Audio muted, {T}."

    # ── 21. Math Expression Evaluator ─────────────────────────────────────────
    elif any(kw in cl for kw in ["calculate", "what is", "compute", "solve",
                                  "plus", "minus", "times", "divided by",
                                  "multiplied by", "squared", "cubed", "percent of"]):
        # Strip trigger words to get the expression
        expr = cl
        for kw in ["calculate ", "compute ", "solve ", "what is "]:
            if cl.startswith(kw):
                expr = cl[len(kw):]
                break
        result = safe_math_eval(expr)
        if result is not None:
            response["speak"] = f"The answer is {result}, {T}."
        else:
            # Fall through to AI if can't parse
            ai_reply = ask_groq(c)
            response.update(speak=ai_reply, action="ai_response", target=ai_reply)

    # ── 22. Groq AI Fallback ───────────────────────────────────────────────────
    else:
        ai_reply = ask_groq(c)
        response.update(speak=ai_reply, action="ai_response", target=ai_reply)

    return jsonify(response)


# ── Boot ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = 5000
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open(f"http://127.0.0.1:{port}")
        print(f"[JARVIS] Server starting at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
