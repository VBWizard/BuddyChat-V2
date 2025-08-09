from core.memory import load_memory, save_all
from core.chat_engine import _load_identity
from interface.ptt_loop import enter_ptt_mode
from audio.tts import speak_response
from utils.config import CONTEXT_WINDOW_SIZE, SPEAK_OUT, USE_PG_MEMORY
from utils.llm import get_chat_client, get_openai_client
from tzlocal import get_localzone
from datetime import datetime
from core.context import process_command
from utils.config import IDENTITY_FILE, CHAT_MODEL
from core.chat_turn import handle_chat_turn
def run():
    """Main REPL loop for text-based interaction."""
    from sentence_transformers import SentenceTransformer

    speak_out_flag = SPEAK_OUT
    chat_history = []
    retrieved_text = ""

    local_tz = get_localzone()
    index, metadata = load_memory()
    identity_info = _load_identity()
    if USE_PG_MEMORY:
        embed_model = SentenceTransformer("BAAI/bge-base-en-v1.5")
    else:
        embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    openai_client = get_openai_client()
    chat_client = get_chat_client()

    print("\n🚀 FAISS Memory Chat Started!")
    print(f"Using {CHAT_MODEL} for chat completions")
    print("Talk to the chatbot, type !help to see optional commands, or type 'exit' to quit.\n")

    while True:
        user_input = input("👤 User: ")
        is_cmd, speak_out_flag = process_command(
            user_input.lower(), metadata, index, identity_info, chat_history, retrieved_text, SPEAK_OUT
        )
        if is_cmd:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "!ptt":
            enter_ptt_mode(index, metadata, identity_info, embed_model, openai_client, chat_client, chat_history, speak_out=SPEAK_OUT)
            continue

        handle_chat_turn(
            user_input,
            embed_model,
            index,
            metadata,
            identity_info,
            chat_client,
            chat_history,
            speak_out_flag,
            openai_client
        )

        if "my name is" in user_input.lower():
            identity_info = {
                "name": user_input.split("my name is")[-1].strip(),
                "timestamp": datetime.now().isoformat()
            }

    save_all(index, metadata, identity_info)
