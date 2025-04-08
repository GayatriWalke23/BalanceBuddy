"""Test script for wake word detection with Vosk-based recognition."""
import time
from processor import WakeWordProcessor

def on_wake_word(audio_data):
    print("\n🎯 Wake word detected! Assistant is ready to listen...")

def main():
    # Define wake phrases (can add multiple variations)
    wake_phrases = [
        "hey buddy",
        "hey balance buddy",
        "okay buddy"
    ]
    
    # Create wake word processor
    processor = WakeWordProcessor(
        wake_phrases=wake_phrases,
        callback=on_wake_word
    )

    try:
        # Start listening
        print("\n🎤 Starting wake word detection...")
        print("📝 Try saying one of these wake phrases:")
        for phrase in wake_phrases:
            print(f"   - '{phrase}'")
        print("\n⌨️  Press Ctrl+C to exit")
        
        processor.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping wake word detection...")
    finally:
        processor.stop()

if __name__ == "__main__":
    main()
