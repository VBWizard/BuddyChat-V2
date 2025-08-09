"""Configuration and file paths for BuddyChat."""

import os

# All project data is stored under the repo's ``data`` directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE    = os.path.join(DATA_DIR, "faiss_metadata.pkl")
IDENTITY_FILE    = os.path.join(DATA_DIR, "identity.pkl")

CONTEXT_WINDOW_SIZE = 1000  # how many messages to keep in chat history
SPEAK_OUT = True             # enable TTS by default

# HTTP proxy settings (optional)
PROXY_HOST = None   # e.g. "proxy.example.com"
PROXY_PORT = None   # e.g. 8080

os.makedirs(DATA_DIR, exist_ok=True)

# Chat LLM configuration
# ``CHAT_BASE_URL`` can point to a local OpenAI-compatible server such as
# LM Studio or Ollama. When ``None`` (the default), OpenAI's servers are used.
# CHAT_BASE_URL = "http://localhost:1234/v1"  # e.g. "http://localhost:1234/v1" for LM Studio
CHAT_BASE_URL = "https://api.openai.com/v1"

# CHAT_MODEL = "Psy-Cet-Mytho-ED2-Prose-Crazy-Ultra-Quality-D_AU-29B-IQ4_XS-imat13.gguf"
CHAT_MODEL = "gpt-4o"

DB_CONFIG = {
    'dbname': 'nova_memory',
    'user': 'postgres',
    'password': 'Hi10081113',
    'host': 'localhost',
    'port': 5432,
}

USE_PG_MEMORY = True
