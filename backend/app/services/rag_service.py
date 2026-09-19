import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Chunk, QueryLog
from app.services.embedding_service import EmbeddingService
from app.services.errors import LLMError

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class RAGService:
    """Service for RAG-based Q&A using Google Gemini."""

    def __init__(self, db: Session):
        """Initialize RAG service."""
        self.db = db
        self.settings = get_settings()
        self.embedding_service = EmbeddingService(db)

        if genai is None:
            raise ImportError("google-generativeai is required")

        genai.configure(api_key=self.settings.gemini_api_key)

    def query_documents(
        self,
        user_id: int,
        query_text: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
    ) -> dict:
        """
        Query documents using the RAG pipeline.

        Steps:
        1. Retrieve relevant chunks using owner-scoped vector search
        2. Augment with LLM for final response
        3. Log the query

        Args:
            user_id: Authenticated user ID (search is scoped to their documents)
            query_text: Query text
            document_ids: Optional narrowing to specific documents
            top_k: Number of chunks to retrieve

        Returns:
            Dict with query, response, and retrieved chunks
        """
        retrieved = self.embedding_service.search_similar_chunks(
            user_id=user_id,
            query_text=query_text,
            document_ids=document_ids,
            top_k=top_k,
        )

        if not retrieved:
            logger.warning("No similar chunks found for query: %s", query_text)
            response = "No relevant information found in your documents."
            chunks_data = []
        else:
            context = "\n\n".join(
                [
                    f"[Document {chunk.document_id}, Chunk {chunk.chunk_index}]:\n{chunk.content}"
                    for chunk, _ in retrieved
                ]
            )

            response = self._generate_answer(context, query_text)

            chunks_data = [
                {
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "token_count": chunk.token_count,
                    "similarity": round(similarity, 4),
                }
                for chunk, similarity in retrieved
            ]

        query_log = QueryLog(
            user_id=user_id,
            query_text=query_text,
            response=response,
            retrieved_chunks_count=len(retrieved),
        )
        self.db.add(query_log)
        self.db.commit()

        return {
            "query": query_text,
            "response": response,
            "retrieved_chunks": chunks_data,
            "chunk_count": len(retrieved),
        }

    def _generate_answer(self, context: str, query_text: str) -> str:
        """Generate an LLM answer from context; raises LLMError on failure."""
        model = genai.GenerativeModel(self.settings.gemini_llm_model)
        prompt = f"""You are a helpful assistant that answers questions based on the provided context. Always cite your sources from the context. If the context does not contain the answer, say so.

Context:
{context}

Question: {query_text}

Provide a comprehensive answer based on the context."""

        try:
            llm_response = model.generate_content(prompt)
            return llm_response.text
        except Exception as e:
            logger.error("Failed to generate LLM response: %s", e)
            raise LLMError(f"LLM generation failed: {e}")

    def get_query_history(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get query history for a user."""
        logs = (
            self.db.query(QueryLog)
            .filter(QueryLog.user_id == user_id)
            .order_by(QueryLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": log.id,
                "query": log.query_text,
                "response": log.response,
                "chunks_count": log.retrieved_chunks_count,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
