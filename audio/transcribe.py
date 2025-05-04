import openai

def transcribe_audio(client, filename="input.wav"):
    print("🧠 Transcribing audio with Whisper...")
    with open(filename, "rb") as f:
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
            return transcript.text.strip()
        except openai.BadRequestError as e:
            if "audio_too_short" in str(e):
                print("⚠️ Audio file too short. Skipping transcription.")
                return ""
            raise
