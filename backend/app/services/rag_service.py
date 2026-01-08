"""RAG query service for retrieval-augmented generation."""
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Chunk, QueryLog, User
from app.services.embedding_service import EmbeddingService

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
        
        genai.configure(api_key=self.settings.google_api_key)

    def query_documents(
        self,
        user_id: int,
        query_text: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
    ) -> dict:
        """
        Query documents using RAG pipeline.
        
        Steps:
        1. Verify user exists
        2. Retrieve relevant chunks using vector search
        3. Augment with LLM for final response
        4. Log the query
        
        Args:
            user_id: User ID
            query_text: Query text
            document_ids: Filter to specific documents
            top_k: Number of chunks to retrieve
        
        Returns:
            Dict with query, response, and retrieved chunks
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Retrieve similar chunks
        retrieved_chunks = self.embedding_service.search_similar_chunks(
            query_text=query_text,
            document_ids=document_ids,
            top_k=top_k,
        )

        if not retrieved_chunks:
            logger.warning(f"No similar chunks found for query: {query_text}")
            response = "No relevant information found in your documents."
            chunks_data = []
        else:
            # Build context from retrieved chunks
            context = "\n\n".join([
                f"[Document {c.document_id}, Chunk {c.chunk_index}]:\n{c.content}"
                for c in retrieved_chunks
            ])

            # Generate LLM response
            try:
                model = genai.GenerativeModel(self.settings.gemini_llm_model)
                prompt = f"""You are a helpful assistant that answers questions based on the provided context. Always cite your sources from the context.

Context:
{context}

Question: {query_text}

Provide a comprehensive answer based on the context."""
                
                llm_response = model.generate_content(prompt)
                response = llm_response.text
            except Exception as e:
                logger.error(f"Failed to generate LLM response: {str(e)}")
                response = f"Error generating response: {str(e)}"

            # Prepare chunks data
            chunks_data = [
                {
                    "id": c.id,
                    "document_id": c.document_id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "token_count": c.token_count,
                }
                for c in retrieved_chunks
            ]

        # Log the query
        query_log = QueryLog(
            user_id=user_id,
            query_text=query_text,
            response=response[:500],  # Store first 500 chars
            retrieved_chunks_count=len(retrieved_chunks),
        )
        self.db.add(query_log)
        self.db.commit()

        return {
            "query": query_text,
            "response": response,
            "retrieved_chunks": chunks_data,
            "chunk_count": len(retrieved_chunks),
        }

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
