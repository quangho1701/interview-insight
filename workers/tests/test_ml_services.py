"""Unit tests for ML services with mocked models."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Check if ML dependencies are available
try:
    import torch
    import faster_whisper
    import transformers
    ML_DEPS_AVAILABLE = True
except ImportError:
    ML_DEPS_AVAILABLE = False

# Create mock modules for testing when deps aren't installed
if not ML_DEPS_AVAILABLE:
    # Create mock torch module
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.float16 = "float16"
    sys.modules["torch"] = mock_torch

    # Create mock faster_whisper module
    mock_faster_whisper = MagicMock()
    sys.modules["faster_whisper"] = mock_faster_whisper

    # Create mock transformers module
    mock_transformers = MagicMock()
    sys.modules["transformers"] = mock_transformers

    # Create mock bitsandbytes module
    mock_bitsandbytes = MagicMock()
    sys.modules["bitsandbytes"] = mock_bitsandbytes


class TestTranscriptionService:
    """Tests for TranscriptionService."""

    def test_transcribe_returns_text(self):
        """Test that transcribe returns combined segment text."""
        # Mock WhisperModel before importing
        mock_whisper_model = MagicMock()

        # Mock segments
        mock_segment1 = MagicMock()
        mock_segment1.text = " Hello, welcome to the interview. "
        mock_segment2 = MagicMock()
        mock_segment2.text = " Tell me about yourself. "

        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.98

        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = (
            iter([mock_segment1, mock_segment2]),
            mock_info,
        )
        mock_whisper_model.return_value = mock_model_instance

        with patch.dict("sys.modules", {"faster_whisper": MagicMock(WhisperModel=mock_whisper_model)}):
            # Need to reload the module to pick up the mock
            if "app.services.transcription" in sys.modules:
                del sys.modules["app.services.transcription"]
            from app.services.transcription import TranscriptionService

            service = TranscriptionService(device="cpu")
            result = service.transcribe("/fake/audio.mp3")

        assert "Hello, welcome to the interview." in result
        assert "Tell me about yourself." in result
        mock_model_instance.transcribe.assert_called_once()

    def test_transcribe_with_timestamps(self):
        """Test transcribe_with_timestamps returns segment dicts."""
        mock_whisper_model = MagicMock()

        mock_segment = MagicMock()
        mock_segment.start = 0.0
        mock_segment.end = 5.0
        mock_segment.text = " Test segment. "

        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95

        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = (iter([mock_segment]), mock_info)
        mock_whisper_model.return_value = mock_model_instance

        with patch.dict("sys.modules", {"faster_whisper": MagicMock(WhisperModel=mock_whisper_model)}):
            if "app.services.transcription" in sys.modules:
                del sys.modules["app.services.transcription"]
            from app.services.transcription import TranscriptionService

            service = TranscriptionService(device="cpu")
            result = service.transcribe_with_timestamps("/fake/audio.mp3")

        assert len(result) == 1
        assert result[0]["start"] == 0.0
        assert result[0]["end"] == 5.0
        assert result[0]["text"] == "Test segment."

    def test_cpu_uses_int8_compute_type(self):
        """Test that CPU device uses int8 compute type."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        with patch.dict("sys.modules", {"torch": mock_torch}):
            if "app.services.transcription" in sys.modules:
                del sys.modules["app.services.transcription"]
            from app.services.transcription import TranscriptionService

            service = TranscriptionService()

            assert service.device == "cpu"
            assert service.compute_type == "int8"


class TestSummarizationService:
    """Tests for SummarizationService."""

    def test_summarize_returns_valid_schema(self):
        """Test that summarize returns all required keys."""
        mock_response = {
            "executive_summary": "This was a technical interview.",
            "key_topics": ["Python", "System Design"],
            "strengths": ["Good communication"],
            "areas_for_improvement": ["Could improve on algorithms"],
            "sentiment_score": 0.7,
        }

        mock_pipe = MagicMock()
        mock_pipe.return_value = [
            {
                "generated_text": [
                    {"role": "assistant", "content": str(mock_response).replace("'", '"')}
                ]
            }
        ]

        mock_pipeline_fn = MagicMock(return_value=mock_pipe)
        mock_bnb_config = MagicMock()

        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.float16 = "float16"

        mock_transformers = MagicMock()
        mock_transformers.pipeline = mock_pipeline_fn
        mock_transformers.BitsAndBytesConfig = mock_bnb_config

        with patch.dict("sys.modules", {
            "torch": mock_torch,
            "transformers": mock_transformers,
        }):
            if "app.services.summarization" in sys.modules:
                del sys.modules["app.services.summarization"]
            from app.services.summarization import SummarizationService

            service = SummarizationService(load_in_4bit=False)
            result = service.summarize("Sample interview transcript")

        assert "executive_summary" in result
        assert "key_topics" in result
        assert "strengths" in result
        assert "areas_for_improvement" in result
        assert "sentiment_score" in result

    def test_extract_json_from_code_block(self):
        """Test JSON extraction from markdown code blocks."""
        from app.services.summarization import SummarizationService

        service = SummarizationService.__new__(SummarizationService)

        text_with_block = '''Here is the analysis:
```json
{"key": "value", "number": 42}
```
'''
        result = service._extract_json(text_with_block)
        assert result == {"key": "value", "number": 42}

    def test_extract_json_plain(self):
        """Test JSON extraction from plain text."""
        from app.services.summarization import SummarizationService

        service = SummarizationService.__new__(SummarizationService)

        text_plain = 'Some text {"key": "value"} more text'
        result = service._extract_json(text_plain)
        assert result == {"key": "value"}

    def test_validate_output_clamps_sentiment(self):
        """Test that sentiment scores are clamped to [-1, 1]."""
        from app.services.summarization import SummarizationService

        service = SummarizationService.__new__(SummarizationService)

        data = {
            "executive_summary": "Test",
            "key_topics": ["Topic"],
            "strengths": ["Strength"],
            "areas_for_improvement": ["Area"],
            "sentiment_score": 5.0,  # Out of range
        }

        result = service._validate_output(data)
        assert result["sentiment_score"] == 1.0

        data["sentiment_score"] = -10.0
        result = service._validate_output(data)
        assert result["sentiment_score"] == -1.0

    def test_validate_output_missing_key_raises(self):
        """Test that missing required keys raise ValueError."""
        from app.services.summarization import SummarizationService

        service = SummarizationService.__new__(SummarizationService)

        data = {
            "executive_summary": "Test",
            # Missing other keys
        }

        with pytest.raises(ValueError, match="Missing required key"):
            service._validate_output(data)


class TestS3Service:
    """Tests for S3Service."""

    @patch("app.services.s3.boto3")
    @patch("app.services.s3.get_settings")
    def test_download_file_calls_s3(self, mock_settings, mock_boto3):
        """Test that download_file calls S3 client correctly."""
        from app.services.s3 import S3Service

        mock_settings.return_value.s3_endpoint_url = "http://localhost:9000"
        mock_settings.return_value.s3_access_key = "test"
        mock_settings.return_value.s3_secret_key = "test"
        mock_settings.return_value.s3_region = "us-east-1"
        mock_settings.return_value.s3_bucket_name = "test-bucket"

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        service = S3Service()

        with patch("app.services.s3.os.makedirs"):
            service.download_file("uploads/test.mp3", "/tmp/test.mp3")

        mock_client.download_file.assert_called_once_with(
            "test-bucket", "uploads/test.mp3", "/tmp/test.mp3"
        )

    @patch("app.services.s3.boto3")
    @patch("app.services.s3.get_settings")
    def test_file_exists_returns_true(self, mock_settings, mock_boto3):
        """Test file_exists returns True when file exists."""
        from app.services.s3 import S3Service

        mock_settings.return_value.s3_endpoint_url = "http://localhost:9000"
        mock_settings.return_value.s3_access_key = "test"
        mock_settings.return_value.s3_secret_key = "test"
        mock_settings.return_value.s3_region = "us-east-1"
        mock_settings.return_value.s3_bucket_name = "test-bucket"

        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client

        service = S3Service()
        result = service.file_exists("uploads/test.mp3")

        assert result is True
        mock_client.head_object.assert_called_once()

    @patch("app.services.s3.boto3")
    @patch("app.services.s3.get_settings")
    def test_file_exists_returns_false_on_error(self, mock_settings, mock_boto3):
        """Test file_exists returns False when file doesn't exist."""
        from botocore.exceptions import ClientError

        from app.services.s3 import S3Service

        mock_settings.return_value.s3_endpoint_url = "http://localhost:9000"
        mock_settings.return_value.s3_access_key = "test"
        mock_settings.return_value.s3_secret_key = "test"
        mock_settings.return_value.s3_region = "us-east-1"
        mock_settings.return_value.s3_bucket_name = "test-bucket"

        mock_client = MagicMock()
        mock_client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadObject"
        )
        mock_boto3.client.return_value = mock_client

        service = S3Service()
        result = service.file_exists("uploads/nonexistent.mp3")

        assert result is False
