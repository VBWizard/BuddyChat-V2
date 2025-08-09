from __future__ import annotations
"""Unified prompt utilities for BuddyChat.

Builds an OpenAI‑style *messages* array that can be sent unchanged to the
public OpenAI Chat API **and** to local servers that expose a compatible
endpoint (LM Studio, Ollama, etc.).

This revision restores the **full internal tag instruction block** so the
model reliably prepends `[Tone: …][UserTone: …]` tags in every reply.
"""

from typing import Dict, List, Tuple
import re

Role = str  # Literal["system", "user", "assistant"] – kept flexible

# ---------------------------------------------------------------------------
# Internal‑tag directive (added verbatim to the system prompt)
# ---------------------------------------------------------------------------

INTERNAL_TAG_INSTRUCTION = (
    "[INTERNAL INSTRUCTION]: Before your response, include two private tags in square brackets:\n"
    "1. A short tone tag: [Tone: gentle], [Tone: confident and upbeat], etc. "
    "this tag is used to control how your voice will sound via OpenAI's TTS engine.\n"
    "Make sure your tone tag is accurate for the emotional delivery you want to achieve, since it directly affects how you are heard.\n"
    "2. A short user tone tag: [UserTone: ...] — your best guess at the user's emotional tone based on their message. "
    "Use your judgment and context.\n"
)

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalise_history_item(entry: object) -> Dict[Role, str]:
    """Coerce a *history* element into the `{role, content}` dict shape.

    Accepted formats:
    * `{"role": "user", "content": "hi"}` – passthrough.
    * `( "assistant", "hello" )` – 2‑tuple.
    * plain string – assumed to be a *user* message.
    """
    if isinstance(entry, dict):
        role = entry.get("role", "user")
        content = entry.get("content", "")
    elif isinstance(entry, tuple) and len(entry) == 2:
        role, content = entry
    else:  # fallback – treat as user text
        role, content = "user", str(entry)
    return {"role": str(role), "content": str(content)}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assemble_messages(
    base_system: str,
    history: List[object],  # accepts dicts, tuples, or strings
    user_msg: str,
    max_history: int = 12,
) -> List[Dict[Role, str]]:
    """Return a list of role‑segmented chat messages ready for the Chat API."""

    system_prompt = (
        base_system.strip()
        + "\n\n"
        + INTERNAL_TAG_INSTRUCTION
    )

    # Begin with system directive
    messages: List[Dict[Role, str]] = [{"role": "system", "content": system_prompt}]

    # Append the most recent history items (already normalised)
    for entry in history[-max_history:]:
        messages.append(_normalise_history_item(entry))

    # Finally the new user message
    messages.append({"role": "user", "content": user_msg.strip()})

    return messages


# ---------------------------------------------------------------------------
# Private‑tag stripper – call this *after* the model responds
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"^\s*\[Tone:[^\]]*]\s*\[UserTone:[^\]]*]\s*", re.I)

def strip_private_tags(text: str) -> str:
    """Remove leading `[Tone: …][UserTone: …]` tags before display/TTS."""
    return _TAG_RE.sub("", text, count=1).lstrip()



# --------‑‑‑ Transport‑agnostic send helper ---------------------------------

_CLIENTS: dict[str, openai.OpenAI] | None = None


def _clients() -> dict[str, openai.OpenAI]:
    """Initialise & cache OpenAI client objects for each backend."""
    global _CLIENTS
    if _CLIENTS is not None:
        return _CLIENTS

    _CLIENTS = {
        "openai": openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")),
        # Local OAI‑compatible server: LM Studio default URL / key
        "local": openai.OpenAI(base_url=os.getenv("LOCAL_OAI_BASE", "http://localhost:11434/v1"),
                                api_key="local"),
    }
    return _CLIENTS


def chat(
    provider: str,
    messages: List[Message],
    *,
    model: str,
    temperature: float = 0.7,
    **kwargs,
) -> str:
    """Send *messages* to the chosen provider and return a cleaned reply.

    Extra **kwargs are passed straight through to `client.chat.completions.create`.
    """
    client = _clients()[provider]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
    raw = response.choices[0].message.content
    return strip_private_tags(raw)
