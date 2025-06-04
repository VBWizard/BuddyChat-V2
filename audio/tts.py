import pygame
import io

def speak_response(text, client, instructions):
    print(f"🗣️ Generating voice with OpenAI TTS (instructions: {instructions})...")

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="ash", # verse
        input=text,
        instructions=instructions
    )

    pygame.mixer.init()
    audio_data = io.BytesIO(response.content)
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
