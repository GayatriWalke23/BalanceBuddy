import sounddevice as sd
import numpy as np

def audio_callback(indata, frames, time, status):
    if status:
        print(f'Error: {status}')
    volume_norm = np.linalg.norm(indata) * 10
    print(f'Volume: {int(volume_norm)}')

try:
    print("Testing microphone... Speak into your microphone.")
    print("Press Ctrl+C to stop.")
    with sd.InputStream(callback=audio_callback,
                       channels=1,
                       samplerate=16000):
        sd.sleep(1000000)
except KeyboardInterrupt:
    print("\nStopping...")
except Exception as e:
    print(f"\nError: {str(e)}")
