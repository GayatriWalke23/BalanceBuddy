"""Wake word recognition using Vosk for offline speech recognition."""
from vosk import Model, KaldiRecognizer
import json
import numpy as np
from pathlib import Path
import os

class WakeWordRecognizer:
    def __init__(
        self,
        wake_phrases: list[str] = ["hey buddy"],
        model_path: str = None,
        sample_rate: int = 16000
    ):
        # Download small model if not provided
        if model_path is None:
            model_path = self._get_default_model()
            
        if not os.path.exists(model_path):
            raise ValueError(f"Model path does not exist: {model_path}")
            
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        # Make wake phrases more flexible by splitting into words
        self.wake_phrases = []
        for phrase in wake_phrases:
            self.wake_phrases.append(phrase.lower())
            # Add variants without spaces
            self.wake_phrases.append(phrase.lower().replace(" ", ""))
            # Add variants with just the key words
            words = phrase.lower().split()
            if len(words) > 1:
                self.wake_phrases.append(words[-1])  # Just the last word (e.g. 'buddy')
                if len(words) > 2:
                    self.wake_phrases.append(f"{words[0]} {words[-1]}")  # First and last (e.g. 'hey buddy')
        
    def _get_default_model(self) -> str:
        """Download and return path to the default small Vosk model."""
        import urllib.request
        import zipfile
        
        model_dir = Path.home() / ".cache" / "vosk"
        model_path = model_dir / "vosk-model-small-en-us-0.15"
        
        if not model_path.exists():
            print("Downloading small Vosk model...")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download and extract model
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            zip_path = model_dir / "model.zip"
            
            urllib.request.urlretrieve(model_url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
                
            zip_path.unlink()  # Remove zip file
            
        return str(model_path)
        
    def accept_waveform(self, audio_data: np.ndarray) -> bool:
        """Process audio data and check for wake word.
        
        Args:
            audio_data: Audio data as numpy array (int16)
            
        Returns:
            bool: True if wake word detected
        """
        # Convert to bytes for Vosk
        audio_bytes = audio_data.tobytes()
        
        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").lower()
            
            print(f"Recognized text: {text}")
            # Check if any wake phrase is in the recognized text
            for phrase in self.wake_phrases:
                if phrase in text:
                    print(f"Found wake phrase: {phrase}")
                    return True
            return False
            
        return False
        
    def reset(self):
        """Reset the recognizer state."""
        self.recognizer.Reset()
