"""Summarization service using Llama 3.3 8B."""

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert interview analyst. Your task is to analyze interview transcripts and provide structured insights.

Analyze the following interview transcript and provide a JSON response with these exact keys:
- "executive_summary": A 2-3 sentence summary of the interview
- "key_topics": An array of 3-5 main topics discussed
- "strengths": An array of 2-4 positive observations about the interviewee
- "areas_for_improvement": An array of 2-4 constructive feedback points
- "sentiment_score": A float between -1.0 (very negative) and 1.0 (very positive) representing the overall tone

Respond ONLY with valid JSON. No additional text or explanation."""

USER_PROMPT_TEMPLATE = """Transcript:
{transcript}

Provide your analysis as JSON:"""


class SummarizationService:
    """Service for summarizing interview transcripts using Llama 3.3 8B."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.3-8B-Instruct",
        device: Optional[str] = None,
        load_in_4bit: bool = True,
    ):
        """Initialize the summarization service.

        Args:
            model_name: HuggingFace model name
            device: Device to use ('cuda' or 'cpu'). Auto-detected if None.
            load_in_4bit: Whether to load model with 4-bit quantization
        """
        self.model_name = model_name
        self.load_in_4bit = load_in_4bit
        self._pipeline = None

        # Auto-detect device
        if device is None:
            try:
                import torch

                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"
        else:
            self.device = device

        # 4-bit quantization requires CUDA
        if self.device == "cpu" and self.load_in_4bit:
            logger.warning("4-bit quantization requires CUDA. Disabling.")
            self.load_in_4bit = False

        logger.info(
            f"SummarizationService initialized: model={model_name}, "
            f"device={self.device}, 4bit={self.load_in_4bit}"
        )

    def _load_pipeline(self):
        """Lazy-load the LLM pipeline."""
        if self._pipeline is None:
            import torch
            from transformers import pipeline, BitsAndBytesConfig

            logger.info(f"Loading LLM model: {self.model_name}")

            model_kwargs = {"torch_dtype": torch.float16}

            if self.load_in_4bit:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"
            else:
                model_kwargs["device_map"] = self.device

            self._pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                model_kwargs=model_kwargs,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.1,
                top_p=0.9,
            )
            logger.info("LLM model loaded successfully")

        return self._pipeline

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from model output, handling markdown code blocks."""
        # Try to find JSON in code blocks first
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if json_match:
            text = json_match.group(1)

        # Find the first { and last } to extract JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        return json.loads(text)

    def _validate_output(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize the output schema."""
        required_keys = [
            "executive_summary",
            "key_topics",
            "strengths",
            "areas_for_improvement",
            "sentiment_score",
        ]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        # Validate and clamp sentiment_score
        score = float(data["sentiment_score"])
        data["sentiment_score"] = max(-1.0, min(1.0, score))

        # Ensure arrays are lists
        for key in ["key_topics", "strengths", "areas_for_improvement"]:
            if not isinstance(data[key], list):
                data[key] = [str(data[key])]

        return data

    def summarize(self, transcript: str) -> dict[str, Any]:
        """Summarize an interview transcript.

        Args:
            transcript: The interview transcript text.

        Returns:
            Dictionary with executive_summary, key_topics, strengths,
            areas_for_improvement, and sentiment_score.
        """
        pipe = self._load_pipeline()

        # Truncate very long transcripts to fit context window
        max_chars = 100000  # ~25k tokens, safe for 128k context
        if len(transcript) > max_chars:
            logger.warning(
                f"Transcript too long ({len(transcript)} chars), truncating"
            )
            transcript = transcript[:max_chars]

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(transcript=transcript)},
        ]

        logger.info(f"Generating summary for transcript ({len(transcript)} chars)")
        outputs = pipe(messages)
        response_text = outputs[0]["generated_text"][-1]["content"]

        logger.debug(f"Raw LLM response: {response_text[:500]}...")

        try:
            result = self._extract_json(response_text)
            result = self._validate_output(result)
            logger.info("Summary generated successfully")
            return result
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse LLM output: {e}")
            # Return a fallback structure
            return {
                "executive_summary": "Analysis could not be completed.",
                "key_topics": [],
                "strengths": [],
                "areas_for_improvement": [],
                "sentiment_score": 0.0,
            }
