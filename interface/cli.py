"""Command-line interface for interacting with BuddyChat."""

from core.memory import load_memory, update_memory, retrieve_context, save_all
from core.chat_engine import generate_response, load_identity
from interface.ptt_loop import enter_ptt_mode
from audio.tts import speak_response
from utils.config import CONTEXT_WINDOW_SIZE, SPEAK_OUT
from utils.network import get_proxy_client
from tzlocal import get_localzone
from datetime import datetime
import openai
from utils.keys import get_api_key
from core.context import process_command
import re

def run():
    """Main REPL loop for text-based interaction."""
    # Import here so heavy dependency loads only when needed
    from sentence_transformers import SentenceTransformer

    speak_out_flag = SPEAK_OUT  # Copy default setting
    chat_history = []
    retrieved_text = ""
    local_tz = get_localzone()

    # Load saved FAISS index and identity information
    index, metadata = load_memory()
    identity_info = load_identity()
    # Embedding model used for similarity search
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    # OpenAI client handles chat and speech API calls
    client = openai.OpenAI(api_key=get_api_key(),
                           http_client=get_proxy_client())

    print("\n🚀 FAISS Memory Chat Started!")

    print("Talk to the chatbot, type !help to see optional commands, or type 'exit' to quit.\n")
    while True:
        user_input = input("👤 User: ")
        # Allow special commands prefixed with ! to be executed
        is_cmd, speak_out_flag  = process_command(user_input.lower(), metadata, index, identity_info, chat_history, retrieved_text, SPEAK_OUT)
        if is_cmd:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "!ptt":
            enter_ptt_mode(index, metadata, identity_info, model, client, chat_history, speak_out=SPEAK_OUT )
            continue

        embedding = model.encode([user_input], convert_to_numpy=True)
        # Recall relevant past conversation using vector search
        retrieved_text = retrieve_context(index, metadata, embedding)
        response = generate_response(user_input, identity_info, retrieved_text, chat_history, client)

        print("\n🔍 FAISS Retrieved Memory:")
        # print(retrieved_text)
        print("\n🤖 Assistant Response:")
        print(f"Assistant: {response}")
        print("-----------------------------------------------------------------------")

        if speak_out_flag:
            # Extract [Tone: ...] if present
            tone_match = re.match(r"\[Tone:(.*?)\]\s*", response)
            if tone_match:
                tts_instructions = tone_match.group(1).strip()
                response = re.sub(r"^\[Tone:.*?\]\s*", "", response)
            else:
                tts_instructions = "Speak naturally."

            # Run text-to-speech in a background thread so the REPL stays responsive
            import threading
            threading.Thread(target=speak_response, args=(response,client, tts_instructions), daemon=True).start()

        now_str = datetime.now(local_tz).strftime("%Y-%m-%d %I:%M %p %Z")
        # Keep a rolling window of conversation for context
        chat_history.append(f"[{now_str}] User: {user_input}")
        chat_history.append(f"[{now_str}] Assistant: {response}")
        chat_history = chat_history[-CONTEXT_WINDOW_SIZE:]

        # Persist this turn into the FAISS index for future recall
        update_memory(index, metadata, user_input, response, model)

        if "my name is" in user_input.lower():
            # Simple extraction of the user's preferred name for personalization
            identity_info = {
                "name": user_input.split("my name is")[-1].strip(),
                "timestamp": datetime.now().isoformat()
            }

    # Persist all data when the session ends
    save_all(index, metadata, identity_info)
