import psycopg2
from typing import List, Tuple
from datetime import datetime
from utils.config import DB_CONFIG

_pg_conn = None  # persistent connection

def get_pg_connection():
    global _pg_conn
    if _pg_conn is None or _pg_conn.closed:
        _pg_conn = psycopg2.connect(
            **DB_CONFIG
        )
    return _pg_conn

# --- SELECT Wrapper ---
def fetch_similar_messages(
    conn,
    table_name: str,
    embedding: List[float],
    top_k: int = 6
) -> List[Tuple[str, str, str, str, datetime, List[float], float]]:
    """Fetch messages ordered by vector distance, returning metadata and embeddings."""
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, conversation_id, author_role, content, timestamp, embedding,
                   embedding <-> %s::vector AS distance
            FROM {table_name}
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """,
            (embedding, embedding, top_k),
        )
        return cur.fetchall()


def fetch_message_context(
    conn,
    conversation_id: str,
    timestamp: datetime,
    window: int = 1,
) -> List[Tuple[str, str, datetime]]:
    """Return surrounding messages within the same conversation for context."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT author_role, content, timestamp
            FROM messages
            WHERE conversation_id = %s AND timestamp < %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (conversation_id, timestamp, window),
        )
        prev_rows = cur.fetchall()[::-1]

        cur.execute(
            """
            SELECT author_role, content, timestamp
            FROM messages
            WHERE conversation_id = %s AND timestamp >= %s
            ORDER BY timestamp ASC
            LIMIT %s
            """,
            (conversation_id, timestamp, window + 1),
        )
        next_rows = cur.fetchall()

    return prev_rows + next_rows

# --- INSERT Wrapper ---
def insert_message_row(
    conn,
    table_name: str,
    role: str,
    content: str,
    timestamp: datetime,
    embedding: List[float]
):
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO {table_name} (author_role, content, timestamp, embedding)
            VALUES (%s, %s, %s, %s)
        """, (role, content, timestamp, embedding))
    conn.commit()
