"""Helper to retrieve the OpenAI API key from environment variables."""

import os

def get_api_key():
    """Return the API key string or a placeholder."""
    return os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or "your-fallback-key-here"
