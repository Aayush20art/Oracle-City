import streamlit as st
import os
import requests
import time
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_community.tools import TavilySearchResults
import json

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CityPulse AI",
    page_icon="🌆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLASSMORPHISM CSS + ANIMATIONS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

/* ── GLOBAL RESET ─────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: transparent !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0015 0%, #07001a 25%, #000d2e 50%, #001a1a 75%, #0a0015 100%) !important;
    min-height: 100vh;
}

/* ── ANIMATED BACKGROUND ORBS ─────────────── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 600px 400px at 15% 20%, rgba(138, 43, 226, 0.25) 0%, transparent 70%),
        radial-gradient(ellipse 500px 350px at 85% 15%, rgba(0, 180, 255, 0.2) 0%, transparent 70%),
        radial-gradient(ellipse 450px 500px at 50% 80%, rgba(0, 255, 200, 0.15) 0%, transparent 70%),
        radial-gradient(ellipse 300px 300px at 75% 60%, rgba(255, 60, 180, 0.18) 0%, transparent 65%);
    animation: orbDrift 12s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(1.5px 1.5px at 10% 15%, rgba(255,255,255,0.55) 0%, transparent 100%),
        radial-gradient(1px 1px at 30% 45%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(2px 2px at 55% 25%, rgba(200,180,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 70%, rgba(255,255,255,0.45) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 88% 35%, rgba(180,220,255,0.55) 0%, transparent 100%),
        radial-gradient(1px 1px at 20% 80%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(2px 2px at 45% 90%, rgba(200,255,240,0.45) 0%, transparent 100%),
        radial-gradient(1px 1px at 92% 85%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1.5px 1.5px at 62% 55%, rgba(255,200,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 5% 55%, rgba(255,255,255,0.35) 0%, transparent 100%);
    animation: starPulse 4s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}

@keyframes orbDrift {
    0%   { transform: scale(1)   rotate(0deg);   opacity: 1; }
    50%  { transform: scale(1.1) rotate(3deg);   opacity: 0.85; }
    100% { transform: scale(0.95) rotate(-2deg); opacity: 1; }
}

@keyframes starPulse {
    0%   { opacity: 0.6; }
    100% { opacity: 1; }
}

/* ── SIDEBAR ──────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(15, 5, 35, 0.6) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(138, 43, 226, 0.3) !important;
    box-shadow: 4px 0 30px rgba(138, 43, 226, 0.12) !important;
}

[data-testid="stSidebar"] * { color: rgba(220, 210, 255, 0.9) !important; }

[data-testid="stSidebarContent"] {
    padding: 1.5rem 1rem !important;
}

/* ── GLASS CARD BASE ─────────────────────── */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 20px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(138,43,226,0.6), rgba(0,180,255,0.6), transparent);
    animation: shimmerLine 3s ease-in-out infinite;
}

@keyframes shimmerLine {
    0%, 100% { opacity: 0.4; transform: scaleX(0.8); }
    50%       { opacity: 1;   transform: scaleX(1); }
}

/* ── HERO TITLE ──────────────────────────── */
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #a855f7 0%, #3b82f6 40%, #06b6d4 70%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.05em;
    animation: titleGlow 3s ease-in-out infinite alternate;
    filter: drop-shadow(0 0 20px rgba(168,85,247,0.5));
}

@keyframes titleGlow {
    0%   { filter: drop-shadow(0 0 15px rgba(168,85,247,0.5)); }
    100% { filter: drop-shadow(0 0 35px rgba(59,130,246,0.7)); }
}

.hero-sub {
    text-align: center;
    color: rgba(180, 160, 255, 0.7);
    font-size: 0.95rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.4rem;
    animation: fadeInUp 1s ease both;
}

@keyframes fadeInUp {
    from { opacity:0; transform: translateY(12px); }
    to   { opacity:1; transform: translateY(0); }
}

/* ── PULSE RING AROUND ICON ─────────────── */
.pulse-icon {
    display: flex;
    justify-content: center;
    margin-bottom: 0.5rem;
}
.pulse-ring {
    position: relative;
    width: 72px; height: 72px;
    display: flex; align-items: center; justify-content: center;
}
.pulse-ring::before, .pulse-ring::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2px solid rgba(138,43,226,0.6);
    animation: pulseRing 2.5s ease-out infinite;
}
.pulse-ring::after { animation-delay: 1.25s; }
@keyframes pulseRing {
    0%   { transform: scale(0.8); opacity: 0.8; }
    100% { transform: scale(1.8); opacity: 0; }
}
.pulse-emoji { font-size: 2.2rem; z-index: 1; }

/* ── TOOL APPROVAL CARD ─────────────────── */
.approval-card {
    background: rgba(255, 160, 50, 0.08);
    border: 1px solid rgba(255, 160, 50, 0.35);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
    animation: approvalPulse 1.5s ease-in-out infinite alternate;
}
@keyframes approvalPulse {
    0%   { box-shadow: 0 0 10px rgba(255,160,50,0.2); }
    100% { box-shadow: 0 0 25px rgba(255,160,50,0.45); }
}

/* ── CHAT BUBBLES ───────────────────────── */
.chat-wrap { display: flex; margin-bottom: 1rem; gap: 0.75rem; align-items: flex-start; }

.chat-user { flex-direction: row-reverse; }

.avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.avatar-user { background: linear-gradient(135deg, #7c3aed, #3b82f6); }
.avatar-bot  { background: linear-gradient(135deg, #0891b2, #10b981); }

.bubble {
    max-width: 78%;
    padding: 0.85rem 1.2rem;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.6;
    animation: bubblePop 0.35s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes bubblePop {
    from { opacity:0; transform: scale(0.85) translateY(6px); }
    to   { opacity:1; transform: scale(1) translateY(0); }
}

.bubble-user {
    background: linear-gradient(135deg, rgba(124,58,237,0.4), rgba(59,130,246,0.35));
    border: 1px solid rgba(124,58,237,0.4);
    color: #e9e0ff;
    backdrop-filter: blur(10px);
    border-bottom-right-radius: 4px;
}
.bubble-bot {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: #d4e8f5;
    backdrop-filter: blur(10px);
    border-bottom-left-radius: 4px;
}
.bubble-tool {
    background: rgba(6,182,212,0.08);
    border: 1px solid rgba(6,182,212,0.25);
    color: #a5f3fc;
    font-family: monospace;
    font-size: 0.82rem;
    border-radius: 10px;
}
.tool-tag {
    display: inline-block;
    background: rgba(6,182,212,0.2);
    border: 1px solid rgba(6,182,212,0.4);
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.72rem;
    color: #67e8f9;
    margin-bottom: 0.4rem;
    letter-spacing: 0.05em;
}

/* ── STATUS BADGE ───────────────────────── */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    animation: dotBlink 1.4s ease-in-out infinite;
}
.status-online  { background: #10b981; box-shadow: 0 0 6px #10b981; }
.status-loading { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.status-denied  { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

@keyframes dotBlink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.3; }
}

/* ── TYPING INDICATOR ───────────────────── */
.typing-dots { display: flex; gap: 5px; padding: 0.6rem 1rem; }
.typing-dots span {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: rgba(168,85,247,0.7);
    animation: typingBounce 1.2s ease-in-out infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingBounce {
    0%,60%,100% { transform: translateY(0); }
    30%          { transform: translateY(-8px); }
}

/* ── STREAMLIT OVERRIDES ────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(138,43,226,0.4) !important;
    border-radius: 14px !important;
    color: #e9e0ff !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(138,43,226,0.8) !important;
    box-shadow: 0 0 0 3px rgba(138,43,226,0.2) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(180,160,255,0.45) !important; }

.stButton > button {
    background: linear-gradient(135deg, rgba(124,58,237,0.7), rgba(59,130,246,0.7)) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
    backdrop-filter: blur(10px) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(138,43,226,0.3) !important;
    border-radius: 12px !important;
    color: #e9e0ff !important;
}

/* success / approve button */
.approve-btn button {
    background: linear-gradient(135deg, rgba(16,185,129,0.7), rgba(6,182,212,0.7)) !important;
    border: 1px solid rgba(16,185,129,0.5) !important;
}
/* deny button */
.deny-btn button {
    background: linear-gradient(135deg, rgba(239,68,68,0.6), rgba(220,38,38,0.6)) !important;
    border: 1px solid rgba(239,68,68,0.4) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(138,43,226,0.4); border-radius: 5px; }

/* hide default streamlit header/footer */
#MainMenu, footer, header { visibility: hidden !important; }

/* label text */
label, .stTextInput label { color: rgba(180,160,255,0.8) !important; font-size: 0.82rem !important; }

/* metric boxes */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    padding: 0.8rem !important;
    backdrop-filter: blur(10px) !important;
}
[data-testid="stMetricValue"] { color: #a78bfa !important; }
[data-testid="stMetricLabel"] { color: rgba(180,160,255,0.6) !important; }

/* divider */
hr { border-color: rgba(138,43,226,0.2) !important; }

/* expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []        # list of dicts: {role, content, kind}
if "pending_tool" not in st.session_state:
    st.session_state.pending_tool = None      # {name, args, call_id, messages_so_far}
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "tool_calls_made" not in st.session_state:
    st.session_state.tool_calls_made = 0
if "denied_calls" not in st.session_state:
    st.session_state.denied_calls = 0
if "approval_mode" not in st.session_state:
    st.session_state.approval_mode = True

# ─────────────────────────────────────────────
#  TOOLS
# ─────────────────────────────────────────────
def get_weather_data(city: str, api_key: str) -> str:
    url = (f"https://api.openweathermap.org/data/2.5/weather"
           f"?q={city},IN&appid={api_key}&units=metric")
    try:
        r = requests.get(url, timeout=8)
        data = r.json()
        if data.get("cod") != 200:
            return f"❌ Error: {data.get('message', 'Could not fetch weather')}"
        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].title()
        wind = data["wind"]["speed"]
        return (f"🌤 **Weather in {city.title()}**\n"
                f"- Condition: {desc}\n"
                f"- Temperature: {temp}°C (feels like {feels}°C)\n"
                f"- Humidity: {humidity}%\n"
                f"- Wind: {wind} m/s")
    except Exception as e:
        return f"❌ Weather fetch failed: {str(e)}"


def get_news_data(city: str, tavily_key: str) -> str:
    try:
        search = TavilySearchResults(max_results=3, api_key=tavily_key)
        results = search.invoke(f"latest news in {city}")
        if not results:
            return f"No news found for {city}"
        items = []
        for r in results:
            title = r.get("title", "No title")
            url = r.get("url", "")
            content = r.get("content", "")[:160]
            items.append(f"📰 **{title}**\n🔗 {url}\n_{content}..._")
        return f"📡 **Latest news in {city.title()}:**\n\n" + "\n\n---\n\n".join(items)
    except Exception as e:
        return f"❌ News fetch failed: {str(e)}"


def get_llm(mistral_key: str):
    return ChatMistralAI(model="mistral-small-2506", api_key=mistral_key)


# ─────────────────────────────────────────────
#  CORE AGENT STEP  (one-shot, tool-aware)
# ─────────────────────────────────────────────
def run_agent_step(user_message: str, mistral_key: str, tavily_key: str, weather_key: str):
    """
    Returns either:
      {"type": "tool_request", "name": ..., "args": ..., "call_id": ..., "messages": [...]}
      {"type": "final",        "content": ...}
    """
    llm = get_llm(mistral_key)

    tools_schema = [
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
                "description": "Get latest news about a city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string", "description": "City name"}},
                    "required": ["city"],
                },
            },
        },
    ]

    llm_with_tools = llm.bind_tools(tools_schema)

    messages = [
        SystemMessage(content="You are a helpful city assistant. You can get weather and news for Indian cities. Always be concise and friendly."),
        HumanMessage(content=user_message),
    ]

    response = llm_with_tools.invoke(messages)

    if response.tool_calls:
        tc = response.tool_calls[0]
        return {
            "type": "tool_request",
            "name": tc["name"],
            "args": tc["args"],
            "call_id": tc["id"],
            "messages": messages + [response],
        }
    return {"type": "final", "content": response.content}


def run_agent_with_tool_result(messages: list, tool_call_id: str, tool_result: str, mistral_key: str):
    llm = get_llm(mistral_key)
    tools_schema = [
        {"type": "function", "function": {"name": "get_weather", "description": "Get weather", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_news", "description": "Get news", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    ]
    llm_with_tools = llm.bind_tools(tools_schema)
    messages_with_result = messages + [ToolMessage(content=tool_result, tool_call_id=tool_call_id)]
    response = llm_with_tools.invoke(messages_with_result)
    return response.content


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin-bottom:1.5rem;'>
      <div class='pulse-icon'>
        <div class='pulse-ring'><span class='pulse-emoji'>🌆</span></div>
      </div>
      <div style='font-family:Orbitron,monospace; font-size:1.15rem; font-weight:700;
                  background:linear-gradient(135deg,#a855f7,#3b82f6);
                  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                  background-clip:text; letter-spacing:0.08em;'>CityPulse AI</div>
      <div style='font-size:0.72rem; color:rgba(180,160,255,0.55); letter-spacing:0.15em; margin-top:4px;'>POWERED BY MISTRAL</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 API Configuration")

    mistral_key = st.text_input("Mistral API Key", type="password",
                                value=st.secrets.get("MISTRAL_API_KEY", ""),
                                placeholder="Enter Mistral key...")
    weather_key = st.text_input("OpenWeather API Key", type="password",
                                value=st.secrets.get("OPENWEATHER_API_KEY", ""),
                                placeholder="Enter OpenWeather key...")
    tavily_key  = st.text_input("Tavily Search API Key", type="password",
                                value=st.secrets.get("TAVILY_API_KEY", ""),
                                placeholder="Enter Tavily key...")

    st.markdown("---")
    st.markdown("#### ⚙️ Settings")
    st.session_state.approval_mode = st.toggle("Human Approval Mode", value=st.session_state.approval_mode,
                                                help="When ON, you approve each tool call before it runs")

    keys_ok = bool(mistral_key and weather_key and tavily_key)
    if keys_ok:
        st.markdown('<span class="status-dot status-online"></span><span style="color:#6ee7b7;font-size:0.82rem;">All APIs Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-dot status-denied"></span><span style="color:#fca5a5;font-size:0.82rem;">APIs Not Configured</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Session Stats")
    c1, c2 = st.columns(2)
    c1.metric("Queries", st.session_state.total_queries)
    c2.metric("Tool Calls", st.session_state.tool_calls_made)
    c3, c4 = st.columns(2)
    c3.metric("Denied", st.session_state.denied_calls)
    c4.metric("Chats", len([m for m in st.session_state.chat_history if m["role"] == "user"]))

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.pending_tool = None
        st.rerun()

    st.markdown("---")
    with st.expander("💡 Example Prompts"):
        st.markdown("""
        - *What's the weather in Mumbai?*
        - *Latest news from Delhi*
        - *Weather and news for Bangalore*
        - *How's the weather in Chandigarh?*
        - *Any news about Hyderabad?*
        """)

# ─────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────
# Hero header
st.markdown("""
<div style='padding: 2rem 0 1rem; position:relative; z-index:1;'>
  <div class='hero-title'>CityPulse AI Agent</div>
  <div class='hero-sub'>Weather · News · Intelligence · Real-Time</div>
</div>
""", unsafe_allow_html=True)

# ── TOOL APPROVAL BANNER ─────────────────────
if st.session_state.pending_tool is not None:
    pt = st.session_state.pending_tool
    st.markdown(f"""
    <div class='approval-card'>
      <div style='font-size:0.75rem; color:rgba(255,160,50,0.7); letter-spacing:0.12em; margin-bottom:0.5rem;'>
        ⚡ TOOL CALL PENDING APPROVAL
      </div>
      <div style='color:#fde68a; font-weight:600; font-size:0.95rem; margin-bottom:0.4rem;'>
        🛠️ &nbsp;<code style='background:rgba(255,160,50,0.15); padding:2px 8px; border-radius:6px;'>{pt['name']}</code>
      </div>
      <div style='color:rgba(253,230,138,0.7); font-family:monospace; font-size:0.83rem;'>
        Args: {json.dumps(pt['args'])}
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_approve, col_deny, col_space = st.columns([1, 1, 3])
    with col_approve:
        st.markdown('<div class="approve-btn">', unsafe_allow_html=True)
        if st.button("✅ Approve", key="approve_btn", use_container_width=True):
            city = pt["args"].get("city", "")
            if pt["name"] == "get_weather":
                result = get_weather_data(city, weather_key)
            else:
                result = get_news_data(city, tavily_key)
            st.session_state.tool_calls_made += 1
            final = run_agent_with_tool_result(pt["messages"], pt["call_id"], result, mistral_key)
            st.session_state.chat_history.append({"role": "tool", "content": f"Tool `{pt['name']}` called for **{city}**", "kind": "tool"})
            st.session_state.chat_history.append({"role": "assistant", "content": final, "kind": "text"})
            st.session_state.pending_tool = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_deny:
        st.markdown('<div class="deny-btn">', unsafe_allow_html=True)
        if st.button("🚫 Deny", key="deny_btn", use_container_width=True):
            st.session_state.denied_calls += 1
            st.session_state.chat_history.append({"role": "assistant", "content": "⚠️ Tool call was denied. I can't fetch that data without tool access. Could you ask something else?", "kind": "text"})
            st.session_state.pending_tool = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── CHAT MESSAGES ────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class='glass-card' style='text-align:center; padding:3rem 2rem; margin:1rem 0;'>
          <div style='font-size:3rem; margin-bottom:1rem;'>🌏</div>
          <div style='color:rgba(180,160,255,0.8); font-size:1.05rem; font-weight:500; margin-bottom:0.5rem;'>
            Ask me about any Indian city
          </div>
          <div style='color:rgba(180,160,255,0.45); font-size:0.85rem;'>
            Weather conditions · Breaking news · Live updates
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class='chat-wrap chat-user'>
                  <div class='avatar avatar-user'>👤</div>
                  <div class='bubble bubble-user'>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            elif msg["role"] == "tool":
                st.markdown(f"""
                <div class='chat-wrap'>
                  <div class='avatar avatar-bot'>⚙️</div>
                  <div class='bubble bubble-tool'>
                    <div class='tool-tag'>TOOL CALL</div><br>{msg['content']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                content_html = msg["content"].replace("\n", "<br>")
                st.markdown(f"""
                <div class='chat-wrap'>
                  <div class='avatar avatar-bot'>🤖</div>
                  <div class='bubble bubble-bot'>{content_html}</div>
                </div>
                """, unsafe_allow_html=True)

# ── INPUT AREA ───────────────────────────────
st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

col_input, col_btn = st.columns([6, 1])
with col_input:
    user_input = st.text_input(
        "Message",
        placeholder="Ask about weather or news in any Indian city… (e.g. 'What's the weather in Pune?')",
        label_visibility="collapsed",
        key="user_msg",
        disabled=(st.session_state.pending_tool is not None),
    )
with col_btn:
    send = st.button("Send ➤", use_container_width=True, disabled=(st.session_state.pending_tool is not None))

# ─────────────────────────────────────────────
#  PROCESS SEND
# ─────────────────────────────────────────────
if send and user_input.strip():
    if not keys_ok:
        st.error("⚠️ Please configure all three API keys in the sidebar first.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip(), "kind": "text"})
        st.session_state.total_queries += 1

        with st.spinner(""):
            result = run_agent_step(user_input.strip(), mistral_key, tavily_key, weather_key)

        if result["type"] == "tool_request":
            if st.session_state.approval_mode:
                # store for human approval
                st.session_state.pending_tool = {
                    "name": result["name"],
                    "args": result["args"],
                    "call_id": result["call_id"],
                    "messages": result["messages"],
                }
            else:
                # auto-execute
                city = result["args"].get("city", "")
                if result["name"] == "get_weather":
                    tool_result = get_weather_data(city, weather_key)
                else:
                    tool_result = get_news_data(city, tavily_key)
                st.session_state.tool_calls_made += 1
                final = run_agent_with_tool_result(result["messages"], result["call_id"], tool_result, mistral_key)
                st.session_state.chat_history.append({"role": "tool", "content": f"Tool `{result['name']}` called for **{city}**", "kind": "tool"})
                st.session_state.chat_history.append({"role": "assistant", "content": final, "kind": "text"})
        else:
            st.session_state.chat_history.append({"role": "assistant", "content": result["content"], "kind": "text"})

        st.rerun()