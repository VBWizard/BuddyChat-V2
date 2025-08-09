import keyboard
from datetime import datetime
from utils.config import CONTEXT_WINDOW_SIZE
from tzlocal import get_localzone
from audio.record import record_audio_ptt
from audio.transcribe import transcribe_audio
from core.chat_turn import handle_chat_turn

local_tz = get_localzone()

def enter_ptt_mode(index, metadata, identity_info, embed_model, openai_client, chat_client, chat_history, speak_out=True):
    """Interactive push-to-talk loop using the microphone."""
    print("🎙️ PTT Mode ON — Hold spacebar to speak. Release to stop. Press Enter to send, or type 'cancel'. Type !ptt_off to exit.")

    while True:
        print("🕒 Waiting for spacebar press to begin recording... (Press Esc to exit)")
        while True:
            event = keyboard.read_event()
            if event.name == "esc":
                print("📴 Exiting PTT Mode.")
                return
            elif event.name == "space" and event.event_type == "down":
                break

        print("🎙️ Recording... release spacebar to stop.")
        if not record_audio_ptt():
            continue

        user_transcript = transcribe_audio(openai_client)
        print(f"👤 Transcribed Input: {user_transcript}")
        decision = input("✅ Press Enter to send, or type 'cancel' to discard: ").strip().lower()
        if decision == "cancel":
            print("❌ Input discarded.")
            continue

        handle_chat_turn(user_transcript, embed_model, index, metadata, identity_info, chat_client, chat_history, speak_out, openai_client)
