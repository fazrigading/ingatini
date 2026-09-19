import pytest

from app.services.text_processor import clean_text, split_into_chunks, split_into_sentences


def test_clean_text_preserves_punctuation():
    text = "Hello (world)!  It's  a test: see https://example.com."
    cleaned = clean_text(text)
    assert "(world)" in cleaned
    assert "It's" in cleaned
    assert "test:" in cleaned
    assert "https://example.com." in cleaned


def test_clean_text_normalizes_whitespace():
    assert clean_text("a \t b\nc") == "a b\nc"


def test_clean_text_strips_control_characters():
    assert "\x00" not in clean_text("bad\x00text")


def test_split_into_sentences():
    sentences = split_into_sentences("First one. Second one! Third?tail")
    assert sentences == ["First one.", "Second one!", "Third?tail"]


def test_split_into_chunks_respects_sentence_boundaries():
    text = " ".join(f"Sentence number {i} says something here." for i in range(20))
    chunks = split_into_chunks(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        # No sentence should be cut mid-word
        assert chunk.startswith("Sentence") or chunk.startswith("number") or "says" in chunk
        for sentence in split_into_sentences(chunk):
            assert sentence in text


def test_split_into_chunks_overlap():
    text = " ".join(f"Sentence {i} with some filler words here." for i in range(30))
    chunks = split_into_chunks(text, chunk_size=150, overlap=60)
    for prev, nxt in zip(chunks, chunks[1:]):
        prev_tail = prev.split()[-3:]
        assert any(word in nxt for word in prev_tail)


def test_split_into_chunks_single_sentence_larger_than_chunk():
    long_sentence = "word " * 300
    chunks = split_into_chunks(long_sentence, chunk_size=100, overlap=10)
    assert chunks == [long_sentence.strip()]
