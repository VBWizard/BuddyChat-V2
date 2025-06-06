"""Audio recording utilities used for voice input."""

import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import threading

def record_audio_ptt(filename="input.wav", fs=16000):
    """Record while spacebar is held (push-to-talk)."""
    import keyboard
    print("🎙️ Listening... recording now!")
    audio = []
    stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16')

    with stream:
        # Wait until spacebar is pressed
        while not keyboard.is_pressed("space"):
            pass
        # Continuously read audio frames while spacebar is held down
        while keyboard.is_pressed("space"):
            data, _ = stream.read(1024)
            audio.append(data)

    if not audio:
        # User released the key before speaking
        print("⚠️ No audio detected. Try again.")
        return False

    audio_data = np.concatenate(audio, axis=0)
    write(filename, fs, audio_data)
    print("✅ PTT recording complete.")
    return True
