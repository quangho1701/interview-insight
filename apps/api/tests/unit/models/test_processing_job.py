"""Unit tests for ProcessingJob model."""

from uuid import UUID, uuid4

import pytest

from app.models.enums import JobStatus
from app.models.processing_job import ProcessingJob


class TestProcessingJobModel:
    """Tests for ProcessingJob SQLModel."""

    def test_processing_job_model(self):
        """Job created with status and s3_audio_key."""
        user_id = uuid4()

        job = ProcessingJob(
            user_id=user_id,
            s3_audio_key="audio/test-file.mp3",
        )

        assert job.user_id == user_id
        assert job.s3_audio_key == "audio/test-file.mp3"
        assert isinstance(job.id, UUID)  # UUID auto-generated

    def test_processing_job_status_enum(self):
        """Only valid status values accepted."""
        # Verify enum values exist
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.PROCESSING.value == "processing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"

        # Create jobs with different statuses
        pending_job = ProcessingJob(
            user_id=uuid4(),
            s3_audio_key="audio/1.mp3",
            status=JobStatus.PENDING,
        )
        processing_job = ProcessingJob(
            user_id=uuid4(),
            s3_audio_key="audio/2.mp3",
            status=JobStatus.PROCESSING,
        )

        assert pending_job.status == JobStatus.PENDING
        assert processing_job.status == JobStatus.PROCESSING

    def test_processing_job_status_default(self):
        """New job starts as PENDING."""
        job = ProcessingJob(
            user_id=uuid4(),
            s3_audio_key="audio/test.mp3",
        )

        assert job.status == JobStatus.PENDING
