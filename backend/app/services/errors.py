"""Service-level error types.

Raised by Gemini-facing services so routers can map failures to the right
HTTP status instead of confusing outages with configuration or 404 errors.
"""


class EmbeddingError(Exception):
    """Embedding generation failed (Gemini API error)."""


class LLMError(Exception):
    """LLM generation failed (Gemini API error or blocked response)."""


class ParsingError(Exception):
    """Document text extraction failed."""
