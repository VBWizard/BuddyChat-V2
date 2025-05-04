import pygame
import io

def speak_response(text, client):
    print("🗣️ Generating voice with OpenAI TTS...")

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="verse",
        input=text,
        instructions="Sound like my best friend."
    )

    pygame.mixer.init()
    audio_data = io.BytesIO(response.content)
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
