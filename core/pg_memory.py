import psycopg2
import numpy as np
from datetime import datetime
from typing import List
from db.database import get_pg_connection, fetch_similar_messages, insert_message_row  # DB helpers

# --- CONFIG ---
EMBEDDING_DIM = 768

# --- Penalty Parameters ---
TOP_K = 100
RELEVANCE_THRESHOLD = 1 #0.24
SHORT_LENGTH_THRESHOLD = 30
SHORT_PENALTY = 0.05
EMOJI_PENALTY_WEIGHT = 0.02
EMOJIS = ["😲", "😘", "💋", "😍", "😳", "😌"]

# --- BGE-Compatible Embedding Wrapper ---
def get_embedding(embed_model, role: str, content: str, timestamp: datetime) -> np.ndarray:
    """
    Format message according to BGE embedding best practices, then embed.
    """
    role_formatted = role.capitalize()
    ts_str = timestamp.strftime("%Y-%m-%d %H:%M")
    enriched_text = f"[{ts_str}] {role_formatted}: {content.strip()}"
    prompt = f"Represent this sentence for retrieval: {enriched_text}"
    return embed_model.encode(prompt)


# --- Main Memory Search ---
def get_embedding(embed_model, role: str, content: str, timestamp: datetime) -> np.ndarray:
    role_formatted = role.capitalize()
    ts_str = timestamp.strftime("%Y-%m-%d %H:%M")
    enriched_text = f"[{ts_str}] {role_formatted}: {content.strip()}"
    prompt = f"Represent this sentence for retrieval: {enriched_text}"
    return embed_model.encode(prompt)

def search_memory(conn, embed_model, user_input: str, table_name: str = "Messages", top_n: int = 6) -> list[str]:
    now = datetime.utcnow()
    query_embedding = get_embedding(embed_model, "user", user_input, now).tolist()

    raw_results = fetch_similar_messages(conn, table_name, query_embedding, top_k=TOP_K)

    scored_results = []

    for role, content, ts, distance in raw_results:
        content = content.strip().replace("\n", " ")

        length_penalty = SHORT_PENALTY if len(content) < SHORT_LENGTH_THRESHOLD else 0
        emoji_count = sum(content.count(e) for e in EMOJIS)
        emoji_penalty = 0 if len(content) > 100 else EMOJI_PENALTY_WEIGHT * emoji_count
        adjusted = distance + length_penalty + emoji_penalty

        if adjusted > RELEVANCE_THRESHOLD:
            continue

        formatted = f"{role.capitalize()} ({ts:%Y-%m-%d %I:%M %p}): {content}"
        scored_results.append((adjusted, formatted))

    # Sort by adjusted score (lower is better) and return top N
    scored_results.sort(key=lambda x: x[0])
    # Deduplicate results
    seen = set()
    deduped = []
    for _, text in scored_results:
        key = text.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
        if len(deduped) >= top_n:
            break

    return deduped


# --- Optional Helper ---
def insert_message(conn, embed_model, role: str, content: str, table_name: str = "BuddyChatMessages"):
    """
    Insert a new message into BuddyChatMessages with embedding.
    """
    timestamp = datetime.utcnow()
    embedding = get_embedding(embed_model, role, content, timestamp).tolist()
    insert_message_row(conn, table_name, role, content, timestamp, embedding)
