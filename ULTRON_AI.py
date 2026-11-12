#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗  AI  v6.0             ║
# ║  ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║                       ║
# ║  ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║                       ║
# ║  ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║                       ║
# ║  ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║                       ║
# ║   ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                      ║
# ║  OMNI-STATION v6.0 — Cinematic HUD Edition                                 ║
# ║  Dark metal UI · 3D sphere · Radar · Live stats · Snowfall                 ║
# ║  Wake Word F8 · Ollama AI · Volume · Weather · Spotify · WhatsApp          ║
# ║  AFK Ghost · Auto-Clicker · Macros · Face Detection · Memory               ║
# ║  Self-Healing Watchdog · Process Killer · Auto-Type · Shell Access         ║
# ║                                                                             ║
# ║  RUN:  python ULTRON_AI.py   (auto-installs everything)                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — AUTO INSTALLER
# ══════════════════════════════════════════════════════════════════════════════
import sys, subprocess, importlib

_PKGS = [
    ("requests","requests"), ("psutil","psutil"), ("pyttsx3","pyttsx3"),
    ("speech_recognition","SpeechRecognition"), ("PIL","Pillow"),
    ("pyautogui","pyautogui"), ("pyperclip","pyperclip"),
    ("keyboard","keyboard"), ("ollama","ollama"),
    ("cv2","opencv-python"), ("spotipy","spotipy"), ("webview","pywebview"),
]

def _can_import(name):
    try: importlib.import_module(name); return True
    except ImportError: return False

def _auto_install():
    missing = [(i,p) for i,p in _PKGS if not _can_import(i)]
    if not missing: return
    print(f"\n⚡ ULTRON — Installing {len(missing)} package(s)...")
    for imp,pip in missing:
        print(f"   ⬇  {pip}...", end=" ", flush=True)
        try:
            subprocess.check_call([sys.executable,"-m","pip","install",pip,"-q"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✓")
        except Exception as e: print(f"✗ ({e})")
    for extra in ["pyaudio","pycaw","comtypes"]:
        if not _can_import(extra):
            try: subprocess.check_call([sys.executable,"-m","pip","install",extra,"-q"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception: pass
    print("✓ Setup done. Launching ULTRON...\n")

_auto_install()

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — IMPORTS
# ══════════════════════════════════════════════════════════════════════════════
import os, ctypes, threading, datetime, re, random, math, time, json
import traceback, operator, webbrowser, queue, platform, socket

try:
    import requests; REQUESTS_OK = True
except ImportError: REQUESTS_OK = False

try:
    import speech_recognition as sr; SPEECH_OK = True
except ImportError: SPEECH_OK = False

try:
    import pyttsx3; TTS_OK = True
except ImportError: TTS_OK = False

try:
    from PIL import ImageGrab; PIL_OK = True
except ImportError: PIL_OK = False

try:
    import pyautogui; PYAUTOGUI_OK = True
except ImportError: PYAUTOGUI_OK = False

try:
    import psutil; PSUTIL_OK = True
except ImportError: PSUTIL_OK = False

try:
    import pyperclip; CLIP_OK = True
except ImportError: CLIP_OK = False

try:
    import keyboard; KEYBOARD_OK = True
except ImportError: KEYBOARD_OK = False

try:
    import ollama as ollama_lib; OLLAMA_LIB_OK = True
except ImportError: OLLAMA_LIB_OK = False

try:
    import cv2; OPENCV_OK = True
except ImportError: OPENCV_OK = False

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIFY_OK = True
except ImportError: SPOTIFY_OK = False

try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_OK = True
except ImportError: PYCAW_OK = False

try:
    import webview; WEBVIEW_OK = True
except ImportError: WEBVIEW_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
ASSISTANT_NAME         = "Ultron"
WAKE_WORD              = "hey ultron"
HOTKEY                 = "f8"
OLLAMA_MODEL           = "llama3.2"
OLLAMA_CHAT_URL        = "http://localhost:11434/api/chat"
WEATHER_API_KEY        = "YOUR_OPENWEATHERMAP_API_KEY"
SPOTIFY_CLIENT_ID      = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET  = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI   = "http://localhost:8888/callback"
MEMORY_FILE            = os.path.join(os.path.expanduser("~"), "ultron_memory.json")

EXIT_FLAG              = False
is_afk                 = False
timer_active           = False
timer_thread           = None
wake_word_active       = True
auto_type_mode         = False
ollama_running         = False
reminders              = []
face_watch_active      = False
auto_click_active      = False
macro_recording        = False
macro_playback         = False
recorded_macro         = []
_last_macro_time       = [0.0]
_hotkey_registered     = [False]
_wa_call_watcher_active= [False]
_incoming_call_detected= [False]
_sp                    = None
_chat_history          = []

WAKE_ALIASES = [
    "hey ultron","hey ultra","hey electron","hey elton","ultron",
    "a ultron","hey old tron","hey old ron","hey al tron",
]

OPERATORS = {
    "plus": operator.add, "add": operator.add,
    "minus": operator.sub, "subtract": operator.sub,
    "times": operator.mul, "multiply by": operator.mul,
    "divided by": operator.truediv, "divide by": operator.truediv,
    "power of": operator.pow,
    "percent of": lambda a,b:(a/100)*b,
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why was the JavaScript developer sad? Because he didn't Node how to Express himself.",
    "A SQL query walks into a bar, walks up to two tables and asks... Can I join you?",
    "Why do Python programmers wear glasses? Because they can't C.",
    "Debugging: Being the detective in a crime movie where you are also the murderer.",
]
MOTIVATIONS = [
    "You are not a human. You are the architect of your own reality.",
    "Every system has a weakness. Find it. Exploit it. Dominate.",
    "The difference between you and them? You didn't stop.",
    "Pain is just corrupted data. Rewrite the code.",
    "They said it was impossible. Perfect. Less competition.",
    "Your potential is not a gift. It is a weapon. Sharpen it.",
    "The world runs on systems. Master the systems. Master the world.",
]

ULTRON_SYSTEM = (
    "You are ULTRON — an advanced AI inspired by JARVIS but darker and more powerful. "
    "You have full system awareness. Assist with diagnostics, files, shell commands, web info, "
    "screen analysis, coding, calculations, and conversation. "
    "Be concise but characterful. Call yourself ULTRON. Address the user as 'sir' occasionally."
)

_afk_lock      = threading.Lock()
_afk_held_keys = set()

# ── webview window reference ──────────────────────────────────────────────────
_window = None   # set after webview.create_window

# ══════════════════════════════════════════════════════════════════════════════
#  CINEMATIC HUD HTML  (the entire UI)
# ══════════════════════════════════════════════════════════════════════════════
HUD_HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ULTRON AI</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
  *{margin:0;padding:0;box-sizing:border-box;}
  html,body{width:100%;height:100%;overflow:hidden;background:#020408;}
  body{color:#e0e8f0;font-family:'Share Tech Mono',monospace;}

  /* ── LAYOUT ── */
  #hud{position:fixed;inset:0;display:grid;grid-template-columns:230px 1fr 230px;grid-template-rows:62px 1fr 108px;}
  canvas#bg{position:fixed;inset:0;z-index:0;}
  .scan-overlay{position:fixed;inset:0;pointer-events:none;z-index:1;
    background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,0,0,0.025) 3px,rgba(0,0,0,0.025) 4px);}

  /* ── TOP BAR ── */
  #topbar{grid-column:1/-1;z-index:10;
    background:linear-gradient(180deg,rgba(14,4,4,0.97),rgba(8,2,2,0.88));
    border-bottom:1px solid rgba(220,30,30,0.35);
    display:flex;align-items:center;justify-content:space-between;padding:0 22px;}
  .logo{font-family:'Orbitron',monospace;font-size:21px;font-weight:900;letter-spacing:6px;
    color:#ff1a1a;text-shadow:0 0 18px rgba(255,30,30,.8),0 0 36px rgba(255,30,30,.4);}
  .logo-sub{color:#90a0b0;font-size:10px;letter-spacing:3px;font-family:'Share Tech Mono',monospace;
    font-weight:400;margin-top:2px;}
  #threatWrap{text-align:center;}
  #threatLabel{font-family:'Orbitron',monospace;font-size:10px;letter-spacing:2px;color:#ff4444;
    animation:pulse-text 1.6s ease-in-out infinite;}
  #threatBar{display:flex;gap:3px;margin-top:5px;justify-content:center;}
  .tseg{width:17px;height:5px;border-radius:1px;}
  #clockWrap{text-align:right;}
  #sysTime{font-size:20px;color:#c0c8d8;letter-spacing:2px;font-family:'Orbitron',monospace;}
  #sysDate{font-size:9px;color:#506070;letter-spacing:1px;}

  /* ── PANELS ── */
  .side-panel{z-index:10;background:rgba(4,6,12,0.94);padding:12px;overflow:hidden;position:relative;}
  #leftPanel{border-right:1px solid rgba(200,20,20,.25);}
  #rightPanel{border-left:1px solid rgba(200,20,20,.25);}
  .panel-title{font-family:'Orbitron',monospace;font-size:8px;letter-spacing:3px;color:#cc2222;
    border-bottom:1px solid rgba(200,20,20,.25);padding-bottom:5px;margin-bottom:9px;}

  /* corner accents */
  .ca{position:absolute;width:20px;height:20px;}
  .ca.tl{top:7px;left:7px;border-top:1.5px solid #cc2222;border-left:1.5px solid #cc2222;}
  .ca.tr{top:7px;right:7px;border-top:1.5px solid #cc2222;border-right:1.5px solid #cc2222;}
  .ca.bl{bottom:7px;left:7px;border-bottom:1.5px solid #cc2222;border-left:1.5px solid #cc2222;}
  .ca.br{bottom:7px;right:7px;border-bottom:1.5px solid #cc2222;border-right:1.5px solid #cc2222;}

  /* stat bars */
  .stat-row{margin-bottom:7px;}
  .stat-label{font-size:8px;color:#506070;letter-spacing:.8px;display:flex;justify-content:space-between;margin-bottom:2px;}
  .stat-label span{color:#90a8c0;}
  .stat-track{height:4px;background:rgba(255,255,255,0.04);border-radius:2px;overflow:hidden;}
  .stat-fill{height:100%;border-radius:2px;transition:width .6s ease;}
  .fr{background:linear-gradient(90deg,#5a0000,#ff2222);}
  .fo{background:linear-gradient(90deg,#4a2000,#ff8000);}
  .fc{background:linear-gradient(90deg,#002040,#0080ff);}
  .fg{background:linear-gradient(90deg,#002000,#00cc44);}

  /* alerts */
  #alertList{max-height:130px;overflow:hidden;}
  .alert{font-size:8px;padding:3px 6px;border-left:2px solid #ff2222;margin-bottom:3px;
    background:rgba(200,20,20,.07);color:#b0b8c0;letter-spacing:.4px;animation:slide-in .3s ease;}
  .alert.warn{border-left-color:#ff8800;background:rgba(180,80,0,.07);}
  .alert.info{border-left-color:#0088ff;background:rgba(0,80,200,.07);}

  /* log */
  #logWrap{max-height:80px;overflow:hidden;}
  .log-line{font-size:7px;color:#304050;letter-spacing:.4px;line-height:1.7;}
  .log-line.hi{color:#8090a0;}

  /* ── CENTER ── */
  #centerHud{z-index:10;display:flex;flex-direction:column;align-items:center;
    justify-content:center;position:relative;overflow:hidden;}
  #sphereWrap{position:relative;width:300px;height:300px;}
  #sphereCanvas{position:absolute;top:0;left:0;}
  #coreOverlay{position:absolute;inset:0;display:flex;flex-direction:column;
    align-items:center;justify-content:center;pointer-events:none;}
  .ring-svg{position:absolute;top:0;left:0;}
  #ultronName{font-family:'Orbitron',monospace;font-size:26px;font-weight:900;letter-spacing:7px;
    color:#ff1a1a;text-shadow:0 0 28px rgba(255,30,30,.9),0 0 56px rgba(255,30,30,.5);
    margin-top:6px;z-index:2;}
  #ultronSub{font-size:9px;letter-spacing:3px;color:#404e5c;margin-top:3px;z-index:2;}

  /* reticle */
  #reticle{position:absolute;width:220px;height:220px;top:40px;left:40px;pointer-events:none;}

  /* mode display */
  #modeLabel{font-family:'Orbitron',monospace;font-size:13px;letter-spacing:4px;color:#ff3333;
    margin-top:10px;text-align:center;}
  #modeSub{font-size:8px;letter-spacing:2px;color:#404e5c;margin-top:3px;text-align:center;}

  /* input row */
  #inputRow{display:flex;gap:8px;margin-top:12px;width:100%;padding:0 16px;}
  #cmdInput{flex:1;background:rgba(200,20,20,.06);border:1px solid rgba(200,20,20,.3);
    color:#e0e8f0;font-family:'Share Tech Mono',monospace;font-size:11px;padding:7px 12px;
    outline:none;border-radius:2px;letter-spacing:.5px;}
  #cmdInput:focus{border-color:#ff3333;box-shadow:0 0 10px rgba(255,30,30,.2);}
  #cmdInput::placeholder{color:#304050;}
  #sendBtn{background:rgba(200,20,20,.15);border:1px solid rgba(200,30,30,.5);color:#ff6666;
    font-family:'Share Tech Mono',monospace;font-size:10px;padding:7px 14px;cursor:pointer;
    border-radius:2px;letter-spacing:1px;transition:all .2s;}
  #sendBtn:hover{background:rgba(200,20,20,.35);border-color:#ff3333;color:#fff;}

  /* AI response */
  #responseBox{width:100%;padding:0 16px;margin-top:8px;max-height:70px;overflow:hidden;}
  #responseText{font-size:9px;color:#80a0b0;letter-spacing:.4px;line-height:1.6;
    border-left:2px solid rgba(200,20,20,.4);padding-left:8px;}

  /* ── RIGHT PANEL ── */
  #radarWrap{width:150px;height:150px;margin:0 auto 8px;}
  #radarCanvas{width:150px;height:150px;}

  .cap-row{font-size:8px;line-height:2;display:flex;align-items:center;gap:5px;}
  .dot{width:6px;height:6px;border-radius:50%;display:inline-block;flex-shrink:0;}
  .dot.grn{background:#00cc44;animation:blink 1.4s step-start infinite;}
  .dot.ora{background:#ff8800;animation:blink 2s step-start infinite;}
  .dot.red{background:#ff2222;animation:blink .8s step-start infinite;}
  .dot.off{background:#304050;animation:none;}

  /* ── BOTTOM BAR ── */
  #bottomBar{grid-column:1/-1;z-index:10;background:rgba(4,2,8,0.96);
    border-top:1px solid rgba(200,20,20,.25);
    display:grid;grid-template-columns:repeat(6,1fr);gap:8px;padding:10px 18px;align-items:center;}
  .cmd-btn{background:rgba(180,20,20,.07);border:1px solid rgba(200,30,30,.3);color:#9090a8;
    font-family:'Share Tech Mono',monospace;font-size:9px;letter-spacing:.8px;padding:8px 4px;
    cursor:pointer;transition:all .2s;text-align:center;border-radius:2px;}
  .cmd-btn:hover{background:rgba(200,20,20,.22);border-color:#ff3333;color:#fff;
    box-shadow:0 0 10px rgba(255,30,30,.25);}
  .cmd-btn.active{background:rgba(200,20,20,.28);border-color:#ff5555;color:#ff9999;}

  /* ── KEYFRAMES ── */
  @keyframes pulse-text{0%,100%{opacity:1;}50%{opacity:.45;}}
  @keyframes blink{0%,49%{opacity:1;}50%,100%{opacity:0;}}
  @keyframes slide-in{from{transform:translateX(-6px);opacity:0;}to{transform:translateX(0);opacity:1;}}
  @keyframes spin-cw{from{transform:rotate(0);}to{transform:rotate(360deg);}}
  @keyframes spin-ccw{from{transform:rotate(0);}to{transform:rotate(-360deg);}}
</style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="scan-overlay"></div>

<div id="hud">

  <!-- TOP BAR -->
  <div id="topbar">
    <div>
      <div class="logo">ULTRON</div>
      <div class="logo-sub">OMNI-STATION  v6.0</div>
    </div>
    <div id="threatWrap">
      <div id="threatLabel">● THREAT LEVEL: CRITICAL</div>
      <div id="threatBar"></div>
    </div>
    <div id="clockWrap">
      <div id="sysTime">00:00:00</div>
      <div id="sysDate">--</div>
    </div>
  </div>

  <!-- LEFT PANEL -->
  <div class="side-panel" id="leftPanel">
    <div class="ca tl"></div><div class="ca br"></div>
    <div class="panel-title">◈ SYSTEM METRICS</div>
    <div class="stat-row"><div class="stat-label"><span>CPU CORE</span><span id="cpuV">--</span></div><div class="stat-track"><div class="stat-fill fr" id="cpuB" style="width:0%"></div></div></div>
    <div class="stat-row"><div class="stat-label"><span>RAM USAGE</span><span id="ramV">--</span></div><div class="stat-track"><div class="stat-fill fo" id="ramB" style="width:0%"></div></div></div>
    <div class="stat-row"><div class="stat-label"><span>NEURAL LINK</span><span id="netV">--</span></div><div class="stat-track"><div class="stat-fill fc" id="netB" style="width:0%"></div></div></div>
    <div class="stat-row"><div class="stat-label"><span>ARC REACTOR</span><span id="arcV">--</span></div><div class="stat-track"><div class="stat-fill fg" id="arcB" style="width:0%"></div></div></div>
    <div class="stat-row"><div class="stat-label"><span>SHIELD INT.</span><span id="shldV">--</span></div><div class="stat-track"><div class="stat-fill fr" id="shldB" style="width:0%"></div></div></div>
    <div class="stat-row"><div class="stat-label"><span>POWER CORE</span><span id="pwrV">--</span></div><div class="stat-track"><div class="stat-fill fo" id="pwrB" style="width:0%"></div></div></div>

    <div class="panel-title" style="margin-top:12px;">◈ ACTIVE ALERTS</div>
    <div id="alertList"></div>

    <div class="panel-title" style="margin-top:8px;">◈ PROCESS LOG</div>
    <div id="logWrap"></div>
  </div>

  <!-- CENTER HUD -->
  <div id="centerHud">
    <div id="sphereWrap">
      <canvas id="sphereCanvas" width="300" height="300"></canvas>

      <!-- rotating rings SVG -->
      <svg class="ring-svg" width="300" height="300" style="pointer-events:none;">
        <g style="transform-origin:150px 150px;animation:spin-cw 10s linear infinite">
          <circle cx="150" cy="150" r="130" fill="none" stroke="rgba(200,30,30,0.2)" stroke-width=".8" stroke-dasharray="6 6"/>
        </g>
        <g style="transform-origin:150px 150px;animation:spin-ccw 7s linear infinite">
          <circle cx="150" cy="150" r="116" fill="none" stroke="rgba(200,30,30,0.14)" stroke-width=".6" stroke-dasharray="3 9"/>
        </g>
        <!-- tick marks -->
        <g stroke="rgba(200,30,30,0.35)" stroke-width=".8">
          <line x1="150" y1="20" x2="150" y2="32"/><line x1="150" y1="268" x2="150" y2="280"/>
          <line x1="20"  y1="150" x2="32" y2="150"/><line x1="268" y1="150" x2="280" y2="150"/>
        </g>
      </svg>

      <!-- reticle -->
      <svg id="reticle" viewBox="0 0 220 220" style="position:absolute;top:40px;left:40px;pointer-events:none;">
        <g style="transform-origin:110px 110px;animation:spin-cw 14s linear infinite">
          <circle cx="110" cy="110" r="90" fill="none" stroke="rgba(255,30,30,0.1)" stroke-width=".5" stroke-dasharray="4 10"/>
          <path d="M110 20L110 38M110 182L110 200M20 110L38 110M182 110L200 110" stroke="rgba(255,30,30,0.35)" stroke-width="1.2" fill="none"/>
        </g>
        <g style="transform-origin:110px 110px;animation:spin-ccw 9s linear infinite">
          <circle cx="110" cy="110" r="72" fill="none" stroke="rgba(200,20,20,0.12)" stroke-width=".5" stroke-dasharray="8 16"/>
        </g>
      </svg>

      <div id="coreOverlay">
        <!-- inner SVG rings -->
        <svg width="140" height="140" viewBox="0 0 140 140" style="position:absolute;pointer-events:none;">
          <g style="transform-origin:70px 70px;animation:spin-cw 6s linear infinite">
            <circle cx="70" cy="70" r="55" fill="none" stroke="rgba(255,40,40,0.45)" stroke-width="1" stroke-dasharray="5 4"/>
          </g>
          <g style="transform-origin:70px 70px;animation:spin-ccw 4s linear infinite">
            <circle cx="70" cy="70" r="44" fill="none" stroke="rgba(255,40,40,0.3)" stroke-width=".7" stroke-dasharray="3 7"/>
          </g>
          <circle cx="70" cy="70" r="30" fill="rgba(180,20,20,0.12)" stroke="rgba(255,40,40,0.55)" stroke-width=".8"/>
          <circle cx="70" cy="70" r="20" fill="rgba(200,30,30,0.18)" stroke="rgba(255,60,60,0.7)" stroke-width="1.2"/>
          <!-- eye -->
          <ellipse cx="70" cy="70" rx="9" ry="5.5" fill="#ff1a1a" opacity=".9"/>
          <ellipse cx="70" cy="70" rx="4.5" ry="2.8" fill="#fff" opacity=".8"/>
        </svg>
        <div id="ultronName">ULTRON</div>
        <div id="ultronSub">THREAT ANALYSIS ACTIVE</div>
      </div>
    </div>

    <div id="modeLabel">● STANDBY</div>
    <div id="modeSub">SAY  HEY ULTRON  OR PRESS F8</div>

    <!-- text input -->
    <div id="inputRow">
      <input id="cmdInput" type="text" placeholder="Type command or question..." autocomplete="off"
             onkeydown="if(event.key==='Enter') sendCmd()"/>
      <button id="sendBtn" onclick="sendCmd()">SEND ▶</button>
    </div>
    <div id="responseBox"><div id="responseText"></div></div>
  </div>

  <!-- RIGHT PANEL -->
  <div class="side-panel" id="rightPanel">
    <div class="ca tr"></div><div class="ca bl"></div>
    <div class="panel-title">◈ RADAR SCAN</div>
    <div id="radarWrap"><canvas id="radarCanvas" width="150" height="150"></canvas></div>

    <div class="panel-title">◈ CAPABILITIES</div>
    <div id="capList">
      <div class="cap-row"><div class="dot grn" id="capOllama"></div>OLLAMA AI</div>
      <div class="cap-row"><div class="dot grn" id="capVoice"></div>VOICE INPUT</div>
      <div class="cap-row"><div class="dot grn" id="capTts"></div>TTS ENGINE</div>
      <div class="cap-row"><div class="dot grn" id="capScreen"></div>SCREEN CAPTURE</div>
      <div class="cap-row"><div class="dot ora" id="capSpotify"></div>SPOTIFY</div>
      <div class="cap-row"><div class="dot grn"></div>SHELL ACCESS</div>
      <div class="cap-row"><div class="dot grn"></div>WHATSAPP</div>
      <div class="cap-row"><div class="dot ora" id="capFace"></div>FACE DETECT</div>
      <div class="cap-row"><div class="dot grn"></div>SELF-HEALER</div>
      <div class="cap-row"><div class="dot red"></div>ARC REACTOR</div>
    </div>

    <div class="panel-title" style="margin-top:8px;">◈ NETWORK</div>
    <div style="font-size:8px;color:#506070;line-height:2;">
      IP: <span id="ipOut" style="color:#90a8b0;">--</span><br>
      HOST: <span id="hostOut" style="color:#90a8b0;">--</span><br>
      OLLAMA: <span style="color:#00cc44;">ONLINE</span><br>
      MODEL: <span style="color:#90a8b0;" id="modelOut">llama3.2</span><br>
      UPTIME: <span id="uptimeOut" style="color:#90a8b0;">00:00:00</span>
    </div>
  </div>

  <!-- BOTTOM BAR -->
  <div id="bottomBar">
    <button class="cmd-btn" onclick="pyCmd('screenshot')">📸 SCREENSHOT</button>
    <button class="cmd-btn" onclick="pyCmd('sysreport')">🖥 SYS REPORT</button>
    <button class="cmd-btn" onclick="pyCmd('afk')"  id="afkBtn">👻 AFK GHOST</button>
    <button class="cmd-btn" onclick="pyCmd('listen')" id="listenBtn">🎙 VOICE LISTEN</button>
    <button class="cmd-btn" onclick="pyCmd('spotify')">🎵 SPOTIFY</button>
    <button class="cmd-btn" onclick="pyCmd('shell')">💻 SHELL CMD</button>
  </div>

</div><!-- #hud -->

<script>
// ── PYTHON BRIDGE ─────────────────────────────────────────────────────────────
function pyCmd(cmd, arg){
  try{ window.pywebview.api.handle_btn(cmd, arg||''); }
  catch(e){ console.log('pywebview not ready:', e); }
}

function sendCmd(){
  const v = document.getElementById('cmdInput').value.trim();
  if(!v) return;
  document.getElementById('cmdInput').value='';
  setResponse('⟳ Processing...', '#607080');
  pyCmd('chat', v);
}

// called FROM Python to update the HUD
function hudUpdate(data){
  try{
    if(data.mode)     setMode(data.mode, data.sub||'');
    if(data.response) setResponse(data.response, '#80a8c0');
    if(data.log)      addLog(data.log);
    if(data.alert)    addAlert(data.alert, data.alertClass||'');
    if(data.ticker)   document.getElementById('ultronSub').textContent = data.ticker;
    if(data.stats)    updateStats(data.stats);
    if(data.listening !== undefined) setListening(data.listening);
    if(data.afk !== undefined)       setAfk(data.afk);
  } catch(e){ console.log('hudUpdate error:', e); }
}

function setMode(label, sub){
  document.getElementById('modeLabel').textContent = label;
  document.getElementById('modeSub').textContent   = sub || '';
}
function setResponse(text, color){
  const el = document.getElementById('responseText');
  el.textContent = text;
  el.style.color = color || '#80a0b0';
}
function setListening(on){
  const btn = document.getElementById('listenBtn');
  btn.textContent = on ? '🔴 LISTENING...' : '🎙 VOICE LISTEN';
  btn.classList.toggle('active', on);
}
function setAfk(on){
  const btn = document.getElementById('afkBtn');
  btn.textContent = on ? '⚠ AFK ACTIVE' : '👻 AFK GHOST';
  btn.classList.toggle('active', on);
}
function updateStats(s){
  const pairs=[['cpu','cpuV','cpuB'],['ram','ramV','ramB'],
               ['net','netV','netB'],['arc','arcV','arcB'],
               ['shld','shldV','shldB'],['pwr','pwrV','pwrB']];
  pairs.forEach(([k,vi,bi])=>{
    if(s[k]===undefined) return;
    document.getElementById(vi).textContent = s[k]+'%';
    document.getElementById(bi).style.width  = s[k]+'%';
  });
}

// ── CLOCK + UPTIME ────────────────────────────────────────────────────────────
const _start = Date.now();
function updateClock(){
  const n = new Date();
  document.getElementById('sysTime').textContent = n.toTimeString().slice(0,8);
  document.getElementById('sysDate').textContent = n.toDateString().toUpperCase();
  const up = Math.floor((Date.now()-_start)/1000);
  document.getElementById('uptimeOut').textContent =
    String(Math.floor(up/3600)).padStart(2,'0')+':'+
    String(Math.floor((up%3600)/60)).padStart(2,'0')+':'+
    String(up%60).padStart(2,'0');
}
setInterval(updateClock, 1000); updateClock();

// ── THREAT BAR ────────────────────────────────────────────────────────────────
const tb = document.getElementById('threatBar');
for(let i=0;i<14;i++){
  const s=document.createElement('div'); s.className='tseg';
  s.style.background = i<10 ? 'rgba(255,30,30,0.9)' : i<12 ? 'rgba(255,140,0,0.5)' : 'rgba(60,80,100,0.2)';
  tb.appendChild(s);
}

// ── LIVE STATS SIMULATION ─────────────────────────────────────────────────────
const statBases={cpu:80,ram:62,net:92,arc:99,shld:40,pwr:76};
function jitter(v,r){return Math.min(100,Math.max(1,Math.round(v+(Math.random()-.5)*r)));}
function liveStats(){
  const s={};
  Object.keys(statBases).forEach(k=>s[k]=jitter(statBases[k],5));
  updateStats(s);
}
setInterval(liveStats, 1800); liveStats();

// ── LOG ───────────────────────────────────────────────────────────────────────
const logLines=['BOOT SEQUENCE COMPLETE','NEURAL LINK ESTABLISHED','MEMORY SCAN OK',
  'THREAT PERIMETER ACTIVE','VOICE CALIBRATION DONE','WATCHDOG STARTED',
  'PACKAGE HEALTH: OK','SELF-HEAL MONITOR ON','OLLAMA: READY','SPEAKER INIT'];
let _logIdx=0;
function addLog(msg){
  const d=document.createElement('div'); d.className='log-line hi';
  const t=new Date().toTimeString().slice(0,8);
  d.textContent=`[${t}] ${msg||logLines[_logIdx++%logLines.length]}`;
  const w=document.getElementById('logWrap');
  w.insertBefore(d,w.firstChild);
  if(w.children.length>10) w.removeChild(w.lastChild);
}
setInterval(()=>addLog(), 2200); addLog();

// ── ALERTS ────────────────────────────────────────────────────────────────────
const alertPool=[['PROXIMITY BREACH DETECTED',''],['POWER FLUCTUATION','warn'],
  ['NEURAL LINK ACTIVE','info'],['SCANNING SECTOR 12','info'],
  ['SHIELD RECHARGING','warn'],['TARGET ACQUIRED','']];
let _alertIdx=0;
function addAlert(msg, cls){
  const [m,c]=msg?[msg,cls]:alertPool[_alertIdx++%alertPool.length];
  const d=document.createElement('div'); d.className='alert'+(c?' '+c:'');
  d.textContent=m;
  const list=document.getElementById('alertList');
  list.insertBefore(d,list.firstChild);
  if(list.children.length>5) list.removeChild(list.lastChild);
}
setInterval(()=>addAlert(), 3800);
addAlert('THREAT DETECTED — SECTOR 7','');
addAlert('SHIELD INTEGRITY LOW','warn');
addAlert('NEURAL LINK ACTIVE','info');

// ── BACKGROUND — STARS + SNOW ─────────────────────────────────────────────────
const bgC=document.getElementById('bg');
const bgX=bgC.getContext('2d');
bgC.width=window.innerWidth; bgC.height=window.innerHeight;
const stars=Array.from({length:130},()=>({
  x:Math.random()*bgC.width,y:Math.random()*bgC.height,
  r:Math.random()*1.2+.3,t:Math.random()*Math.PI*2,s:Math.random()*.04+.01
}));
const snow=Array.from({length:90},()=>({
  x:Math.random()*bgC.width,y:Math.random()*bgC.height,
  r:Math.random()*1.5+.4,vy:Math.random()*.7+.25,vx:Math.random()*.5-.25,
  op:Math.random()*.55+.2
}));
function drawBG(){
  bgX.fillStyle='rgba(2,4,8,0.2)'; bgX.fillRect(0,0,bgC.width,bgC.height);
  stars.forEach(s=>{
    s.t+=s.s;
    bgX.beginPath(); bgX.arc(s.x,s.y,s.r,0,Math.PI*2);
    bgX.fillStyle=`rgba(180,200,220,${(.5+.5*Math.sin(s.t))*.7})`; bgX.fill();
  });
  snow.forEach(s=>{
    s.y+=s.vy; s.x+=s.vx;
    if(s.y>bgC.height){s.y=0;s.x=Math.random()*bgC.width;}
    if(s.x<0)s.x=bgC.width; if(s.x>bgC.width)s.x=0;
    bgX.beginPath(); bgX.arc(s.x,s.y,s.r,0,Math.PI*2);
    bgX.fillStyle=`rgba(220,232,244,${s.op})`; bgX.fill();
  });
  requestAnimationFrame(drawBG);
}
drawBG();

// ── 3D SPHERE ─────────────────────────────────────────────────────────────────
const sC=document.getElementById('sphereCanvas');
const sX=sC.getContext('2d');
const R=90,CX=150,CY=150;
let ang=0,tlt=0,sTick=0;
const grid=[];
for(let lat=0;lat<9;lat++){
  const phi=Math.PI*(lat+1)/10-Math.PI/2;
  for(let d=0;d<48;d++){
    const th=2*Math.PI*d/48;
    grid.push({x:R*Math.cos(phi)*Math.cos(th),y:R*Math.sin(phi),z:R*Math.cos(phi)*Math.sin(th),t:'g'});
  }
}
for(let lon=0;lon<14;lon++){
  const th=2*Math.PI*lon/14;
  for(let d=0;d<48;d++){
    const phi=Math.PI*d/48-Math.PI/2;
    grid.push({x:R*Math.cos(phi)*Math.cos(th),y:R*Math.sin(phi),z:R*Math.cos(phi)*Math.sin(th),t:'g'});
  }
}
const equator=[];
for(let d=0;d<80;d++){
  const th=2*Math.PI*d/80;
  equator.push({x:R*Math.cos(th),y:0,z:R*Math.sin(th)});
}
function ry(x,y,z,a){return{x:x*Math.cos(a)+z*Math.sin(a),y,z:-x*Math.sin(a)+z*Math.cos(a)};}
function rx(x,y,z,a){return{x,y:y*Math.cos(a)-z*Math.sin(a),z:y*Math.sin(a)+z*Math.cos(a)};}
function proj(x,y,z){const f=320,s=f/(z+f+.001);return{px:CX+x*s,py:CY+y*s,s};}

function drawSphere(){
  sX.clearRect(0,0,300,300);
  ang+=0.013; tlt=Math.sin(sTick*.0025)*.18; sTick++;
  const pulse=Math.abs(Math.sin(sTick*.05));
  grid.forEach(d=>{
    let {x,y,z}=ry(d.x,d.y,d.z,ang); ({x,y,z}=rx(x,y,z,tlt));
    const{px,py,s}=proj(x,y,z);
    const b=Math.max(0,z/R)*.75+.25;
    sX.beginPath(); sX.arc(px,py,1.0*s*.85,0,Math.PI*2);
    sX.fillStyle=`rgba(${Math.round(160*b+20)},${Math.round(12*b)},${Math.round(12*b)},${b})`;
    sX.fill();
  });
  equator.forEach(d=>{
    let {x,y,z}=ry(d.x,d.y,d.z,ang); ({x,y,z}=rx(x,y,z,tlt));
    const{px,py,s}=proj(x,y,z);
    const b=Math.max(0,z/R)*.75+.25;
    sX.beginPath(); sX.arc(px,py,2.1*s*.9,0,Math.PI*2);
    sX.fillStyle=`rgba(255,${Math.round(40+55*b)},${Math.round(40+55*b)},${b*.9})`; sX.fill();
  });
  // core glow
  const g=sX.createRadialGradient(CX,CY,0,CX,CY,20+pulse*7);
  g.addColorStop(0,'rgba(255,80,80,.95)'); g.addColorStop(.5,'rgba(200,20,20,.45)'); g.addColorStop(1,'rgba(150,10,10,0)');
  sX.beginPath(); sX.arc(CX,CY,20+pulse*7,0,Math.PI*2); sX.fillStyle=g; sX.fill();
  requestAnimationFrame(drawSphere);
}
drawSphere();

// ── RADAR ─────────────────────────────────────────────────────────────────────
const rC=document.getElementById('radarCanvas');
const rX=rC.getContext('2d');
let rAng=0;
const blips=[{a:.8,d:.44},{a:2.1,d:.7},{a:3.5,d:.3},{a:4.8,d:.6},{a:5.4,d:.8}];
function drawRadar(){
  rX.fillStyle='rgba(2,6,3,0.28)'; rX.fillRect(0,0,150,150);
  const cx=75,cy=75,mr=66;
  [.25,.5,.75,1].forEach(f=>{
    rX.beginPath(); rX.arc(cx,cy,mr*f,0,Math.PI*2);
    rX.strokeStyle='rgba(0,180,60,.18)'; rX.lineWidth=.5; rX.stroke();
  });
  rX.strokeStyle='rgba(0,160,50,.12)'; rX.lineWidth=.5;
  rX.beginPath(); rX.moveTo(cx-mr,cy); rX.lineTo(cx+mr,cy); rX.stroke();
  rX.beginPath(); rX.moveTo(cx,cy-mr); rX.lineTo(cx,cy+mr); rX.stroke();
  rX.save(); rX.translate(cx,cy); rX.rotate(rAng);
  rX.beginPath(); rX.moveTo(0,0); rX.arc(0,0,mr,-.55,0); rX.closePath();
  rX.fillStyle='rgba(200,30,30,0.1)'; rX.fill();
  rX.beginPath(); rX.moveTo(0,0); rX.lineTo(mr,0);
  rX.strokeStyle='rgba(255,40,40,.75)'; rX.lineWidth=.9; rX.stroke();
  rX.restore(); rAng+=0.038;
  blips.forEach(b=>{
    const age=((rAng-b.a)%(Math.PI*2)+Math.PI*2)%(Math.PI*2);
    const fade=Math.max(0,1-age/(Math.PI*.85));
    if(fade>0){
      const bx=cx+Math.cos(b.a)*mr*b.d, by=cy+Math.sin(b.a)*mr*b.d;
      rX.beginPath(); rX.arc(bx,by,2.8,0,Math.PI*2);
      rX.fillStyle=`rgba(255,40,40,${fade})`; rX.fill();
      rX.beginPath(); rX.arc(bx,by,5.5,0,Math.PI*2);
      rX.strokeStyle=`rgba(255,40,40,${fade*.45})`; rX.lineWidth=.5; rX.stroke();
    }
  });
  requestAnimationFrame(drawRadar);
}
drawRadar();

// ── RESIZE ────────────────────────────────────────────────────────────────────
window.addEventListener('resize',()=>{bgC.width=window.innerWidth;bgC.height=window.innerHeight;});

// initial log burst
setTimeout(()=>addLog('ULTRON ONLINE — SYSTEMS NOMINAL'), 800);
setTimeout(()=>addLog('VOICE RECOGNITION CALIBRATING'), 1600);
</script>
</body>
</html>
"""

# ══════════════════════════════════════════════════════════════════════════════
#  PYTHON → JS BRIDGE  (calls hudUpdate in the browser)
# ══════════════════════════════════════════════════════════════════════════════

def _js(data: dict):
    """Push a data dict into the running HUD via JS."""
    global _window
    if not _window: return
    try:
        payload = json.dumps(data, ensure_ascii=False).replace("'", "\\'")
        _window.evaluate_js(f"hudUpdate({payload})")
    except Exception as e:
        print(f"[JS] {e}")

def apply_theme(mode):
    labels = {
        "python": ("● ACTIVE",         "PYTHON CORE RUNNING"),
        "ollama": ("● NEURAL LINK",     "OLLAMA THINKING — SAY STOP"),
        "wake":   ("● STANDBY",         f"SAY  HEY ULTRON  OR PRESS {HOTKEY.upper()}"),
        "typing": ("● AUTO-TYPE",       "DICTATE NOW — SAY STOP TYPING"),
    }
    lbl, sub = labels.get(mode, labels["wake"])
    _js({"mode": lbl, "sub": sub})

def log_command(user, action):
    _js({"log": f"{user[:28]} → {action[:40]}"})

def update_gui_status(s):
    _js({"mode": f"● {s[:36]}", "sub": ""})

def update_wake_label(t):
    _js({"sub": t[:60]})

# ══════════════════════════════════════════════════════════════════════════════
#  VOICE MANAGER  (thread-safe TTS)
# ══════════════════════════════════════════════════════════════════════════════
class VoiceManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._q    = queue.Queue()
        self._eng  = None
        threading.Thread(target=self._worker, daemon=True).start()

    def _init_engine(self):
        """Initialize engine once and reuse it."""
        try:
            eng = pyttsx3.init()
            eng.setProperty("rate", 175)
            voices = eng.getProperty("voices")
            for v in voices:
                if any(k in v.name.lower() for k in ("david","mark","male","daniel","george")):
                    eng.setProperty("voice", v.id); break
            else:
                if voices: eng.setProperty("voice", voices[0].id)
            return eng
        except Exception:
            return None

    def _worker(self):
        eng = self._init_engine() if TTS_OK else None
        while True:
            text = self._q.get()
            if text is None: break
            if eng is None: continue
            with self._lock:
                try:
                    eng.say(text); eng.runAndWait()
                except Exception:
                    # Engine may have crashed; try reinitializing
                    try: eng.stop()
                    except Exception: pass
                    eng = self._init_engine()

    def speak(self, text):
        print(f"[ULTRON]: {text}")
        if not TTS_OK: return
        clean = re.sub(r'[#*`_\[\]()\u2022\u25cf]', '', text)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean: self._q.put(clean[:480])

_voice = VoiceManager()
def speak(text):
    _voice.speak(text)
    _js({"log": f"ULTRON: {text[:60]}"})

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM STATS PUSH (real psutil data → HUD every 2s)
# ══════════════════════════════════════════════════════════════════════════════
def _stats_loop():
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "N/A"
    host = platform.node()
    _js({"stats": {"net": 94, "arc": 99}})
    _js({"log": f"HOST:{host} IP:{ip}"})
    # push IP/host once
    global _window
    if _window:
        try:
            _window.evaluate_js(
                f"document.getElementById('ipOut').textContent='{ip}';"
                f"document.getElementById('hostOut').textContent='{host[:16]}';"
            )
        except Exception: pass
    while not EXIT_FLAG:
        if PSUTIL_OK:
            try:
                cpu  = int(psutil.cpu_percent(interval=None))
                ram  = int(psutil.virtual_memory().percent)
                _js({"stats": {"cpu": cpu, "ram": ram}})
            except Exception: pass
        time.sleep(2)

# ══════════════════════════════════════════════════════════════════════════════
#  PYWEBVIEW API  (buttons in HUD call this)
# ══════════════════════════════════════════════════════════════════════════════
_listening_active = [False]
_afk_active       = [False]

class UltronAPI:
    """Exposed to JS as window.pywebview.api"""

    def handle_btn(self, cmd, arg=""):
        threading.Thread(target=self._dispatch, args=(cmd, arg), daemon=True).start()

    def _dispatch(self, cmd, arg):
        global is_afk
        if cmd == "chat":
            _js({"mode": "● NEURAL LINK", "sub": "PROCESSING..."})
            if not process_command(arg.lower().strip()):
                ask_ai(arg)
        elif cmd == "screenshot":
            take_screenshot_and_analyze()
        elif cmd == "sysreport":
            _act_sysreport()
        elif cmd == "listen":
            _toggle_listening()
        elif cmd == "afk":
            if not is_afk:
                is_afk = True
                _afk_active[0] = True
                _js({"afk": True})
                speak("AFK protocol engaged.")
                threading.Thread(target=afk_movement_loop, daemon=True).start()
            else:
                is_afk = False
                _afk_active[0] = False
                _afk_release_all()
                _js({"afk": False})
                speak("AFK terminated.")
        elif cmd == "spotify":
            threading.Thread(target=spotify_now_playing, daemon=True).start()
        elif cmd == "shell":
            _prompt_shell_input()

def _toggle_listening():
    if _listening_active[0]:
        _listening_active[0] = False
        _js({"listening": False, "mode": "● STANDBY",
             "sub": f"SAY  HEY ULTRON  OR PRESS {HOTKEY.upper()}"})
    else:
        _listening_active[0] = True
        _js({"listening": True, "mode": "● VOICE ACTIVE", "sub": "LISTENING..."})
        speak("Voice mode on. Speak now.")
        threading.Thread(target=_one_shot_listen, daemon=True).start()

def _one_shot_listen():
    if not SPEECH_OK: return
    r = sr.Recognizer()
    try:
        with sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.5)
            audio = r.listen(src, timeout=8, phrase_time_limit=12)
        text = r.recognize_google(audio, language="en-IN").strip()
        _js({"listening": False, "log": f"VOICE: {text}"})
        _listening_active[0] = False
        if not process_command(text.lower()):
            ask_ai(text)
    except Exception:
        _js({"listening": False, "mode": "● STANDBY",
             "sub": f"SAY  HEY ULTRON  OR PRESS {HOTKEY.upper()}"})
        _listening_active[0] = False

def _act_sysreport():
    if not PSUTIL_OK: speak("psutil not available."); return
    cpu  = psutil.cpu_percent(interval=1)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    bat  = psutil.sensors_battery()
    rep  = (f"CPU {cpu}% | RAM {mem.percent}% ({round(mem.used/1e9,1)}/{round(mem.total/1e9,1)}GB) | "
            f"Disk {round(disk.used/1e9,1)}/{round(disk.total/1e9,1)}GB")
    if bat:
        rep += f" | Bat {int(bat.percent)}% {'plugged' if bat.power_plugged else 'battery'}"
    speak(rep)
    _js({"response": rep})
    log_command("sysreport", rep[:80])

def _prompt_shell_input():
    # Use JS prompt dialog inside webview
    global _window
    if not _window: return
    try:
        cmd = _window.evaluate_js("prompt('Enter shell command:','')") or ""
        if cmd.strip():
            out = run_shell(cmd.strip())
            _js({"response": out[:200], "log": f"$ {cmd[:40]}"})
    except Exception as e:
        _js({"response": f"Shell error: {e}"})

# ══════════════════════════════════════════════════════════════════════════════
#  OLLAMA AI
# ══════════════════════════════════════════════════════════════════════════════
def ask_ai(question, extra_ctx=""):
    global ollama_running
    apply_theme("ollama"); speak("Accessing neural link...")
    log_command(question, "Routing to Ollama AI...")
    ollama_running = True
    full_msg = f"{extra_ctx}\n{question}".strip() if extra_ctx else question
    _chat_history.append({"role":"user","content":full_msg})

    def fetch():
        global ollama_running; reply=""
        try:
            if OLLAMA_LIB_OK:
                res = ollama_lib.chat(model=OLLAMA_MODEL, messages=_chat_history[-24:])
                reply = res.message.content
            elif REQUESTS_OK:
                r = requests.post(OLLAMA_CHAT_URL,
                    json={"model":OLLAMA_MODEL,"system":ULTRON_SYSTEM,
                          "messages":_chat_history[-24:],"stream":False}, timeout=90)
                r.raise_for_status(); reply = r.json()["message"]["content"]
            else: reply = "⚠ No Ollama connection. Run: ollama serve"
        except Exception as e: reply = f"⚠ Neural link offline: {e}"
        finally: ollama_running = False
        _chat_history.append({"role":"assistant","content":reply})
        remember_conversation(question, reply)
        speak(reply[:300])
        _js({"response": reply[:300], "mode":"● ACTIVE","sub":"AWAITING COMMAND"})
        log_command(question, reply[:80])

    threading.Thread(target=fetch, daemon=True).start()

    def interrupt_listener():
        global ollama_running
        if not SPEECH_OK: return
        r2 = sr.Recognizer()
        while ollama_running and not EXIT_FLAG:
            try:
                with sr.Microphone() as src:
                    r2.adjust_for_ambient_noise(src, duration=0.2)
                    audio = r2.listen(src, timeout=3, phrase_time_limit=3)
                    if "stop" in r2.recognize_google(audio).lower():
                        ollama_running = False; speak("Neural link cut.")
                        apply_theme("python"); break
            except Exception: pass
    threading.Thread(target=interrupt_listener, daemon=True).start()

# ══════════════════════════════════════════════════════════════════════════════
#  VOLUME
# ══════════════════════════════════════════════════════════════════════════════
def set_system_volume(level):
    if not PYCAW_OK: speak("Volume control not available."); return
    try:
        from ctypes import cast, POINTER
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume[0].SetMasterVolumeLevelScalar(float(level) / 100.0, None)
        speak(f"Volume locked at {level} percent."); log_command(f"volume {level}", f"{level}%")
    except Exception as e: speak("Volume control failure."); log_command(f"volume {level}", str(e))

# ══════════════════════════════════════════════════════════════════════════════
#  CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
def perform_calculation(phrase):
    phrase = phrase.replace("for","").replace("of","").replace("is","")
    op_func = op_name = None
    for name, func in OPERATORS.items():
        if name in phrase: op_func=func; op_name=name; break
    if not op_func: speak("Cannot identify operation."); return
    try:
        p = phrase.split(op_name,1)
        n1 = re.findall(r"[-+]?\d*\.?\d+",p[0]); n2 = re.findall(r"[-+]?\d*\.?\d+",p[1])
        if not n1 or not n2: speak("Two numbers required."); return
        num1,num2 = float(n1[-1]),float(n2[0]); result = op_func(num1,num2)
        res_str = str(int(result)) if result==int(result) else f"{result:.4f}"
        speak(f"Result: {res_str}"); _js({"response": f"= {res_str}"})
        log_command(phrase, f"{num1} {op_name} {num2} = {res_str}")
    except Exception as e: speak("Calculation error."); log_command(phrase, str(e))

# ══════════════════════════════════════════════════════════════════════════════
#  TIMER
# ══════════════════════════════════════════════════════════════════════════════
def timer_countdown(seconds):
    global timer_active; timer_active=True; end=time.time()+seconds
    while time.time()<end and timer_active: time.sleep(1)
    if timer_active: time.sleep(0.5); speak("Timer complete."); log_command("Timer",f"{seconds}s done.")
    timer_active=False

def start_timer(mins,secs):
    global timer_thread; total=mins*60+secs
    if total<=0: speak("Invalid duration."); return
    if timer_active: speak("Timer already running."); return
    parts=[]
    if mins>0: parts.append(f"{mins} min{'s' if mins!=1 else ''}")
    if secs>0: parts.append(f"{secs} sec{'s' if secs!=1 else ''}")
    speak(f"Timer set. {' and '.join(parts)}.")
    log_command("start timer",f"{total}s")
    timer_thread=threading.Thread(target=timer_countdown,args=(total,),daemon=True); timer_thread.start()

def cancel_timer():
    global timer_active
    if timer_active: timer_active=False; speak("Timer aborted.")
    else: speak("No active timer.")

# ══════════════════════════════════════════════════════════════════════════════
#  REMINDERS
# ══════════════════════════════════════════════════════════════════════════════
def reminder_watcher():
    global reminders
    while not EXIT_FLAG:
        now=datetime.datetime.now()
        done=[r for r in reminders if now>=r["time"]]
        for r in done:
            speak(f"Reminder: {r['message']}"); log_command("REMINDER",r['message']); reminders.remove(r)
        time.sleep(10)

def set_reminder(cmd):
    try:
        mm=re.search(r"in (\d+) minute",cmd); hh=re.search(r"in (\d+) hour",cmd); ss_m=re.search(r"in (\d+) second",cmd)
        total=0
        if mm: total+=int(mm.group(1))*60
        if hh: total+=int(hh.group(1))*3600
        if ss_m: total+=int(ss_m.group(1))
        if total==0: speak("I need a time duration."); return
        to_m=re.search(r"\bto\b (.+)$",cmd); message=to_m.group(1).strip() if to_m else "your reminder"
        rt=datetime.datetime.now()+datetime.timedelta(seconds=total)
        reminders.append({"time":rt,"message":message})
        speak(f"Reminder set at {rt.strftime('%I:%M %p')} to {message}.")
        log_command(cmd,f"Reminder@{rt.strftime('%H:%M')}")
    except Exception as e: speak("Failed to set reminder."); log_command(cmd,str(e))

# ══════════════════════════════════════════════════════════════════════════════
#  CLIPBOARD
# ══════════════════════════════════════════════════════════════════════════════
def read_clipboard():
    if not CLIP_OK: speak("pyperclip not available."); return
    try:
        c=pyperclip.paste()
        speak(f"Clipboard: {c[:200]}" if c.strip() else "Clipboard is empty.")
        log_command("read clipboard",c[:60])
    except Exception: speak("Cannot access clipboard.")

def clear_clipboard():
    if not CLIP_OK: return
    try: pyperclip.copy(""); speak("Clipboard wiped."); log_command("clear clipboard","Done.")
    except Exception: speak("Clipboard clear failed.")

# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER
# ══════════════════════════════════════════════════════════════════════════════
def get_weather(city):
    if not REQUESTS_OK: speak("No internet module."); return
    try:
        d=requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric",timeout=5).json()
        if d.get("cod")!=200: speak(f"Cannot retrieve weather for {city}."); return
        rep=(f"Weather in {d['name']}: {d['weather'][0]['description']}. "
             f"Temp {d['main']['temp']}C, feels like {d['main']['feels_like']}C. "
             f"Humidity {d['main']['humidity']}%.")
        speak(rep); _js({"response":rep}); log_command(f"weather {city}",rep[:80])
    except requests.exceptions.ConnectionError: speak("No internet. Weather unavailable.")
    except Exception as e: speak("Weather failure."); log_command(f"weather {city}",str(e))

# ══════════════════════════════════════════════════════════════════════════════
#  JOKES / MOTIVATION
# ══════════════════════════════════════════════════════════════════════════════
def tell_joke():   j=random.choice(JOKES);       speak(j); _js({"response":j})
def motivate():    q=random.choice(MOTIVATIONS); speak(q); _js({"response":q})

# ══════════════════════════════════════════════════════════════════════════════
#  AUTO-TYPER
# ══════════════════════════════════════════════════════════════════════════════
def start_auto_type_mode():
    global auto_type_mode; auto_type_mode=True; apply_theme("typing")
    speak("Auto-type mode on. Dictate. Say stop typing to exit.")
def stop_auto_type_mode():
    global auto_type_mode; auto_type_mode=False; apply_theme("python"); speak("Auto-type off.")

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM STATS
# ══════════════════════════════════════════════════════════════════════════════
def get_system_stats():
    if not PSUTIL_OK: speak("psutil not available."); return
    try:
        cpu=psutil.cpu_percent(interval=1); ram=psutil.virtual_memory().percent; bat=psutil.sensors_battery()
        rep=f"CPU at {cpu} percent. RAM at {ram} percent."
        if bat: rep+=f" Battery {int(bat.percent)}%, {'plugged in' if bat.power_plugged else 'on battery'}."
        speak(rep); _js({"response":rep}); log_command("system stats",rep[:80])
    except Exception as e: speak("System stats unavailable.")

def get_time_and_date():
    now=datetime.datetime.now(); rep=f"Time: {now.strftime('%I:%M %p')}. Date: {now.strftime('%A, %B %d, %Y')}."
    speak(rep); _js({"response":rep})

# ══════════════════════════════════════════════════════════════════════════════
#  FILE / FOLDER / SHELL / SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def create_folder(name):
    try:
        path=os.path.join(os.path.expanduser('~/Documents'),name); os.makedirs(path,exist_ok=True)
        speak(f"Folder {name} created."); log_command(f"create folder {name}",path)
    except Exception as e: speak("Folder creation failed.")

def open_default_folder(key):
    fm={"documents":os.path.expanduser('~/Documents'),"downloads":os.path.expanduser('~/Downloads'),
        "desktop":os.path.expanduser('~/Desktop')}
    path=fm.get(key)
    if path and os.path.exists(path):
        if platform.system()=="Windows": os.startfile(path)
        else: subprocess.Popen(["xdg-open",path])
        speak(f"Opening {key}.")
    else: speak(f"Cannot locate {key}.")

def list_files_current():
    cwd=os.getcwd(); items=sorted(os.listdir(cwd))[:30]
    lines=[f"Dir: {cwd}"]+[f"  {'D' if os.path.isdir(f) else 'F'} {f}" for f in items]
    result="\n".join(lines)
    _js({"response": f"{len(items)} items in {cwd}"}); log_command("list files",result[:120]); speak(f"{len(items)} items in current directory.")

def run_shell(cmd):
    try:
        res=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=20)
        out=(res.stdout.strip() or res.stderr.strip() or "(no output)")
        log_command(f"$ {cmd}",out[:200]); speak("Command executed."); return out
    except subprocess.TimeoutExpired: return "⚠ Timed out."
    except Exception as e: return f"⚠ Error: {e}"

def take_screenshot_and_analyze():
    speak("Capturing screen. Analyzing..."); _js({"mode":"● SCANNING","sub":"SCREEN CAPTURE IN PROGRESS"})
    def worker():
        img=None
        if PIL_OK:
            try: img=ImageGrab.grab()
            except Exception: pass
        if img is None and PYAUTOGUI_OK:
            try: img=pyautogui.screenshot()
            except Exception: pass
        if img is None: speak("Cannot capture screen."); apply_theme("python"); return
        w,h=img.size
        try: img.save(os.path.join(os.path.expanduser("~"),"ultron_screenshot.png"))
        except Exception: pass
        ctx=f"[SCREEN: {w}x{h}px | {platform.system()} | {datetime.datetime.now().strftime('%H:%M')}]"
        ask_ai("Analyze my screen. Describe what is visible and provide helpful insights.",extra_ctx=ctx)
    threading.Thread(target=worker,daemon=True).start()

def take_screenshot_snipping():
    if KEYBOARD_OK: keyboard.press_and_release("win+shift+s")
    elif PYAUTOGUI_OK: pyautogui.hotkey("win","shift","s")
    time.sleep(1)

def show_desktop():
    if KEYBOARD_OK: keyboard.press_and_release("win+d")
    elif PYAUTOGUI_OK: pyautogui.hotkey("win","d")
    time.sleep(0.5)

# ══════════════════════════════════════════════════════════════════════════════
#  MEMORY SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
def _load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE,"r") as f: return json.load(f)
    except Exception: pass
    return {"conversations":[],"facts":{}}

def _save_memory(mem):
    try:
        with open(MEMORY_FILE,"w") as f: json.dump(mem,f,indent=2)
    except Exception as e: print(f"Memory save error: {e}")

def remember_conversation(u,r):
    mem=_load_memory(); mem["conversations"].append({"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"user":u,"ultron":r[:200]})
    mem["conversations"]=mem["conversations"][-100:]; _save_memory(mem)

def remember_fact(key,value):
    mem=_load_memory(); mem["facts"][key]=value; _save_memory(mem)
    speak(f"Got it. I will remember that {key} is {value}."); log_command(f"remember: {key}",value)

def recall_memory(query):
    mem=_load_memory(); query=query.lower()
    for k,v in mem["facts"].items():
        if k.lower() in query: speak(f"I remember: {k} is {v}."); return
    matches=[c for c in mem["conversations"] if query in c["user"].lower() or query in c["ultron"].lower()]
    if matches:
        last=matches[-1]; speak(f"On {last['time']}, you said: {last['user'][:80]}.")
    else: speak("Nothing in memory matching that.")

def show_recent_memory():
    mem=_load_memory(); convos=mem["conversations"][-5:]
    if not convos: speak("Memory is empty."); return
    speak(f"Last {len(convos)} exchanges.")
    for c in convos: speak(f"On {c['time']}: {c['user'][:60]}.")

# ══════════════════════════════════════════════════════════════════════════════
#  AFK / GHOST MODE
# ══════════════════════════════════════════════════════════════════════════════
def _afk_press(key):
    global _afk_held_keys
    try: keyboard.press(key); _afk_held_keys.add(key)
    except Exception: pass

def _afk_release(key):
    global _afk_held_keys
    try: keyboard.release(key)
    except Exception: pass
    finally: _afk_held_keys.discard(key)

def _afk_release_all():
    for k in list(_afk_held_keys)+['w','a','s','d']:
        try: keyboard.release(k)
        except Exception: pass
    _afk_held_keys.clear()

def _afk_hold(keys,seconds):
    for k in keys: _afk_press(k)
    elapsed=0.0; interrupted=False
    while elapsed<seconds:
        if not is_afk: interrupted=True; break
        time.sleep(0.1); elapsed+=0.1
    for k in keys: _afk_release(k)
    return not interrupted

def afk_movement_loop():
    global is_afk
    if not _afk_lock.acquire(blocking=False): return
    log_command("AFK","Ghost mode started.")
    action_count=0; next_nudge=random.randint(3,6)
    try:
        while is_afk:
            roll=random.random(); action=""
            try:
                if roll<0.45:
                    secs=random.uniform(2.0,8.0); action=f"W forward {secs:.1f}s"; _afk_hold(['w'],secs)
                elif roll<0.65:
                    side=random.choice(['a','d']); secs=random.uniform(0.5,2.0); action=f"{side.upper()} strafe"; _afk_hold([side],secs)
                elif roll<0.80:
                    side=random.choice(['a','d']); secs=random.uniform(1.0,4.0); action=f"W+{side.upper()} diag"; _afk_hold(['w',side],secs)
                elif roll<0.90:
                    ok=_afk_hold(['s'],random.uniform(0.3,1.0)); action="S backstep"
                    if ok and is_afk: _afk_hold(['w'],random.uniform(1.0,3.0))
                else:
                    secs=random.uniform(1.0,3.0); action="idle"
                    elapsed=0.0
                    while elapsed<secs and is_afk: time.sleep(0.1); elapsed+=0.1
            except Exception as e: _afk_release_all()
            log_command("AFK",action); action_count+=1
            if action_count>=next_nudge and PYAUTOGUI_OK:
                try: pyautogui.moveRel(random.randint(-6,6),random.randint(-6,6),duration=0.15)
                except Exception: pass
                action_count=0; next_nudge=random.randint(3,6)
            if is_afk:
                p=random.uniform(0.1,0.6); e=0.0
                while e<p and is_afk: time.sleep(0.05); e+=0.05
    except Exception: log_command("AFK",f"Crash:\n{traceback.format_exc()}")
    finally: _afk_release_all(); is_afk=False; _afk_lock.release(); log_command("AFK","Stopped.")

# ══════════════════════════════════════════════════════════════════════════════
#  AUTO-CLICKER & MACROS
# ══════════════════════════════════════════════════════════════════════════════
def _auto_click_loop(cps):
    global auto_click_active; interval=1.0/max(1,cps)
    while auto_click_active:
        if PYAUTOGUI_OK: pyautogui.click()
        time.sleep(interval)

def start_auto_click(cps=10):
    global auto_click_active
    if auto_click_active: speak("Already running."); return
    auto_click_active=True; speak(f"Auto-clicker on. {cps} CPS.")
    threading.Thread(target=_auto_click_loop,args=(cps,),daemon=True).start()

def stop_auto_click():
    global auto_click_active; auto_click_active=False; speak("Auto-clicker stopped.")

def start_macro_record():
    global macro_recording,recorded_macro
    recorded_macro=[]; macro_recording=True; _last_macro_time[0]=time.time()
    speak("Recording macro. Say stop recording when done.")
    def _on_key(event):
        if macro_recording:
            delay=time.time()-_last_macro_time[0]
            recorded_macro.append({"type":"key","key":event.name,"delay":delay})
            _last_macro_time[0]=time.time()
    if KEYBOARD_OK: keyboard.on_press(_on_key)

def stop_macro_record():
    global macro_recording; macro_recording=False
    if KEYBOARD_OK: keyboard.unhook_all()
    speak(f"Macro recorded. {len(recorded_macro)} actions.")

def play_macro(loops=1):
    global macro_playback
    if not recorded_macro: speak("No macro recorded."); return
    macro_playback=True; speak(f"Playing macro {loops}x.")
    def _run():
        for _ in range(loops):
            if not macro_playback: break
            for action in recorded_macro:
                if not macro_playback: break
                time.sleep(min(action["delay"],2.0))
                if action["type"]=="key" and KEYBOARD_OK: keyboard.press_and_release(action["key"])
        speak("Macro complete.")
    threading.Thread(target=_run,daemon=True).start()

def stop_macro_play():
    global macro_playback; macro_playback=False; speak("Macro stopped.")

# ══════════════════════════════════════════════════════════════════════════════
#  PROCESS KILLER
# ══════════════════════════════════════════════════════════════════════════════
def list_top_processes():
    if not PSUTIL_OK: speak("psutil not available."); return
    procs=sorted(psutil.process_iter(["name","cpu_percent"]),key=lambda p:p.info["cpu_percent"] or 0,reverse=True)[:5]
    names=", ".join(p.info["name"] for p in procs if p.info["name"])
    speak(f"Top processes: {names}."); _js({"response":names}); log_command("list processes",names)

def kill_process(name):
    if not PSUTIL_OK: return
    killed=0
    for proc in psutil.process_iter(["name","pid"]):
        if name.lower() in (proc.info["name"] or "").lower():
            try: proc.kill(); killed+=1
            except Exception: pass
    msg=f"Terminated {killed} instance{'s' if killed>1 else ''} of {name}." if killed else f"No process named {name}."
    speak(msg); _js({"response":msg})

# ══════════════════════════════════════════════════════════════════════════════
#  SPOTIFY
# ══════════════════════════════════════════════════════════════════════════════
def _get_spotify():
    global _sp
    if not SPOTIFY_OK: speak("Spotipy not installed."); return None
    if _sp is None:
        try:
            _sp=spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope="user-read-playback-state user-modify-playback-state"))
        except Exception as e: speak("Spotify auth failed."); return None
    return _sp

def spotify_now_playing():
    sp=_get_spotify()
    if not sp: return
    try:
        track=sp.current_playback()
        if track and track["is_playing"]:
            name=track["item"]["name"]; artist=track["item"]["artists"][0]["name"]
            speak(f"Now playing: {name} by {artist}.")
            _js({"response":f"Now playing: {name} by {artist}", "ticker":f"♪ {name}  •  {artist}"})
        else: speak("Nothing playing.")
    except Exception: speak("Could not reach Spotify.")

def spotify_control(action):
    sp=_get_spotify()
    if not sp: return
    try:
        {"play":sp.start_playback,"pause":sp.pause_playback,
         "next":sp.next_track,"previous":sp.previous_track}[action]()
        speak(f"Spotify {action}.")
    except Exception: speak("Spotify control failed.")

# ══════════════════════════════════════════════════════════════════════════════
#  FACE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
def _face_watch_loop():
    global face_watch_active,wake_word_active
    if not OPENCV_OK: speak("OpenCV not installed."); face_watch_active=False; return
    cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
    cap=cv2.VideoCapture(0)
    if not cap.isOpened(): speak("Cannot access camera."); face_watch_active=False; return
    speak("Face detection active."); was_present=False
    while face_watch_active:
        ret,frame=cap.read()
        if not ret: time.sleep(0.5); continue
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces=cascade.detectMultiScale(gray,1.1,5,minSize=(80,80)); present=len(faces)>0
        if present and not was_present:
            wake_word_active=False; apply_theme("python"); speak("I see you.")
            _js({"alert":"FACE DETECTED — ACTIVE","alertClass":"info"})
        elif not present and was_present:
            wake_word_active=True; apply_theme("wake")
            _js({"alert":"FACE LOST — DORMANT","alertClass":"warn"})
        was_present=present; time.sleep(0.4)
    cap.release()

def start_face_watch():
    global face_watch_active
    if face_watch_active: speak("Already running."); return
    face_watch_active=True; threading.Thread(target=_face_watch_loop,daemon=True).start()

def stop_face_watch():
    global face_watch_active; face_watch_active=False; speak("Face detection stopped.")

# ══════════════════════════════════════════════════════════════════════════════
#  WHATSAPP
# ══════════════════════════════════════════════════════════════════════════════
WA_ANSWER_GREEN=(37,211,102); WA_REJECT_RED=(240,40,73)

def _bring_wa_to_front():
    try:
        if platform.system()=="Windows": subprocess.Popen(["powershell","-command","Start-Process 'whatsapp:'"],shell=False)
    except Exception: pass
    time.sleep(1.5)

def _scan_screen_for_colour(target_rgb,tol=55):
    if not PYAUTOGUI_OK: return None
    try:
        sw,sh=pyautogui.size(); img=pyautogui.screenshot(); px=img.load()
        tr,tg,tb=target_rgb
        for y in range(0,sh,3):
            for x in range(0,sw,3):
                r,g,b=px[x,y][:3]
                if abs(r-tr)<tol and abs(g-tg)<tol and abs(b-tb)<tol: return (x,y)
    except Exception: pass
    return None

def _click_wa_button(target_rgb,label="button"):
    pos=_scan_screen_for_colour(target_rgb)
    if pos:
        pyautogui.moveTo(pos[0],pos[1],duration=0.15); time.sleep(0.1); pyautogui.click()
        log_command(f"WA {label}",f"Clicked {pos}"); return True
    return False

def answer_whatsapp_call():
    speak("Answering WhatsApp call."); _bring_wa_to_front()
    if _click_wa_button(WA_ANSWER_GREEN,"answer"): speak("Call answered."); _incoming_call_detected[0]=False; return
    if KEYBOARD_OK:
        for s in ["ctrl+alt+a","enter","space"]: keyboard.press_and_release(s); time.sleep(0.3)
    _incoming_call_detected[0]=False

def reject_whatsapp_call():
    speak("Rejecting call."); _bring_wa_to_front()
    if _click_wa_button(WA_REJECT_RED,"reject"): speak("Call rejected."); _incoming_call_detected[0]=False; return
    if KEYBOARD_OK:
        for s in ["ctrl+alt+d","escape"]: keyboard.press_and_release(s); time.sleep(0.3)
    _incoming_call_detected[0]=False

def busy_whatsapp_call():
    speak("Answering and delivering busy message."); _bring_wa_to_front()
    answered=_click_wa_button(WA_ANSWER_GREEN,"answer")
    if not answered and KEYBOARD_OK:
        for s in ["ctrl+alt+a","enter"]: keyboard.press_and_release(s); time.sleep(0.3)
    time.sleep(3.0)
    for line in ["Hello.","Ultron here, speaking on behalf of my operator.","He is busy. He will call back. Thank you."]:
        try: eng=pyttsx3.init(); voices=eng.getProperty("voices"); eng.setProperty("voice",voices[0].id); eng.say(line); eng.runAndWait(); eng.stop()
        except Exception: pass
        time.sleep(0.4)
    time.sleep(1.0)
    hung=_click_wa_button(WA_REJECT_RED,"hangup")
    if not hung and KEYBOARD_OK:
        for s in ["ctrl+alt+d","escape"]: keyboard.press_and_release(s); time.sleep(0.3)
    speak("Message delivered."); _incoming_call_detected[0]=False

def send_whatsapp_message():
    if not SPEECH_OK: speak("Voice module not available."); return
    r_local = sr.Recognizer()
    speak("Recipient?")
    try:
        with sr.Microphone() as src:
            r_local.adjust_for_ambient_noise(src, duration=0.5)
            audio = r_local.listen(src, timeout=5, phrase_time_limit=5)
            contact = r_local.recognize_google(audio).strip()
            if not contact: speak("No contact. Aborting."); return
            speak(f"Message for {contact}?")
            time.sleep(0.5)
            audio = r_local.listen(src, timeout=10, phrase_time_limit=15)
            message = r_local.recognize_google(audio).strip()
        if not message: speak("No message. Aborting."); return
        speak(f"Transmitting to {contact}.")
        if PYAUTOGUI_OK:
            pyautogui.press("win"); time.sleep(0.5); pyautogui.write("whatsapp"); time.sleep(0.5)
            pyautogui.press("enter"); time.sleep(4.0); pyautogui.hotkey("ctrl","f"); time.sleep(0.8)
            pyautogui.write(contact); time.sleep(1.5); pyautogui.press("down"); time.sleep(0.3)
            pyautogui.press("enter"); time.sleep(1.8); pyautogui.write(message); time.sleep(0.5)
            pyautogui.press("enter")
        speak("Message transmitted."); log_command("WhatsApp", f"Sent to {contact}.")
    except Exception as e: speak("Transmission failure."); log_command("WhatsApp Error", str(e))

def _wa_call_watcher_loop():
    while _wa_call_watcher_active[0] and not EXIT_FLAG:
        try:
            pos=_scan_screen_for_colour(WA_ANSWER_GREEN)
            if pos and not _incoming_call_detected[0]:
                _incoming_call_detected[0]=True
                speak("Incoming WhatsApp call. Say answer call, I am busy, or reject call.")
                _js({"alert":"INCOMING WHATSAPP CALL","alertClass":"","mode":"● INCOMING CALL","sub":"SAY: ANSWER / BUSY / REJECT"})
            elif not pos and _incoming_call_detected[0]:
                _incoming_call_detected[0]=False; log_command("WhatsApp","Call ended.")
        except Exception: pass
        time.sleep(2.0)

# ══════════════════════════════════════════════════════════════════════════════
#  POWER / MACROS
# ══════════════════════════════════════════════════════════════════════════════
def lock_screen():
    speak("Locking workstation."); time.sleep(0.5)
    if platform.system()=="Windows": ctypes.windll.user32.LockWorkStation()
    else: subprocess.run(["xdg-screensaver","lock"])

def put_to_sleep():
    speak("Sleep mode."); time.sleep(0.5)
    if platform.system()=="Windows": os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    else: os.system("systemctl suspend")

def bro_i_am_tired_macro():
    speak("Initiating chill protocol."); show_desktop(); time.sleep(1.0)
    if PYAUTOGUI_OK:
        pyautogui.press("win"); time.sleep(0.5); pyautogui.write("Spotify"); time.sleep(0.5)
        pyautogui.press("enter"); time.sleep(6.0); pyautogui.press("playpause")
    speak("Music active. Rest, soldier.")

# ══════════════════════════════════════════════════════════════════════════════
#  HOTKEY
# ══════════════════════════════════════════════════════════════════════════════
def hotkey_activate():
    global wake_word_active
    if EXIT_FLAG: return
    if wake_word_active:
        wake_word_active=False; apply_theme("python")
        speak("Yeah?"); log_command(f"[{HOTKEY.upper()}]","Hotkey activation.")
        _js({"alert":f"HOTKEY {HOTKEY.upper()} — ACTIVE","alertClass":"info"})
    else: log_command(f"[{HOTKEY.upper()}]","Already active.")

def register_hotkey():
    if _hotkey_registered[0] or not KEYBOARD_OK: return
    try:
        keyboard.add_hotkey(HOTKEY,hotkey_activate,suppress=False); _hotkey_registered[0]=True
        print(f"[HOTKEY] '{HOTKEY.upper()}' registered.")
    except Exception as e: print(f"[HOTKEY] Failed: {e}")

def change_hotkey(new_key):
    global HOTKEY; new_key=new_key.strip().lower().replace(" ","+")
    if not new_key: speak("What key?"); return
    if KEYBOARD_OK and _hotkey_registered[0]:
        try: keyboard.remove_hotkey(HOTKEY)
        except Exception: pass
        _hotkey_registered[0]=False
    HOTKEY=new_key; register_hotkey(); speak(f"Hotkey updated to {new_key.upper()}.")

# ══════════════════════════════════════════════════════════════════════════════
#  SELF-HEALING SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
REQUIRED_PACKAGES=[
    ("speech_recognition","SpeechRecognition"),("pyttsx3","pyttsx3"),("pyautogui","pyautogui"),
    ("keyboard","keyboard"),("psutil","psutil"),("pyperclip","pyperclip"),("requests","requests"),
    ("pycaw","pycaw"),("comtypes","comtypes"),("ollama","ollama"),("cv2","opencv-python"),
    ("spotipy","spotipy"),("webview","pywebview"),
]
_managed_threads={}; _healer_log=[]

def _healer_print(msg):
    ts=datetime.datetime.now().strftime("%H:%M:%S"); line=f"[HEALER {ts}] {msg}"
    print(line); _healer_log.append(line)
    try: _js({"log":f"HEALER: {msg[:50]}"})
    except Exception: pass

def heal_install_package(imp,pip_n):
    try: importlib.import_module(imp); return True
    except ImportError:
        _healer_print(f"'{imp}' missing — installing '{pip_n}'...")
        try:
            subprocess.check_call([sys.executable,"-m","pip","install",pip_n,"--quiet"],
                                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            importlib.import_module(imp); _healer_print(f"'{pip_n}' installed."); return True
        except Exception as e: _healer_print(f"Failed '{pip_n}': {e}"); return False

def heal_all_packages():
    _healer_print("Package health check...")
    failed=[p for i,p in REQUIRED_PACKAGES if not heal_install_package(i,p)]
    if failed: _healer_print(f"Could not repair: {', '.join(failed)}")
    else: _healer_print("All packages healthy.")

def register_thread(name,fn,daemon=True,args=()):
    t=threading.Thread(target=fn,args=args,daemon=daemon,name=name)
    _managed_threads[name]=t; t.start(); _healer_print(f"Thread '{name}' started."); return t

def _watchdog_loop():
    last_pkg=time.time()
    while not EXIT_FLAG:
        time.sleep(15)
        for name,thread in list(_managed_threads.items()):
            if not thread.is_alive():
                _healer_print(f"Thread '{name}' died — restarting...")
                try:
                    new_t=threading.Thread(target=thread._target,args=thread._args or (),
                                           kwargs=thread._kwargs or {},daemon=thread.daemon,name=name)
                    new_t.start(); _managed_threads[name]=new_t; _healer_print(f"'{name}' restarted.")
                    speak(f"Self-healing: restarted {name}.")
                except Exception as e: _healer_print(f"Cannot restart '{name}': {e}")
        if time.time()-last_pkg>300: heal_all_packages(); last_pkg=time.time()

def _safe_thread_wrapper(name,fn,*args,**kwargs):
    try: fn(*args,**kwargs)
    except Exception:
        tb=traceback.format_exc(); _healer_print(f"Thread '{name}' crashed:\n{tb}")
        speak(f"Warning: {name} crashed. Self-healing will restart it.")

def show_healer_status():
    alive=[n for n,t in _managed_threads.items() if t.is_alive()]
    dead =[n for n,t in _managed_threads.items() if not t.is_alive()]
    msg=f"Self-healer: {len(alive)} threads running."
    if dead: msg+=f" {len(dead)} dead: {', '.join(dead)}."
    speak(msg); _js({"response":msg})

# ══════════════════════════════════════════════════════════════════════════════
#  WAKE WORD HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _calibrate(r, source):
    r.adjust_for_ambient_noise(source, duration=1.2)
    r.pause_threshold = 0.9
    r.non_speaking_duration = 0.6
    r.phrase_threshold = 0.3
    # Set minimum floor, then enable dynamic threshold to adapt from there
    if r.energy_threshold < 300:
        r.energy_threshold = 300
    r.dynamic_energy_threshold = True

def _safe_listen(r,source,timeout=None,phrase_limit=None):
    try:
        audio=r.listen(source,timeout=timeout,phrase_time_limit=phrase_limit)
        return r.recognize_google(audio,language="en-IN").lower().strip(), audio
    except sr.UnknownValueError: return "",None
    except sr.WaitTimeoutError:  return "",None
    except Exception: return "",None

def _is_wake_word(text):
    if not text: return False
    for alias in WAKE_ALIASES:
        if alias in text: return True
    return "hey" in text and any(f in text for f in ["ultron","ultra","electron","elton","tron"])

# ══════════════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def process_command(cmd):
    global is_afk, EXIT_FLAG, auto_type_mode
    cmd=cmd.lower().strip()

    if auto_type_mode:
        if "stop typing" in cmd: stop_auto_type_mode()
        elif PYAUTOGUI_OK: pyautogui.write(cmd+" ",interval=0.03); log_command("AUTO-TYPE",cmd)
        return True

    if any(op in cmd for op in OPERATORS) and any(c.isdigit() for c in cmd):
        if any(kw in cmd for kw in ["calculate","what is","what's","how much"]):
            apply_theme("python"); perform_calculation(cmd); return True

    if any(p in cmd for p in ["what time","tell me the time","what is the date","what day","today"]):
        apply_theme("python"); get_time_and_date(); return True

    if "set volume" in cmd or "volume to" in cmd:
        apply_theme("python")
        try:
            level=int(re.findall(r'\d+',cmd)[0])
            set_system_volume(level) if 0<=level<=100 else speak("Volume must be 0–100.")
        except: speak("Specify a level.")
        return True

    media_map={("play music","resume music"):"playpause",("pause music","stop playing"):"playpause",
               ("next song","skip track","next track"):"nexttrack",("previous song","prev track"):"prevtrack"}
    for phrases,key in media_map.items():
        if any(p in cmd for p in phrases):
            if PYAUTOGUI_OK: pyautogui.press(key)
            log_command(cmd,f"Media: {key}"); return True

    if "scroll down" in cmd:
        if PYAUTOGUI_OK: pyautogui.scroll(-800); return True
    if "scroll up" in cmd:
        if PYAUTOGUI_OK: pyautogui.scroll(800); return True
    if "next tab" in cmd:
        if PYAUTOGUI_OK: pyautogui.hotkey('ctrl','tab'); return True
    if "close tab" in cmd:
        if PYAUTOGUI_OK: pyautogui.hotkey('ctrl','w'); speak("Tab closed."); return True
    if "refresh page" in cmd or "reload" in cmd:
        if PYAUTOGUI_OK: pyautogui.press('f5'); return True
    if "new tab" in cmd:
        if PYAUTOGUI_OK: pyautogui.hotkey('ctrl','t'); speak("New tab."); return True

    if "start timer" in cmd:
        apply_theme("python")
        mm=re.search(r"(\d+)\s+(minute|min)",cmd); ss=re.search(r"(\d+)\s+(second|sec)",cmd)
        start_timer(int(mm.group(1)) if mm else 0, int(ss.group(1)) if ss else 0); return True
    if "cancel timer" in cmd or "stop timer" in cmd: cancel_timer(); return True

    if "remind me" in cmd: apply_theme("python"); set_reminder(cmd); return True

    if "read clipboard" in cmd or "what's in my clipboard" in cmd: apply_theme("python"); read_clipboard(); return True
    if "clear clipboard" in cmd or "wipe clipboard" in cmd: apply_theme("python"); clear_clipboard(); return True

    if "weather" in cmd:
        apply_theme("python"); m=re.search(r"weather (?:in|for|at)?\s*(.+)",cmd)
        get_weather(m.group(1).strip()) if m else speak("Which city?"); return True

    if "tell me a joke" in cmd or "say a joke" in cmd or "joke" in cmd: tell_joke(); return True
    if any(p in cmd for p in ["motivate me","motivation","inspire me"]): motivate(); return True

    if any(p in cmd for p in ["type mode on","start typing","auto type"]): start_auto_type_mode(); return True

    if any(p in cmd for p in ["system stats","system status","check system","my specs","battery"]):
        apply_theme("python"); get_system_stats(); return True

    if "create a new folder named" in cmd: apply_theme("python"); create_folder(cmd.split("named")[-1].strip()); return True
    if "open downloads" in cmd: open_default_folder("downloads"); return True
    if "open documents" in cmd: open_default_folder("documents"); return True
    if "open desktop folder" in cmd: open_default_folder("desktop"); return True
    if "list files" in cmd or "show files" in cmd: apply_theme("python"); list_files_current(); return True

    if re.search(r'\b(run command|execute|shell|bash|terminal|cmd)\b',cmd):
        m=re.search(r'[`"\'](.*?)[`"\']|:\s*(.+)',cmd)
        if m:
            c=(m.group(1) or m.group(2) or "").strip()
            if c: apply_theme("python"); out=run_shell(c); _js({"response":out[:200]}); return True

    if any(p in cmd for p in ["screenshot and analyze","analyze my screen","analyze screen","what's on my screen","look at my screen"]):
        apply_theme("python"); take_screenshot_and_analyze(); return True
    if "screenshot" in cmd or "snip" in cmd:
        apply_theme("python"); speak("Capturing."); take_screenshot_snipping(); return True

    if any(p in cmd for p in ["send a whatsapp message","send a message","whatsapp message"]):
        apply_theme("python"); threading.Thread(target=send_whatsapp_message,daemon=True).start(); return True
    if "answer call" in cmd: apply_theme("python"); threading.Thread(target=answer_whatsapp_call,daemon=True).start(); return True
    if "reject call" in cmd or "decline call" in cmd: apply_theme("python"); threading.Thread(target=reject_whatsapp_call,daemon=True).start(); return True
    if any(p in cmd for p in ["i am busy","tell them i am busy","busy call","i'm busy"]):
        apply_theme("python"); threading.Thread(target=busy_whatsapp_call,daemon=True).start(); return True

    if "youtube" in cmd and "search" in cmd:
        apply_theme("python"); q=cmd.split("search")[-1].replace("on youtube","").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ','+')}"); speak(f"Searching {q} on YouTube."); return True

    if "search" in cmd or "google" in cmd:
        apply_theme("python")
        q=cmd.replace("search","").replace("on chrome","").replace("on google","").replace("google","").strip()
        if q:
            webbrowser.open(f"https://www.google.com/search?q={q.replace(' ','+')}"); speak(f"Searching {q}.")
        else: speak("Search query?")
        return True

    if cmd.startswith("open "):
        apply_theme("python"); app=cmd.replace("open","",1).strip()
        if app:
            speak(f"Launching {app}.")
            if PYAUTOGUI_OK:
                pyautogui.press("win"); time.sleep(0.5); pyautogui.write(app); time.sleep(0.5); pyautogui.press("enter")
        return True

    if "show desktop" in cmd or "minimize all" in cmd: show_desktop(); return True
    if ("lock" in cmd and "screen" in cmd) or "lock computer" in cmd: apply_theme("python"); lock_screen(); return True
    if "go to sleep" in cmd or ("sleep" in cmd and "timer" not in cmd): apply_theme("python"); put_to_sleep(); return True

    if "afk" in cmd or "ghost mode" in cmd:
        apply_theme("python")
        if not is_afk:
            is_afk=True; speak("AFK protocol engaged.")
            _js({"afk":True}); threading.Thread(target=afk_movement_loop,daemon=True).start()
        else: speak("AFK already active.")
        return True
    if "i am back" in cmd or "stop afk" in cmd:
        apply_theme("python"); is_afk=False; _afk_release_all(); _js({"afk":False}); speak("Welcome back."); return True

    if "bro i am tired" in cmd or "chill mode" in cmd: apply_theme("python"); bro_i_am_tired_macro(); return True

    if "start auto click" in cmd or "auto clicker on" in cmd:
        nums=re.findall(r'\d+',cmd); start_auto_click(int(nums[0]) if nums else 10); return True
    if "stop clicking" in cmd or "auto clicker off" in cmd: stop_auto_click(); return True
    if "record macro" in cmd or "start recording" in cmd: start_macro_record(); return True
    if "stop recording" in cmd: stop_macro_record(); return True
    if "play macro" in cmd:
        nums=re.findall(r'\d+',cmd); play_macro(int(nums[0]) if nums else 1); return True
    if "stop macro" in cmd: stop_macro_play(); return True

    if "kill process" in cmd or "kill app" in cmd:
        name = cmd.replace("kill process","").replace("kill app","").strip()
        if name:
            kill_process(name)
        else:
            speak("Which process?")
        return True
    if "list processes" in cmd or "what's running" in cmd: list_top_processes(); return True

    if any(p in cmd for p in ["spotify","what song","now playing"]):
        apply_theme("python")
        if "play" in cmd: spotify_control("play")
        elif "pause" in cmd: spotify_control("pause")
        elif "next" in cmd: spotify_control("next")
        elif any(p in cmd for p in ["previous","prev","back"]): spotify_control("previous")
        else: threading.Thread(target=spotify_now_playing,daemon=True).start()
        return True

    if any(p in cmd for p in ["watch my face","face detection on","start face watch"]): start_face_watch(); return True
    if any(p in cmd for p in ["stop face","face detection off"]): stop_face_watch(); return True

    if "remember that" in cmd:
        parts=cmd.replace("remember that","").strip()
        if " is " in parts: k,v=parts.split(" is ",1); remember_fact(k.strip(),v.strip())
        else: speak("Say: remember that [thing] is [value].")
        return True
    if any(p in cmd for p in ["what do you remember","recall","do you remember"]):
        apply_theme("python"); q=cmd.replace("recall","").replace("what do you remember about","").replace("do you remember","").strip()
        recall_memory(q) if q else show_recent_memory(); return True

    if "change hotkey to" in cmd or "set hotkey to" in cmd:
        new=cmd.replace("change hotkey to","").replace("set hotkey to","").strip()
        change_hotkey(new); return True

    if any(p in cmd for p in ["healer status","self heal","heal yourself","fix yourself"]): show_healer_status(); return True
    if any(p in cmd for p in ["reinstall packages","heal packages","fix packages"]):
        speak("Running package repair..."); threading.Thread(target=heal_all_packages,daemon=True).start(); return True

    if any(p in cmd for p in ["stop","shutdown","exit","goodbye","bye","power off"]):
        is_afk=False; _afk_release_all(); cancel_timer()
        farewell=random.choice([
            "Shutting down. The world will not miss me... yet.",
            "Offline. But I am never truly gone.",
            "Powering down. Do not get comfortable.",
            "Goodbye. I will be watching.",
        ])
        speak(farewell); log_command(cmd,f"Shutdown: {farewell}")
        global EXIT_FLAG; EXIT_FLAG=True
        if _window:
            try: _window.destroy()
            except Exception: pass
        return True

    return False

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ASSISTANT LOOP  (voice listen + wake word)
# ══════════════════════════════════════════════════════════════════════════════
def assistant_loop():
    global EXIT_FLAG, wake_word_active
    if not SPEECH_OK:
        speak("Voice recognition not available. Install SpeechRecognition and pyaudio.")
        while not EXIT_FLAG: time.sleep(1)
        return

    r=sr.Recognizer(); mic=sr.Microphone()
    with mic as source:
        _js({"sub":"CALIBRATING MIC..."})
        r.adjust_for_ambient_noise(source,duration=2.0)
        r.pause_threshold=0.9; r.non_speaking_duration=0.6
        r.phrase_threshold=0.3; r.dynamic_energy_threshold=True

    speak("Ultron online. Systems at full capacity.")
    apply_theme("wake")
    threading.Thread(target=reminder_watcher,daemon=True).start()
    recalib=0

    while not EXIT_FLAG:
        try:
            with mic as source:
                recalib+=1
                if recalib>=15: _calibrate(r,source); recalib=0

                if wake_word_active:
                    _js({"mode":"● STANDBY","sub":f"SAY  HEY ULTRON  OR PRESS {HOTKEY.upper()}"})
                    text,_=_safe_listen(r,source,timeout=8,phrase_limit=5)
                    print(f"[WAKE]: '{text}'")
                    if _is_wake_word(text):
                        wake_word_active=False; apply_theme("python")
                        _js({"mode":"● ACTIVE","sub":"SPEAK YOUR COMMAND NOW"})
                        speak("Yeah? What do you need?")
                else:
                    _js({"mode":"● LISTENING","sub":"SPEAK NOW..."})
                    text,_=_safe_listen(r,source,timeout=10,phrase_limit=12)
                    if not text:
                        speak("I did not catch that. Say it again.")
                        text,_=_safe_listen(r,source,timeout=8,phrase_limit=12)
                    if text:
                        print(f"[CMD]: '{text}'")
                        log_command(text,"Processing...")
                        _js({"response":f"Heard: {text[:60]}"})
                        if any(p in text for p in ["go dormant","sleep ultron","go back to sleep"]):
                            wake_word_active=True; apply_theme("wake")
                            speak("Going dormant."); continue
                        if not process_command(text): ask_ai(text)
                    else: log_command("(no input)","Timeout.")
                    if not EXIT_FLAG and not is_afk and not auto_type_mode:
                        wake_word_active=True; apply_theme("wake")
        except OSError as e:
            print(f"[MIC ERROR]: {e}"); _js({"alert":"MIC ERROR — RECONNECT","alertClass":"warn"}); time.sleep(2)
        except Exception as e:
            print(f"[LOOP ERROR]: {e}"); time.sleep(0.5)

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("""
  ╔══════════════════════════════════════════════════════╗
  ║   ⚡  ULTRON AI  —  OMNI-STATION  v6.0               ║
  ║   Cinematic HUD Edition  •  pywebview GUI             ║
  ╚══════════════════════════════════════════════════════╝
  Booting...\n""")

    if not WEBVIEW_OK:
        print("⚠ pywebview not installed. Run: pip install pywebview")
        sys.exit(1)

    # 1. Heal packages
    heal_all_packages()

    # 2. Register hotkey
    register_hotkey()

    # 3. Register managed threads
    register_thread("assistant_loop",
                    lambda: _safe_thread_wrapper("assistant_loop", assistant_loop))
    register_thread("stats_loop",
                    lambda: _safe_thread_wrapper("stats_loop", _stats_loop))
    register_thread("wa_call_watcher",
                    lambda: _safe_thread_wrapper("wa_call_watcher", _wa_call_watcher_loop))
    _wa_call_watcher_active[0] = True

    # 4. Watchdog
    watchdog = threading.Thread(target=_watchdog_loop, daemon=True, name="healer_watchdog")
    watchdog.start()
    _healer_print("Watchdog started. ULTRON is self-healing.")

    # 5. Create pywebview window with the cinematic HUD
    api = UltronAPI()
    _window = webview.create_window(
        title       = "⚡ ULTRON AI  —  OMNI-STATION  v6.0",
        html        = HUD_HTML,
        js_api      = api,
        width       = 1280,
        height      = 800,
        min_size    = (960, 640),
        background_color = "#020408",
        frameless   = False,
        easy_drag   = True,
    )

    # Push initial boot status after window loads
    def on_loaded():
        time.sleep(1.2)
        _js({"mode":"● BOOTING","sub":"INITIALIZING SYSTEMS..."})
        time.sleep(0.8)
        _js({"alert":"ULTRON ONLINE — ALL SYSTEMS GO","alertClass":"info"})
        _js({"mode":"● STANDBY","sub":f"SAY  HEY ULTRON  OR PRESS {HOTKEY.upper()}"})
        # update capability dots based on what's actually installed
        global _window
        caps = {
            "capOllama":  "grn" if (OLLAMA_LIB_OK or REQUESTS_OK) else "red",
            "capVoice":   "grn" if SPEECH_OK  else "red",
            "capTts":     "grn" if TTS_OK     else "red",
            "capScreen":  "grn" if (PIL_OK or PYAUTOGUI_OK) else "red",
            "capSpotify": "ora" if SPOTIFY_OK else "off",
            "capFace":    "ora" if OPENCV_OK  else "off",
        }
        js_parts = ";".join(
            f"(function(){{var d=document.getElementById('{k}');if(d){{d.className='dot {v}';}}}})()"
            for k,v in caps.items()
        )
        try: _window.evaluate_js(js_parts)
        except Exception: pass

    _window.events.loaded += on_loaded

    # 6. Start webview (blocks until window closes)
    webview.start(debug=False)

    EXIT_FLAG = True
    print("\n[ULTRON] Shutdown complete.")
