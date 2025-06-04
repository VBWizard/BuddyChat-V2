"""Persistence layer using FAISS for vector similarity search."""

import os
import pickle
import faiss
from datetime import datetime, timezone
import pytz
from tzlocal import get_localzone

# Constants
from utils.config import FAISS_INDEX_FILE, METADATA_FILE, IDENTITY_FILE

local_tz = get_localzone()

def load_memory():
    """Load the FAISS index and associated metadata from disk."""
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(METADATA_FILE):
        print("🔄 Loading FAISS memory from disk...")
        index = faiss.read_index(FAISS_INDEX_FILE)
        with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)
    else:
        print("🚀 No saved memory found. Starting fresh.")
        index = faiss.IndexFlatL2(384)
        metadata = []
    return index, metadata

def update_memory(index, metadata, user_input, assistant_response, model):
    """Add a chat turn to the FAISS index and metadata list."""
    timestamp = datetime.now(timezone.utc).isoformat()
    new_entry = {
        "text": [f"User: {user_input}", f"Assistant: {assistant_response}"],
        "timestamp": timestamp
    }
    # Compute a vector embedding for the combined user+assistant text
    embedding = model.encode([" | ".join(new_entry["text"])], convert_to_numpy=True)
    # Store embedding in FAISS for later similarity search
    index.add(embedding)
    metadata.append(new_entry)
    return new_entry

def save_all(index, metadata, identity_info):
    """Persist the FAISS index, metadata and identity info."""
    print("💾 Saving FAISS memory to disk...")
    # The FAISS index is saved separately from its metadata
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    with open(IDENTITY_FILE, "wb") as f:
        pickle.dump(identity_info, f)

def retrieve_context(index, metadata, query_embedding):
    """Retrieve most relevant prior chat snippets using FAISS."""
    if not metadata:
        return "No prior memory available."

    # Search for embeddings most similar to the current query
    D, indices = index.search(query_embedding, k=8)
    results = []

    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        matched_data = metadata[idx]
        # Convert stored UTC timestamp to local timezone for ordering
        utc_time = datetime.fromisoformat(matched_data["timestamp"]).replace(tzinfo=pytz.utc)
        local_time = utc_time.astimezone(local_tz).timestamp()
        results.append((matched_data, D[0][i], local_time))

    # Sort by distance (smaller is better) and then by recency
    results.sort(key=lambda x: (x[1], -x[2]))
    top_results = results[:6]
    # Format results nicely for the prompt
    return "\n".join([
        f"[{datetime.fromisoformat(res[0]['timestamp']).astimezone(local_tz).strftime('%Y-%m-%d %I:%M %p %Z')}] " +
        " | ".join(res[0]["text"]) for res in top_results
    ])
