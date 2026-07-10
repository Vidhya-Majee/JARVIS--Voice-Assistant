// ==========================================================================
// JARVIS CORE FRONTEND CONTROLLER
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const body = document.body;
    const systemTime = document.getElementById('system-time-display');
    const systemDate = document.getElementById('system-date-display');
    const statusText = document.getElementById('status-display-text');
    const statusDot = document.getElementById('status-dot');
    const terminalLog = document.getElementById('terminal-log');
    const consoleForm = document.getElementById('console-form');
    const consoleInput = document.getElementById('console-input');
    const reactorBtn = document.getElementById('reactor-trigger-btn');
    const voiceHint = document.getElementById('voice-hint-text');
    const muteBtn = document.getElementById('mute-voice-btn');
    const clearBtn = document.getElementById('clear-console-btn');
    const musicContainer = document.getElementById('music-library-container');
    const newsContainer = document.getElementById('news-feed-container');
    const micStatus = document.getElementById('mic-status-text');
    
    // State variables
    let isListening = false;
    let isMuted = false;
    let recognition = null;
    let speechSynth = window.speechSynthesis;
    let speakingUtterance = null;

    // Initialize System Clock
    function updateClock() {
        const now = new Date();
        
        // Time format
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        systemTime.textContent = `${hours}:${minutes}:${seconds}`;
        
        // Date format
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        systemDate.textContent = `${day}/${month}/${year}`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Helper: Log message to the console panel
    function logToConsole(message, type = 'system') {
        const line = document.createElement('div');
        line.className = `terminal-line ${type}-line`;
        line.innerHTML = `&gt; ${message}`;
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;
    }

    // Initialize Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            isListening = true;
            body.className = 'cyber-hud state-listening';
            statusText.textContent = 'LISTENING FOR COMMAND...';
            voiceHint.textContent = 'SPEAK NOW...';
            micStatus.textContent = 'ACTIVE';
            micStatus.style.color = '#ff2a5f';
            logToConsole('Voice feed active. Listening...', 'system');
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            logToConsole(`Microphone input error: ${event.error}`, 'error');
            resetState();
        };

        recognition.onend = () => {
            isListening = false;
            if (body.classList.contains('state-listening')) {
                resetState();
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            logToConsole(`Captured: "${transcript}"`, 'user');
            sendCommandToServer(transcript);
        };
    } else {
        logToConsole('Speech recognition API not supported in this browser. Please use Chrome or Edge.', 'error');
        voiceHint.textContent = 'VOICE RECOGNITION UNSUPPORTED';
        reactorBtn.disabled = true;
    }

    // Toggle speech recognition
    function toggleVoiceInput() {
        if (!recognition) return;
        
        // Cancel ongoing speech synthesis if any
        if (speechSynth.speaking) {
            speechSynth.cancel();
            resetState();
        }

        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (err) {
                console.error(err);
                logToConsole('Failed to initiate microphone feed.', 'error');
            }
        }
    }

    // Reset HUD state back to Standby
    function resetState() {
        body.className = 'cyber-hud';
        statusText.textContent = 'SYSTEM STANDBY';
        voiceHint.textContent = 'CLICK THE ARC REACTOR TO INITIATE VOICE COMMAND';
        micStatus.textContent = 'DISCONNECTED';
        micStatus.style.color = '';
    }

    // Speech Synthesis
    function speak(text) {
        if (!text) return;
        if (isMuted) {
            logToConsole(`[Muted Speech] Jarvis: "${text}"`, 'jarvis');
            return;
        }

        // Cancel current speak
        if (speechSynth.speaking) {
            speechSynth.cancel();
        }

        speakingUtterance = new SpeechSynthesisUtterance(text);
        
        // Configure voice parameters
        speakingUtterance.rate = 1.0;  // Standard speed
        speakingUtterance.pitch = 0.95; // Slightly deeper, robotic Jarvis feel
        
        // Find a suitable male English voice if available
        const voices = speechSynth.getVoices();
        const preferredVoice = voices.find(voice => 
            (voice.name.includes('Google US English') || voice.name.includes('Microsoft David')) && voice.lang.startsWith('en')
        );
        if (preferredVoice) {
            speakingUtterance.voice = preferredVoice;
        }

        speakingUtterance.onstart = () => {
            body.className = 'cyber-hud state-speaking';
            statusText.textContent = 'JARVIS SPEAKING...';
            logToConsole(`Jarvis: "${text}"`, 'jarvis');
        };

        speakingUtterance.onend = () => {
            resetState();
        };

        speakingUtterance.onerror = (e) => {
            console.error('Speech synthesis error:', e);
            resetState();
        };

        speechSynth.speak(speakingUtterance);
    }
    
    // Chrome speech voices load asynchronously
    if (speechSynth.onvoiceschanged !== undefined) {
        speechSynth.onvoiceschanged = () => {
            // Warm up speech voices list
        };
    }

    // Send text command to Flask Backend
    function sendCommandToServer(commandText) {
        body.className = 'cyber-hud state-thinking';
        statusText.textContent = 'PROCESSING COMMAND...';
        logToConsole(`Analyzing query sequence...`, 'system');

        fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: commandText })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response not ok');
            }
            return response.json();
        })
        .then(data => {
            // 1. Speak response
            speak(data.speak);
            
            // 2. Perform frontend action
            handleBackendAction(data.action, data.target);
        })
        .catch(error => {
            console.error('API Error:', error);
            logToConsole('API response failure. Core backend offline.', 'error');
            speak("I encountered a connection error. Please verify the Flask server is running.");
            resetState();
        });
    }

    // Handle Actions returned by the Flask API
    function handleBackendAction(action, target) {
        if (action === 'open_url') {
            logToConsole(`Opening link target: ${target}`, 'system');
            // Try to open link in new tab
            const opened = window.open(target, '_blank');
            if (!opened) {
                logToConsole('Popup blocked. Please check your browser address bar permissions.', 'error');
            }
        }
        else if (action === 'show_news') {
            logToConsole(`Parsing top headlines feed...`, 'system');
            const newsStatus = document.getElementById('news-status');
            if (newsStatus) newsStatus.textContent = 'LIVE';
            renderNews(target);
        }
        else if (action === 'show_weather') {
            logToConsole(`Weather data received for ${target.city}.`, 'system');
            renderWeather(target);
        }
        else if (action === 'show_info') {
            logToConsole(`Wikipedia data retrieved: "${target.title}"`, 'system');
            renderInfo(target);
        }
        else if (action === 'ai_response') {
            logToConsole(`AI core response logged.`, 'system');
        }
        else if (action === 'app_opened') {
            logToConsole(`Application launch sequence initiated.`, 'system');
        }
    }

    // Render Weather Card in the news panel (temporary display)
    function renderWeather(w) {
        if (!w || !w.success) return;
        newsContainer.innerHTML = `
            <div class="news-card" style="cursor:default; border-color: var(--accent-cyan);">
                <div class="news-meta">
                    <span class="news-source" style="color:var(--accent-cyan)">🌡 WEATHER REPORT</span>
                    <span class="news-time">${w.city}</span>
                </div>
                <div class="news-title" style="font-size:1.1rem; line-height:1.7">
                    ${w.description} &nbsp;|&nbsp; <strong>${w.temp_c}°C</strong> / ${w.temp_f}°F<br>
                    <span style="font-size:0.8rem; opacity:0.7">
                        Feels like ${w.feels_like}°C &nbsp;·&nbsp;
                        Humidity ${w.humidity}% &nbsp;·&nbsp;
                        Wind ${w.wind_kmph} km/h &nbsp;·&nbsp;
                        Visibility ${w.visibility} km
                    </span>
                </div>
            </div>
        `;
        const newsStatus = document.getElementById('news-status');
        if (newsStatus) newsStatus.textContent = 'WEATHER';
    }

    // Render Wikipedia Info Card in the news panel
    function renderInfo(info) {
        if (!info) return;
        newsContainer.innerHTML = `
            <div class="news-card" style="cursor:default; border-color: var(--accent-cyan);">
                <div class="news-meta">
                    <span class="news-source" style="color:var(--accent-cyan)">📖 WIKIPEDIA</span>
                    <span class="news-time">${info.title}</span>
                </div>
                <div class="news-title" style="font-size:0.85rem; line-height:1.7; white-space:normal;">
                    ${info.text}
                </div>
            </div>
        `;
        const newsStatus = document.getElementById('news-status');
        if (newsStatus) newsStatus.textContent = 'WIKI';
    }

    // Render News Widget Cards
    function renderNews(newsItems) {
        if (!newsItems || newsItems.length === 0) {
            newsContainer.innerHTML = '<div class="loading-placeholder">No articles available.</div>';
            return;
        }

        newsContainer.innerHTML = '';
        newsItems.forEach(item => {
            const card = document.createElement('div');
            card.className = 'news-card';
            card.onclick = () => window.open(item.link, '_blank');
            
            // Clean time display
            let timeStr = item.date;
            try {
                const dateObj = new Date(item.date);
                timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' - ' + dateObj.toLocaleDateString();
            } catch (e) {
                // Keep original string if date parsing fails
            }

            card.innerHTML = `
                <div class="news-meta">
                    <span class="news-source">${item.source}</span>
                    <span class="news-time">${timeStr}</span>
                </div>
                <div class="news-title">${item.title}</div>
            `;
            newsContainer.appendChild(card);
        });
    }

    // Fetch and Render Music Library
    function loadMusicLibrary() {
        fetch('/api/music')
        .then(response => response.json())
        .then(songs => {
            if (!songs || songs.length === 0) {
                musicContainer.innerHTML = '<div class="loading-placeholder">Library dictionary empty.</div>';
                return;
            }
            
            musicContainer.innerHTML = '';
            songs.forEach(song => {
                const card = document.createElement('button');
                card.className = 'music-card';
                card.type = 'button';
                card.onclick = () => {
                    logToConsole(`Requesting track playback: "play ${song.name}"`, 'system');
                    sendCommandToServer(`play ${song.name}`);
                };
                
                card.innerHTML = `
                    <span class="track-icon">♫</span>
                    <span class="track-title">${song.name}</span>
                    <span class="track-action">PLAY TRACK</span>
                `;
                musicContainer.appendChild(card);
            });
        })
        .catch(err => {
            console.error('Error fetching music:', err);
            musicContainer.innerHTML = '<div class="loading-placeholder" style="color: var(--accent-red)">sync failed</div>';
        });
    }

    // Event Listeners
    reactorBtn.addEventListener('click', toggleVoiceInput);
    
    // Mute speech toggle
    muteBtn.addEventListener('click', () => {
        isMuted = !isMuted;
        muteBtn.setAttribute('aria-pressed', isMuted);
        if (isMuted) {
            muteBtn.textContent = 'UNMUTE VOICE FEED';
            muteBtn.classList.remove('outline-btn');
            muteBtn.classList.add('glow-btn');
            muteBtn.style.backgroundColor = 'var(--accent-red)';
            muteBtn.style.color = '#fff';
            if (speechSynth.speaking) {
                speechSynth.cancel();
                resetState();
            }
            logToConsole('Voice output disabled.', 'system');
        } else {
            muteBtn.textContent = 'MUTE VOICE FEED';
            muteBtn.classList.remove('glow-btn');
            muteBtn.classList.add('outline-btn');
            muteBtn.style.backgroundColor = '';
            muteBtn.style.color = '';
            logToConsole('Voice output enabled.', 'system');
        }
    });

    // Clear console logs
    clearBtn.addEventListener('click', () => {
        terminalLog.innerHTML = `<div class="terminal-line system-line">&gt; Terminal cleared. System ready.</div>`;
    });

    // Form Manual Submission
    consoleForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const cmd = consoleInput.value.trim();
        if (!cmd) return;
        
        consoleInput.value = '';
        logToConsole(cmd, 'user');
        sendCommandToServer(cmd);
    });

    // Keyboard trigger: Pressing Spacebar activates/stops voice recognition
    window.addEventListener('keydown', (e) => {
        // Only trigger if not typing in console input
        if (document.activeElement === consoleInput) return;
        
        if (e.code === 'Space') {
            e.preventDefault(); // Stop page scrolling
            toggleVoiceInput();
        }
    });

    // Initial Load
    loadMusicLibrary();
});
