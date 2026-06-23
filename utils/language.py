"""
utils/language.py  –  Language Detection Utility
===================================================
Detects whether input text is English or Tamil.
Uses langdetect library with a simple fallback heuristic.
"""

import logging
logger = logging.getLogger(__name__)

# Supported languages: {code: display_name}
SUPPORTED_LANGUAGES = {
    "en": "🇬🇧 English",
    "ta": "🇮🇳 Tamil",
}

# Tamil Unicode character range check (simple heuristic)
TAMIL_UNICODE_RANGE = range(0x0B80, 0x0BFF)


def _is_tamil_script(text: str) -> bool:
    """Return True if the text contains Tamil Unicode characters."""
    return any(ord(char) in TAMIL_UNICODE_RANGE for char in text)


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Strategy:
    1. Check for Tamil script characters (fast, no library needed)
    2. Use langdetect if available
    3. Default to English

    Args:
        text: Input text string.

    Returns:
        Language code: 'en' or 'ta'.
    """
    if not text.strip():
        return "en"

    # Fast check: Tamil script detection
    if _is_tamil_script(text):
        logger.debug("Detected Tamil script in input.")
        return "ta"

    # Attempt langdetect for romanized Tamil / ambiguous cases
    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 42  # Reproducible results
        lang = detect(text)
        logger.debug(f"langdetect result: {lang}")
        return "ta" if lang == "ta" else "en"
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")

    return "en"   # Safe default
