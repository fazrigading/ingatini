import re
from typing import List


def clean_text(text: str) -> str:
    """Normalize whitespace and strip control characters, preserving punctuation."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences on punctuation and paragraph breaks."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_chunks(
    text: str,
    chunk_size: int = 1024,
    overlap: int = 100,
) -> List[str]:
    """
    Split text into overlapping, sentence-aligned chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Target overlap between consecutive chunks in characters

    Returns:
        List of text chunks
    """
    text = clean_text(text)
    sentences = split_into_sentences(text)
    chunks = []

    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        if current and current_len + len(sentence) + 1 > chunk_size:
            chunks.append(" ".join(current))

            # Carry trailing sentences forward as overlap
            tail: List[str] = []
            tail_len = 0
            for prev in reversed(current):
                if tail_len + len(prev) + 1 > overlap:
                    break
                tail.insert(0, prev)
                tail_len += len(prev) + 1
            current = tail
            current_len = sum(len(s) + 1 for s in current) - 1 if current else 0

        current.append(sentence)
        current_len += len(sentence) + 1

    if current:
        chunks.append(" ".join(current))

    return [chunk for chunk in chunks if chunk.strip()]


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count for Gemini models.

    Approximation: ~4 characters = 1 token
    """
    return len(text) // 4
