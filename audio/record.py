import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import threading

def record_audio(filename="input.wav", fs=16000):
    print("🎙️ Speak now... Press Enter when you're done...")
    event = threading.Event()
    recording = []

    def _record():
        nonlocal recording
        recording = sd.rec(int(60 * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        event.set()

    t = threading.Thread(target=_record)
    t.start()
    input()
    sd.stop()
    event.wait()
    write(filename, fs, recording)
    print("✅ Recording complete.")

def record_audio_ptt(filename="input.wav", fs=16000):
    import keyboard
    print("🎙️ Listening... recording now!")
    audio = []
    stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16')

    with stream:
        while not keyboard.is_pressed("space"):
            pass
        while keyboard.is_pressed("space"):
            data, _ = stream.read(1024)
            audio.append(data)

    if not audio:
        print("⚠️ No audio detected. Try again.")
        return False

    audio_data = np.concatenate(audio, axis=0)
    write(filename, fs, audio_data)
    print("✅ PTT recording complete.")
    return True
