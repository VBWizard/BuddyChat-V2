import psycopg2
import numpy as np
from datetime import datetime
from typing import List
from db.database import (
    get_pg_connection,
    fetch_similar_messages,
    insert_message_row,
    fetch_message_context,
)  # DB helpers

# --- CONFIG ---
EMBEDDING_DIM = 768

# --- Penalty Parameters ---
TOP_K = 100
RELEVANCE_THRESHOLD = 1  # 0.24
SHORT_LENGTH_THRESHOLD = 30
SHORT_PENALTY = 0.05
EMOJI_PENALTY_WEIGHT = 0.02
EMOJIS = ["😲", "😘", "💋", "😍", "😳", "😌"]


def is_meaningful(text: str) -> bool:
    """Filter out short or low-information strings (e.g., emoji-only)."""
    stripped = text.strip()
    if len(stripped) < SHORT_LENGTH_THRESHOLD:
        return False
    alnum = sum(ch.isalnum() for ch in stripped)
    if alnum / max(len(stripped), 1) < 0.3:
        return False
    return True


def mmr(
    query_vec: np.ndarray,
    candidates: List[dict],
    top_n: int,
    lambda_param: float = 0.75,
) -> List[dict]:
    """Maximal Marginal Relevance for diversity."""
    selected = []
    candidates = candidates.copy()
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    for c in candidates:
        emb = c["embedding"]
        c["norm_emb"] = emb / (np.linalg.norm(emb) + 1e-10)
        c["query_sim"] = float(np.dot(c["norm_emb"], q_norm))

    while candidates and len(selected) < top_n:
        if not selected:
            idx = int(np.argmax([c["query_sim"] for c in candidates]))
        else:
            for c in candidates:
                sim_selected = max(
                    float(np.dot(c["norm_emb"], s["norm_emb"])) for s in selected
                )
                c["mmr_score"] = lambda_param * c["query_sim"] - (
                    1 - lambda_param
                ) * sim_selected
            idx = int(np.argmax([c["mmr_score"] for c in candidates]))
        selected.append(candidates.pop(idx))

    return selected

# --- BGE-Compatible Embedding Wrapper ---
def get_embedding(embed_model, role: str, content: str, timestamp: datetime) -> np.ndarray:
    role_formatted = role.capitalize()
    ts_str = timestamp.strftime("%Y-%m-%d %H:%M")
    enriched_text = f"[{ts_str}] {role_formatted}: {content.strip()}"
    prompt = f"Represent this sentence for retrieval: {enriched_text}"
    return embed_model.encode(prompt)

def search_memory(
    conn, embed_model, user_input: str, table_name: str = "Messages", top_n: int = 6
) -> list[str]:
    now = datetime.utcnow()
    query_vec = get_embedding(embed_model, "user", user_input, now)

    raw_results = fetch_similar_messages(
        conn, table_name, query_vec.tolist(), top_k=TOP_K
    )

    candidates = []
    for (
        msg_id,
        convo_id,
        role,
        content,
        ts,
        emb,
        distance,
    ) in raw_results:
        content = content.strip().replace("\n", " ")
        if not is_meaningful(content):
            continue
        length_penalty = SHORT_PENALTY if len(content) < SHORT_LENGTH_THRESHOLD else 0
        emoji_count = sum(content.count(e) for e in EMOJIS)
        emoji_penalty = 0 if len(content) > 100 else EMOJI_PENALTY_WEIGHT * emoji_count
        adjusted = distance + length_penalty + emoji_penalty
        if adjusted > RELEVANCE_THRESHOLD:
            continue
        candidates.append(
            {
                "id": msg_id,
                "conversation_id": convo_id,
                "role": role,
                "content": content,
                "timestamp": ts,
                "embedding": np.array(emb, dtype=float),
                "adjusted": adjusted,
            }
        )

    diversified = mmr(query_vec, candidates, top_n)

    snippets = []
    for c in diversified:
        context_rows = fetch_message_context(
            conn, c["conversation_id"], c["timestamp"], window=1
        )
        lines = [
            f"{r.capitalize()} ({t:%Y-%m-%d %I:%M %p}): {s.strip().replace('\n', ' ')}"
            for r, s, t in context_rows
        ]
        snippet = "\n".join(lines)
        snippets.append(snippet)

    deduped = []
    seen = set()
    for text in snippets:
        key = text.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
    return deduped


# --- Optional Helper ---
def insert_message(conn, embed_model, role: str, content: str, table_name: str = "BuddyChatMessages"):
    """
    Insert a new message into BuddyChatMessages with embedding.
    """
    timestamp = datetime.utcnow()
    embedding = get_embedding(embed_model, role, content, timestamp).tolist()
    insert_message_row(conn, table_name, role, content, timestamp, embedding)
