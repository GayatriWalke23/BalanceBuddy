# BalanceBuddy Voice Assistant 🎙️

A smart voice-controlled assistant that helps you maintain a healthy lifestyle by generating personalized daily plans, setting reminders, and tracking your progress.

## Features

- 🗣️ **Voice Activation**: Wake up the assistant with phrases like "hey buddy", "hey balance buddy", or "okay buddy"
- 📅 **Daily Plans**: Get personalized meal and workout plans based on your preferences
- 🔔 **Smart Notifications**: Receive timely reminders for meals and workouts
- 🌐 **Web Interface**: Access your plans and settings through a modern web dashboard

## Project Structure

### Voice Assistant (`voice_assistant/`)
- **wake_word/**: Voice activation system using Vosk
  - `detector.py`: Audio input processing
  - `processor.py`: Wake word detection logic
  - `test_detector.py`: Testing utilities
- **db/**: Database models and utilities
- **api/**: FastAPI endpoints for web interface

### Core Features (`src/`)
- **test.py**: Daily plan generation using LangChain and OpenAI

## Requirements

- Python 3.8+
- OpenAI API key for plan generation
- System dependencies for audio processing:
  - PortAudio (for PyAudio)
  - CUDA-compatible GPU recommended for voice processing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. Test wake word detection:
```bash
python voice_assistant/wake_word/test_detector.py
```

## Development Status

- ✅ Wake word detection system
- ✅ Daily plan generation
- 🚧 Web interface (in progress)
- 🚧 Notification system (in progress)
- 📅 Mobile app (planned)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.