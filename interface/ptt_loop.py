"""Push-to-talk loop for voice interaction."""

import keyboard
from datetime import datetime
from utils.config import CONTEXT_WINDOW_SIZE
from tzlocal import get_localzone
from audio.record import record_audio_ptt
from audio.transcribe import transcribe_audio
from audio.tts import speak_response
import re

local_tz = get_localzone()

def enter_ptt_mode(index, metadata, identity_info, model, client, chat_history, speak_out=True):
    """Interactive push-to-talk loop using the microphone."""
    print("🎙️ PTT Mode ON — Hold spacebar to speak. Release to stop. Press Enter to send, or type 'cancel'. Type !ptt_off to exit.")

    while True:
        # Wait for the user to hold the spacebar to start recording
        print("🕒 Waiting for spacebar press to begin recording... (Press Esc to exit)")
        while True:
            event = keyboard.read_event()
            if event.name == "esc":
                print("📴 Exiting PTT Mode.")
                return
            elif event.name == "space" and event.event_type == "down":
                break

        print("🎙️ Recording... release spacebar to stop.")
        # Record microphone input while spacebar is held
        if not record_audio_ptt():
            continue

        # Convert recorded audio to text using OpenAI Whisper API
        user_transcript = transcribe_audio(client)
        print(f"👤 Transcribed Input: {user_transcript}")
        decision = input("✅ Press Enter to send, or type 'cancel' to discard: ").strip().lower()
        if decision == "cancel":
            print("❌ Input discarded.")
            continue

        from core.memory import retrieve_context, update_memory
        from core.chat_engine import generate_response

        # Retrieve relevant past conversation to provide context
        embedding = model.encode([user_transcript], convert_to_numpy=True)
        retrieved_text = retrieve_context(index, metadata, embedding)
        response = generate_response(user_transcript, identity_info, retrieved_text, chat_history, client)

        print("🔍 FAISS Retrieved Memory:")
        # print(retrieved_text)
        print("🤖 Assistant Response:")
        print(f"Assistant: {response}")
        print("-----------------------------------------------------------------------")

        if speak_out:
            # Extract [Tone: ...] if present
            tone_match = re.match(r"\[Tone:(.*?)\]\s*", response)
            if tone_match:
                tts_instructions = tone_match.group(1).strip()
                response = re.sub(r"^\[Tone:.*?\]\s*", "", response)
            else:
                tts_instructions = "Speak naturally."
            # Play the response audio asynchronously
            import threading
            threading.Thread(target=speak_response, args=(response,client,tts_instructions), daemon=True).start()

        now_str = datetime.now(local_tz).strftime("%Y-%m-%d %I:%M %p %Z")
        # Maintain chat history window for later context
        chat_history.append(f"[{now_str}] User: {user_transcript}")
        chat_history.append(f"[{now_str}] Assistant: {response}")
        chat_history[:] = chat_history[-CONTEXT_WINDOW_SIZE:]
        update_memory(index, metadata, user_transcript, response, model)
