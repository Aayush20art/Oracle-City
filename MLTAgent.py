import streamlit as st
import os
import requests
import json

# ──────────────────────────────────────────────────────────────
#  PAGE CONFIG  — must be first Streamlit call
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AuraCity AI",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
#  SESSION STATE
# ──────────────────────────────────────────────────────────────
for key, default in {
    "chat_history": [],
    "pending_tool": None,
    "total_queries": 0,
    "tool_calls_made": 0,
    "denied_calls": 0,
    "approval_mode": True,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── LOAD API KEYS FROM STREAMLIT SECRETS ──
MISTRAL_KEY = st.secrets["MISTRAL_API_KEY"]
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]
TAVILY_KEY  = st.secrets["TAVILY_API_KEY"]

# ──────────────────────────────────────────────────────────────
#  FULL CSS — Cyberpunk Neon City theme
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;800&display=swap');

/* ── ROOT RESET ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
[data-testid="stDecoration"],
section[data-testid="stSidebar"] { display: none !important; }

/* ── BODY / APP BG ── */
html, body { margin: 0; padding: 0; }

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: #020008 !important;
    min-height: 100vh;
}

/* animated scanline overlay */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 255, 200, 0.015) 2px,
        rgba(0, 255, 200, 0.015) 4px
    );
    animation: scanMove 8s linear infinite;
}
@keyframes scanMove {
    from { background-position: 0 0; }
    to   { background-position: 0 100px; }
}

/* animated city grid floor */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 800px 500px at 20% 10%, rgba(0,255,180,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 600px 400px at 80% 5%,  rgba(255,20,147,0.08) 0%, transparent 65%),
        radial-gradient(ellipse 500px 600px at 50% 90%, rgba(0,150,255,0.06)  0%, transparent 65%);
    animation: auraPulse 6s ease-in-out infinite alternate;
}
@keyframes auraPulse {
    0%   { opacity: 0.7; transform: scale(1); }
    100% { opacity: 1;   transform: scale(1.04); }
}

/* ── MAIN BLOCK CONTAINER ── */
.block-container {
    max-width: 960px !important;
    margin: 0 auto !important;
    padding: 0 1.5rem 3rem !important;
    position: relative; z-index: 1;
}

/* ── HERO ── */
.hero-wrap {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.hero-eyebrow {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    color: #00ffc8;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    animation: fadeIn 0.8s ease both;
}
.hero-title {
    font-family: 'Exo 2', sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 6vw, 4rem);
    line-height: 1;
    letter-spacing: -0.01em;
    color: #fff;
    text-shadow:
        0 0 30px rgba(0,255,200,0.6),
        0 0 80px rgba(0,255,200,0.2);
    animation: titleFlare 4s ease-in-out infinite alternate;
    margin-bottom: 0.5rem;
}
.hero-title span { color: #00ffc8; }
@keyframes titleFlare {
    0%   { text-shadow: 0 0 20px rgba(0,255,200,0.5), 0 0 60px rgba(0,255,200,0.15); }
    100% { text-shadow: 0 0 40px rgba(0,255,200,0.9), 0 0 120px rgba(0,255,200,0.3), 0 0 200px rgba(255,20,147,0.15); }
}
.hero-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    color: rgba(0,255,200,0.5);
    text-transform: uppercase;
    animation: fadeIn 1.2s ease both;
}
@keyframes fadeIn {
    from { opacity:0; transform: translateY(8px); }
    to   { opacity:1; transform: translateY(0); }
}

/* divider line */
.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #00ffc8, rgba(255,20,147,0.8), transparent);
    margin: 1rem 0 1.5rem;
    animation: dividerGlow 3s ease-in-out infinite alternate;
}
@keyframes dividerGlow {
    0%   { opacity: 0.5; }
    100% { opacity: 1; box-shadow: 0 0 12px rgba(0,255,200,0.6); }
}

/* ── API KEY PANEL ── */
.api-panel {
    background: rgba(0,255,200,0.03);
    border: 1px solid rgba(0,255,200,0.2);
    border-radius: 4px;
    padding: 1.2rem 1.5rem 1rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.api-panel::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00ffc8, #ff1493, #00ffc8);
    background-size: 200% 100%;
    animation: borderSlide 3s linear infinite;
}
@keyframes borderSlide {
    0%   { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}
.api-panel-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    color: #00ffc8;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* ── STATS ROW ── */
.stats-row {
    display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;
}
.stat-box {
    flex: 1; min-width: 100px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(0,255,200,0.15);
    border-radius: 4px;
    padding: 0.8rem 1rem;
    text-align: center;
}
.stat-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.6rem;
    color: #00ffc8;
    line-height: 1;
    text-shadow: 0 0 12px rgba(0,255,200,0.6);
}
.stat-lbl {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    color: rgba(0,255,200,0.4);
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ── APPROVAL CARD ── */
.approval-card {
    background: rgba(255, 180, 0, 0.05);
    border: 1px solid rgba(255,180,0,0.4);
    border-radius: 4px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    animation: approvalBeat 1.2s ease-in-out infinite alternate;
    position: relative; overflow: hidden;
}
.approval-card::before {
    content: ''; position: absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, #ffb400, #ff6b00, #ffb400);
    background-size: 200% 100%;
    animation: borderSlide 2s linear infinite;
}
@keyframes approvalBeat {
    0%   { box-shadow: 0 0 8px rgba(255,180,0,0.15); }
    100% { box-shadow: 0 0 24px rgba(255,180,0,0.4); }
}
.approval-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.35em;
    color: #ffb400; text-transform: uppercase; margin-bottom: 0.5rem;
}
.approval-tool {
    font-family: 'Exo 2', sans-serif; font-weight: 600; font-size: 1rem;
    color: #ffe08a; margin-bottom: 0.3rem;
}
.approval-args {
    font-family: 'Share Tech Mono', monospace; font-size: 0.78rem;
    color: rgba(255,224,138,0.6);
}

/* ── CHAT AREA ── */
.chat-outer {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(0,255,200,0.12);
    border-radius: 4px;
    padding: 1.2rem;
    min-height: 320px;
    margin-bottom: 1rem;
    position: relative;
}
.chat-empty {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-height: 260px; gap: 0.6rem;
}
.chat-empty-icon {
    font-size: 3rem;
    filter: drop-shadow(0 0 16px rgba(0,255,200,0.5));
    animation: iconFloat 3s ease-in-out infinite;
}
@keyframes iconFloat {
    0%,100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
}
.chat-empty-text {
    font-family: 'Rajdhani', sans-serif; font-weight: 600;
    font-size: 1rem; letter-spacing: 0.1em;
    color: rgba(0,255,200,0.5); text-align: center;
}
.chat-empty-hint {
    font-family: 'Share Tech Mono', monospace; font-size: 0.72rem;
    color: rgba(0,255,200,0.25); text-align: center;
}

/* chat message rows */
.msg-row { display: flex; gap: 0.7rem; margin-bottom: 1rem; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.avatar {
    width: 34px; height: 34px; border-radius: 3px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700;
}
.av-user {
    background: rgba(255,20,147,0.2);
    border: 1px solid rgba(255,20,147,0.5);
    color: #ff69b4;
    box-shadow: 0 0 10px rgba(255,20,147,0.25);
}
.av-bot {
    background: rgba(0,255,200,0.1);
    border: 1px solid rgba(0,255,200,0.4);
    color: #00ffc8;
    box-shadow: 0 0 10px rgba(0,255,200,0.2);
}
.av-tool {
    background: rgba(100,180,255,0.1);
    border: 1px solid rgba(100,180,255,0.35);
    color: #64b4ff;
}

.bubble {
    max-width: 80%; border-radius: 3px;
    padding: 0.75rem 1rem; font-size: 0.88rem; line-height: 1.65;
    animation: bubbleIn 0.3s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes bubbleIn {
    from { opacity:0; transform: scale(0.9) translateY(5px); }
    to   { opacity:1; transform: scale(1) translateY(0); }
}
.bubble-user {
    font-family: 'Rajdhani', sans-serif; font-weight: 500;
    background: rgba(255,20,147,0.08);
    border: 1px solid rgba(255,20,147,0.3);
    color: #ffd6ec;
    border-bottom-right-radius: 0;
}
.bubble-bot {
    font-family: 'Rajdhani', sans-serif; font-weight: 400;
    background: rgba(0,255,200,0.04);
    border: 1px solid rgba(0,255,200,0.18);
    color: #c8fff4;
    border-bottom-left-radius: 0;
}
.bubble-tool {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    background: rgba(100,180,255,0.05);
    border: 1px solid rgba(100,180,255,0.2);
    color: #a8d4ff;
    border-bottom-left-radius: 0;
}
.tool-badge {
    display: inline-block;
    background: rgba(100,180,255,0.15);
    border: 1px solid rgba(100,180,255,0.3);
    border-radius: 2px; padding: 1px 7px;
    font-size: 0.62rem; letter-spacing: 0.2em;
    color: #64b4ff; margin-bottom: 0.35rem; text-transform: uppercase;
}

/* ── INPUT ROW ── */
.input-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.3em;
    color: rgba(0,255,200,0.45); text-transform: uppercase;
    margin-bottom: 0.3rem;
}

/* Streamlit input override */
.stTextInput > div > div > input {
    background: rgba(0,255,200,0.04) !important;
    border: 1px solid rgba(0,255,200,0.3) !important;
    border-radius: 3px !important;
    color: #c8fff4 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1rem !important;
    caret-color: #00ffc8 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00ffc8 !important;
    box-shadow: 0 0 0 2px rgba(0,255,200,0.15), 0 0 20px rgba(0,255,200,0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(0,255,200,0.25) !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}
.stTextInput label { display: none !important; }

/* password input same style */
.stTextInput > div > div > input[type="password"] {
    background: rgba(0,255,200,0.03) !important;
    border: 1px solid rgba(0,255,200,0.2) !important;
    color: #00ffc8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 3px !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease !important;
    color: #020008 !important;
}

/* primary send button */
div[data-testid="column"]:last-child .stButton > button {
    background: #00ffc8 !important;
    border: none !important;
    box-shadow: 0 0 16px rgba(0,255,200,0.4) !important;
}
div[data-testid="column"]:last-child .stButton > button:hover {
    background: #fff !important;
    box-shadow: 0 0 32px rgba(0,255,200,0.7) !important;
    transform: translateY(-1px) !important;
}

/* approve button */
.approve-wrap .stButton > button {
    background: rgba(0,255,200,0.15) !important;
    border: 1px solid #00ffc8 !important;
    color: #00ffc8 !important;
    box-shadow: 0 0 10px rgba(0,255,200,0.2) !important;
}
.approve-wrap .stButton > button:hover {
    background: #00ffc8 !important;
    color: #020008 !important;
    box-shadow: 0 0 24px rgba(0,255,200,0.6) !important;
}

/* deny button */
.deny-wrap .stButton > button {
    background: rgba(255,20,147,0.1) !important;
    border: 1px solid rgba(255,20,147,0.6) !important;
    color: #ff69b4 !important;
}
.deny-wrap .stButton > button:hover {
    background: rgba(255,20,147,0.3) !important;
    box-shadow: 0 0 20px rgba(255,20,147,0.4) !important;
}

/* clear/save buttons */
.util-wrap .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(0,255,200,0.25) !important;
    color: rgba(0,255,200,0.6) !important;
    font-size: 0.75rem !important;
}
.util-wrap .stButton > button:hover {
    border-color: rgba(0,255,200,0.6) !important;
    color: #00ffc8 !important;
}

/* toggle */
.stCheckbox label {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    color: rgba(0,255,200,0.7) !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stCheckbox"] { margin-bottom: 0 !important; }

/* status pill */
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.15em;
}
.status-ok  { background: rgba(0,255,200,0.1); border: 1px solid rgba(0,255,200,0.3); color: #00ffc8; }
.status-err { background: rgba(255,60,60,0.1);  border: 1px solid rgba(255,60,60,0.4);  color: #ff6060; }
.blink { animation: blink 1.2s step-end infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,255,200,0.25); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,200,0.5); }

/* expander */
[data-testid="stExpander"] summary {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    color: rgba(0,255,200,0.5) !important;
    text-transform: uppercase !important;
}
[data-testid="stExpander"] {
    background: rgba(0,255,200,0.02) !important;
    border: 1px solid rgba(0,255,200,0.1) !important;
    border-radius: 3px !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
#  LAZY IMPORTS (only after page config)
# ──────────────────────────────────────────────────────────────
try:
    from langchain_mistralai import ChatMistralAI
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
    from langchain_community.tools import TavilySearchResults
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

# ──────────────────────────────────────────────────────────────
#  TOOL FUNCTIONS
# ──────────────────────────────────────────────────────────────
def get_weather_data(city: str, api_key: str) -> str:
    url = (f"https://api.openweathermap.org/data/2.5/weather"
           f"?q={city},IN&appid={api_key}&units=metric")
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'Could not fetch weather')}"
        temp    = data["main"]["temp"]
        feels   = data["main"]["feels_like"]
        humidity= data["main"]["humidity"]
        desc    = data["weather"][0]["description"].title()
        wind    = data["wind"]["speed"]
        icon_map = {
            "clear": "☀️", "cloud": "☁️", "rain": "🌧️",
            "storm": "⛈️", "snow": "❄️", "mist": "🌫️", "haze": "🌫️",
        }
        icon = next((v for k, v in icon_map.items() if k in desc.lower()), "🌡️")
        return (
            f"{icon} Weather in {city.title()}\n"
            f"Condition   : {desc}\n"
            f"Temperature : {temp}°C  (feels like {feels}°C)\n"
            f"Humidity    : {humidity}%\n"
            f"Wind speed  : {wind} m/s"
        )
    except Exception as e:
        return f"Weather fetch failed: {e}"


def get_news_data(city: str, tavily_key: str) -> str:
    try:
        search  = TavilySearchResults(max_results=3, api_key=tavily_key)
        results = search.invoke(f"latest news in {city} India today")
        if not results:
            return f"No news found for {city}."
        items = []
        for r in results:
            title   = r.get("title", "No title")
            url     = r.get("url", "")
            content = r.get("content", "")[:180]
            items.append(f"» {title}\n  {url}\n  {content}...")
        return f"📡 Latest news — {city.title()}\n\n" + "\n\n".join(items)
    except Exception as e:
        return f"News fetch failed: {e}"


# ──────────────────────────────────────────────────────────────
#  AGENT HELPERS
# ──────────────────────────────────────────────────────────────
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather of a city in India",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get latest news about a city in India",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "You are AuraCity — a sleek, intelligent city assistant. "
    "You help users get real-time weather and news for Indian cities. "
    "Be concise, friendly, and precise. Always use the tools provided."
)


def make_llm(key: str):
    return ChatMistralAI(model="mistral-small-2506", api_key=key)


def agent_first_step(user_msg: str, mistral_key: str):
    llm = make_llm(mistral_key).bind_tools(TOOLS_SCHEMA)
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_msg)]
    response = llm.invoke(messages)
    if response.tool_calls:
        tc = response.tool_calls[0]
        return {"type": "tool_request", "name": tc["name"], "args": tc["args"],
                "call_id": tc["id"], "messages": messages + [response]}
    return {"type": "final", "content": response.content}


def agent_with_result(messages, tool_call_id: str, tool_result: str, mistral_key: str) -> str:
    llm = make_llm(mistral_key).bind_tools(TOOLS_SCHEMA)
    msgs = messages + [ToolMessage(content=tool_result, tool_call_id=tool_call_id)]
    return llm.invoke(msgs).content


# ──────────────────────────────────────────────────────────────
#  RENDER HELPERS
# ──────────────────────────────────────────────────────────────
def render_chat():
    if not st.session_state.chat_history:
        st.markdown("""
        <div class='chat-outer'>
          <div class='chat-empty'>
            <div class='chat-empty-icon'>🌆</div>
            <div class='chat-empty-text'>Ask about any Indian city</div>
            <div class='chat-empty-hint'>weather · news · real-time data</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    html = "<div class='chat-outer'>"
    for msg in st.session_state.chat_history:
        role = msg["role"]
        content = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        if role == "user":
            html += f"""
            <div class='msg-row user'>
              <div class='avatar av-user'>U</div>
              <div class='bubble bubble-user'>{content}</div>
            </div>"""
        elif role == "tool":
            html += f"""
            <div class='msg-row'>
              <div class='avatar av-tool'>⚙</div>
              <div class='bubble bubble-tool'>
                <div class='tool-badge'>tool call</div><br>{content}
              </div>
            </div>"""
        else:
            html += f"""
            <div class='msg-row'>
              <div class='avatar av-bot'>AI</div>
              <div class='bubble bubble-bot'>{content}</div>
            </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  LAYOUT
# ──────────────────────────────────────────────────────────────

# ── HERO ────────────────────────────────────────────────────
st.markdown("""
<div class='hero-wrap'>
  <div class='hero-eyebrow'>▸ Real-Time City Intelligence</div>
  <div class='hero-title'>Aura<span>City</span></div>
  <div class='hero-sub'>Weather · News · Powered by Mistral AI</div>
</div>
<div class='neon-divider'></div>
""", unsafe_allow_html=True)

# ── API KEYS LOADED FROM STREAMLIT SECRETS (no manual entry needed) ──

# ── STATS + CONTROLS ROW ────────────────────────────────────
r1, r2, r3, r4, r5 = st.columns([1, 1, 1, 1, 2])
r1.markdown(f"""<div class='stat-box'>
  <div class='stat-val'>{st.session_state.total_queries}</div>
  <div class='stat-lbl'>Queries</div>
</div>""", unsafe_allow_html=True)
r2.markdown(f"""<div class='stat-box'>
  <div class='stat-val'>{st.session_state.tool_calls_made}</div>
  <div class='stat-lbl'>Tool Calls</div>
</div>""", unsafe_allow_html=True)
r3.markdown(f"""<div class='stat-box'>
  <div class='stat-val'>{st.session_state.denied_calls}</div>
  <div class='stat-lbl'>Denied</div>
</div>""", unsafe_allow_html=True)
r4.markdown(f"""<div class='stat-box'>
  <div class='stat-val'>{len([m for m in st.session_state.chat_history if m['role']=='user'])}</div>
  <div class='stat-lbl'>Messages</div>
</div>""", unsafe_allow_html=True)
with r5:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    approval_mode = st.checkbox(
        "⚡ Human Approval Mode",
        value=st.session_state.approval_mode,
        help="When ON — you approve every tool call before it runs"
    )
    st.session_state.approval_mode = approval_mode
    st.markdown('<div class="util-wrap">', unsafe_allow_html=True)
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_tool = None
        st.session_state.total_queries = 0
        st.session_state.tool_calls_made = 0
        st.session_state.denied_calls = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── APPROVAL BANNER ─────────────────────────────────────────
if st.session_state.pending_tool is not None:
    pt = st.session_state.pending_tool
    st.markdown(f"""
    <div class='approval-card'>
      <div class='approval-label'>⚡ Tool Call — Awaiting Approval</div>
      <div class='approval-tool'>🛠 {pt['name']}</div>
      <div class='approval-args'>args → {json.dumps(pt['args'])}</div>
    </div>
    """, unsafe_allow_html=True)

    a1, a2, a3 = st.columns([1, 1, 5])
    with a1:
        st.markdown('<div class="approve-wrap">', unsafe_allow_html=True)
        if st.button("✅ Approve", key="approve_btn", use_container_width=True):
            city = pt["args"].get("city", "")
            if pt["name"] == "get_weather":
                tool_result = get_weather_data(city, WEATHER_KEY)
            else:
                tool_result = get_news_data(city, TAVILY_KEY)
            st.session_state.tool_calls_made += 1
            final = agent_with_result(pt["messages"], pt["call_id"], tool_result, MISTRAL_KEY)
            st.session_state.chat_history.append({"role": "tool",      "content": f"Tool [{pt['name']}] executed for city: {city}"})
            st.session_state.chat_history.append({"role": "assistant", "content": final})
            st.session_state.pending_tool = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="deny-wrap">', unsafe_allow_html=True)
        if st.button("🚫 Deny", key="deny_btn", use_container_width=True):
            st.session_state.denied_calls += 1
            st.session_state.chat_history.append({"role": "assistant", "content": "Tool call denied. I cannot fetch data without tool access — try asking something else."})
            st.session_state.pending_tool = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ── CHAT MESSAGES ────────────────────────────────────────────
render_chat()

# ── INPUT ROW ────────────────────────────────────────────────
st.markdown("<div class='input-label'>▸ Your message</div>", unsafe_allow_html=True)
inp_col, btn_col = st.columns([7, 1])
with inp_col:
    user_input = st.text_input(
        "msg",
        placeholder="e.g.  what's the weather in Mumbai?  /  latest news from Delhi...",
        label_visibility="collapsed",
        key="user_msg",
        disabled=(st.session_state.pending_tool is not None),
    )
with btn_col:
    send = st.button(
        "Send ➤",
        use_container_width=True,
        disabled=(st.session_state.pending_tool is not None),
    )

# example prompts
with st.expander("💡  Example prompts"):
    st.markdown("""
    <div style='font-family: Share Tech Mono, monospace; font-size:0.8rem; color:rgba(0,255,200,0.5); line-height:2;'>
    » What's the weather in Mumbai?<br>
    » Latest news from Delhi<br>
    » How's the weather in Chandigarh today?<br>
    » Any news about Bangalore?<br>
    » Weather and news for Hyderabad
    </div>
    """, unsafe_allow_html=True)

# ── PROCESS SEND ─────────────────────────────────────────────
if send and user_input.strip():
    if not IMPORTS_OK:
        st.error(f"Missing dependency: {IMPORT_ERROR}. Run: pip install langchain langchain-mistralai langchain-community")
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.total_queries += 1

        with st.spinner("Thinking..."):
            try:
                result = agent_first_step(user_input.strip(), MISTRAL_KEY)
            except Exception as e:
                result = {"type": "final", "content": f"Agent error: {e}"}

        if result["type"] == "tool_request":
            if st.session_state.approval_mode:
                st.session_state.pending_tool = {
                    "name":     result["name"],
                    "args":     result["args"],
                    "call_id":  result["call_id"],
                    "messages": result["messages"],
                }
            else:
                city = result["args"].get("city", "")
                if result["name"] == "get_weather":
                    tool_result = get_weather_data(city, WEATHER_KEY)
                else:
                    tool_result = get_news_data(city, TAVILY_KEY)
                st.session_state.tool_calls_made += 1
                try:
                    final = agent_with_result(result["messages"], result["call_id"], tool_result, MISTRAL_KEY)
                except Exception as e:
                    final = f"Error generating response: {e}"
                st.session_state.chat_history.append({"role": "tool",      "content": f"Tool [{result['name']}] → city: {city}"})
                st.session_state.chat_history.append({"role": "assistant", "content": final})
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": result["content"]})

        st.rerun()
