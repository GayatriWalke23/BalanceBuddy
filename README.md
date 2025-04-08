# BalanceBuddy Voice Assistant

Turn your BalanceBuddy "daily plan" generator into a hands-free, voice-controlled to-do & reminder assistant!

## Project Structure

See `voice_assistant/` for the new modules:
- **wake_word**: Snowboy/Porcupine + VAD  
- **asr**: Vosk streaming ASR  
- **nlu**: Intent & slot extractor (DistilBERT or rules)  
- **api**: FastAPI endpoints for tasks & reminders  
- **scheduler**: APScheduler triggers desktop/mobile notifications

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# Coming soon
```