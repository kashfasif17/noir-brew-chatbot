import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="Noir & Brew — AI Barista",
    page_icon="☕",
    layout="wide"
)

# ── LOAD SYSTEM PROMPT ──
with open("context.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

SYSTEM_PROMPT = prompts["barista_system_prompt"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── CUSTOM CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

* {
    box-sizing: border-box;
}

html, body {
    background-color: #1A0A00 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stApp {
    background-color: #1A0A00 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #1A0A00 !important;
    color: #F5E6D3 !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    max-width: 900px !important;
    margin: 0 auto !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

[data-testid="stHeader"] {
    background-color: #1A0A00 !important;
}

[data-testid="stToolbar"] {
    background-color: #1A0A00 !important;
}

[data-testid="stBottomBlockContainer"] {
    background-color: #1A0A00 !important;
}

[data-testid="stSidebar"] {
    background-color: #231108 !important;
    border-right: 1px solid rgba(201,168,76,0.2) !important;
}

[data-testid="stSidebarContent"] {
    background-color: #231108 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #2a1408 !important;
    border: 1px solid rgba(201,168,76,0.15) !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(201,168,76,0.15) !important;
    border-color: rgba(201,168,76,0.3) !important;
}

[data-testid="stChatMessage"] p {
    color: #F5E6D3 !important;
}

/* Chat input box */
[data-testid="stChatInput"] {
    background-color: #1A0A00 !important;
}

[data-testid="stChatInput"] textarea {
    background: #2a1408 !important;
    color: #F5E6D3 !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 1px #C9A84C !important;
}

[data-testid="stChatInput"] button {
    background: #C9A84C !important;
    color: #1A0A00 !important;
    border-radius: 6px !important;
}

/* Sidebar buttons */
.stButton > button {
    background: transparent !important;
    color: #C9A84C !important;
    border: 1px solid rgba(201,168,76,0.35) !important;
    border-radius: 20px !important;
    font-size: 0.78rem !important;
    padding: 0.3rem 0.9rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-align: left !important;
}

.stButton > button:hover {
    background: rgba(201,168,76,0.15) !important;
    border-color: #C9A84C !important;
}

hr {
    border-color: rgba(201,168,76,0.2) !important;
}

#MainMenu, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── GROQ API CALL ──
def get_groq_reply(messages_history):
    if not GROQ_API_KEY:
        return "⚠️ GROQ_API_KEY not set. Please add it in Streamlit Secrets."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "max_tokens": 200,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages_history
    }
    try:
        res = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        data = res.json()
        if res.status_code != 200:
            return f"⚠️ {data.get('error', {}).get('message', 'Groq API error')}"
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-size:2.5rem;'>☕</div>
        <div style='font-family: "Playfair Display", serif; font-size:1.3rem; color:#C9A84C; margin-top:0.4rem;'>Noir & Brew</div>
        <div style='font-size:0.72rem; color:#8B7355; letter-spacing:0.15em; text-transform:uppercase; margin-top:0.2rem;'>AI Barista</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("<p style='font-size:0.72rem; letter-spacing:0.15em; text-transform:uppercase; color:#8B7355; margin-bottom:0.5rem;'>Quick Questions</p>", unsafe_allow_html=True)

    quick_prompts = [
        "☕ What's your most popular drink?",
        "🍵 Do you have dairy-free options?",
        "🧊 Tell me about Cold Brew Reserve",
        "📍 Where are you located?",
        "🕐 What are your opening hours?",
        "🫘 Where do you source your beans?",
    ]

    for prompt in quick_prompts:
        if st.button(prompt, key=prompt):
            st.session_state.pending_prompt = prompt.split(" ", 1)[1]

    st.divider()

    if st.button("🗑️ Clear Chat", key="clear"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style='margin-top:1rem; padding:1rem; background:rgba(201,168,76,0.08); border-radius:8px; border:1px solid rgba(201,168,76,0.15);'>
        <p style='font-size:0.72rem; color:#8B7355; margin:0 0 0.4rem; text-transform:uppercase; letter-spacing:0.1em;'>Our Menu</p>
        <p style='font-size:0.78rem; color:#F5E6D3; line-height:1.7; margin:0;'>
        ☕ Noir Espresso — Rs. 350<br>
        🥛 Velvet Latte — Rs. 480<br>
        🧊 Cold Brew Reserve — Rs. 550<br>
        🍵 Matcha Ceremony — Rs. 520<br>
        🧁 Dark Cardamom Cake — Rs. 280<br>
        🫖 Saffron Chai — Rs. 320
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── MAIN HEADER ──
st.markdown("""
<div style='text-align:center; padding: 1.5rem 0 0.5rem;'>
    <p style='font-size:0.72rem; letter-spacing:0.25em; text-transform:uppercase; color:#C9A84C; margin-bottom:0.5rem;'>Powered by Groq AI</p>
    <h1 style='font-family: "Playfair Display", serif; font-size:2.2rem; color:#F5E6D3; margin:0;'>Ask our <em style="color:#C9A84C;">AI Barista</em></h1>
    <p style='color:#8B7355; font-size:0.88rem; margin-top:0.5rem;'>Not sure what to order? Ask Café anything about our menu, hours, or coffee. ☕</p>
</div>
<hr>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ── WELCOME MESSAGE ──
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="☕"):
        st.markdown("Salam! I'm **Café**, your AI barista at Noir & Brew. Ask me anything — what to order, dairy-free options, or what pairs well with cold brew. ☕")

# ── DISPLAY CHAT HISTORY ──
for msg in st.session_state.messages:
    avatar = "☕" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── HANDLE QUICK PROMPT CLICK ──
if st.session_state.pending_prompt:
    user_input = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="☕"):
        with st.spinner("Brewing a response..."):
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            reply = get_groq_reply(history)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# ── CHAT INPUT BOX ──
if user_input := st.chat_input("Ask me anything about our menu or coffee..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="☕"):
        with st.spinner("Brewing a response..."):
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            reply = get_groq_reply(history)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
