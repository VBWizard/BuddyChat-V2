import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FAISS_INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_FILE    = os.path.join(DATA_DIR, "faiss_metadata.pkl")
IDENTITY_FILE    = os.path.join(DATA_DIR, "identity.pkl")

CONTEXT_WINDOW_SIZE = 1000
SPEAK_OUT = True

os.makedirs(DATA_DIR, exist_ok=True)
