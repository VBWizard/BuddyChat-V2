from datetime import datetime
from core.memory import retrieve_context, update_memory
from core.chat_engine import generate_response
from core.prompt_builder import strip_private_tags
from audio.tts import speak_response
from utils.config import CONTEXT_WINDOW_SIZE
from tzlocal import get_localzone
import re
import threading
from core.pg_memory import search_memory, insert_message
from db.database import get_pg_connection
from utils.config import USE_PG_MEMORY  # make sure this is defined in your config
import openai


local_tz = get_localzone()

from core.pg_memory import search_memory, insert_message
from db.database import get_pg_connection
from utils.config import USE_PG_MEMORY
from audio.tts import speak_response
from core.memory import retrieve_context  # FAISS fallback

_pg_conn = None  # internal static var

def handle_chat_turn(user_input, embed_model, index, metadata, identity_info, chat_client: openai.OpenAI, chat_history, speak_out=True, openai_client=None):
    global _pg_conn

    if USE_PG_MEMORY:
        if _pg_conn is None:
            _pg_conn = get_pg_connection()

        context = search_memory(_pg_conn, embed_model, user_input, table_name="Messages")
    else:
        embedding = embed_model.encode([user_input])
        context = retrieve_context(index, metadata, embedding)

    # Convert context to plain text block
    assistant_response = generate_response(
        user_input=user_input,
        identity_info=identity_info,
        retrieved_text="\n".join(context),  # context is our memory list
        chat_history=chat_history,
        client=chat_client,
    )

    if USE_PG_MEMORY:
        # Persist this turn into PG index for future recall
#        insert_message(_pg_conn, embed_model, "user", user_input, table_name="BuddyChatMessages")
#        insert_message(_pg_conn, embed_model, "assistant", assistant_response, table_name="BuddyChatMessages")
        pass
    else:
        # Persist this turn into the FAISS index for future recall
        update_memory(index, metadata, user_input, assistant_response, embed_model)
    print("\n🤖 Assistant Response:")
    print(f"Assistant: {assistant_response}")
    print("-----------------------------------------------------------------------")
    if speak_out:
        # Extract [Tone: ...] if present
        tone_match = re.match(r"\[Tone:(.*?)\]\s*", assistant_response)
        if tone_match:
            tts_instructions = tone_match.group(1).strip()
            assistant_response = re.sub(r"^\[Tone:.*?\]\s*", "", assistant_response)
        else:
            tts_instructions = "Speak naturally."

        # Run text-to-speech in a background thread so the REPL stays responsive
        import threading
        threading.Thread(target=speak_response, args=(assistant_response,openai_client, tts_instructions), daemon=True).start()

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": assistant_response})

    return assistant_response
