"""Document management service."""
from app.models import Document
from app.services.base import BaseService


class DocumentService(BaseService):
    """Service for document operations."""

    def get_document(self, doc_id: int) -> Document | None:
        """Get document by ID."""
        return self.db.query(Document).filter(Document.id == doc_id).first()

    def get_user_documents(self, user_id: int) -> list[Document]:
        """Get all documents for a user."""
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def create_document(
        self, user_id: int, filename: str, file_path: str = None, file_size: int = None
    ) -> Document:
        """Create a new document record."""
        document = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
        )
        self.db.add(document)
        return self.commit_and_refresh(document)

    def delete_document(self, doc_id: int) -> bool:
        """Delete a document and its chunks."""
        document = self.get_document(doc_id)
        if document:
            self.db.delete(document)
            self.db.commit()
            return True
        return False

    def update_chunk_count(self, doc_id: int, chunk_count: int) -> Document:
        """Update the chunk count for a document."""
        document = self.get_document(doc_id)
        if document:
            document.total_chunks = chunk_count
            return self.commit_and_refresh(document)
        return None
