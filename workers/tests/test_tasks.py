"""Unit tests for Celery tasks."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


class TestProcessInterviewTask:
    """Tests for process_interview task."""

    @patch("app.tasks.get_session")
    @patch("app.tasks.time.sleep")
    def test_process_interview_success(self, mock_sleep, mock_get_session):
        """Task successfully processes job and updates status."""
        job_id = str(uuid4())

        # Mock database session context manager
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__ = MagicMock(
            return_value=mock_session
        )
        mock_get_session.return_value.__exit__ = MagicMock(return_value=False)

        # Import and run task
        from app.tasks import process_interview

        result = process_interview(job_id)

        assert result["status"] == "completed"
        assert result["job_id"] == job_id

        # Verify session.execute was called (for status updates)
        assert mock_session.execute.called
        assert mock_session.commit.called
        # Should be called twice: once for PROCESSING, once for COMPLETED
        assert mock_session.execute.call_count == 2
        assert mock_session.commit.call_count == 2

    @patch("app.tasks.get_session")
    @patch("app.tasks.time.sleep")
    def test_process_interview_updates_to_processing_first(
        self, mock_sleep, mock_get_session
    ):
        """Task updates status to PROCESSING before work."""
        job_id = str(uuid4())

        mock_session = MagicMock()
        mock_get_session.return_value.__enter__ = MagicMock(
            return_value=mock_session
        )
        mock_get_session.return_value.__exit__ = MagicMock(return_value=False)

        from app.tasks import process_interview

        process_interview(job_id)

        # Check first execute call contained PROCESSING status
        first_call_args = mock_session.execute.call_args_list[0]
        # The second argument is the params dict
        params = first_call_args[0][1]
        assert params["status"] == "processing"

    @patch("app.tasks.get_session")
    @patch("app.tasks.time.sleep")
    def test_process_interview_updates_to_completed_after_work(
        self, mock_sleep, mock_get_session
    ):
        """Task updates status to COMPLETED after work."""
        job_id = str(uuid4())

        mock_session = MagicMock()
        mock_get_session.return_value.__enter__ = MagicMock(
            return_value=mock_session
        )
        mock_get_session.return_value.__exit__ = MagicMock(return_value=False)

        from app.tasks import process_interview

        process_interview(job_id)

        # Check second execute call contained COMPLETED status
        second_call_args = mock_session.execute.call_args_list[1]
        params = second_call_args[0][1]
        assert params["status"] == "completed"

    @patch("app.tasks.get_session")
    @patch("app.tasks.time.sleep")
    def test_process_interview_simulates_work(
        self, mock_sleep, mock_get_session
    ):
        """Task simulates work via sleep."""
        job_id = str(uuid4())

        mock_session = MagicMock()
        mock_get_session.return_value.__enter__ = MagicMock(
            return_value=mock_session
        )
        mock_get_session.return_value.__exit__ = MagicMock(return_value=False)

        from app.tasks import process_interview

        process_interview(job_id)

        # Verify sleep was called (simulating work)
        mock_sleep.assert_called_once_with(5)

    def test_task_registered_with_correct_name(self):
        """Task is registered with expected name."""
        from app.main import celery_app

        assert "vibecheck.tasks.process_interview" in celery_app.tasks


class TestJobStatusEnum:
    """Tests for JobStatus enum in tasks."""

    def test_job_status_values_match_api(self):
        """JobStatus values match expected API enum values."""
        from app.tasks import JobStatus

        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.PROCESSING.value == "processing"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
