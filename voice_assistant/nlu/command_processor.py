"""Process voice commands and execute corresponding actions."""
from typing import Optional, Callable, Dict, Any
import threading
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import time
from datetime import datetime
from typing import Optional
from dateutil import parser

from voice_assistant.nlu.intent_recognizer import IntentRecognizer, Intent
from voice_assistant.task_manager import TaskManager


class CommandProcessor:
    def __init__(
        self,
        sample_rate: int = 16000,
        model_path: Optional[str] = None,
        on_command: Optional[Callable[[Intent], None]] = None,
        on_listening: Optional[Callable[[], None]] = None,
        on_processing: Optional[Callable[[], None]] = None
    ):
        # Initialize Vosk model for speech recognition
        if model_path is None:
            from ..wake_word.recognizer import WakeWordRecognizer
            dummy = WakeWordRecognizer()  # This will download model if needed
            model_path = dummy._get_default_model()
            
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        self.intent_recognizer = IntentRecognizer()
        self.task_manager = TaskManager()
        
        # Start checking for reminders
        self.task_manager.start_reminder_checker()
        
        # Audio settings
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self._stop_event = threading.Event()
        
        # Callbacks
        self.on_command = on_command
        self.on_listening = on_listening
        self.on_processing = on_processing
        
        # Command timeout
        self.command_timeout = 5  # seconds
        self.last_audio_time = 0
        
    def start_listening(self):
        """Start listening for commands."""
        if self.is_listening:
            return
            
        self.is_listening = True
        self._stop_event.clear()
        self.last_audio_time = time.time()
        
        if self.on_listening:
            self.on_listening()
        
        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"Error in audio stream: {status}")
                return
                
            # Convert float32 to int16
            audio_data = (indata.flatten() * 32767).astype(np.int16)
            self.audio_queue.put(audio_data)
            self.last_audio_time = time.time()
            
        # Start audio stream
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            callback=audio_callback
        ):
            while not self._stop_event.is_set():
                try:
                    audio_data = self.audio_queue.get(timeout=0.5)
                    
                    # Check for command timeout
                    if time.time() - self.last_audio_time > self.command_timeout:
                        print("\nCommand timeout. Please try again.")
                        self.stop_listening()
                        break
                        
                    # Process audio with Vosk
                    if self.recognizer.AcceptWaveform(audio_data.tobytes()):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()
                        
                        if text:
                            if self.on_processing:
                                self.on_processing()
                                
                            # Recognize and handle intent
                            intent = self.intent_recognizer.recognize(text)
                            if intent:
                                if self.on_processing:
                                    self.on_processing()
                                response = self._handle_intent(intent)
                                print(f"\n🤖 {response}")
                                if self.on_command:
                                    self.on_command(intent)
                                self.stop_listening()
                                break
                            
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Error processing command: {e}")
                    self.stop_listening()
                    break
                    
    def stop_listening(self):
        """Stop listening for commands."""
        self._stop_event.set()
        self.is_listening = False
        
    def get_example_commands(self) -> Dict[str, Any]:
        """Get example commands that can be spoken."""
        return self.intent_recognizer.get_example_commands()
        
    def _handle_intent(self, intent: Intent) -> str:
        """Handle recognized intent and return response."""
        if intent.name == "help":
            return self._handle_help()
        elif intent.name == "add_task":
            return self._handle_add_task(intent)
        elif intent.name == "list_tasks":
            return self._handle_list_tasks()
        elif intent.name == "set_reminder":
            return self._handle_set_reminder(intent)
        elif intent.name == "delete_task":
            return self._handle_delete_task(intent)
        else:
            return "Sorry, I don't know how to handle that command yet."
    
    def _handle_help(self) -> str:
        """Handle help command."""
        return """Here are the commands I understand:
        - Add a task: 'add task buy groceries'
        - List tasks: 'show my tasks'
        - Set reminder: 'remind me to call John at 3pm'
        - Delete task: 'delete task 1' or 'mark task 2 as done'
        - Help: 'what can you do' or 'help'"""

    def _handle_add_task(self, intent: Intent) -> str:
        """Handle add task command."""
        task = intent.parameters.get("task")
        if not task:
            return "What task would you like to add?"
        
        # Add task without reminder
        task_id = self.task_manager.add_task(task)
        return f"Added task {task_id}: {task}"

    def _handle_list_tasks(self) -> str:
        """Handle list tasks command."""
        tasks = self.task_manager.list_tasks()
        if not tasks:
            return "You have no tasks."
        return "Listed your tasks above."

    def _handle_set_reminder(self, intent: Intent) -> str:
        """Handle set reminder command."""
        task = intent.parameters.get("task")
        time_str = intent.parameters.get("time")
        
        if not task or not time_str:
            return "Please specify both task and time for the reminder."
        
        try:
            # Parse the time string into a datetime
            reminder_time = parser.parse(time_str)
            
            # If only time was given, assume today's date
            if reminder_time.date() == datetime.now().date():
                # If the time has already passed today, assume tomorrow
                if reminder_time < datetime.now():
                    reminder_time = reminder_time.replace(
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day + 1
                    )
            
            # Add task with reminder
            task_id = self.task_manager.add_task(task, reminder_time)
            return f"Set reminder for task {task_id} at {reminder_time.strftime('%I:%M %p on %B %d')}"
            
        except ValueError as e:
            return f"Sorry, I couldn't understand the time format: {time_str}"

    def _handle_delete_task(self, intent: Intent) -> str:
        """Handle delete task command."""
        task_id_str = intent.parameters.get("task_id")
        if not task_id_str:
            return "Which task would you like to mark as done?"
        
        try:
            task_id = int(task_id_str)
            if self.task_manager.complete_task(task_id):
                return f"Marked task {task_id} as done"
            return f"Couldn't find task {task_id}"
        except ValueError:
            return f"Invalid task number: {task_id_str}"
            
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'task_manager'):
            self.task_manager.stop_reminder_checker()
