import os
import sys
import webbrowser
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request
import musicLibrary

app = Flask(__name__)

# Function to fetch news headlines from Google News RSS
def get_news():
    try:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        # Set User-Agent to avoid getting blocked
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        response = urllib.request.urlopen(req, timeout=5)
        data = response.read()
        root = ET.fromstring(data)
        news_list = []
        for item in root.findall('.//item')[:6]:  # Get top 6 articles
            title = item.find('title').text
            link = item.find('link').text
            pub_date = item.find('pubDate').text
            
            # Extract source from title if possible (e.g. "Title - Source")
            source = "Google News"
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1]
                
            news_list.append({
                "title": title,
                "link": link,
                "source": source,
                "date": pub_date
            })
        return news_list
    except Exception as e:
        print("Error fetching news:", e)
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/music', methods=['GET'])
def get_music():
    # Return list of songs from musicLibrary
    songs = [{"name": key, "url": val} for key, val in musicLibrary.music.items()]
    return jsonify(songs)

@app.route('/api/command', methods=['POST'])
def process_command():
    data = request.json or {}
    c = data.get("command", "").strip().lower()
    
    response = {
        "speak": "",
        "action": "none",
        "target": "",
        "original_command": c
    }
    
    if not c:
        response["speak"] = "I didn't catch that. Could you repeat?"
        return jsonify(response)
    
    # 1. Open common websites
    if "open google" in c:
        response["speak"] = "Opening Google"
        response["action"] = "open_url"
        response["target"] = "https://google.com"
        
    elif "open facebook" in c:
        response["speak"] = "Opening Facebook"
        response["action"] = "open_url"
        response["target"] = "https://facebook.com"
        
    elif "open youtube" in c:
        response["speak"] = "Opening YouTube"
        response["action"] = "open_url"
        response["target"] = "https://youtube.com"
        
    elif "open linkedin" in c:
        response["speak"] = "Opening LinkedIn"
        response["action"] = "open_url"
        response["target"] = "https://linkedin.com"
        
    elif "open github" in c:
        response["speak"] = "Opening GitHub"
        response["action"] = "open_url"
        response["target"] = "https://github.com"
        
    # 2. Play music from library or search YouTube
    elif c.startswith("play "):
        song_query = c.replace("play ", "").strip()
        matched_song = None
        
        # Check direct match
        for s in musicLibrary.music.keys():
            if s == song_query or s in song_query or song_query in s:
                matched_song = s
                break
                
        if matched_song:
            link = musicLibrary.music[matched_song]
            response["speak"] = f"Playing {matched_song} from your library"
            response["action"] = "open_url"
            response["target"] = link
        else:
            # Fallback to search YouTube
            search_url = f"https://www.youtube.com/results?search_query={song_query.replace(' ', '+')}"
            response["speak"] = f"Searching YouTube for {song_query}"
            response["action"] = "open_url"
            response["target"] = search_url
            
    # 3. News
    elif "news" in c:
        news_data = get_news()
        if news_data:
            response["speak"] = "Here are the top news headlines."
            response["action"] = "show_news"
            response["target"] = news_data
        else:
            response["speak"] = "Sorry, I couldn't fetch the news right now."
            
    # 4. Web Search
    elif "search" in c:
        search_query = c.replace("search", "").strip()
        if not search_query:
            response["speak"] = "What would you like me to search for?"
        else:
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            response["speak"] = f"Searching Google for {search_query}"
            response["action"] = "open_url"
            response["target"] = search_url
            
    # 5. Greeting commands
    elif "hello" in c or "hi jarvis" in c or "hey jarvis" in c:
        response["speak"] = "Hello! I am Jarvis, your digital assistant. How can I help you today?"
        
    elif "how are you" in c:
        response["speak"] = "I am operating at full capacity. All systems are functional. Thank you for asking!"
        
    elif "who are you" in c:
        response["speak"] = "I am Jarvis, an advanced digital assistant created using Python."
        
    # 6. Fallback
    else:
        # Search Google for the unhandled phrase to be helpful
        search_url = f"https://www.google.com/search?q={c.replace(' ', '+')}"
        response["speak"] = f"Searching Google for {c}"
        response["action"] = "open_url"
        response["target"] = search_url
        
    return jsonify(response)

if __name__ == "__main__":
    # In a local development environment, open the browser automatically
    port = 5000
    # Prevent browser from opening twice and duplicate console logs due to Flask debug mode reloader
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open(f"http://127.0.0.1:{port}")
        print(f"Jarvis Web server starting locally at http://127.0.0.1:{port}")
        print(f"To access on mobile/tablet (same Wi-Fi), find your local IP and use: http://<your-computer-ip>:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
