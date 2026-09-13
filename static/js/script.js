// ==========================================================================
// J.A.R.V.I.S. — STARK INDUSTRIES NEURAL CORE FRONTEND
// MARK IX — COMPLETE FRONTEND CONTROLLER  v9.1
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM References ───────────────────────────────────────────────────────
    const body          = document.body;
    const systemTime    = document.getElementById('system-time-display');
    const systemDate    = document.getElementById('system-date-display');
    const uptimeEl      = document.getElementById('uptime-counter');
    const statusText    = document.getElementById('status-display-text');
    const terminalLog   = document.getElementById('terminal-log');
    const consoleForm   = document.getElementById('console-form');
    const consoleInput  = document.getElementById('console-input');
    const reactorBtn    = document.getElementById('reactor-trigger-btn');
    const rippleContainer = document.getElementById('ripple-container');
    const voiceHint     = document.getElementById('voice-hint-text');
    const muteBtn       = document.getElementById('mute-voice-btn');
    const clearBtn      = document.getElementById('clear-console-btn');
    const clearMemBtn   = document.getElementById('clear-memory-btn');
    const musicGrid     = document.getElementById('music-library-container');
    const newsFeed      = document.getElementById('news-feed-container');
    const newsStatus    = document.getElementById('news-status');
    const micStatus     = document.getElementById('mic-status-text');
    const energyFill    = document.getElementById('energy-fill');
    const energyPct     = document.getElementById('energy-pct');
    const bootOverlay   = document.getElementById('boot-overlay');
    const bootLog       = document.getElementById('boot-log');
    const bootBar       = document.getElementById('boot-bar');
    const cmdCountEl    = document.getElementById('cmd-count');
    const memTurnEl     = document.getElementById('mem-turn-count');
    const musicSearch   = document.getElementById('music-search');
    const musicBadge    = document.getElementById('music-count-badge');
    const edgeFps       = document.getElementById('edge-fps');
    const edgeLatency   = document.getElementById('edge-latency');
    const footerStatus  = document.getElementById('footer-status');

    // ── State ────────────────────────────────────────────────────────────────
    let isListening  = false;
    let isMuted      = false;
    let recognition  = null;
    let cmdCount     = 0;
    let memTurns     = 0;
    let energyLevel  = 100;
    let allSongs     = [];          // full music library cache
    let currentPlaying = null;      // track name currently playing
    let cmdHistory   = [];          // command history for ↑↓ navigation
    let cmdHistoryIdx = -1;
    const synth      = window.speechSynthesis;
    const bootTime   = Date.now();
    let frameCount   = 0;
    let lastFpsTime  = Date.now();


    // ══════════════════════════════════════════════════════
    // BOOT SEQUENCE
    // ══════════════════════════════════════════════════════
    const BOOT_LINES = [
        '[INIT]  Loading Stark Industries neural core...',
        '[SYS]   Mounting encrypted file system...',
        '[OK]    Arc reactor power: 100% nominal.',
        '[OK]    Voice synthesis engine calibrated.',
        '[OK]    Speech recognition module active.',
        '[OK]    Groq AI model: qwen/qwen3.8-27b loaded.',
        '[OK]    SQLite memory database connected.',
        '[OK]    Music library synced — 148 tracks ready.',
        '[BOOT]  JARVIS MARK IX online. Standing by.',
    ];

    function runBootSequence() {
        let idx = 0;
        const pct = [10, 20, 35, 50, 62, 74, 84, 93, 100];
        const interval = setInterval(() => {
            if (idx >= BOOT_LINES.length) {
                clearInterval(interval);
                setTimeout(() => {
                    bootOverlay.classList.add('hidden');
                    setTimeout(() => { bootOverlay.style.display = 'none'; }, 700);
                }, 500);
                return;
            }
            const span = document.createElement('span');
            span.className = 'bl';
            span.textContent = BOOT_LINES[idx];
            bootLog.appendChild(span);
            bootBar.style.width = pct[idx] + '%';
            idx++;
        }, 200);
    }
    runBootSequence();


    // ══════════════════════════════════════════════════════
    // PARTICLE CANVAS BACKGROUND
    // ══════════════════════════════════════════════════════
    const pCanvas = document.getElementById('particle-canvas');
    const pCtx    = pCanvas.getContext('2d');

    function resizeParticle() {
        pCanvas.width  = window.innerWidth;
        pCanvas.height = window.innerHeight;
    }
    resizeParticle();
    window.addEventListener('resize', resizeParticle);

    const PARTICLE_COUNT = 72;
    const particles = Array.from({ length: PARTICLE_COUNT }, () => createParticle(true));

    function createParticle(scattered = false) {
        return {
            x:     scattered ? Math.random() * window.innerWidth  : window.innerWidth  / 2,
            y:     scattered ? Math.random() * window.innerHeight : window.innerHeight / 2,
            vx:    (Math.random() - 0.5) * 0.45,
            vy:    (Math.random() - 0.5) * 0.45,
            r:     Math.random() * 1.8 + 0.3,
            alpha: Math.random() * 0.5 + 0.1,
            life:  Math.random(),
            hue:   Math.random() > 0.85 ? 160 : 185,  // occasional green tints
        };
    }

    // Get particle color based on current state
    function particleColor(p) {
        if (body.classList.contains('state-listening')) return `rgba(255,42,95,${p.alpha})`;
        if (body.classList.contains('state-thinking'))  return `rgba(255,170,0,${p.alpha * 0.7})`;
        if (body.classList.contains('state-speaking'))  return `rgba(0,230,118,${p.alpha})`;
        return `hsla(${p.hue}, 100%, 65%, ${p.alpha})`;
    }

    function drawParticles() {
        // FPS counter
        frameCount++;
        const now = Date.now();
        if (now - lastFpsTime >= 1000) {
            if (edgeFps) edgeFps.textContent = `${frameCount} FPS`;
            frameCount = 0;
            lastFpsTime = now;
        }

        pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
        particles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;
            p.life += 0.003;
            p.alpha = 0.12 + Math.sin(p.life * Math.PI) * 0.28;

            if (p.x < 0 || p.x > pCanvas.width || p.y < 0 || p.y > pCanvas.height) {
                particles[i] = createParticle(true);
                return;
            }

            pCtx.beginPath();
            pCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            pCtx.fillStyle = particleColor(p);
            pCtx.fill();
        });

        // Draw faint connecting lines
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx   = particles[i].x - particles[j].x;
                const dy   = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 110) {
                    const a = 0.055 * (1 - dist / 110);
                    pCtx.beginPath();
                    pCtx.moveTo(particles[i].x, particles[i].y);
                    pCtx.lineTo(particles[j].x, particles[j].y);
                    if (body.classList.contains('state-listening'))     pCtx.strokeStyle = `rgba(255,42,95,${a})`;
                    else if (body.classList.contains('state-thinking')) pCtx.strokeStyle = `rgba(255,170,0,${a * 0.6})`;
                    else if (body.classList.contains('state-speaking')) pCtx.strokeStyle = `rgba(0,230,118,${a})`;
                    else pCtx.strokeStyle = `rgba(0,240,255,${a})`;
                    pCtx.lineWidth = 0.5;
                    pCtx.stroke();
                }
            }
        }
        requestAnimationFrame(drawParticles);
    }
    drawParticles();


    // ══════════════════════════════════════════════════════
    // WAVEFORM CANVAS
    // ══════════════════════════════════════════════════════
    const wCanvas = document.getElementById('waveform-canvas');
    const wCtx    = wCanvas.getContext('2d');
    let wavePhase = 0;
    let waveAmp   = 8;
    let waveAmpTarget = 8;

    function drawWaveform() {
        // Smooth amp transition
        waveAmp += (waveAmpTarget - waveAmp) * 0.1;

        wCtx.clearRect(0, 0, wCanvas.width, wCanvas.height);
        const W = wCanvas.width;
        const H = wCanvas.height;
        const mid = H / 2;

        let color = '#00f0ff';
        if (body.classList.contains('state-listening')) color = '#ff2a5f';
        else if (body.classList.contains('state-thinking')) color = '#ffaa00';
        else if (body.classList.contains('state-speaking')) color = '#00e676';

        // Draw THREE mirrored waveform lines for richer look
        const lines = [
            { ampMul: 1.0, width: 2.0 },
            { ampMul: 0.6, width: 1.2 },
            { ampMul: 0.35, width: 0.7 },
        ];

        for (const { ampMul, width } of lines) {
            for (let mirror = -1; mirror <= 1; mirror += 2) {
                wCtx.beginPath();
                for (let x = 0; x <= W; x += 2) {
                    const y = mid + mirror * (
                        Math.sin(x * 0.018 + wavePhase)        * (waveAmp * ampMul) +
                        Math.sin(x * 0.034 + wavePhase * 1.3)  * (waveAmp * ampMul * 0.45) +
                        Math.sin(x * 0.055 + wavePhase * 0.7)  * (waveAmp * ampMul * 0.2)
                    );
                    x === 0 ? wCtx.moveTo(x, y) : wCtx.lineTo(x, y);
                }
                const grad = wCtx.createLinearGradient(0, 0, W, 0);
                grad.addColorStop(0,    'transparent');
                grad.addColorStop(0.12, color);
                grad.addColorStop(0.88, color);
                grad.addColorStop(1,    'transparent');
                wCtx.strokeStyle = grad;
                wCtx.lineWidth   = width;
                wCtx.shadowColor = color;
                wCtx.shadowBlur  = width > 1 ? 8 : 3;
                wCtx.globalAlpha = width > 1 ? 1.0 : 0.4;
                wCtx.stroke();
            }
        }
        wCtx.shadowBlur  = 0;
        wCtx.globalAlpha = 1;

        wavePhase += 0.046;
        requestAnimationFrame(drawWaveform);
    }
    drawWaveform();


    // ══════════════════════════════════════════════════════
    // CLOCK + UPTIME
    // ══════════════════════════════════════════════════════
    function pad(n) { return String(n).padStart(2, '0'); }

    function updateClock() {
        const now = new Date();
        if (systemTime) systemTime.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
        if (systemDate) systemDate.textContent = `${pad(now.getDate())} / ${pad(now.getMonth() + 1)} / ${now.getFullYear()}`;

        const elapsed = Math.floor((Date.now() - bootTime) / 1000);
        const hh = Math.floor(elapsed / 3600);
        const mm = Math.floor((elapsed % 3600) / 60);
        const ss = elapsed % 60;
        if (uptimeEl) uptimeEl.textContent = `${pad(hh)}:${pad(mm)}:${pad(ss)}`;
    }
    setInterval(updateClock, 1000);
    updateClock();


    // ══════════════════════════════════════════════════════
    // CONSOLE LOGGER
    // ══════════════════════════════════════════════════════
    function logToConsole(message, type = 'system', prefix = null) {
        const line = document.createElement('div');
        line.className = `terminal-line ${type}-line`;

        const tagMap = {
            system:  '[SYS]',
            user:    '[YOU]',
            jarvis:  '[JARVIS]',
            success: '[OK]',
            error:   '[ERR]',
            warning: '[WARN]',
        };
        const tag = prefix || tagMap[type] || '[SYS]';
        line.innerHTML = `<span class="ts">${tag}</span>${escapeHtml(message)}`;
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;
        return line;
    }

    // Typewriter effect for JARVIS responses
    function logJarvisTyped(message) {
        const line = document.createElement('div');
        line.className = 'terminal-line jarvis-line jarvis-typing';
        line.innerHTML = `<span class="ts">[JARVIS]</span><span class="typed-text"></span>`;
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;

        const textEl = line.querySelector('.typed-text');
        const chars  = message.split('');
        let i = 0;
        const timer = setInterval(() => {
            if (i >= chars.length) {
                clearInterval(timer);
                line.classList.remove('jarvis-typing');
                return;
            }
            textEl.textContent += chars[i++];
            terminalLog.scrollTop = terminalLog.scrollHeight;
        }, 18);
    }

    function escapeHtml(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }


    // ══════════════════════════════════════════════════════
    // ENERGY BAR
    // ══════════════════════════════════════════════════════
    function drainEnergy(amount = 8) {
        energyLevel = Math.max(12, energyLevel - amount);
        if (energyFill) energyFill.style.width = energyLevel + '%';
        if (energyPct)  energyPct.textContent = energyLevel + '%';
        // Slowly recover
        clearTimeout(drainEnergy._recovery);
        drainEnergy._recovery = setTimeout(() => {
            const recover = setInterval(() => {
                energyLevel = Math.min(100, energyLevel + 2);
                if (energyFill) energyFill.style.width = energyLevel + '%';
                if (energyPct)  energyPct.textContent = energyLevel + '%';
                if (energyLevel >= 100) clearInterval(recover);
            }, 200);
        }, 2000);
    }

    // ── Ripple effect on reactor click ──────────────────────────────────────
    function triggerRipple() {
        if (!rippleContainer) return;
        const el = document.createElement('div');
        el.className = 'reactor-ripple';
        rippleContainer.appendChild(el);
        setTimeout(() => el.remove(), 800);
    }


    // ══════════════════════════════════════════════════════
    // SPEECH RECOGNITION
    // ══════════════════════════════════════════════════════
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous     = false;
        recognition.lang           = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            isListening = true;
            waveAmpTarget = 22;
            setState('listening', 'LISTENING — SPEAK NOW', 'SPEAK NOW...');
            micStatus.textContent  = 'ACTIVE';
            micStatus.style.color  = 'var(--red)';
            logToConsole('Voice feed active. Listening...', 'system');
            setThreatLevel(3);
        };

        recognition.onend = () => {
            isListening = false;
            waveAmpTarget = 8;
            if (body.classList.contains('state-listening')) resetState();
        };

        recognition.onerror = (e) => {
            logToConsole(`Voice error: ${e.error}`, 'error');
            waveAmpTarget = 8;
            resetState();
        };

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            logToConsole(transcript, 'user');
            sendCommand(transcript);
        };
    } else {
        logToConsole('Web Speech API not supported. Use Chrome or Edge.', 'error');
        if (voiceHint) voiceHint.textContent = 'VOICE UNSUPPORTED IN THIS BROWSER';
        reactorBtn.disabled = true;
    }

    function toggleVoice() {
        if (!recognition) return;
        if (synth.speaking) { synth.cancel(); resetState(); }
        triggerRipple();
        if (isListening) {
            recognition.stop();
        } else {
            try { recognition.start(); } catch (e) {
                logToConsole('Mic failed to start.', 'error');
            }
        }
    }


    // ══════════════════════════════════════════════════════
    // STATE MANAGER
    // ══════════════════════════════════════════════════════
    function setState(cls, status, hint) {
        body.className = `cyber-hud state-${cls}`;
        if (statusText) statusText.textContent = status;
        if (voiceHint)  voiceHint.textContent  = hint;
    }

    function resetState() {
        body.className             = 'cyber-hud';
        if (statusText) statusText.textContent = 'SYSTEM STANDBY';
        if (voiceHint)  voiceHint.textContent  = 'CLICK ARC REACTOR OR PRESS SPACE';
        micStatus.textContent      = 'OFFLINE';
        micStatus.style.color      = '';
        waveAmpTarget              = 8;
        setThreatLevel(1);
    }

    // ── Threat Level ──────────────────────────────────────────────────────────
    function setThreatLevel(lvl) {
        const dots = document.querySelectorAll('.threat-dot');
        const textEl = document.getElementById('threat-text');
        dots.forEach((d, i) => {
            d.classList.toggle('active', i < lvl);
        });
        if (textEl) {
            textEl.textContent = `LVL ${lvl}`;
            const colors = ['','var(--green)','#aaee00','var(--orange)','#ff6600','var(--red)'];
            textEl.style.color = colors[lvl] || 'var(--green)';
        }
    }


    // ══════════════════════════════════════════════════════
    // SPEECH SYNTHESIS
    // ══════════════════════════════════════════════════════
    function speak(text) {
        if (!text) return;
        if (isMuted) {
            logJarvisTyped(text);
            return;
        }
        if (synth.speaking) synth.cancel();

        const utt = new SpeechSynthesisUtterance(text);
        utt.rate  = 1.0;
        utt.pitch = 0.88;

        const voices = synth.getVoices();
        const pick = voices.find(v =>
            (v.name.includes('Google US English') ||
             v.name.includes('Microsoft David') ||
             v.name.includes('Microsoft Mark') ||
             v.name.includes('Daniel')) && v.lang.startsWith('en')
        );
        if (pick) utt.voice = pick;

        utt.onstart = () => {
            waveAmpTarget = 28;
            setState('speaking', 'J.A.R.V.I.S. SPEAKING', '▶ TRANSMITTING...');
            logJarvisTyped(text);
            setThreatLevel(2);
        };
        utt.onend   = () => { waveAmpTarget = 8; resetState(); };
        utt.onerror = () => { waveAmpTarget = 8; resetState(); };

        synth.speak(utt);
    }

    if (synth.onvoiceschanged !== undefined) {
        synth.onvoiceschanged = () => {};
    }


    // ══════════════════════════════════════════════════════
    // API COMMAND
    // ══════════════════════════════════════════════════════
    function sendCommand(cmd) {
        setState('thinking', 'PROCESSING QUERY...', '⟳ ANALYZING...');
        logToConsole(`Processing: "${cmd}"`, 'system');
        drainEnergy(6);
        setThreatLevel(4);

        // Track command count
        cmdCount++;
        if (cmdCountEl) cmdCountEl.textContent = cmdCount;

        // Add to command history
        if (cmd.trim()) {
            cmdHistory.unshift(cmd);
            if (cmdHistory.length > 30) cmdHistory.pop();
            cmdHistoryIdx = -1;
        }

        // Measure latency
        const start = Date.now();

        fetch('/api/command', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ command: cmd }),
        })
        .then(r => {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(data => {
            const ms = Date.now() - start;
            if (edgeLatency) edgeLatency.textContent = `${ms}ms`;
            speak(data.speak);
            handleAction(data.action, data.target);
            // Count memory turns for AI responses
            if (data.action === 'ai_response') {
                memTurns++;
                if (memTurnEl) memTurnEl.textContent = `${memTurns} TURNS`;
            }
        })
        .catch(err => {
            logToConsole(`API error: ${err.message}`, 'error');
            speak('Connection error. Please verify the Flask server is running.');
            resetState();
            if (footerStatus) { footerStatus.textContent = 'ERROR'; footerStatus.style.color = 'var(--red)'; }
        });
    }


    // ══════════════════════════════════════════════════════
    // ACTION HANDLER
    // ══════════════════════════════════════════════════════
    function handleAction(action, target) {
        switch (action) {
            case 'open_url':
                logToConsole(`Opening: ${target}`, 'system');
                const w = window.open(target, '_blank');
                if (!w) logToConsole('Popup blocked — check browser settings.', 'warning');
                break;

            case 'show_news':
                if (newsStatus) newsStatus.textContent = 'LIVE';
                renderNews(target);
                logToConsole(`${target.length} headlines loaded.`, 'success');
                break;

            case 'show_weather':
                renderWeather(target);
                if (newsStatus) newsStatus.textContent = 'WEATHER';
                logToConsole(`Weather retrieved: ${target.city}.`, 'success');
                break;

            case 'show_info':
                renderInfo(target);
                if (newsStatus) newsStatus.textContent = 'WIKI';
                logToConsole(`Wikipedia: "${target.title}"`, 'success');
                break;

            case 'ai_response':
                renderAIResponse(target);
                if (newsStatus) newsStatus.textContent = 'AI';
                logToConsole('AI core response received.', 'system');
                break;

            case 'app_opened':
                logToConsole('Application launch initiated.', 'success');
                break;

            default:
                break;
        }
    }


    // ══════════════════════════════════════════════════════
    // WEATHER RENDERER — upgraded grid layout
    // ══════════════════════════════════════════════════════
    function renderWeather(w) {
        if (!w || !w.success) return;
        newsFeed.innerHTML = `
            <div class="info-card">
                <div class="card-heading">🌡 WEATHER REPORT — ${escapeHtml(w.city)}</div>
                <div class="card-body">
                    <div class="big-temp">${w.temp_c}°C</div>
                    <div style="font-size:0.85rem; color:#b8ddf0; margin:5px 0 0;">
                        ${escapeHtml(w.description)} · Feels like ${w.feels_like}°C
                    </div>
                    <div class="weather-grid">
                        <div class="weather-stat"><div class="ws-label">HUMIDITY</div><div class="ws-val">💧 ${w.humidity}%</div></div>
                        <div class="weather-stat"><div class="ws-label">WIND</div><div class="ws-val">💨 ${w.wind_kmph} km/h</div></div>
                        <div class="weather-stat"><div class="ws-label">VISIBILITY</div><div class="ws-val">👁 ${w.visibility} km</div></div>
                        <div class="weather-stat"><div class="ws-label">FAHRENHEIT</div><div class="ws-val">🌡 ${w.temp_f}°F</div></div>
                    </div>
                </div>
            </div>`;
    }


    // ══════════════════════════════════════════════════════
    // WIKIPEDIA RENDERER
    // ══════════════════════════════════════════════════════
    function renderInfo(info) {
        if (!info) return;
        newsFeed.innerHTML = `
            <div class="info-card">
                <div class="card-heading">📖 WIKIPEDIA — ${escapeHtml(info.title)}</div>
                <div class="card-body" style="font-size:0.83rem; line-height:1.7;">
                    ${escapeHtml(info.text)}
                </div>
            </div>`;
    }


    // ══════════════════════════════════════════════════════
    // AI RESPONSE RENDERER — new styled card
    // ══════════════════════════════════════════════════════
    function renderAIResponse(text) {
        if (!text) return;
        newsFeed.innerHTML = `
            <div class="ai-response-card">
                <div class="ai-heading">⬡ JARVIS AI RESPONSE · QWEN3-27B</div>
                <div class="ai-body">${escapeHtml(text)}</div>
            </div>`;
    }


    // ══════════════════════════════════════════════════════
    // NEWS RENDERER
    // ══════════════════════════════════════════════════════
    function renderNews(items) {
        if (!items || !items.length) {
            newsFeed.innerHTML = '<div class="loading-placeholder">No articles found.</div>';
            return;
        }
        newsFeed.innerHTML = '';
        items.forEach((item, idx) => {
            const card = document.createElement('div');
            card.className = 'news-card';
            card.style.animationDelay = (idx * 60) + 'ms';
            card.addEventListener('click', () => window.open(item.link, '_blank'));

            let timeStr = item.date;
            try {
                const d = new Date(item.date);
                timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } catch (_) {}

            card.innerHTML = `
                <div class="news-meta">
                    <span class="news-source">${escapeHtml(item.source)}</span>
                    <span class="news-time">${escapeHtml(timeStr)}</span>
                </div>
                <div class="news-title">${escapeHtml(item.title)}</div>`;
            newsFeed.appendChild(card);
        });
    }


    // ══════════════════════════════════════════════════════
    // MUSIC LIBRARY — with search filter + playing state
    // ══════════════════════════════════════════════════════
    function loadMusicLibrary() {
        fetch('/api/music')
            .then(r => r.json())
            .then(songs => {
                allSongs = songs || [];
                if (musicBadge) musicBadge.textContent = `${allSongs.length} TRACKS`;
                renderMusicCards(allSongs);
            })
            .catch(() => {
                musicGrid.innerHTML = '<div class="loading-placeholder" style="color:var(--red)">Sync failed.</div>';
            });
    }

    function renderMusicCards(songs) {
        if (!songs || !songs.length) {
            musicGrid.innerHTML = '<div class="loading-placeholder">No tracks found.</div>';
            return;
        }
        musicGrid.innerHTML = '';
        songs.forEach(song => {
            const card = document.createElement('button');
            card.className = 'music-card';
            card.type      = 'button';
            card.dataset.name = song.name;
            if (song.name === currentPlaying) card.classList.add('playing');
            card.addEventListener('click', () => {
                // Mark as playing
                document.querySelectorAll('.music-card').forEach(c => c.classList.remove('playing'));
                card.classList.add('playing');
                currentPlaying = song.name;
                logToConsole(`Requesting: play ${song.name}`, 'system');
                sendCommand(`play ${song.name}`);
            });
            card.innerHTML = `
                <span class="track-icon">${song.name === currentPlaying ? '▶' : '♫'}</span>
                <span class="track-title">${escapeHtml(song.name)}</span>`;
            musicGrid.appendChild(card);
        });
    }

    // Music search filter
    if (musicSearch) {
        musicSearch.addEventListener('input', () => {
            const q = musicSearch.value.toLowerCase().trim();
            const filtered = q ? allSongs.filter(s => s.name.toLowerCase().includes(q)) : allSongs;
            renderMusicCards(filtered);
        });
    }


    // ══════════════════════════════════════════════════════
    // EVENT LISTENERS
    // ══════════════════════════════════════════════════════

    // Arc reactor click
    reactorBtn.addEventListener('click', toggleVoice);

    // Spacebar shortcut
    window.addEventListener('keydown', e => {
        const activeEl = document.activeElement;
        // Don't intercept if user is typing
        if (activeEl === consoleInput || activeEl === musicSearch) {
            // Up/Down history in console
            if (activeEl === consoleInput) {
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (cmdHistoryIdx < cmdHistory.length - 1) {
                        cmdHistoryIdx++;
                        consoleInput.value = cmdHistory[cmdHistoryIdx] || '';
                    }
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (cmdHistoryIdx > 0) {
                        cmdHistoryIdx--;
                        consoleInput.value = cmdHistory[cmdHistoryIdx] || '';
                    } else {
                        cmdHistoryIdx = -1;
                        consoleInput.value = '';
                    }
                } else if (e.key === 'Escape') {
                    consoleInput.value = '';
                    cmdHistoryIdx = -1;
                }
            }
            return;
        }
        if (e.code === 'Space') { e.preventDefault(); toggleVoice(); }
    });

    // Console form submit
    consoleForm.addEventListener('submit', e => {
        e.preventDefault();
        const cmd = consoleInput.value.trim();
        if (!cmd) return;
        consoleInput.value = '';
        cmdHistoryIdx = -1;
        logToConsole(cmd, 'user');
        sendCommand(cmd);
    });

    // Quick command buttons
    document.querySelectorAll('.quick-cmd').forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.dataset.cmd;
            if (!cmd) return;
            logToConsole(cmd, 'user');
            sendCommand(cmd);
            // Tiny visual feedback
            btn.style.borderColor = 'var(--cyan)';
            setTimeout(() => { btn.style.borderColor = ''; }, 600);
        });
    });

    // Mute toggle
    muteBtn.addEventListener('click', () => {
        isMuted = !isMuted;
        muteBtn.setAttribute('aria-pressed', isMuted);
        if (isMuted) {
            muteBtn.innerHTML = '<span class="btn-icon">🔇</span> UNMUTE';
            muteBtn.classList.replace('outline-btn', 'glow-btn');
            muteBtn.style.background = 'var(--red)';
            muteBtn.style.color      = '#fff';
            muteBtn.style.boxShadow  = '0 0 14px rgba(255,42,95,0.4)';
            if (synth.speaking) { synth.cancel(); resetState(); }
            logToConsole('Voice output muted.', 'warning');
        } else {
            muteBtn.innerHTML = '<span class="btn-icon">🔊</span> MUTE';
            muteBtn.classList.replace('glow-btn', 'outline-btn');
            muteBtn.style.background = '';
            muteBtn.style.color      = '';
            muteBtn.style.boxShadow  = '';
            logToConsole('Voice output enabled.', 'success');
        }
    });

    // Clear console
    clearBtn.addEventListener('click', () => {
        terminalLog.innerHTML = `<div class="terminal-line system-line"><span class="ts">[SYS]</span>&nbsp;Terminal cleared. Awaiting commands.</div>`;
    });

    // Clear memory
    if (clearMemBtn) {
        clearMemBtn.addEventListener('click', () => {
            fetch('/api/clear-memory', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    memTurns = 0;
                    if (memTurnEl) memTurnEl.textContent = '0 TURNS';
                    logToConsole('AI conversation memory cleared.', 'success');
                    speak('Memory wiped, Sir. We start fresh.');
                    // Reset news feed
                    if (newsFeed) newsFeed.innerHTML = '<div class="loading-placeholder">Memory cleared.</div>';
                    if (newsStatus) newsStatus.textContent = 'STANDBY';
                })
                .catch(() => logToConsole('Memory wipe failed.', 'error'));
        });
    }


    // ══════════════════════════════════════════════════════
    // INIT
    // ══════════════════════════════════════════════════════
    loadMusicLibrary();
    logToConsole('JARVIS MARK IX is online. Say "Hello JARVIS" or type below.', 'success');

});
