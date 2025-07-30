import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def processCommand(c):
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
    #elif c.lower().startswith("play"):
    elif c.startswith("play"):
     parts = c.split(" ", 1)
     if len(parts) == 2:
        song = parts[1]
        print("Looking for song:", song)
        print("Available songs:", musicLibrary.music.keys())
        if song in musicLibrary.music:
            link = musicLibrary.music[song]
            webbrowser.open(link)
            speak(f"Playing {song}")
        else:
            speak(f"Sorry, I couldn't find the song '{song}' in your music library.")
     else:
        speak("Please say the name of the song you want me to play.")

        #song=c.lower().split(" ")[1]
        # link=musicLibrary.music[song]
        # webbrowser.open(link)

    elif "news" in c.lower():
    #...............................................

if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word 'Jarvis'...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)
                word = recognizer.recognize_google(audio)
                print("You said:", word)

                if "jarvis" in word.lower():
                    speak("Ya")
                    with sr.Microphone() as source:
                        print("Jarvis is Active. Listening for command...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        command = recognizer.recognize_google(audio)
                        print("Command:", command)
                        processCommand(command)

        except sr.WaitTimeoutError:
            print("Timeout. No speech detected.")
        except sr.UnknownValueError:
            print("Sorry, could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print("Error:", e)
