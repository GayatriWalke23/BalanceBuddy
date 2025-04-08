import pyaudio
import wave

def list_audio_devices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    print("\nAvailable Audio Devices:")
    print("-----------------------")
    
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:  # Only input devices
            print(f"Device {i}: {device_info.get('name')}")
            print(f"   Input channels: {device_info.get('maxInputChannels')}")
            print(f"   Default sample rate: {device_info.get('defaultSampleRate')}")
            print()
    
    p.terminate()

if __name__ == "__main__":
    try:
        list_audio_devices()
        print("\nIf you see your microphone listed above, it means it's detected by the system.")
        print("Press Ctrl+C to exit.")
        
        # Keep the script running
        while True:
            pass
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
