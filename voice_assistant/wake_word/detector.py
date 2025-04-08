"""Wake word detection using webrtcvad for Voice Activity Detection."""
import webrtcvad
import sounddevice as sd
import queue
import threading
import time
from typing import Callable, Optional
import numpy as np

class WakeWordDetector:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_duration: int = 10,  # ms (reduced further for better responsiveness)
        vad_mode: int = 0,  # 0-3, 0 is most sensitive
        silence_threshold: float = 0.15,  # seconds (reduced further)
        min_speech_duration: float = 0.02,  # seconds (reduced for quicker detection)
    ):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_length = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(vad_mode)
        self.silence_threshold = silence_threshold
        self.min_speech_duration = min_speech_duration
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self._stop_event = threading.Event()
        
        # Debug flags
        self.debug = True  # Set to True to see audio levels
        self.last_debug_time = 0
        self.debug_interval = 1  # seconds

    def start_listening(self, callback: Optional[Callable] = None):
        """Start listening for wake word."""
        self.is_listening = True
        self._stop_event.clear()

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Error in audio stream: {status}")
                return
            
            # Convert float32 to int16 for VAD
            audio_data = (indata.flatten() * 32767).astype(np.int16)
            
            # Debug audio level occasionally
            if len(audio_data) > 0:
                audio_level = np.abs(audio_data).mean()
                if audio_level > 100:  # Much lower threshold
                    print(f"🎤 Sound detected ({audio_level:.0f})")
            
            self.audio_queue.put(audio_data)

        # Start audio stream
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=self.frame_length,
            device=None,  # Use default input device
            callback=audio_callback
        ):
            print("🎤 Listening for wake word...")
            speech_start_time = None
            last_voice_time = time.time()
            voice_frames = []
            consecutive_speech_frames = 0
            consecutive_silence_frames = 0
            min_speech_frames = int(self.min_speech_duration * 1000 / self.frame_duration)

            while not self._stop_event.is_set():
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)  # Reduced timeout for responsiveness
                    
                    # Check if this frame contains speech
                    try:
                        is_speech = self.vad.is_speech(
                            audio_frame.tobytes(),
                            self.sample_rate
                        )
                    except Exception as e:
                        print(f"VAD error: {e}")
                        continue

                    current_time = time.time()
                    
                    if is_speech:
                        consecutive_silence_frames = 0
                        consecutive_speech_frames += 1
                        voice_frames.append(audio_frame)
                        last_voice_time = current_time
                        print(f"Speech frames: {consecutive_speech_frames}")
                        
                        # If we have enough continuous speech, process it
                        if consecutive_speech_frames >= min_speech_frames:
                            if callback and len(voice_frames) > 0:
                                audio_data = np.concatenate(voice_frames)
                                callback(audio_data)
                            # Reset for next detection
                            voice_frames = []
                            consecutive_speech_frames = 0
                            
                    else:  # Not speech
                        consecutive_speech_frames = max(0, consecutive_speech_frames - 0.5)  # Slower decrease
                        consecutive_silence_frames += 1
                        
                        # If we have voice frames but hit silence threshold
                        if voice_frames and (current_time - last_voice_time) > self.silence_threshold:
                            if callback and len(voice_frames) > 0:
                                audio_data = np.concatenate(voice_frames)
                                callback(audio_data)
                            # Reset for next detection
                            voice_frames = []
                            consecutive_speech_frames = 0

                except queue.Empty:
                    # Timeout is normal, just continue
                    continue
                except Exception as e:
                    print(f"❌ Error: {e}")
                    break

    def stop_listening(self):
        """Stop listening for wake word."""
        self._stop_event.set()
        self.is_listening = False
