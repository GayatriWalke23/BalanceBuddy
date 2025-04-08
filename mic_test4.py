import pyaudio
import wave
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "test_recording.wav"
DEVICE_INDEX = 1  # MacBook Pro Microphone

def record_audio():
    p = pyaudio.PyAudio()
    
    # Open stream with specific device
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   input_device_index=DEVICE_INDEX,
                   frames_per_buffer=CHUNK)

    print("\nRecording for 3 seconds...")
    print("Please speak into your MacBook Pro microphone...")
    
    frames = []
    
    # Record for RECORD_SECONDS
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        # Print a dot every second
        if i % int(RATE / CHUNK) == 0:
            print(".", end="", flush=True)
    
    print("\nFinished recording!")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded data as a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    print(f"\nSaved recording to {WAVE_OUTPUT_FILENAME}")
    print("Now trying to play it back...")
    
    # Play back the recording
    p = pyaudio.PyAudio()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                   channels=wf.getnchannels(),
                   rate=wf.getframerate(),
                   output=True)
    
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("\nPlayback finished!")

if __name__ == "__main__":
    try:
        record_audio()
    except KeyboardInterrupt:
        print("\nRecording stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
