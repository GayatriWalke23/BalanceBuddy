"""Wake word processor that coordinates detection and activation."""
import numpy as np
from typing import Callable, Optional, List
import threading
from voice_assistant.wake_word.detector import WakeWordDetector
from voice_assistant.wake_word.recognizer import WakeWordRecognizer

class WakeWordProcessor:
    def __init__(
        self,
        wake_phrases: List[str] = ["hey buddy"],
        callback: Optional[Callable] = None,
        sample_rate: int = 16000,
        model_path: Optional[str] = None
    ):
        if isinstance(wake_phrases, str):
            wake_phrases = [wake_phrases]
            
        self.wake_phrases = [phrase.lower() for phrase in wake_phrases]
        self.callback = callback
        self.sample_rate = sample_rate
        
        # Initialize components
        self.detector = WakeWordDetector(sample_rate=sample_rate)
        self.wake_phrases = wake_phrases or [
            "hey buddy",
            "hey balance buddy",
            "okay buddy",
            "hi buddy",  # Added more variations
            "hello buddy"
        ]
        
        self.recognizer = WakeWordRecognizer(
            wake_phrases=self.wake_phrases,
            model_path=model_path,
            sample_rate=sample_rate
        )
        
        self.detection_thread = None
        self.is_active = False
        self.last_detection_time = 0
        self.detection_cooldown = 3.0  # seconds between detections

    def start(self):
        """Start listening for wake word."""
        if self.is_active:
            print("Wake word processor is already active")
            return

        self.is_active = True
        self.detection_thread = threading.Thread(
            target=self._run_detection,
            daemon=True
        )
        self.detection_thread.start()

    def stop(self):
        """Stop listening for wake word."""
        if not self.is_active:
            return

        self.is_active = False
        if self.detector:
            self.detector.stop_listening()
        if self.detection_thread:
            self.detection_thread.join(timeout=1)

    def _run_detection(self):
        """Run the wake word detection loop."""
        import time
        
        def on_voice_detected(audio_data: np.ndarray):
            current_time = time.time()
            
            # Check cooldown period
            if current_time - self.last_detection_time < self.detection_cooldown:
                return
                
            # Process audio with wake word recognizer
            if self.recognizer.accept_waveform(audio_data):
                print("\n Wake word detected! Listening for command...")
                self.last_detection_time = current_time
                if self.callback:
                    self.callback(audio_data)
                    
            # Reset recognizer state
            self.recognizer.reset()

        self.detector.start_listening(callback=on_voice_detected)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
