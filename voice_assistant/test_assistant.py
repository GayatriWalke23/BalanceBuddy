"""Test script for the complete voice assistant flow."""
import time
from voice_assistant.wake_word.processor import WakeWordProcessor
from voice_assistant.nlu.command_processor import CommandProcessor
from voice_assistant.nlu.intent_recognizer import Intent

class VoiceAssistant:
    def __init__(self):
        # Initialize command processor first (this will download model if needed)
        self.command_processor = CommandProcessor(
            on_command=self._handle_command,
            on_listening=self._on_listening,
            on_processing=self._on_processing
        )
        
        # Initialize wake word detector
        self.wake_word_processor = WakeWordProcessor(
            wake_phrases=["hey buddy", "hey balance buddy", "okay buddy"],
            callback=self._on_wake_word
        )
        
        self.is_running = False
        
    def start(self):
        """Start the voice assistant."""
        self.is_running = True
        
        print("\n🎤 Voice Assistant is ready!")
        print("\n📝 Try saying one of these wake phrases:")
        print("   - 'hey buddy'")
        print("   - 'hey balance buddy'")
        print("   - 'okay buddy'")
        
        print("\n💡 After wake word, try these commands:")
        for intent, examples in self.command_processor.get_example_commands().items():
            print(f"\n{intent}:")
            for example in examples[:2]:  # Show first 2 examples
                print(f"   - '{example}'")
                
        print("\n⌨️  Press Ctrl+C to exit")
        
        # Start wake word detection
        self.wake_word_processor.start()
        
        try:
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Stop the voice assistant."""
        print("\n🛑 Stopping voice assistant...")
        self.is_running = False
        self.wake_word_processor.stop()
        self.command_processor.stop_listening()
        
    def _on_wake_word(self, audio_data):
        """Called when wake word is detected."""
        print("\n🎯 Wake word detected! What would you like to do?")
        self.command_processor.start_listening()
        
    def _on_listening(self):
        """Called when starting to listen for command."""
        print("👂 Listening for command...")
        
    def _on_processing(self):
        """Called when processing a command."""
        print("🔄 Processing command...")
        
    def _handle_command(self, intent: Intent):
        """Handle recognized command intent."""
        print(f"\n✨ Recognized command: {intent.name}")
        print(f"Parameters: {intent.params}")
        
        # Here you would implement the actual command handling
        # For now, we'll just print what we would do
        if intent.name == "add_task":
            print(f"📝 Adding task: {intent.params['task_description']}")
        elif intent.name == "list_tasks":
            print("📋 Listing all tasks...")
        elif intent.name == "set_reminder":
            print(f"⏰ Setting reminder: {intent.params['task_description']}")
            print(f"   Time: {intent.params['reminder_time']}")
        elif intent.name == "delete_task":
            print(f"🗑️  Deleting task: {intent.params['task_id']}")
        elif intent.name == "help":
            print("❓ Showing help...")
            
def main():
    assistant = VoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()
