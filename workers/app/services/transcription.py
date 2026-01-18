"""Transcription service using faster-whisper."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio files using faster-whisper."""

    def __init__(
        self,
        model_size: str = "distil-large-v3",
        device: Optional[str] = None,
        compute_type: str = "float16",
    ):
        """Initialize the transcription service.

        Args:
            model_size: Whisper model size (default: distil-large-v3)
            device: Device to use ('cuda' or 'cpu'). Auto-detected if None.
            compute_type: Compute type for inference (float16, int8, etc.)
        """
        self.model_size = model_size
        self.compute_type = compute_type
        self._model = None

        # Auto-detect device
        if device is None:
            try:
                import torch

                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
        else:
            self.device = device

        # Adjust compute type for CPU
        if self.device == "cpu":
            self.compute_type = "int8"

        logger.info(
            f"TranscriptionService initialized: model={model_size}, "
            f"device={self.device}, compute_type={self.compute_type}"
        )

    def _load_model(self):
        """Lazy-load the Whisper model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info(f"Loading Whisper model: {self.model_size}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("Whisper model loaded successfully")
        return self._model

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file to text.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Full transcript text.
        """
        model = self._load_model()

        logger.info(f"Transcribing audio file: {audio_path}")
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,  # Auto-detect language
            vad_filter=True,  # Filter out non-speech
        )

        logger.info(
            f"Detected language: {info.language} "
            f"(probability: {info.language_probability:.2f})"
        )

        # Combine all segments into full transcript
        transcript_parts = []
        for segment in segments:
            transcript_parts.append(segment.text.strip())

        transcript = " ".join(transcript_parts)
        logger.info(f"Transcription complete: {len(transcript)} characters")

        return transcript

    def transcribe_with_timestamps(self, audio_path: str) -> list[dict]:
        """Transcribe audio with timestamp information.

        Args:
            audio_path: Path to the audio file.

        Returns:
            List of segments with start, end, and text.
        """
        model = self._load_model()

        logger.info(f"Transcribing audio with timestamps: {audio_path}")
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,
            vad_filter=True,
        )

        result = []
        for segment in segments:
            result.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                }
            )

        logger.info(f"Transcription complete: {len(result)} segments")
        return result
