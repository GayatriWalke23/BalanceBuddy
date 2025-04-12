"""Main application entry point for BalanceBuddy."""
import uvicorn
from fastapi import FastAPI
from voice_assistant.api.server import app as api_app
from voice_assistant.wake_word.processor import WakeWordProcessor
from voice_assistant.scheduler.scheduler import NotificationScheduler
from voice_assistant.db.database import Database
from config import (
    DATABASE_URL, API_HOST, API_PORT, WAKE_PHRASES,
    DEFAULT_MEAL_TIMES, DEFAULT_WORKOUT_DAYS, DEFAULT_WORKOUT_TIME
)

def setup_wake_word():
    """Set up and start the wake word detection."""
    def on_wake_word(audio_data):
        print("\n🎯 Wake word detected! Assistant is ready to listen...")
    
    processor = WakeWordProcessor(
        wake_phrases=WAKE_PHRASES,
        callback=on_wake_word
    )
    processor.start()
    return processor

def setup_scheduler():
    """Set up and start the notification scheduler."""
    scheduler = NotificationScheduler()
    
    # Schedule meal reminders
    for meal, time in DEFAULT_MEAL_TIMES.items():
        scheduler.schedule_meal_reminder(meal, time)
    
    # Schedule workout reminders
    scheduler.schedule_workout_reminder(
        DEFAULT_WORKOUT_DAYS,
        DEFAULT_WORKOUT_TIME
    )
    
    scheduler.start()
    return scheduler

def main():
    # Initialize database
    db = Database(db_url=DATABASE_URL)
    
    # Set up wake word detection
    wake_processor = setup_wake_word()
    
    # Set up scheduler
    scheduler = setup_scheduler()
    
    # Mount the API app
    root_app = FastAPI(title="BalanceBuddy")
    root_app.mount("/api", api_app)
    
    try:
        # Start the web server
        print("\n🚀 Starting BalanceBuddy...")
        print(f"📝 API documentation available at http://{API_HOST}:{API_PORT}/docs")
        print("⌨️  Press Ctrl+C to exit")
        
        uvicorn.run(root_app, host=API_HOST, port=API_PORT)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    finally:
        wake_processor.stop()
        scheduler.stop()

if __name__ == "__main__":
    main()
