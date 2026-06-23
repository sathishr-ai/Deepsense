"""
core/chatbot.py  –  AI Response Engine
=========================================
Two modes:
  1. OpenAI GPT-4o-mini (online, powerful, context-aware)
  2. Rule-based NLP (offline fallback using keyword matching + templates)

Both modes are context-aware — they receive the full conversation memory.
"""

import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()  # Load OPENAI_API_KEY from .env file
logger = logging.getLogger(__name__)

# ── OpenAI Response ────────────────────────────────────────────────────────────

def _get_openai_response_stream(user_input: str, context: list[dict], language: str = "en", image_b64: str = None, document_context: str = None):
    """
    Get a streaming response from OpenRouter/OpenAI model (Multimodal + RAG).

    Yields:
        Chunks of text as they are generated.
    """
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            yield "⚠️ Error: API Key not found in .env"
            return

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

        lang_instruction = (
            "You are responding in beautiful, standard Tamil (தமிழ்). Use proper grammar and respectful terms." if language == "ta"
            else "You are responding in clear, sophisticated, yet friendly English (UK/US standard)."
        )

        system_prompt = f"""You are DeepSense, a high-performance Artificial Intelligence agent.
{lang_instruction}

Guidelines:
1. Answer clearly, correctly, and with technical elegance.
2. If unsure about a fact, state that you are not certain. Avoid misinformation.
3. Match your response length to the user's prompt. If they ask a simple question, be concise. If they ask for an essay, code, or detailed analysis, provide a comprehensive, long-form response.
4. You are highly encouraged to use Markdown formatting (bolding, headers, bullet points, code blocks) to make your responses look beautiful and readable.
5. Maintain a professional, 'Elite' persona."""

        if image_b64:
            system_prompt += "\n\n[CRITICAL SYSTEM OVERRIDE - VISION ENABLED]: You HAVE been provided with an image in the user's message. You CAN and MUST analyze it. If the image contains a person or a face, DO NOT attempt to identify them by name. Instead, you MUST describe their physical appearance, expression, clothing, and surroundings in detail. NEVER refuse to analyze an image."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        
        user_content = []
        if document_context:
            # Inject document directly into user message to prevent AI from ignoring it
            user_content.append({"type": "text", "text": f"[DOCUMENT CONTENT]:\n{document_context[:15000]}\n\n[USER PROMPT]: {user_input}"})
        else:
            user_content.append({"type": "text", "text": user_input})
            
        if image_b64:
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
            
        if document_context or image_b64:
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": user_input})

        stream = client.chat.completions.create(
            model="openai/gpt-4o-mini", # Changed from llama to support Multimodal Vision
            messages=messages,
            temperature=0.7,
            max_tokens=2500,
            stream=True,  # 🎉 Real-time optimization
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"I experienced a neural glitch. Falling back... {_get_offline_response(user_input, language)}"


# ── Offline Rule-Based NLP ────────────────────────────────────────────────────


def _get_time():
    """Return current time string."""
    from datetime import datetime
    return f"The current time is {datetime.now().strftime('%I:%M %p')}."


def _get_date():
    """Return current date string."""
    from datetime import datetime
    return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."


# Keyword patterns → response templates
RESPONSE_PATTERNS = [
    (r"\b(hi|hello|hey|vanakkam)\b",             "Hello! I'm DeepSense, your AI assistant. How can I help you today?"),
    (r"\bhow are you\b",                          "I'm doing great, thank you for asking! I'm ready to assist you."),
    (r"\byour name\b",                            "My name is DeepSense — your Voice and Mind combined!"),
    (r"\btime\b",                                 _get_time),          # callable → dynamic
    (r"\bdate|today\b",                           _get_date),
    (r"\bweather\b",                              "I don't have live weather data, but you can check Google Weather or a weather app."),
    (r"\b(bye|goodbye|see you|exit)\b",           "Goodbye! It was great talking with you. Have a wonderful day!"),
    (r"\bthank(s| you)\b",                        "You're very welcome! Is there anything else I can help you with?"),
    (r"\bwhat (is|are) (ai|artificial intelligence)\b",
                                                  "Artificial Intelligence is the simulation of human intelligence by machines, enabling tasks like learning, reasoning, and speech recognition."),
    (r"\b(joke|funny)\b",                         "Why did the programmer quit his job? Because he didn't get arrays! 😄"),
    (r"\bcapital of india\b",                     "The capital of India is New Delhi."),
    (r"\bcapital of tamil nadu\b",                "The capital of Tamil Nadu is Chennai."),
    (r"\bpython\b",                               "Python is a versatile, beginner-friendly programming language widely used in AI, web development, and data science."),
]


def _get_offline_response(user_input: str, language: str = "en") -> str:
    """
    Rule-based response engine for offline use.

    Args:
        user_input: User's message.
        language: Language code.

    Returns:
        Best-matching response string.
    """
    text = user_input.lower().strip()

    for pattern, reply in RESPONSE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # reply can be a callable (e.g., _get_time) or a string
            return reply() if callable(reply) else reply

    # Default fallback
    tamil_default = "மன்னிக்கவும், என்னால் அதை புரிந்துகொள்ள முடியவில்லை. மீண்டும் கேட்கவும்."
    english_default = "I'm not sure about that, but I'm learning! Could you rephrase your question?"

    return tamil_default if language == "ta" else english_default


# ── Trained LSTM Seq2Seq Response ─────────────────────────────────────────────

# Cached LSTM model (loaded once, reused across requests)
_lstm_inference = None


def _load_lstm_model():
    """Load the trained LSTM Seq2Seq model (cached singleton)."""
    global _lstm_inference
    if _lstm_inference is not None:
        return _lstm_inference

    try:
        from data.preprocessing import TextPreprocessor
        from model.seq2seq_model import Encoder, Decoder
        from model.inference import ChatbotInference
        import config as cfg
        import tensorflow as tf

        # Load preprocessor
        preprocessor = TextPreprocessor.load()

        # Rebuild model architecture
        encoder = Encoder(
            vocab_size=preprocessor.vocab_size,
            embedding_dim=cfg.EMBEDDING_DIM,
            enc_units=cfg.ENCODER_UNITS,
        )
        decoder = Decoder(
            vocab_size=preprocessor.vocab_size,
            embedding_dim=cfg.EMBEDDING_DIM,
            dec_units=cfg.DECODER_UNITS,
        )

        # Restore trained weights from checkpoint
        checkpoint = tf.train.Checkpoint(encoder=encoder, decoder=decoder)
        latest = tf.train.latest_checkpoint(cfg.CHECKPOINT_DIR)
        if latest:
            checkpoint.restore(latest).expect_partial()
            logger.info(f"LSTM model loaded from: {latest}")
        else:
            logger.warning("No LSTM checkpoint found. Train first with: python train_chatbot.py")
            return None

        _lstm_inference = ChatbotInference(encoder, decoder, preprocessor)
        return _lstm_inference

    except Exception as e:
        logger.error(f"Failed to load LSTM model: {e}")
        return None


def _get_lstm_response(user_input: str) -> str:
    """
    Generate a response using the trained LSTM Seq2Seq model.

    Args:
        user_input: User's message.

    Returns:
        Generated response string.
    """
    engine = _load_lstm_model()
    if engine is None:
        return "⚠️ LSTM model not trained yet. Run: python train_chatbot.py"

    try:
        return engine.predict(user_input)
    except Exception as e:
        logger.error(f"LSTM inference error: {e}")
        return f"⚠️ LSTM inference error. Falling back... {_get_offline_response(user_input)}"


# ── Public Interface ──────────────────────────────────────────────────────────

def get_ai_response(
    user_input: str,
    context: list[dict],
    use_openai: bool = True,
    language: str = "en",
    engine_mode: str = "openai",
    image_b64: str = None,
    document_context: str = None
):
    """
    Route to the appropriate AI engine (returns a generator for streaming).

    Args:
        user_input: The user's message.
        context: Conversation history for context-aware replies.
        use_openai: If True, use OpenAI streaming API (legacy flag).
        language: Language code.
        engine_mode: "openai", "lstm", or "offline".

    Yields:
        Chunks of text from the AI.
    """
    if engine_mode == "lstm":
        # Trained LSTM Seq2Seq model (offline, self-trained)
        yield _get_lstm_response(user_input)
    elif engine_mode == "openai" or use_openai:
        yield from _get_openai_response_stream(user_input, context, language, image_b64, document_context)
    else:
        # Offline rule-based mode
        yield _get_offline_response(user_input, language)
