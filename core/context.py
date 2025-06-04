from datetime import datetime, timezone
from tzlocal import get_localzone

local_tz = get_localzone()

def dump_memory(metadata):
    print("\n📝 🔍 FAISS Memory Dump:")
    for i, entry in enumerate(metadata):
        utc_time = datetime.fromisoformat(entry["timestamp"]).replace(tzinfo=timezone.utc)
        local_time = utc_time.astimezone(local_tz).strftime("%Y-%m-%d %I:%M %p %Z")
        print(f"{i+1}. [Timestamp: {local_time}] {' | '.join(entry['text'])}")
    print("\n✅ End of FAISS Memory Dump.\n")

def show_context(chat_history, retrieved_text):
    print("\n📜 🔍 Current AI Context:")
    print("\n[Current Conversation Context]:")
    print("\n".join(chat_history))
    print("\n[Previous conversation retrieved from FAISS]:")
    print(retrieved_text)
    print("\n✅ End of Context.\n")

def process_command(cmd, metadata, index, identity_info, chat_history, retrieved_text, speak_out_flag):
    if cmd == "!dump":
        dump_memory(metadata)
        return True, speak_out_flag
    if cmd == "!context":
        show_context(chat_history, retrieved_text)
        return True, speak_out_flag
    if cmd == "!mute":
        print("🔇 Voice output muted.")
        return True, False
    if cmd == "!unmute":
        print("🔊 Voice output unmuted.")
        return True, True
    if cmd == "!help" or cmd == "help":
        print("\n🤖 Buddy Voice Command Help:")
        print("  !help       - Show this help message")
        print("  !dump       - Dump all stored FAISS memory entries")
        print("  !context    - Show current chat history and recalled context")
        print("  !mute       - Disable voice output (TTS off)")
        print("  !unmute     - Enable voice output (TTS on)")
        print("  !ptt        - Enter Push-to-Talk voice mode (hold spacebar to talk)")
        print("  !ptt_off    - Exit Push-to-Talk voice mode")
        print("  exit        - Quit the program\n")
        print("  🧠 Memory powered by FAISS. Voice powered by OpenAI.")
        print("  🐶 Tip: Buddy never drops a byte—he’s loyal like that.\n")
        return True, speak_out_flag
        
    return False, speak_out_flag
