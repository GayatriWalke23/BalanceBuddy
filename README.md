# BalanceBuddy Voice Assistant 🎙️

A smart voice-controlled assistant that helps you maintain a healthy lifestyle by generating personalized daily plans, setting reminders, and tracking your progress.

## Features
- 🗣️ **Voice Activation**: Wake up the assistant with phrases like "hey buddy", "hey balance buddy", or "okay buddy"
- 📅 **Daily Plans**: Get personalized meal and workout plans based on your preferences
- 🔔 **Smart Notifications**: Receive timely reminders for meals and workouts
- 🌐 **Web Interface**: Access your plans and settings through a modern web dashboard

## Project Structure

```
BalanceBuddy/
├── config.py                 # Central configuration
├── requirements.txt          # Project dependencies
├── src/                      # Web interface
│   ├── main.py              # FastAPI web server
│   ├── static/              # Static assets
│   └── templates/           # HTML templates
├── tests/                   # Test files
│   └── test_microphone.py   # Audio input testing
└── voice_assistant/         # Voice assistant module
    ├── main.py             # Voice assistant entry point
    ├── wake_word/          # Voice activation system
    ├── db/                 # Database models
    └── api/                # FastAPI endpoints
```

## Requirements

- Python 3.8+
- OpenAI API key for plan generation
- System dependencies:
  - PortAudio (for PyAudio)
  - CUDA-compatible GPU recommended for voice processing

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BalanceBuddy.git
cd BalanceBuddy
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Running the Application

1. Start the web interface:
```bash
python src/main.py
```
Visit http://localhost:8000 in your browser

2. Start the voice assistant:
```bash
python voice_assistant/main.py
```

3. Test your microphone setup (optional):
```bash
python tests/test_microphone.py
```

## Development Status

- ✅ Wake word detection system
- ✅ Daily plan generation
- ✅ Web interface
- 🚧 Notification system (in progress)
- 📅 Mobile app (planned)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.