"""
memory/conversation_memory.py  –  Conversation Memory
========================================================
Stores conversation history and builds context windows
for context-aware AI responses.

Features:
- Rolling window (keeps last N turns to avoid token overflow)
- Persistent storage to JSON (survives app restarts)
- Clear and reset support
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

MEMORY_FILE = Path("memory/conversation_log.json")


class ConversationMemory:
    """
    Manages conversation history for context-aware chatbot responses.

    Keeps a rolling window of recent turns to feed into the AI model.
    Also persists the full history to disk for review/export.
    """

    def __init__(self, max_turns: int = 20):
        """
        Args:
            max_turns: Maximum number of conversation turns to keep in context.
                       Each turn = 1 user message + 1 assistant reply.
        """
        self.max_turns = max_turns
        self._history: list[dict] = []   # Full session history
        self._load_from_disk()           # Load existing conversations if any

    # ── Public API ────────────────────────────────────────────────────────────

    def add_turn(self, user: str, assistant: str, session_id: str = "default") -> None:
        """
        Store a user + assistant exchange.

        Args:
            user: User's message text.
            assistant: AI's response text.
            session_id: The ID of the current chat session.
        """
        turn = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "assistant": assistant,
        }
        self._history.append(turn)
        self._save_to_disk()
        logger.debug(f"Memory: stored turn #{len(self._history)} in session {session_id}")

    def build_context(self, current_input: str, session_id: str = "default") -> list[dict]:
        """
        Build the context window for the AI model.

        Returns the last `max_turns` exchanges formatted as OpenAI
        message objects: [{"role": "user"|"assistant", "content": str}]

        Args:
            current_input: The new user message (NOT included — caller adds it).
            session_id: The active session ID to filter history by.

        Returns:
            List of message dicts for the AI API.
        """
        # Filter history by session_id before taking the most recent turns
        session_history = [t for t in self._history if t.get("session_id", "default") == session_id]
        recent = session_history[-self.max_turns:]

        context = []
        for turn in recent:
            context.append({"role": "user",      "content": turn["user"]})
            context.append({"role": "assistant",  "content": turn["assistant"]})

        return context

    def get_summary(self) -> str:
        """Return a readable summary of recent conversation turns."""
        if not self._history:
            return "No conversation history yet."

        lines = []
        for i, turn in enumerate(self._history[-5:], 1):   # Last 5 turns
            ts = turn["timestamp"][:16].replace("T", " ")
            lines.append(f"[{ts}] You: {turn['user'][:60]}...")
            lines.append(f"         Bot: {turn['assistant'][:60]}...")

        return "\n".join(lines)

    def clear(self) -> None:
        """Reset in-memory history and delete the persistent file."""
        self._history = []
        if MEMORY_FILE.exists():
            MEMORY_FILE.unlink()
        logger.info("Conversation memory cleared.")

    def delete_session(self, session_id: str) -> None:
        """Delete all turns associated with a specific session ID."""
        original_length = len(self._history)
        self._history = [t for t in self._history if t.get("session_id", "default") != session_id]
        if len(self._history) < original_length:
            self._save_to_disk()
            logger.info(f"Deleted session {session_id} from memory.")

    @property
    def turn_count(self) -> int:
        """Number of conversation turns stored."""
        return len(self._history)

    # ── Persistence ──────────────────────────────────────────────────────────

    def _save_to_disk(self) -> None:
        """Save full conversation history to JSON file."""
        try:
            MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Could not save memory to disk: {e}")

    def _load_from_disk(self) -> None:
        """Load existing conversation history from JSON file (if it exists)."""
        if not MEMORY_FILE.exists():
            return
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                self._history = json.load(f)
            logger.info(f"Loaded {len(self._history)} turns from disk.")
        except Exception as e:
            logger.warning(f"Could not load memory from disk: {e}")
            self._history = []
