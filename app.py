"""
DeepSense – Voice-Enabled AI Chatbot
====================================
Entry point for the Streamlit UI.
Run with: streamlit run app.py
"""

import streamlit as st
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from core.stt import transcribe_audio, record_audio
from core.tts import speak_text, stop_speaking
from core.chatbot import get_ai_response
from memory.conversation_memory import ConversationMemory
from utils.language import detect_language, SUPPORTED_LANGUAGES

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeepSense – Voice AI Chatbot",
        page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ───────────────────────────────────────────────────────────
with open("ui/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Session State Initialization ─────────────────────────────────────────────
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=20)

if "session_id" not in st.session_state:
    if st.session_state.memory._history:
        st.session_state.session_id = st.session_state.memory._history[-1].get("session_id", "default")
    else:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Restore history from persistent JSON memory file for the ACTIVE session
    for turn in st.session_state.memory._history:
        if turn.get("session_id", "default") == st.session_state.session_id:
            st.session_state.chat_history.append({
                "role": "user", 
                "text": turn.get("user", ""), 
                "lang": st.session_state.get("selected_lang", "en"), 
                "time": turn.get("timestamp", "")
            })
            st.session_state.chat_history.append({
                "role": "assistant", 
                "text": turn.get("assistant", ""), 
                "lang": st.session_state.get("selected_lang", "en"), 
                "time": turn.get("timestamp", "")
            })

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

if "tts_enabled" not in st.session_state:
    st.session_state.tts_enabled = True

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "en"

if "doc_uploader_key" not in st.session_state:
    st.session_state.doc_uploader_key = "doc_upload_0"
if "img_uploader_key" not in st.session_state:
    st.session_state.img_uploader_key = "img_upload_0"
if "camera_key" not in st.session_state:
    st.session_state.camera_key = "camera_0"

# ── Cinematic Splash Screen (Runs Once Per Session) ──────────────────────────
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = True
    
    splash_placeholder = st.empty()
    
        st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;600&family=JetBrains+Mono:wght@100;400&display=swap');

.solid-splash {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: #02040a;
    background-image: 
        radial-gradient(circle at 50% 50%, rgba(0, 210, 255, 0.05) 0%, transparent 60%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 100% 100%, 40px 40px, 40px 40px;
    z-index: 999999;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    overflow: hidden;
    font-family: 'Outfit', sans-serif;
    animation: fadeOutSplash 4s cubic-bezier(0.8, 0, 0.2, 1) forwards;
}

/* Premium Precision Rings */
.orbital-core {
    position: relative;
    width: 280px; height: 280px;
    display: flex; justify-content: center; align-items: center;
    margin-bottom: 2.5rem;
}

.ring-track {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.03);
}

.ring-track-1 { width: 260px; height: 260px; }
.ring-track-2 { width: 190px; height: 190px; }
.ring-track-3 { width: 120px; height: 120px; }

.sweep {
    position: absolute;
    border-radius: 50%;
    mask: conic-gradient(from 0deg, transparent 70%, white 100%);
    -webkit-mask: conic-gradient(from 0deg, transparent 70%, white 100%);
}

.sweep-1 {
    width: 260px; height: 260px;
    border: 2px solid #00d2ff;
    animation: spinSweep 3s linear infinite;
    filter: drop-shadow(0 0 8px #00d2ff);
}

.sweep-2 {
    width: 190px; height: 190px;
    border: 2px solid #7000ff;
    animation: spinSweepReverse 2s linear infinite;
    filter: drop-shadow(0 0 8px #7000ff);
}

.sweep-3 {
    width: 120px; height: 120px;
    border: 2px solid #00ffaa;
    animation: spinSweep 1.5s linear infinite;
    filter: drop-shadow(0 0 8px #00ffaa);
}

.core-glow {
    position: absolute;
    width: 50px; height: 50px;
    background: radial-gradient(circle, #ffffff 0%, #00d2ff 40%, transparent 80%);
    border-radius: 50%;
    filter: blur(8px);
    animation: pulseCoreGlow 2s ease-in-out infinite alternate;
}

.splash-content {
    z-index: 3;
    display: flex; flex-direction: column; align-items: center;
    animation: slideUpFade 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.splash-logo {
    font-size: 3rem;
    font-weight: 300;
    letter-spacing: 12px;
    color: #ffffff;
    margin-right: -12px;
    text-transform: uppercase;
    text-shadow: 0 0 30px rgba(0, 210, 255, 0.4);
}

.splash-subtitle {
    font-size: 0.75rem;
    font-weight: 100;
    color: rgba(255,255,255,0.5);
    letter-spacing: 8px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 5px;
    margin-bottom: 2.5rem;
}

/* Glassmorphism Console */
.status-console {
    width: 340px;
    background: rgba(10, 15, 24, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(0, 210, 255, 0.02);
}

.status-line {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.status-value {
    color: #00d2ff;
    font-weight: 400;
    text-shadow: 0 0 8px rgba(0, 210, 255, 0.4);
}

.progress-track {
    width: 100%;
    height: 2px;
    background: rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
    margin-top: 4px;
    border-radius: 1px;
}

.progress-fill {
    position: absolute;
    top: 0; left: 0; height: 100%; width: 0%;
    background: linear-gradient(90deg, transparent, #00d2ff, #ffffff);
    box-shadow: 0 0 10px #00d2ff;
    animation: fillProgress 3.8s cubic-bezier(0.8, 0, 0.2, 1) forwards;
}

@keyframes spinSweep {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes spinSweepReverse {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(-360deg); }
}

@keyframes pulseCoreGlow {
    0% { transform: scale(0.9); opacity: 0.6; }
    100% { transform: scale(1.1); opacity: 1; }
}

@keyframes slideUpFade {
    0% { opacity: 0; transform: translateY(30px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes fillProgress {
    0% { width: 0%; }
    40% { width: 35%; }
    75% { width: 85%; }
    100% { width: 100%; }
}

@keyframes fadeOutSplash {
    0%, 85% { opacity: 1; visibility: visible; }
    100% { opacity: 0; visibility: hidden; }
}

.sys-boot::after { 
    content: "";
    animation: textGlitch 3.8s steps(1) forwards; 
}
@keyframes textGlitch {
    0% { content: "INITIALIZING..."; color: #00d2ff;}
    20% { content: "ESTABLISHING NEURAL LINK..."; color: #00d2ff; }
    45% { content: "LOADING LANGUAGE MODELS..."; color: #00d2ff; }
    70% { content: "VERIFYING ENCRYPTION..."; color: #00d2ff; }
    90% { content: "SYSTEM ONLINE"; color: #00ffaa; text-shadow: 0 0 10px #00ffaa;}
}

.sys-mem::after { 
    content: "";
    animation: memTick 3.8s steps(1) forwards; 
}
@keyframes memTick {
    0% { content: "0.0 TB"; }
    20% { content: "128.4 TB"; }
    45% { content: "512.8 TB"; }
    70% { content: "1024.0 TB"; }
    90% { content: "OPTIMIZED"; color: #00ffaa; }
}
</style>

<div class="solid-splash">
<div class="orbital-core">
<div class="ring-track ring-track-1"></div>
<div class="sweep sweep-1"></div>
<div class="ring-track ring-track-2"></div>
<div class="sweep sweep-2"></div>
<div class="ring-track ring-track-3"></div>
<div class="sweep sweep-3"></div>
<div class="core-glow"></div>
</div>

<div class="splash-content">
<div class="splash-logo">DEEPSENSE</div>
<div class="splash-subtitle">Neural Intelligence Engine</div>

<div class="status-console">
<div class="status-line">
<span>System Status</span>
<span class="status-value sys-boot"></span>
</div>
<div class="status-line">
<span>Active Memory</span>
<span class="status-value sys-mem"></span>
</div>
<div class="progress-track">
<div class="progress-fill"></div>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        
        # Force the Python backend to hold this screen for exactly 3.8 seconds to let the fade-out complete
        time.sleep(3.8)
        
    # Physically destroy the splash screen from the application DOM forever
    splash_placeholder.empty()
        
# ── Delete Confirmation Dialog ────────────────────────────────────────────────
@st.dialog("🗑️ Confirm Deletion")
def confirm_delete_dialog(sid: str):
    st.markdown("Are you sure you want to delete this conversation? **This action cannot be undone.**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Delete Permanently", type="primary", use_container_width=True):
            st.session_state.memory.delete_session(sid)
            # If we deleted the currently active session, clear the screen
            if st.session_state.session_id == sid:
                st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
                st.session_state.chat_history = []
            
            # Queue a success message to display after the page reloads
            st.session_state.show_toast = "Chat permanently deleted."
            st.rerun()

# Check for queued toast messages after a reload
if st.session_state.get("show_toast"):
    st.toast(st.session_state.show_toast)
    del st.session_state.show_toast

# ── Sidebar (The Intelligence Vault) ──────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='margin-top:0; font-family:Outfit;'>Workspace</h2>", unsafe_allow_html=True)
    
    # New Chat Button (Minimalist)
    if st.button("＋ New Chat", use_container_width=True, key="new_chat_btn", type="primary"):
        st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Recent Links (Session-based History) ──
    st.markdown("<small style='color:var(--text-zinc-400); font-weight:600; text-transform:uppercase; letter-spacing:1px;'>Recent Chats</small>", unsafe_allow_html=True)
    # Group history into unique sessions
    sessions = {}
    for turn in st.session_state.memory._history:
        sid = turn.get("session_id", "default")
        if sid not in sessions:
            sessions[sid] = turn.get("user", "Empty Chat")
            
    if not sessions:
        st.markdown("<div style='color:var(--text-zinc-400); font-size:0.8rem; padding:10px;'>No recent chats found.</div>", unsafe_allow_html=True)
    else:
        # Display the last 5 sessions
        for sid in list(sessions.keys())[-5:][::-1]:
            title = sessions[sid]
            truncated = (title[:28] + '...') if len(title) > 28 else title
            
            # Place the load button and the delete button side-by-side with no gap
            col1, col2 = st.columns([0.85, 0.15], gap="small", vertical_alignment="center")
            with col1:
                if st.button(f"💬 {truncated}", key=f"load_{sid}", use_container_width=True):
                    st.session_state.session_id = sid
                    st.session_state.chat_history = []
                    for t in st.session_state.memory._history:
                        if t.get("session_id", "default") == sid:
                            st.session_state.chat_history.append({"role": "user", "text": t.get("user", ""), "lang": st.session_state.get("selected_lang", "en"), "time": t.get("timestamp", "")})
                            st.session_state.chat_history.append({"role": "assistant", "text": t.get("assistant", ""), "lang": st.session_state.get("selected_lang", "en"), "time": t.get("timestamp", "")})
                    st.rerun()
            with col2:
                # The \u200b (zero-width space) forces the icon button to be exactly as tall as the text button!
                if st.button("\u200b", icon=":material/delete:", key=f"del_{sid}", help="Delete chat", use_container_width=True):
                    confirm_delete_dialog(sid)

      # ── Sticky Bottom Container ──
    with st.sidebar.container(key="sidebar_bottom"):
        # ── Export Transcript Feature (PDF) ──
        if st.session_state.chat_history:
            def generate_pdf():
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", 'B', 16)
                pdf.cell(0, 10, "DeepSense - Neural Link Transcript", ln=True, align="C")
                pdf.ln(10)
                
                for m in st.session_state.chat_history:
                    role = "User" if m["role"] == "user" else "DeepSense"
                    pdf.set_font("Helvetica", 'B', 12)
                    if role == "DeepSense":
                        pdf.set_text_color(255, 94, 0)
                    else:
                        pdf.set_text_color(0, 0, 0)
                    pdf.cell(0, 8, f"{role}:", ln=True)
                    
                    pdf.set_font("Helvetica", '', 11)
                    pdf.set_text_color(50, 50, 50)
                    clean_text = m['text'].encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 6, clean_text)
                    pdf.ln(4)
                
                return bytes(pdf.output())
            
            _pdf = st.download_button(
                label="📄 Export Neural Log (.PDF)",
                data=generate_pdf(),
                file_name="deepsense_neural_log.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_export",
            )
        
        with st.expander("⚙️ Settings", expanded=False):
            st.session_state.tts_enabled = st.toggle(
                "🔊 Voice Output", value=st.session_state.tts_enabled, key="tts_toggle"
            )
            
            # Advanced Voice Controls
            st.session_state.voice_matrix = st.selectbox("🗣️ Voice Matrix", ["Neural Male", "Neural Female", "Deep Studio"], key="voice_sel")
            voice_speed = st.slider("⏱️ Synthesis Speed", 0.5, 2.0, 1.0, 0.1, key="speed_sl")
            
            st.session_state.selected_lang = st.selectbox(
                "🌐 Language",
                options=list(SUPPORTED_LANGUAGES.keys()),
                format_func=lambda k: SUPPORTED_LANGUAGES[k],
                index=0,
                key="lang_sel",
            )
            with st.expander("🛠️ Advanced Settings", expanded=False):
                ai_mode = st.selectbox(
                    "🤖 Engine",
                    options=["OpenAI GPT-4o-mini", "Trained LSTM (Offline)", "Rule-Based (Offline)"],
                    index=0,
                    key="engine_sel",
                )

        st.markdown(
            "<div style='text-align:center; padding-top:10px;'><small style='color:var(--text-zinc-400); opacity:0.6;'>DeepSense v2.1</small></div>",
            unsafe_allow_html=True,
        )



# ── Share Dialog Modal ────────────────────────────────────────────────────────
@st.dialog("📤 Share Neural Response")
def share_dialog(text: str):
    import urllib.parse
    st.markdown("Share this response directly to your networks:")

    encoded_text = urllib.parse.quote(f'"{text[:250]}..."\n\n— Generated by DeepSense AI')

    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        <a href="https://twitter.com/intent/tweet?text={encoded_text}" target="_blank" style="text-decoration:none; background:#1DA1F2; color:white; padding:10px 15px; border-radius:8px; font-weight:bold; font-size:0.9rem;">🐦 Twitter / X</a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://deepsense.com" target="_blank" style="text-decoration:none; background:#0077b5; color:white; padding:10px 15px; border-radius:8px; font-weight:bold; font-size:0.9rem;">💼 LinkedIn</a>
        <a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank" style="text-decoration:none; background:#25D366; color:white; padding:10px 15px; border-radius:8px; font-weight:bold; font-size:0.9rem;">💬 WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.text_area("Or copy the raw text:", text, height=150)

# ── Process & Respond ─────────────────────────────────────────────────────────
def process_message(text: str, image_b64: str = None, document_context: str = None):
    """Core pipeline: AI (Streaming) → response → Parallel TTS."""
    # Detect language
    lang = detect_language(text) or st.session_state.selected_lang

    # Build context-aware prompt with conversation memory (filtered by current session)
    context = st.session_state.memory.build_context(text, session_id=st.session_state.session_id)

    # Pre-allocate assistant message to save partial text if user clicks Stop
    msg_index = len(st.session_state.chat_history)
    st.session_state.chat_history.append(
        {"role": "assistant", "text": "", "lang": lang, "time": datetime.now().strftime("%I:%M %p")}
    )

    # placeholder for the AI response in the UI
    with st.chat_message("assistant", avatar=":material/psychology:"):
        response_placeholder = st.empty()
        
        # ── Animated Thinking Indicator ──
        response_placeholder.markdown("""
        <div class="thinking-indicator">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Get AI streaming response
        if "LSTM" in ai_mode:
            engine_mode = "lstm"
        elif "OpenAI" in ai_mode:
            engine_mode = "openai"
        else:
            engine_mode = "offline"
        use_openai = engine_mode == "openai"
        
        # We wrap the generator to handle streaming and continuous state saving
        def stream_without_auto_tts():
            full_response = ""
            for chunk in get_ai_response(text, context, use_openai, lang, engine_mode=engine_mode, image_b64=image_b64, document_context=document_context):
                full_response += chunk
                st.session_state.chat_history[msg_index]["text"] = full_response
                yield chunk

        # Render the stream
        full_response = response_placeholder.write_stream(stream_without_auto_tts())

    # Store in memory linked to the current active session
    st.session_state.memory.add_turn(user=text, assistant=full_response, session_id=st.session_state.session_id)

    # ── Premium Notification Chime ──
    st.markdown("""
    <img src="x" style="display:none;" onerror="
        try {
            var a = new (window.AudioContext || window.webkitAudioContext)();
            function p(f, t, d) {
                var o = a.createOscillator(), g = a.createGain();
                o.type = 'sine'; o.frequency.value = f;
                g.gain.setValueAtTime(0.08, a.currentTime + t);
                g.gain.exponentialRampToValueAtTime(0.001, a.currentTime + t + d);
                o.connect(g); g.connect(a.destination);
                o.start(a.currentTime + t); o.stop(a.currentTime + t + d);
            }
            p(880, 0, 0.15); p(1320, 0.12, 0.2);
        } catch(e) {}
    " />
    """, unsafe_allow_html=True)

    st.rerun()

    # ── Minimalist Navigation ──────────────────────────────────────────────────
st.markdown(
    """
    <div class='nav-container'>
        <div class='nav-logo'><span class='logo-vox'>DEEP</span><span class='logo-mind'>SENSE</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Chat History Display (Centered Pillar) ──────────────────────────────────
welcome_placeholder = st.empty()

if not st.session_state.chat_history:
    with welcome_placeholder.container():
        st.markdown(
            """
            <div class='welcome-card'>
                <div class='welcome-logo'>🧠</div>
                <h1 class='welcome-title'>How can I assist you today?</h1>
                <p class='welcome-subtitle'>
                    DeepSense is ready to process your intelligence requests 
                    via voice or text in multiple languages.
                </p>
                 </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Quick-Action Suggestion Chips ──
        suggestions = [
            ("💡", "Explain how neural networks learn"),
            ("🐍", "Write a Python function to sort a list"),
            ("🌍", "Tell me 5 interesting facts about space"),
            ("😂", "Tell me a clever joke"),
        ]

        chip_cols = st.columns(len(suggestions))
        for idx, (icon, prompt) in enumerate(suggestions):
            with chip_cols[idx]:
                if st.button(f"{icon}  {prompt}", key=f"chip_{idx}", use_container_width=True):
                    welcome_placeholder.empty()
                    st.session_state.chat_history.append({"role": "user", "text": prompt, "lang": st.session_state.selected_lang, "time": datetime.now().strftime("%I:%M %p")})
                    st.session_state.pending_prompt = prompt
                    st.rerun()

for i, msg in enumerate(st.session_state.chat_history):
    avatar = ":material/person:" if msg["role"] == "user" else ":material/psychology:"
    with st.chat_message(msg["role"], avatar=avatar):
        # Show attachment chip if file was attached to this message
        if msg.get("attachment"):
            att = msg["attachment"]
            att_icon = "🖼️" if att["type"] == "image" else "📄"
            att_size = att.get("size", 0)
            if att_size > 1048576:
                att_size_str = f"{att_size / 1048576:.1f} MB"
            elif att_size > 1024:
                att_size_str = f"{att_size / 1024:.1f} KB"
            elif att_size > 0:
                att_size_str = f"{att_size} B"
            else:
                att_size_str = ""
            size_part = f' · {att_size_str}' if att_size_str else ''
            st.markdown(f'''
            <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(0, 210, 255, 0.06); border: 1px solid rgba(0, 210, 255, 0.2); border-radius: 10px; padding: 6px 14px; font-size: 0.78rem; color: #e4e4e7; margin-bottom: 10px; font-weight: 500;">
                <span style="font-size: 1rem;">{att_icon}</span>
                <span style="color: #d4d4d8;">{att["name"]}</span>
                <span style="color: #52525b; font-size: 0.68rem;">{size_part}</span>
            </div>
            ''', unsafe_allow_html=True)

        if msg.get("web_search_used"):
            st.markdown("""
            <div style="display: inline-flex; align-items: center; gap: 6px; background: transparent; border: 1px solid rgba(0, 210, 255, 0.4); border-radius: 12px; padding: 4px 12px; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 8px; font-weight: 500;">
                <span style="color: #00d2ff;">🌐</span> Global Network Connected
            </div>
            """, unsafe_allow_html=True)
            
        # Strip system override prefixes for display so the user doesn't see the raw prompt context
        display_text = msg["text"]
        if display_text.startswith("SYSTEM OVERRIDE:"):
            # The user prompt is appended at the very end after "User prompt: "
            parts = display_text.split("User Prompt: ")
            if len(parts) > 1:
                display_text = parts[-1]
            else:
                parts2 = display_text.split("User prompt: ")
                if len(parts2) > 1:
                    display_text = parts2[-1]
                
        st.write(display_text)

        # Elegant Timestamp
        ts = msg.get("time", "")
        if ts:
            st.markdown(f"<div class='msg-timestamp'>{ts}</div>", unsafe_allow_html=True)

        # Add Action Buttons below AI messages
        if msg["role"] == "assistant":
                # Feedback State Management
                if "feedback" not in st.session_state:
                    st.session_state.feedback = {}
                
                fb_state = st.session_state.feedback.get(i, None)
                
                # Inject Feedback CSS OUTSIDE the columns so it doesn't push the buttons down!
                css_injection = ""
                if fb_state == "like":
                    css_injection = f"<style>div[class*='st-key-like_{i}'] span {{ font-variation-settings: 'FILL' 1 !important; color: #22c55e !important; }}</style>"
                elif fb_state == "dislike":
                    css_injection = f"<style>div[class*='st-key-dislike_{i}'] span {{ font-variation-settings: 'FILL' 1 !important; color: #ef4444 !important; }}</style>"
                
                st.markdown(f"<div style='height: 5px;'></div>{css_injection}", unsafe_allow_html=True)
                
                # Professional Action Bar Layout — ALL buttons always visible
                action_cols = st.columns([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 7])
                
                with action_cols[0]:
                    if st.button(" ", icon=":material/volume_up:", key=f"listen_{i}", help="Read aloud"):
                        st.toast("Synthesizing audio...", icon="⏳")
                        speak_text(
                            msg["text"], 
                            msg.get("lang", st.session_state.selected_lang), 
                            st.session_state.get("voice_matrix", "Neural Male")
                        )

                with action_cols[1]:
                    if st.button(" ", icon=":material/stop_circle:", key=f"stop_{i}", help="Stop reading"):
                        stop_speaking()
                        st.toast("Playback stopped.", icon="🔇")

                with action_cols[2]:
                    if st.button(" ", icon=":material/content_copy:", key=f"copy_{i}", help="Copy text"):
                        st.toast("Select text and press Ctrl+C / Cmd+C to copy.", icon="📋")
                        
                with action_cols[3]:
                    if st.button(" ", icon=":material/thumb_up:", key=f"like_{i}", help="Good response"):
                        st.session_state.feedback[i] = "like"
                        st.toast("Feedback recorded! We're glad it helped.", icon="👍")
                        st.rerun()
                        
                with action_cols[4]:
                    if st.button(" ", icon=":material/thumb_down:", key=f"dislike_{i}", help="Bad response"):
                        st.session_state.feedback[i] = "dislike"
                        st.toast("Feedback recorded! We will improve our model.", icon="👎")
                        st.rerun()
                        
                with action_cols[5]:
                    if st.button(" ", icon=":material/share:", key=f"share_{i}", help="Share response"):
                        share_dialog(msg["text"])

# ── Custom Floating UI above input ──
with st.popover("＋", use_container_width=False):

    if st.button("📎 Add photos & files", type="tertiary", use_container_width=True):
        st.toast("Please use the 'Browse Files' buttons below to select your files.", icon="📎")
    if st.button("⛶ Take screenshot", type="tertiary", use_container_width=True):
        st.toast("Screenshot captured to memory!", icon="📸")
    if st.button("📷 Take photo", type="tertiary", use_container_width=True):
        st.session_state.show_camera = not st.session_state.get("show_camera", False)
        st.rerun()
        
    if st.session_state.get("show_camera", False):
        st.camera_input("Take a photo", key=st.session_state.camera_key)
    st.markdown("<div style='height: 5px'></div>", unsafe_allow_html=True)
    st.markdown("📄 **Upload Documents (Max 200MB)**")
    uploaded_doc = st.file_uploader("Browse Files", type=["txt", "csv", "md", "pdf"], key=st.session_state.doc_uploader_key, label_visibility="collapsed")
    st.markdown("👁️ **Upload Images (Max 20MB)**")
    uploaded_img = st.file_uploader("Browse Images", type=["png", "jpg", "jpeg"], key=st.session_state.img_uploader_key, label_visibility="collapsed")
    
    # Auto-close popover when a file is uploaded using Javascript
    if (uploaded_doc or uploaded_img) and not st.session_state.get("_popover_file_seen"):
        st.session_state["_popover_file_seen"] = True
        st.markdown("""
        <script>
            // Close the popover by simulating a click outside
            setTimeout(function() {
                const backdrops = window.parent.document.querySelectorAll('[data-testid="stPopoverBody"]');
                if (backdrops && backdrops.length > 0) {
                    // Click on the main container to dismiss popover
                    const mainContainer = window.parent.document.querySelector('.stApp');
                    if (mainContainer) {
                        mainContainer.click();
                    }
                }
            }, 50);
        </script>
        """, unsafe_allow_html=True)
        st.rerun()
    elif not (uploaded_doc or uploaded_img):
        st.session_state.pop("_popover_file_seen", None)

if "web_search" not in st.session_state:
    st.session_state.web_search = False

if st.button("Web Search", icon=":material/check_circle:" if st.session_state.web_search else ":material/language:", key="web_search_container"):
    st.session_state.web_search = not st.session_state.web_search
    st.rerun()

if st.button(" ", icon=":material/mic:", key="voice_mic_btn"):
    st.session_state.is_recording = True
    st.rerun()

# ── Upload Preview (in the prompting area above st.chat_input) ──
active_file = None
uploaded_doc = st.session_state.get(st.session_state.doc_uploader_key)
uploaded_img = st.session_state.get(st.session_state.img_uploader_key)
camera_photo = st.session_state.get(st.session_state.camera_key)

if uploaded_doc:
    active_file = uploaded_doc
elif uploaded_img:
    active_file = uploaded_img
elif camera_photo:
    active_file = camera_photo

upload_preview_placeholder = st.empty()

if active_file:
    col1, col2 = upload_preview_placeholder.columns([0.92, 0.08])
    with col1:
        file_name = getattr(active_file, "name", "Captured Photo")
        if not file_name:
            file_name = "photo_capture.jpg"
        file_icon = "🖼️" if (uploaded_img or camera_photo) else "📄"
        file_size = getattr(active_file, "size", 0)
        if file_size > 1048576:
            size_str = f"{file_size / 1048576:.1f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        elif file_size > 0:
            size_str = f"{file_size} B"
        else:
            size_str = "Ready"
        st.markdown(f'''
        <style>
            /* The overall wrapper (stHorizontalBlock) */
            .custom-upload-wrapper {{
                background-color: #0b0d14 !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 12px !important;
                padding: 12px 16px !important;
                display: flex !important;
                align-items: center !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
                margin-bottom: 8px !important;
            }}
            /* The file icon box */
            .file-icon-wrap {{
                width: 40px;
                height: 40px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 14px;
            }}
            /* Text container */
            .upload-preview-pill {{
                display: flex;
                align-items: center;
                flex-grow: 1;
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                box-shadow: none !important;
            }}
            /* Ensure the text is aligned correctly */
            .upload-preview-text-box {{
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
        </style>
        <div class="upload-preview-pill" id="upload-preview-container">
            <div class="file-icon-wrap">
                <span style="font-size: 1.2rem;">{file_icon}</span>
            </div>
            <div class="upload-preview-text-box">
                <span style="font-size: 0.9rem; font-weight: 700; color: #ffffff; margin-bottom: 2px;">{file_name}</span>
                <span style="font-size: 0.75rem; color: #71717a;">{size_str} · Ready to send</span>
            </div>
        </div>
        <script>
            setTimeout(function() {{
                const doc = window.parent.document;
                const pill = doc.getElementById('upload-preview-container');
                const cancelBtnWrapper = doc.querySelector('.st-key-clear_upload_btn');
                if (cancelBtnWrapper) {{
                    cancelBtnWrapper.addEventListener('click', function() {{
                        if (pill) {{
                            const block = pill.closest('[data-testid="stHorizontalBlock"]');
                            if (block) block.style.opacity = '0';
                        }}
                    }});
                }}
            }}, 50);
        </script>
        ''', unsafe_allow_html=True)
    with col2:
        if st.button(" ", icon=":material/close:", key="clear_upload_btn", help="Cancel upload"):
            import time
            st.session_state.doc_uploader_key = f"doc_upload_{time.time()}"
            st.session_state.img_uploader_key = f"img_upload_{time.time()}"
            st.session_state.camera_key = f"camera_{time.time()}"
            st.session_state.show_camera = False
            st.session_state.pop("_popover_file_seen", None)
            st.rerun()

# ── Chat Input (Auto-styled as Floating Pill via CSS) ───────────────────────
chat_text = st.chat_input("Ask anything")

if chat_text:
    welcome_placeholder.empty()
    upload_preview_placeholder.empty()
    
    # ── Global Network Web Search Logic ──
    web_context = ""
    needs_live_data = st.session_state.web_search or any(k in chat_text.lower() for k in ["current ", "today", "latest ", "live price", "right now", "who is the"])
    
    # Build attachment metadata for chat history display
    attachment_meta = None
    uploaded_file_for_history = uploaded_doc or uploaded_img or camera_photo
    if uploaded_file_for_history:
        _fname = getattr(uploaded_file_for_history, "name", "Captured Photo") or "photo_capture.jpg"
        _fsize = getattr(uploaded_file_for_history, "size", 0)
        _ftype = "image" if (uploaded_img or camera_photo) else "document"
        attachment_meta = {"name": _fname, "size": _fsize, "type": _ftype}
    
    st.session_state.chat_history.append({
        "role": "user", 
        "text": chat_text, 
        "lang": st.session_state.selected_lang, 
        "time": datetime.now().strftime("%I:%M %p"),
        "web_search_used": needs_live_data,
        "attachment": attachment_meta
    })
    
    # Immediately render the user's message so the UI doesn't look frozen
    with st.chat_message("user", avatar=":material/person:"):
        st.write(chat_text)
    
    if needs_live_data:
        with st.spinner("Accessing Global Network..."):
            try:
                import urllib.request, urllib.parse, json, re, os
                tavily_key = os.getenv("TAVILY_API_KEY")
                if tavily_key:
                    req_data = json.dumps({"api_key": tavily_key, "query": chat_text, "search_depth": "advanced", "include_answer": True}).encode('utf-8')
                    req = urllib.request.Request("https://api.tavily.com/search", data=req_data, headers={'Content-Type': 'application/json'})
                    data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode('utf-8'))
                    snippets = [r.get('content', '') for r in data.get('results', [])[:4]]
                    web_context = f"LIVE WEB SEARCH RESULTS:\n{' | '.join(snippets)}"
                else:
                    safe_query = urllib.parse.quote(chat_text)
                    html = urllib.request.urlopen(f"https://search.yahoo.com/search?p={safe_query}", timeout=5).read().decode('utf-8')
                    snippets = re.findall(r'<div class="[^"]*compText[^"]*".*?>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
                    web_context = " ".join([re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:3]])
            except Exception:
                pass

    if web_context:
        chat_text = f"SYSTEM OVERRIDE: You are connected to the internet. Use this live data to answer the prompt. DO NOT mention your knowledge cutoff date. CRITICAL RULE: You MUST extract the exact numerical values directly from the raw data provided below. If you see multiple conflicting prices across the sources for the same item, output the HIGHEST price found (as it represents the most recent market peak). Do not round or guess. Live Data: '{web_context}'. User Prompt: {chat_text}"

    # ── Document & Image Processing Logic ──
    document_context = ""
    image_b64 = None
    uploaded_file = uploaded_doc or uploaded_img or camera_photo
    if uploaded_file:
        with st.spinner("Analyzing neural data streams..."):
            try:
                is_image = False
                if hasattr(uploaded_file, 'name') and uploaded_file.name and uploaded_file.name.endswith(('.png', '.jpg', '.jpeg')):
                    is_image = True
                elif camera_photo:
                    is_image = True

                if is_image:
                    import base64
                    image_b64 = base64.b64encode(uploaded_file.read()).decode("utf-8")
                elif hasattr(uploaded_file, 'name') and uploaded_file.name.endswith('.pdf'):
                    import PyPDF2
                    pdf = PyPDF2.PdfReader(uploaded_file)
                    document_context = "\\n".join(page.extract_text() or "" for page in pdf.pages)
                elif hasattr(uploaded_file, 'name') and uploaded_file.name.endswith('.csv'):
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                    document_context = df.to_string(index=False)
                else:
                    document_context = uploaded_file.read().decode("utf-8")
                
                if document_context:
                    chat_text = f"SYSTEM OVERRIDE: Context document provided. {document_context}\n\nUser prompt: {chat_text}"
            except Exception:
                pass

    # Clear uploads BEFORE processing (data already extracted into variables)
    if uploaded_file:
        import time as _t
        st.session_state.doc_uploader_key = f"doc_upload_{_t.time()}"
        st.session_state.img_uploader_key = f"img_upload_{_t.time()}"
        st.session_state.camera_key = f"camera_{_t.time()}"
        st.session_state.show_camera = False
        st.session_state.pop("_popover_file_seen", None)

    process_message(chat_text, image_b64=image_b64, document_context=document_context)

# Execute pending prompt from chips (since chips still require a rerun to clear the buttons cleanly)
if st.session_state.get("pending_prompt"):
    prompt_to_process = st.session_state.pending_prompt
    del st.session_state.pending_prompt
    process_message(prompt_to_process)

# ── Voice Recording Flow ──────────────────────────────────────────────────────
if st.session_state.is_recording:
    with st.status("🎙️ Voice Interface Active", expanded=True) as status:
        # ── Real-Time Audio Visualizer ──
        st.markdown("""
        <div class="audio-visualizer">
            <div class="bar"></div><div class="bar"></div><div class="bar"></div>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
        <p style="color:#a1a1aa; font-family:'JetBrains Mono', monospace; font-size:0.9rem; text-align:center;">Awaiting voice input...</p>
        """, unsafe_allow_html=True)
        
        # Get duration from sidebar or default
        rec_duration = st.sidebar.slider("Recording Time", 3, 15, 5)
        audio_data = record_audio(duration=rec_duration)
        
        if audio_data:
            transcript = transcribe_audio(
                audio_data, language=st.session_state.selected_lang
            )
            if transcript:
                status.update(label=f"✅ Captured: {transcript}", state="complete")
                time.sleep(1)
                st.session_state.is_recording = False
                process_message(transcript)
            else:
                status.update(label="❌ No speech detected.", state="error")
                st.session_state.is_recording = False
        else:
            status.update(label="❌ Hardware Error", state="error")
            st.session_state.is_recording = False
    
    time.sleep(2)
    st.rerun()
