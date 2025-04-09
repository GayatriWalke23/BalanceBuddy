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
            
        try:
            if not os.path.exists(model_path):
                raise ValueError(f"Model path does not exist: {model_path}")
                
            print("🎯 Loading speech recognition model...")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, sample_rate)
            print("✅ Model loaded successfully!\n")
            
        except Exception as e:
            print(f"\n❌ Error loading model: {e}")
            print("Please ensure the model is downloaded correctly.")
            raise
        # Make wake phrases more flexible
        self.wake_phrases = []
        self.primary_phrases = [phrase.lower() for phrase in wake_phrases]
        
        for phrase in wake_phrases:
            phrase = phrase.lower()
            self.wake_phrases.append(phrase)
            
            # Add variants without spaces
            self.wake_phrases.append(phrase.replace(" ", ""))
            
            # Add common variations
            words = phrase.split()
            if len(words) > 1:
                # Just the key words (e.g. 'buddy')
                self.wake_phrases.append(words[-1])
                
                # First and last words (e.g. 'hey buddy')
                if len(words) > 2:
                    self.wake_phrases.append(f"{words[0]} {words[-1]}")
                    
                # Handle common word variations
                variations = {
                    'hey': ['hi', 'hello', 'hay'],
                    'hello': ['hey', 'hi', 'helo'],
                    'hi': ['hey', 'hello'],
                    'buddy': ['buddie', 'budi', 'body']
                }
                
                # Add variations of first and last words
                for i, word in enumerate(words):
                    if word in variations:
                        for variant in variations[word]:
                            variant_phrase = list(words)
                            variant_phrase[i] = variant
                            self.wake_phrases.append(' '.join(variant_phrase))
        
        # Remove duplicates while preserving order
        self.wake_phrases = list(dict.fromkeys(self.wake_phrases))
        print("Available wake phrases and variations:")
        for phrase in self.wake_phrases:
            print(f"  - {phrase}")
        
    def _get_default_model(self) -> str:
        """Download and return path to the default small Vosk model."""
        import urllib.request
        import zipfile
        import sys
        
        model_dir = Path.home() / ".cache" / "vosk"
        model_path = model_dir / "vosk-model-en-us-0.22"
        
        if not model_path.exists():
            print("\n📥 Downloading Vosk speech recognition model...")
            print("This may take a few minutes depending on your internet speed.")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download and extract model
            model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
            zip_path = model_dir / "model.zip"
            
            try:
                # Show download progress
                def progress(count, block_size, total_size):
                    percent = int(count * block_size * 100 / total_size)
                    sys.stdout.write(f"\rDownloading: {percent}% [{percent * '=' + (100-percent) * ' '}]")
                    sys.stdout.flush()
                
                urllib.request.urlretrieve(model_url, zip_path, reporthook=progress)
                print("\n\n📦 Extracting model...")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(model_dir)
                    
                zip_path.unlink()  # Remove zip file
                print("✅ Model ready!\n")
                
            except Exception as e:
                print(f"\n❌ Error downloading model: {e}")
                print("Please check your internet connection and try again.")
                raise
            
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
        
        # Process the audio
        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "").lower().strip()
            
            if text:  # Only print if we got some text
                print(f"\n🎙️ Heard: {text}")
            
                # First check primary phrases with exact match
                for phrase in self.primary_phrases:
                    if phrase == text:
                        print(f"✅ Found exact wake phrase: {phrase}")
                        return True
                
                # Then check all variations with partial match
                for phrase in self.wake_phrases:
                    if phrase in text:
                        print(f"✅ Found wake phrase variation: {phrase}")
                        return True
                        
                # Check for close matches (allow one word to be different)
                text_words = set(text.split())
                for phrase in self.primary_phrases:
                    phrase_words = set(phrase.split())
                    common_words = text_words & phrase_words
                    if len(common_words) >= max(len(phrase_words) - 1, 1):
                        print(f"✅ Found close match to wake phrase: {phrase}")
                        return True
        
        # Also check partial results for debugging
        partial = json.loads(self.recognizer.PartialResult())
        partial_text = partial.get("partial", "").strip()
        if partial_text:
            print(f"\r🔊 Listening: {partial_text}", end="")
            
        return False
        
    def reset(self):
        """Reset the recognizer state."""
        self.recognizer.Reset()
