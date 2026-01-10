import re
from typing import List


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text) # Remove extra whitespace
    text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text) # Remove special characters but keep basic punctuation
    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    # Simple sentence splitting on periods, question marks, exclamation marks
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_chunks(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    text = clean_text(text)
    chunks = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
        
        if i + chunk_size >= len(text):
            break
    
    return chunks


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count for Gemini models.
    
    Approximation: ~4 characters = 1 token
    """
    return len(text) // 4
