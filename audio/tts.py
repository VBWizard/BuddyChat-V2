"""Functions for converting text responses to speech."""

import pygame
import io

def speak_response(text, client, instructions):
    """Play the assistant's text reply using OpenAI text-to-speech."""
    print(f"🗣️ Generating voice with OpenAI TTS (instructions: {instructions})...")

    # Request audio from OpenAI's TTS endpoint
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="ash",  # voice name
        input=text,
        instructions=instructions
    )

    pygame.mixer.init()
    audio_data = io.BytesIO(response.content)
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()
    # Block until the audio has finished playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
