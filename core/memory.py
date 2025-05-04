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
    timestamp = datetime.now(timezone.utc).isoformat()
    new_entry = {
        "text": [f"User: {user_input}", f"Assistant: {assistant_response}"],
        "timestamp": timestamp
    }
    embedding = model.encode([" | ".join(new_entry["text"])], convert_to_numpy=True)
    index.add(embedding)
    metadata.append(new_entry)
    return new_entry

def save_all(index, metadata, identity_info):
    print("💾 Saving FAISS memory to disk...")
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    with open(IDENTITY_FILE, "wb") as f:
        pickle.dump(identity_info, f)

def retrieve_context(index, metadata, query_embedding):
    if not metadata:
        return "No prior memory available."

    D, indices = index.search(query_embedding, k=8)
    results = []

    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        matched_data = metadata[idx]
        utc_time = datetime.fromisoformat(matched_data["timestamp"]).replace(tzinfo=pytz.utc)
        local_time = utc_time.astimezone(local_tz).timestamp()
        results.append((matched_data, D[0][i], local_time))

    results.sort(key=lambda x: (x[1], -x[2]))
    top_results = results[:6]
    return "\n".join([
        f"[{datetime.fromisoformat(res[0]['timestamp']).astimezone(local_tz).strftime('%Y-%m-%d %I:%M %p %Z')}] " +
        " | ".join(res[0]["text"]) for res in top_results
    ])
