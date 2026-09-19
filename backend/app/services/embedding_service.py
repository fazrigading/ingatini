import logging
import time
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Chunk, Document
from app.services.errors import EmbeddingError
from app.services.text_processor import estimate_tokens, split_into_chunks

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None

EMBEDDING_DIMENSION = 768
GEMINI_MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 1.0


class EmbeddingService:
    """Service for generating embeddings using Google Gemini API."""

    def __init__(self, db: Session):
        """Initialize embedding service."""
        self.db = db
        self.settings = get_settings()

        if genai is None:
            raise ImportError(
                "google-generativeai is required. Install with: pip install google-generativeai"
            )

        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

        genai.configure(api_key=self.settings.gemini_api_key)

    def _embed_with_retry(self, content):
        """Call Gemini embeddings with retry/backoff; returns list(s) of floats."""
        last_error = None
        for attempt in range(GEMINI_MAX_RETRIES + 1):
            try:
                result = genai.embed_content(
                    model=self.settings.gemini_embedding_model,
                    content=content,
                    output_dimensionality=EMBEDDING_DIMENSION,
                )
                return result["embedding"]
            except Exception as e:
                last_error = e
                if attempt < GEMINI_MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
        raise EmbeddingError(f"Failed to generate embedding: {last_error}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for a single text."""
        return self._embed_with_retry(text)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts in one API call."""
        if not texts:
            return []
        result = self._embed_with_retry(texts)
        if len(result) != len(texts):
            raise EmbeddingError(
                f"Gemini returned {len(result)} embeddings for {len(texts)} inputs"
            )
        return result

    def embed_document(self, document_id: int, text: str) -> int:
        """
        Process document text and create embeddings for chunks.

        Args:
            document_id: ID of the document
            text: Full text content

        Returns:
            Number of chunks created
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise EmbeddingError(f"Document {document_id} not found")

        chunks = split_into_chunks(text, chunk_size=1024, overlap=100)
        if not chunks:
            raise EmbeddingError(f"Document {document_id} produced no text chunks")

        embeddings = self.generate_embeddings(chunks)

        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            self.db.add(
                Chunk(
                    document_id=document_id,
                    chunk_index=idx,
                    content=chunk_text,
                    token_count=estimate_tokens(chunk_text),
                    embedding=embedding,
                    embedding_model=self.settings.gemini_embedding_model,
                )
            )

        document.total_chunks = len(chunks)
        self.db.commit()

        return len(chunks)

    def search_similar_chunks(
        self,
        user_id: int,
        query_text: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for chunks similar to a query, scoped to documents owned by `user_id`.

        Uses cosine distance (`<=>`) on pgvector; returns (chunk, similarity) pairs
        with similarity >= similarity_threshold, best first.
        """
        query_embedding = self.generate_embedding(query_text)

        # Cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite.
        max_distance = 1.0 - similarity_threshold
        query = (
            self.db.query(Chunk, (1.0 - Chunk.embedding.op("<=>")(query_embedding)).label("similarity"))
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.user_id == user_id)
            .filter(Chunk.embedding.op("<=>")(query_embedding) < max_distance)
            .order_by(Chunk.embedding.op("<=>")(query_embedding))
            .limit(top_k)
        )

        if document_ids:
            query = query.filter(Chunk.document_id.in_(document_ids))

        return [(chunk, float(similarity)) for chunk, similarity in query.all()]
