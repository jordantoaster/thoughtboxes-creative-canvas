"""
Transcript Ingestor — Component B.

Accepts raw transcript text, cleans it, and splits it into chunks
for downstream LLM processing.
"""

import logging
import re
from app.models import CleanedTranscript

log = logging.getLogger(__name__)

# Patterns treated as low-signal and stripped before processing
_TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(:\d{2})?\b")
_FILLER_RE = re.compile(
    r"\b(um+|uh+|er+|ah+|you know|like,|sort of,|kind of,)\b",
    re.IGNORECASE,
)
_SPEAKER_LABEL_RE = re.compile(r"^[A-Z][A-Za-z ]+:\s*", re.MULTILINE)

CHUNK_SIZE = 1500  # characters per chunk sent to LLM


def _clean(text: str) -> str:
    text = _TIMESTAMP_RE.sub("", text)
    text = _SPEAKER_LABEL_RE.sub("", text)
    text = _FILLER_RE.sub("", text)
    # Collapse excess whitespace
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _chunk(text: str) -> list[str]:
    """Split on paragraph boundaries, accumulating paragraphs until CHUNK_SIZE is reached."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        if current and current_len + len(para) > CHUNK_SIZE:
            chunks.append("\n\n".join(current))
            current, current_len = [], 0
        current.append(para)
        current_len += len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def ingest(session_id: str, raw_text: str) -> CleanedTranscript:
    log.info(
        "Ingestor  session=%s  raw_chars=%d  raw_lines=%d",
        session_id,
        len(raw_text),
        raw_text.count("\n"),
    )
    cleaned = _clean(raw_text)
    chunks = _chunk(cleaned)
    reduction = 100 * (1 - len(cleaned) / max(len(raw_text), 1))
    log.info(
        "Ingestor done  session=%s  cleaned_chars=%d  chunks=%d  reduction=%.0f%%",
        session_id,
        len(cleaned),
        len(chunks),
        reduction,
    )
    return CleanedTranscript(
        session_id=session_id,
        raw_text=raw_text,
        cleaned_text=cleaned,
        chunks=chunks,
    )
