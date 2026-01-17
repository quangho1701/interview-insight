# VibeCheck ML Worker

GPU-accelerated worker for audio transcription and sentiment analysis.

## Status

**Not yet implemented** - This is a placeholder for the ML worker.

## Planned Features

- Celery task consumer
- Whisper transcription
- Pyannote speaker diarization
- Sentiment analysis
- PII redaction via NER
- Metrics calculation
- S3 audio cleanup

## Tech Stack

- Python 3.11+
- Celery
- OpenAI Whisper
- Pyannote.audio
- Transformers (HuggingFace)
- PyTorch (CUDA)

## GPU Requirements

- NVIDIA GPU with CUDA support
- Minimum 8GB VRAM recommended
