"""Wake word processor that coordinates detection and activation."""
import threading
import time
import numpy as np
from typing import Callable, Optional, List
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
            "hi buddy",
            "hello buddy",
            "yo buddy",
            "hey there buddy",
            "hey pal",
            "hey friend"
        ]
        
        self.recognizer = WakeWordRecognizer(
            wake_phrases=self.wake_phrases,
            model_path=model_path,
            sample_rate=sample_rate
        )
        
        self.detection_thread = None
        self.is_active = False
        self.last_detection_time = 0
        self.detection_cooldown = 1.0  # reduced cooldown between detections
        self.consecutive_detections = 0
        self.max_consecutive_detections = 2  # reduced number of detections needed

    def start(self):
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
        if not self.is_active:
            return

        self.is_active = False
        if self.detector:
            self.detector.stop_listening()
        if self.detection_thread:
            self.detection_thread.join(timeout=1)

    def _run_detection(self):
        """Run the wake word detection loop."""
        def on_voice_detected(audio_data: np.ndarray):
            current_time = time.time()
            
            if current_time - self.last_detection_time < self.detection_cooldown:
                return
            
            if self.recognizer.accept_waveform(audio_data):
                if current_time - self.last_detection_time > self.detection_cooldown * 2:
                    self.consecutive_detections = 0
                
                self.consecutive_detections += 1
                print(f"\n🎯 Wake word detection {self.consecutive_detections}/{self.max_consecutive_detections}")
                
                if self.consecutive_detections >= self.max_consecutive_detections:
                    print("\n🎙️ Wake word confirmed! Listening for command...")
                    if self.callback:
                        self.callback()
                    self.consecutive_detections = 0
                
                self.last_detection_time = current_time
                
            self.recognizer.reset()

        self.detector.start_listening(callback=on_voice_detected)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
