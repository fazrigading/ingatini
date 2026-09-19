import pytest

from app.services.embedding_service import (
    EMBEDDING_DIMENSION,
    EmbeddingService,
)
from app.services.errors import EmbeddingError


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    from app.core.config import get_settings

    get_settings.cache_clear()
    svc = EmbeddingService(db=None)
    yield svc
    get_settings.cache_clear()


def _fake_embed(monkeypatch, service, results):
    calls = []

    def fake_embed_content(model, content, output_dimensionality=None):
        calls.append({"content": content, "dim": output_dimensionality})
        return {"embedding": results}

    import google.generativeai as genai

    monkeypatch.setattr(genai, "embed_content", fake_embed_content)
    return calls


def test_generate_embedding_pins_output_dimension(service, monkeypatch):
    calls = _fake_embed(monkeypatch, service, [0.1] * EMBEDDING_DIMENSION)
    embedding = service.generate_embedding("hello")
    assert len(embedding) == EMBEDDING_DIMENSION
    assert calls[0]["dim"] == EMBEDDING_DIMENSION


def test_generate_embeddings_batch_preserves_order(service, monkeypatch):
    results = [[float(i)] * EMBEDDING_DIMENSION for i in range(3)]
    calls = _fake_embed(monkeypatch, service, results)
    embeddings = service.generate_embeddings(["a", "b", "c"])
    assert len(calls) == 1  # single batched API call
    assert embeddings == results


def test_batch_size_mismatch_raises(service, monkeypatch):
    _fake_embed(monkeypatch, service, [[0.1] * EMBEDDING_DIMENSION])
    with pytest.raises(EmbeddingError):
        service.generate_embeddings(["a", "b"])


def test_retries_then_raises_embedding_error(service, monkeypatch):
    import google.generativeai as genai

    monkeypatch.setattr(
        "app.services.embedding_service.time.sleep", lambda s: None
    )
    attempts = []

    def fail(*args, **kwargs):
        attempts.append(1)
        raise RuntimeError("api down")

    monkeypatch.setattr(genai, "embed_content", fail)

    with pytest.raises(EmbeddingError):
        service.generate_embedding("hello")
    assert len(attempts) == 3  # initial + 2 retries


def test_recovers_on_transient_failure(service, monkeypatch):
    import google.generativeai as genai

    monkeypatch.setattr(
        "app.services.embedding_service.time.sleep", lambda s: None
    )
    state = {"n": 0}

    def flaky(model, content, output_dimensionality=None):
        state["n"] += 1
        if state["n"] < 2:
            raise RuntimeError("transient")
        return {"embedding": [0.5] * EMBEDDING_DIMENSION}

    monkeypatch.setattr(genai, "embed_content", flaky)

    embedding = service.generate_embedding("hello")
    assert len(embedding) == EMBEDDING_DIMENSION
    assert state["n"] == 2
