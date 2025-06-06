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
