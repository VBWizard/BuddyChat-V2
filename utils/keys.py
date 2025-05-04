import os

def get_api_key():
    return os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY") or "your-fallback-key-here"
