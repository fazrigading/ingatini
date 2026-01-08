"""Document management endpoints."""
import logging
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Document, User
from app.schemas import DocumentResponse, DocumentUploadResponse
from app.services.document_parser import extract_text_from_file
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload and process a document with embedding pipeline.
    
    Supports: PDF, DOCX, TXT files.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read file: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    # Create document service
    doc_service = DocumentService(db)
    
    # Create document record
    try:
        document = doc_service.create_document(
            user_id=user_id,
            filename=file.filename,
            file_size=len(file_content),
        )
    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create document record")

    # Extract text from file
    try:
        extracted_text = extract_text_from_file(file.filename, file_content)
    except ValueError as e:
        logger.error(f"Unsupported file format: {str(e)}")
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to extract text: {str(e)}")
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=500, detail="Failed to extract text from document")

    # Generate embeddings
    try:
        embedding_service = EmbeddingService(db)
        chunk_count = embedding_service.embed_document(document.id, extracted_text)
        logger.info(f"Created {chunk_count} chunks for document {document.id}")
    except ValueError as e:
        logger.error(f"Invalid configuration: {str(e)}")
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=500, detail="Embedding service not configured")
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        total_chunks=chunk_count,
        message=f"Document processed successfully with {chunk_count} chunks",
    )


@router.get("/{user_id}", response_model=list[DocumentResponse])
def list_user_documents(user_id: int, db: Session = Depends(get_db)):
    """Get all documents for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    documents = db.query(Document).filter(Document.user_id == user_id).all()
    return documents


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get a specific document."""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document and its chunks."""
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}
