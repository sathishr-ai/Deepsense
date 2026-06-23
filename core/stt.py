"""
core/stt.py  –  Speech-to-Text Engine
========================================
Uses Google SpeechRecognition as primary.
Falls back to OpenAI Whisper (local) if available.
Supports English and Tamil.
"""

import io
import os
import time
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)

# ── Audio Recording ────────────────────────────────────────────────────────────

def record_audio(duration: int = 5) -> sr.AudioData | None:
    """
    Record audio from the default microphone.

    Args:
        duration: How many seconds to record.

    Returns:
        sr.AudioData object or None if recording fails.
    """
    recognizer = sr.Recognizer()

    # Tune these for accuracy and to prevent cutting off early
    recognizer.energy_threshold = 300        # Mic sensitivity
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.5         # Wait 1.5 seconds of silence before cutting off

    try:
        with sr.Microphone() as source:
            logger.info(f"Recording for {duration}s...")
            # Brief calibration to handle ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Wait indefinitely for speech to start (timeout=None), but limit phrase to duration
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=duration)
            logger.info("Recording complete.")
            return audio
    except sr.WaitTimeoutError:
        logger.warning("No speech detected within timeout.")
        return None
    except Exception as e:
        logger.error(f"Recording error: {e}")
        return None


# ── Transcription ──────────────────────────────────────────────────────────────

def transcribe_audio(audio: sr.AudioData | None, language: str = "en") -> str:
    """
    Convert recorded audio to text.

    Strategy:
    1. Try Google Speech Recognition (free, online)
    2. If unavailable, try Whisper (local, offline)
    3. Return empty string on failure

    Args:
        audio: AudioData from record_audio()
        language: BCP-47 language code (e.g. "en-US", "ta-IN")

    Returns:
        Transcribed text string.
    """
    if audio is None:
        return ""

    # Map short codes to BCP-47 tags Google understands
    lang_map = {
        "en": "en-US",
        "ta": "ta-IN",
    }
    google_lang = lang_map.get(language, "en-US")

    recognizer = sr.Recognizer()

    # ── Strategy 1: Google Web Speech API (free tier) ──────────────────────
    try:
        text = recognizer.recognize_google(audio, language=google_lang)
        logger.info(f"Google STT result: {text}")
        return text.strip()
    except sr.UnknownValueError:
        logger.warning("Google STT: Could not understand audio.")
    except sr.RequestError as e:
        logger.warning(f"Google STT unavailable: {e}. Trying Whisper...")

    # ── Strategy 2: OpenAI Whisper (local, offline fallback) ───────────────
    try:
        import whisper  # pip install openai-whisper
        model = whisper.load_model("base")  # 'tiny' is faster, 'small' is more accurate

        # Whisper needs a file path; write audio to temp WAV
        import tempfile, soundfile as sf, numpy as np
        audio_array = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_array, samplerate=16000)
            tmp_path = tmp.name

        result = model.transcribe(tmp_path, language=language if language != "en" else None)
        os.unlink(tmp_path)  # Clean up temp file
        text = result.get("text", "").strip()
        logger.info(f"Whisper STT result: {text}")
        return text

    except ImportError:
        logger.warning("Whisper not installed. Install with: pip install openai-whisper")
    except Exception as e:
        logger.error(f"Whisper STT error: {e}")

    return ""
