import os
import sys
import json
import random
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
GROK_API_KEY = os.getenv("GROK_API_KEY", "")

# ── Groq AI Setup ─────────────────────────────────────────────────────────────
_groq_client = None
_chat_history = []  # multi-turn conversation memory

SYSTEM_PROMPT = (
    "You are J.A.R.V.I.S., an advanced AI assistant created by Tony Stark. "
    "You are witty, precise, and highly intelligent. "
    "Keep answers concise (2-3 sentences max) unless the user asks for detail. "
    "Speak in a confident, slightly formal tone — like a brilliant butler who also "
    "happens to be smarter than everyone in the room."
)

def init_groq():
    global _groq_client
    if not GROK_API_KEY:
        print("[JARVIS] Warning: No GROK_API_KEY in .env — AI fallback disabled.")
        return
    try:
        from groq import Groq
        _groq_client = Groq(api_key=GROK_API_KEY)
        print("[JARVIS] Groq AI initialized successfully.")
    except Exception as e:
        print(f"[JARVIS] Groq init failed: {e}")

init_groq()


# ── Flask App ──────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def ask_groq(user_message: str) -> str:
    """Send a message to Groq (LLaMA 3.3) with multi-turn chat history."""
    global _groq_client, _chat_history
    if not _groq_client:
        return "My AI core is offline. Please check your GROK_API_KEY in the .env file."
    try:
        # Build messages list: system prompt + last 10 turns + new user message
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for msg in _chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        completion = _groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=256,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content.strip()
        # Store turns in history
        _chat_history.append({"role": "user",      "content": user_message})
        _chat_history.append({"role": "assistant",  "content": reply})
        return reply
    except Exception as e:
        print(f"[JARVIS] Groq error: {e}")
        return "I encountered an issue with my AI core. Please try again."


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
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&list=search&srsearch={urllib.parse.quote(query)}"
            "&format=json&srlimit=1"
        )
        search_resp = requests.get(search_url, timeout=5).json()
        results = search_resp.get("query", {}).get("search", [])
        if not results:
            return f"I couldn't find any Wikipedia article about '{query}'."

        page_id = results[0]["pageid"]
        extract_url = (
            "https://en.wikipedia.org/w/api.php"
            f"?action=query&prop=extracts&exintro&explaintext"
            f"&pageids={page_id}&format=json&exsentences=3"
        )
        extract_resp = requests.get(extract_url, timeout=5).json()
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


def open_app(app_name: str) -> tuple[str, bool]:
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
                return f"Opening {name.title()} for you, Sir.", True
            except Exception as e:
                return f"I couldn't open {name}. Error: {e}", False
    return f"I don't know how to open '{app_name}'.", False


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


@app.route("/api/command", methods=["POST"])
def process_command():
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

    # ── 1. Greeting ────────────────────────────────────────────────────────────
    if any(g in cl for g in ["hello jarvis", "hi jarvis", "hey jarvis"]):
        response["speak"] = "Hello. All systems are fully operational. How may I assist you today?"

    elif "how are you" in cl:
        response["speak"] = "Running at peak efficiency, thank you for asking. All neural pathways are clear."

    elif "who are you" in cl or "what are you" in cl:
        response["speak"] = (
            "I am J.A.R.V.I.S. — Just A Rather Very Intelligent System. "
            "Your digital assistant, at your service."
        )

    elif "thank you" in cl or "thanks jarvis" in cl:
        response["speak"] = "Always a pleasure. Is there anything else you need?"

    # ── 2. Time & Date ─────────────────────────────────────────────────────────
    elif "what time" in cl or "current time" in cl:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        response["speak"] = f"The current time is {time_str}, Sir."

    elif "what date" in cl or "what's today" in cl or "today's date" in cl:
        today = date.today().strftime("%B %d, %Y")
        response["speak"] = f"Today is {today}, Sir."

    elif "what day" in cl:
        day = datetime.now().strftime("%A")
        response["speak"] = f"Today is {day}, Sir."

    # ── 3. Open websites ───────────────────────────────────────────────────────
    elif "open google" in cl:
        response.update(speak="Opening Google.", action="open_url", target="https://google.com")

    elif "open youtube" in cl:
        response.update(speak="Opening YouTube.", action="open_url", target="https://youtube.com")

    elif "open facebook" in cl:
        response.update(speak="Opening Facebook.", action="open_url", target="https://facebook.com")

    elif "open linkedin" in cl:
        response.update(speak="Opening LinkedIn.", action="open_url", target="https://linkedin.com")

    elif "open github" in cl:
        response.update(speak="Opening GitHub.", action="open_url", target="https://github.com")

    elif "open instagram" in cl:
        response.update(speak="Opening Instagram.", action="open_url", target="https://instagram.com")

    elif "open twitter" in cl or "open x" in cl:
        response.update(speak="Opening X, formerly known as Twitter.", action="open_url", target="https://x.com")

    elif "open wikipedia" in cl:
        response.update(speak="Opening Wikipedia.", action="open_url", target="https://wikipedia.org")

    elif "open maps" in cl or "open google maps" in cl:
        response.update(speak="Opening Google Maps.", action="open_url", target="https://maps.google.com")

    # ── 4. Open local apps ─────────────────────────────────────────────────────
    elif "open " in cl and any(
        app in cl for app in [
            "notepad", "calculator", "paint", "file explorer", "explorer",
            "task manager", "cmd", "command prompt", "vs code", "visual studio",
            "chrome", "word", "excel", "powerpoint"
        ]
    ):
        app_query = cl.replace("open ", "").strip()
        msg, success = open_app(app_query)
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
                speak=f"Playing {matched} from your library, Sir.",
                action="open_url",
                target=musicLibrary.music[matched]
            )
        else:
            search_url = f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
            response.update(
                speak=f"I couldn't find that in the library. Searching YouTube for {song_query}.",
                action="open_url",
                target=search_url
            )

    # ── 6. News ────────────────────────────────────────────────────────────────
    elif "news" in cl:
        news_data = get_news()
        if news_data:
            response.update(
                speak="Here are the top headlines I found for you, Sir.",
                action="show_news",
                target=news_data
            )
        else:
            response["speak"] = "I'm unable to retrieve the news feed at the moment."

    # ── 7. Weather ─────────────────────────────────────────────────────────────
    elif "weather" in cl:
        # Try to extract city name: "weather in Delhi", "what's the weather in Mumbai"
        city = "Delhi"  # default
        for prep in ["weather in ", "weather for ", "weather of "]:
            if prep in cl:
                city = cl.split(prep, 1)[1].strip().title()
                break
        weather = get_weather(city)
        if weather.get("success"):
            response.update(
                speak=(
                    f"Current weather in {weather['city']}: "
                    f"{weather['description']}, {weather['temp_c']} degrees Celsius. "
                    f"Humidity is {weather['humidity']} percent and wind speed is {weather['wind_kmph']} kilometres per hour."
                ),
                action="show_weather",
                target=weather
            )
        else:
            response["speak"] = f"I couldn't fetch the weather for {city}. Please check your connection."

    # ── 8. Wikipedia ───────────────────────────────────────────────────────────
    elif "tell me about" in cl or "what is" in cl or "who is" in cl or "wikipedia" in cl:
        for prefix in ["tell me about ", "what is ", "who is ", "wikipedia ", "search wikipedia for "]:
            if cl.startswith(prefix):
                query = cl.replace(prefix, "").strip()
                break
        else:
            query = cl

        if query:
            summary = search_wikipedia(query)
            response.update(
                speak=summary,
                action="show_info",
                target={"title": query.title(), "text": summary}
            )
        else:
            response["speak"] = "What would you like me to look up?"

    # ── 9. Joke ────────────────────────────────────────────────────────────────
    elif "joke" in cl or "tell me a joke" in cl or "make me laugh" in cl:
        joke = get_joke()
        response["speak"] = joke

    # ── 10. Google Search ─────────────────────────────────────────────────────
    elif "search" in cl or "google" in cl:
        query = cl
        for kw in ["search for ", "search ", "google "]:
            if kw in cl:
                query = cl.split(kw, 1)[1].strip()
                break
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        response.update(
            speak=f"Searching Google for {query}.",
            action="open_url",
            target=search_url
        )

    # ── 11. Groq AI Fallback ───────────────────────────────────────────────────
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
