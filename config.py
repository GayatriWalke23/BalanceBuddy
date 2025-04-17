"""Configuration settings for BalanceBuddy."""
from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/balancebuddy.db")

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DOCS_URL = "/docs"
API_REDOC_URL = "/redoc"

# OpenAI Settings
GOOGLE_API_KEY = 'AIzaSyAeSwmnYTllWDDdFvQfp27hBrjo9plTnDE'
OPENAI_TEMPERATURE = 0.8

# Wake Word Settings
WAKE_PHRASES = [
    "hey buddy",
    "hey balance buddy",
    "okay buddy",
    "hi buddy",
    "hello buddy"
]

# Default meal times (24-hour format)
DEFAULT_MEAL_TIMES = {
    "breakfast": "08:00",
    "morning_snack": "10:30",
    "lunch": "12:30",
    "afternoon_snack": "16:00",
    "dinner": "19:00"
}

# Default workout days and time
DEFAULT_WORKOUT_DAYS = ["mon", "wed", "fri"]
DEFAULT_WORKOUT_TIME = "17:00"

# Notification settings
NOTIFICATION_ICON = None  # Path to icon file if needed
NOTIFICATION_TIMEOUT = 10  # seconds
