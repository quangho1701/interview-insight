"""Unit tests for InterviewAnalysis model."""

from uuid import UUID, uuid4

import pytest

from app.models.interview_analysis import InterviewAnalysis


class TestInterviewAnalysisModel:
    """Tests for InterviewAnalysis SQLModel."""

    def test_interview_analysis_model(self):
        """Analysis links user_id and interviewer_id correctly."""
        user_id = uuid4()
        interviewer_id = uuid4()

        analysis = InterviewAnalysis(
            user_id=user_id,
            interviewer_id=interviewer_id,
            sentiment_score=0.75,
        )

        assert analysis.user_id == user_id
        assert analysis.interviewer_id == interviewer_id
        assert analysis.sentiment_score == 0.75
        assert isinstance(analysis.id, UUID)  # UUID auto-generated

    def test_interview_analysis_metrics_json(self):
        """Analysis stores arbitrary metrics dict."""
        user_id = uuid4()
        interviewer_id = uuid4()
        metrics = {
            "interruption_count": 5,
            "speaking_ratio": 0.4,
            "sentiment_volatility": 0.15,
        }

        analysis = InterviewAnalysis(
            user_id=user_id,
            interviewer_id=interviewer_id,
            sentiment_score=0.65,
            metrics_json=metrics,
        )

        assert analysis.metrics_json is not None
        assert analysis.metrics_json["interruption_count"] == 5
        assert analysis.metrics_json["speaking_ratio"] == 0.4
        assert analysis.metrics_json["sentiment_volatility"] == 0.15
