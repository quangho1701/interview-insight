# Phase 5 Research: Transcription & Summarization (Jan 2026)

## 1. Executive Summary
This document outlines the state-of-the-art (SOTA) technologies available in January 2026 for implementing the transcription and summarization pipeline for VibeCheck.

**Recommendation:**
- **Transcription:** `faster-whisper` (Implementation of OpenAI Whisper using CTranslate2).
- **Summarization:** `Meta Llama 3.3 8B Instruct` (run locally via `transformers` or `vllm` for speed).

## 2. Transcription: State of the Art
### Top Contenders
1.  **OpenAI Whisper V3 (and variants):** Remains the gold standard for robust, multilingual speech recognition.
    -   *Pros:* High accuracy, handles accents/noise well, timestamp alignment.
    -   *Cons:* Standard PyTorch implementation can be slow.
2.  **Faster-Whisper:** A reimplementation using CTranslate2.
    -   *Pros:* Up to 4x faster than standard Whisper with significantly lower memory usage.
    -   *Cons:* Requires slightly different API usage than the core generic library.
3.  **Deepgram (API):** Extremely fast, but violates our "local/private" preference if we want to keep costs zero and data internal.

### Selected Approach: `faster-whisper`
We will use the `large-v3` model (or `distil-large-v3` for speed) via `faster-whisper`.
- **Reasoning:** It provides the best balance of SOTA accuracy and inference speed on consumer/cloud GPUs (e.g., T4, A10, L4). It runs completely offline, ensuring data privacy (Audio Deletion policy).

## 3. Summarization: State of the Art
### Top Contenders
1.  **Meta Llama 3.3 (8B / 70B):** The standard for open-weights LLMs. The 8B Instruct version is perfectly sized for summarization tasks on a single GPU.
2.  **Qwen 3 (72B / 14B):** Excellent performance, specifically in reasoning, but Llama usually has better ecosystem optimization (vLLM support, quantization).
3.  **Mistral / Mixtral:** Strong contenders, but Llama 3.3 generally edges out on instruction following for structured summaries (JSON output).

### Selected Approach: `Llama 3.3 8B Instruct`
We will run a quantized (4-bit or 8-bit) version of Llama 3.3 8B using `bitsandbytes` + `transformers` or `vllm`.
- **Reasoning:** 8B parameters fit comfortably in <16GB VRAM (standard on most cloud GPU instances). It is powerful enough to summarize interview transcripts into structured JSON (Key Takeaways, Pros/Cons).

## 4. Implementation Strategy (Phase 5)

### Architecture
The Worker service will need to load these models into memory.
- **Cold vs Warm Start:** Loading models takes time. Ideally, the Celery worker has a global `ModelManager` that loads models on startup or first request and keeps them in GPU VRAM (if persistent).
- **GPU Memory Management:**
    -   Whisper Large-v3: ~3GB VRAM.
    -   Llama 3.3 8B (4-bit): ~6GB VRAM.
    -   **Total:** ~10GB. Fits easily on an NVIDIA T4 (16GB) or A10 (24GB).

### Prompt Engineering for Summarization
We need a strict system prompt to ensure the LLM returns consistent sections:
1.  **Executive Summary:** 2-3 sentences.
2.  **Key Topics:** Bullet points.
3.  **Strengths:** Evidence-based observations.
4.  **Areas for Improvement:** Constructive feedback.

### Proposed Python Stack
- `faster-whisper`
- `torch`
- `transformers`
- `accelerate`
- `bitsandbytes` (for 4-bit loading)
- `scipy` (for audio processing utilities)

## 5. Risks & Mitigations
- **Long Audio Files:** Whisper handles 30s chunks, but the LLM context window is the limit. Llama 3.3 supports 128k context, which is plenty for even 1-2 hour interviews.
- **Hallucination:** Set `temperature=0.1` to minimize creative writing. Focus on extraction.
