"""Embedding service for generating and storing vector embeddings."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Chunk, Document
from app.services.text_processor import estimate_tokens, split_into_chunks

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class EmbeddingService:
    """Service for generating embeddings using Google Gemini API."""

    def __init__(self, db: Session):
        """Initialize embedding service."""
        self.db = db
        self.settings = get_settings()
        
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")
        
        if not self.settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Configure Gemini client
        genai.configure(api_key=self.settings.gemini_api_key)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Google Gemini API.
        
        Returns:
            List of floats representing the embedding vector
        """
        if not self.settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            result = genai.embed_content(
                model=self.settings.gemini_embedding_model,
                content=text,
            )
            return result['embedding']
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")

    def embed_document(self, document_id: int, text: str) -> int:
        """
        Process document text and create embeddings for chunks.
        
        Args:
            document_id: ID of the document
            text: Full text content
        
        Returns:
            Number of chunks created
        """
        # Get document
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Split into chunks
        chunks = split_into_chunks(text, chunk_size=512, overlap=50)
        
        # Create Chunk records with embeddings
        chunk_records = []
        for idx, chunk_text in enumerate(chunks):
            # Generate embedding
            embedding = self.generate_embedding(chunk_text)
            
            # Create chunk record
            chunk_record = Chunk(
                document_id=document_id,
                chunk_index=idx,
                content=chunk_text,
                token_count=estimate_tokens(chunk_text),
                embedding=embedding,
                embedding_model=self.settings.gemini_embedding_model,
            )
            chunk_records.append(chunk_record)
            self.db.add(chunk_record)
        
        # Update document chunk count
        document.total_chunks = len(chunks)
        
        # Commit all changes
        self.db.commit()
        
        return len(chunks)

    def search_similar_chunks(
        self,
        query_text: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
    ) -> List[Chunk]:
        """
        Search for chunks similar to query using vector similarity.
        
        Args:
            query_text: Query text
            document_ids: Filter by document IDs
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of similar chunks
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Search in database using vector similarity
        # Note: PostgreSQL pgvector allows using <-> operator for L2 distance
        query = self.db.query(Chunk).order_by(
            Chunk.embedding.op('<->')(query_embedding)
        )
        
        # Filter by documents if specified
        if document_ids:
            query = query.filter(Chunk.document_id.in_(document_ids))
        
        # Get top k results
        chunks = query.limit(top_k).all()
        
        return chunks
