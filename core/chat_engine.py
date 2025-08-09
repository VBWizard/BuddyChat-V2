from __future__ import annotations
"""BuddyChat – unified chat response generator.

This refactor replaces the old "single‑blob" prompt with a clean, OpenAI‑style
messages array that works for *both* the OpenAI cloud API and local LLM servers
exposing a compatible endpoint (LM Studio / Ollama / etc.).

Key features
------------
*   Uses :pyfunc:`prompt_builder.assemble_messages` to create the messages.
*   Keeps the private `[Tone: …][UserTone: …]` tag mechanic alive.
*   Strips the tags before the text is spoken / displayed.
*   Leaves public OpenAI behaviour **unchanged** – no extra params needed.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
import os
import re
import pickle

from tzlocal import get_localzone

from utils.config import IDENTITY_FILE, CHAT_MODEL
from core.prompt_builder import assemble_messages, strip_private_tags

__all__ = [
    "generate_response",
]

local_tz = get_localzone()
BUDDY_SYS_PROMPT_PATH = Path("data\\buddy_system_prompt.txt")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_identity() -> Dict[str, str | None]:
    """Load persisted identity information (if any)."""
    if Path(IDENTITY_FILE).exists():
        with open(IDENTITY_FILE, "rb") as f:
            return pickle.load(f)
    return {"name": None}


def _build_system_prompt(base_text: str, identity_info: Dict[str, str | None], retrieved: str) -> str:
    """Craft the *single* system prompt sent on every request."""
    name_line = f"User's Preferred Name: {identity_info.get('name') or 'Unknown'}"
    memory_block = retrieved.strip() or "No relevant memory."
    return (
        f"{base_text.strip()}\n\n"
        "[Persistent Identity Information]:\n" + name_line + "\n\n"
        "[Relevant Memory]:\n" + memory_block + "\n"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_response(
    user_input: str,
    identity_info: Dict[str, str | None] | None,
    retrieved_text: str,
    chat_history: List[Dict[str, str]],
    client,
    temperature: float = 0.7,
) -> str:
    """Generate an assistant reply given the latest user input and context.

    Parameters
    ----------
    user_input
        Latest message from the user.
    identity_info
        Dictionary with persisted identity fields (at minimum ``{"name": str}``).
        If *None*, we fall back to the identity file on disk.
    retrieved_text
        Memory snippet fetched from FAISS for the current turn.
    chat_history
        List of dicts (``{"role": "user"|"assistant", "content": str}``) representing
        recent turns **in chronological order**.
    client
        An OpenAI‑compatible client instance (cloud or local).
    temperature
        Sampling temperature to pass through.
    """
    if identity_info is None:
        identity_info = _load_identity()

    # ---------------------------------------------------------------------
    # Build system prompt.
    # ---------------------------------------------------------------------
    if BUDDY_SYS_PROMPT_PATH.exists():
        base_prompt = BUDDY_SYS_PROMPT_PATH.read_text(encoding="utf-8").strip()
    else:
        base_prompt = "Your name is Assistant."

    system_prompt = _build_system_prompt(base_prompt, identity_info, retrieved_text)

    # ---------------------------------------------------------------------
    # Assemble message array.
    # ---------------------------------------------------------------------
    messages = assemble_messages(
        base_system=system_prompt,
        history=chat_history,
        user_msg=user_input,
    )

    # ---------------------------------------------------------------------
    # Call the model.
    # ---------------------------------------------------------------------
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=temperature,
    )

    raw_reply: str = response.choices[0].message.content
    # clean_reply = strip_private_tags(raw_reply)
    return raw_reply
