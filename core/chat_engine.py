"""Utilities for generating chat responses using OpenAI's API."""

import os
from datetime import datetime
from utils.config import IDENTITY_FILE
from tzlocal import get_localzone
import pickle

local_tz = get_localzone()

def load_identity():
    """Load persisted identity information if available."""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "rb") as f:
            return pickle.load(f)
    return {"name": None}

def generate_response(user_input, identity_info, retrieved_text, chat_history, client):
    """Generate a chat reply from OpenAI based on history and memory.

    Args:
        user_input (str): Latest message from the user.
        identity_info (dict): Stored user identity information.
        retrieved_text (str): Prior conversation pulled from FAISS.
        chat_history (list[str]): Recent chat turns for context.
        client (openai.OpenAI): OpenAI client used for API calls.

    Returns:
        str: Assistant response text including optional tone tags.
    """

    # System prompt can be overridden by a text file for easy tweaking
    default_prompt = "Your name is Buddy."
    if os.path.exists("buddy_system_prompt.txt"):
        with open("buddy_system_prompt.txt", "r", encoding="utf-8") as f:
            default_prompt = f.read().strip()

    current_time = datetime.now(local_tz).strftime("%Y-%m-%d %I:%M %p %Z")
    identity_text = f"{identity_info['name']} (User's Preferred Name)" if identity_info["name"] else "No stored name yet."

    # Build a detailed prompt including chat history and recalled memory
    ai_prompt = f"""
[INTERNAL INSTRUCTION]: Before your response, include two private tags in square brackets:
1. A short tone tag: [Tone: gentle], [Tone: confident and upbeat], etc. This tag will not be shown or spoken aloud—it is used to control how your voice will sound via OpenAI's TTS engine.
Make sure your tone tag is accurate for the emotional delivery you want to achieve, since it directly affects how you are heard.
2. A short user tone tag: [UserTone: ...] — your best guess at the user's emotional tone based on their message. This will not be shown to the user or spoken aloud. Use your judgment and context.


[Current Conversation Context]:
{"\n".join(chat_history)}

[Previous conversation retrieved from FAISS]:
{retrieved_text}

[Persistent Identity Information]:
{identity_text}

[User’s new message] (Current Time: {current_time}):
{user_input}

[Task]:
Use the conversation context to continue the discussion naturally.
Reference retrieved memory only if relevant, or if you want to take the conversation in a new direction.
Ensure responses feel continuous and time-aware.
"""

    # Send the full prompt to GPT-4o to get the assistant's reply
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"{default_prompt} You are an AI assistant with memory."},
            {"role": "user", "content": ai_prompt}
        ]
    )
    return response.choices[0].message.content
