import os
import logging
import threading
import tempfile
import queue
import time
import asyncio

logger = logging.getLogger(__name__)

# ── Voice Profiles ───────────────────────────────────────────────────────────
VOICE_MAP = {
    "Neural Male": "en-US-GuyNeural",
    "Neural Female": "en-US-JennyNeural",
    "Deep Studio": "en-US-DavisNeural",
}

# ── Global Speech Queue & Worker ─────────────────────────────────────────────
_speech_queue = queue.Queue()
_stop_event = threading.Event()

def _speech_worker():
    """Background thread that consumes the speech queue and plays sequentially."""
    while True:
        try:
            text, language, voice_name = _speech_queue.get()
            if text is None: break  # Sentinel to stop
            
            if _stop_event.is_set():
                _speech_queue.task_done()
                continue
            
            _speak_edge_tts(text, language, voice_name)
            
        except Exception as e:
            logger.error(f"Speech worker execution error: {e}")
            print(f"Speech worker execution error: {e}")
        finally:
            _speech_queue.task_done()

# Start the worker once
_worker_thread = threading.Thread(target=_speech_worker, daemon=True)
_worker_thread.start()

def _ensure_worker_alive():
    global _worker_thread
    if not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=_speech_worker, daemon=True)
        _worker_thread.start()

def _speak_edge_tts(text: str, language: str, voice_name: str):
    """Use Microsoft Edge TTS for high-quality neural voices (male/female/deep)."""
    try:
        import edge_tts
        import pygame
        
        # Resolve the voice from the profile map
        voice = VOICE_MAP.get(voice_name, "en-US-JennyNeural")
        
        # Tamil Override
        if language == "ta":
            if "Female" in voice_name:
                voice = "ta-IN-PallaviNeural"
            else:
                voice = "ta-IN-ValluvarNeural"
                
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        # Run the async edge-tts in a new event loop
        async def _generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
        
        asyncio.run(_generate())
        
        # Check stop flag after generation
        if _stop_event.is_set():
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return
        
        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if _stop_event.is_set():
                pygame.mixer.music.stop()
                break
            time.sleep(0.05)
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception as e:
        logger.error(f"Edge TTS error: {e}, falling back to gTTS")
        # Fallback to gTTS if edge-tts fails
        _speak_gtts_fallback(text, language)

def _speak_gtts_fallback(text: str, language: str):
    """Fallback to gTTS if Edge TTS is unavailable."""
    try:
        from gtts import gTTS
        import pygame
        
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
            tts.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if _stop_event.is_set():
                pygame.mixer.music.stop()
                break
            time.sleep(0.05)
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    except Exception as e:
        logger.error(f"gTTS fallback error: {e}")

# ── Public Interface ──────────────────────────────────────────────────────────

def speak_text(text: str, language: str = "en", voice_name: str = "Neural Male") -> None:
    """
    Queue text for speech synthesis with voice selection.
    """
    if not text or not text.strip():
        return
        
    # Force language detection on the actual text to be spoken
    try:
        from utils.language import detect_language
        if detect_language(text) == "ta":
            language = "ta"
    except Exception:
        pass
    
    import re
    # Strip markdown symbols like #, **, *, _, etc., so TTS reads naturally
    clean_text = re.sub(r'[*_#`~>]+', '', text)
    # Also replace multiple spaces with a single space
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    _stop_event.clear()
    _ensure_worker_alive()
    _speech_queue.put((clean_text, language, voice_name))

def stop_speaking() -> None:
    """Immediately stop any ongoing speech playback and flush the queue."""
    _stop_event.set()
    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass
    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            break
