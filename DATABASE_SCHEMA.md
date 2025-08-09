# Database Schema – Nova Memory System

## Table: conversations
Stores metadata for each conversation.

| Column       | Type      | Description                         |
|--------------|-----------|-------------------------------------|
| id           | uuid (PK) | Unique conversation identifier      |
| title        | text      | Conversation title                  |
| create_time  | timestamp | Creation time (UTC)                 |
| update_time  | timestamp | Last update time (UTC)               |

---

## Table: messages
Stores individual messages within conversations, along with embeddings for semantic search.

| Column           | Type           | Description                                    |
|------------------|----------------|------------------------------------------------|
| id               | uuid (PK)      | Unique message identifier                      |
| conversation_id  | uuid (FK)      | Links to `conversations.id`                    |
| parent_id        | uuid (FK)      | Links to `messages.id` for threaded structure  |
| author_role      | text           | Role of author (e.g., 'user', 'assistant')     |
| content          | text           | Message text                                   |
| timestamp        | timestamp      | Time message was created (UTC)                 |
| model_slug       | text           | Identifier for model used                      |
| metadata         | jsonb          | Additional metadata                            |
| raw_json         | jsonb          | Original message JSON                          |
| end_turn         | boolean        | Indicates if the turn ended                    |
| weight           | double         | Weight score                                   |
| recipient        | text           | Recipient of the message                       |
| embedding        | vector(768)    | Semantic embedding for vector search           |

### Indexes:
- **Primary key:** `messages_pkey (id)`
- **Foreign keys:**  
  - `conversation_id → conversations.id` (cascade on delete)  
  - `parent_id → messages.id` (set null on delete)  
- **Indexes:**  
  - `idx_messages_author (author_role)`  
  - `idx_messages_convo (conversation_id)`  
  - `idx_messages_model (model_slug)`  
  - `idx_messages_parent (parent_id)`  
  - `idx_messages_timestamp (timestamp)`  
  - `idx_unembedded_messages` – messages where `embedding IS NULL AND content IS NOT NULL`
