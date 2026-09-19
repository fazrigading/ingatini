import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Document, User
from app.schemas import DocumentResponse, DocumentUploadResponse
from app.services.document_parser import extract_text_from_file
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingError, EmbeddingService
from app.services.errors import ParsingError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _validate_upload(file: UploadFile) -> None:
    """Reject oversize files and disallowed types before reading the body."""
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and process a document with the embedding pipeline.

    Supports PDF, DOCX, TXT files up to 10 MB.
    """
    _validate_upload(file)

    try:
        file_content = file.file.read(MAX_UPLOAD_BYTES + 1)
    except Exception:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(status_code=400, detail="Failed to read uploaded file")

    if len(file_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    doc_service = DocumentService(db)

    try:
        document = doc_service.create_document(
            user_id=current_user.id,
            filename=file.filename,
            file_size=len(file_content),
            content_type=file.content_type,
        )
    except Exception:
        logger.exception("Failed to create document record")
        raise HTTPException(status_code=500, detail="Failed to create document record")

    try:
        extracted_text = extract_text_from_file(file.filename, file_content)
    except ParsingError as e:
        logger.error("Unsupported file format: %s", e)
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to extract text from document %s", document.id)
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=500, detail="Failed to extract text from document")

    try:
        embedding_service = EmbeddingService(db)
        chunk_count = embedding_service.embed_document(document.id, extracted_text)
        logger.info("Created %d chunks for document %d", chunk_count, document.id)
    except EmbeddingError:
        doc_service.delete_document(document.id)
        logger.exception("Embedding failed for document %s", document.id)
        raise HTTPException(status_code=502, detail="Embedding service unavailable")
    except Exception:
        logger.exception("Failed to process document %s", document.id)
        doc_service.delete_document(document.id)
        raise HTTPException(status_code=500, detail="Failed to process document")

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        total_chunks=chunk_count,
        message=f"Document processed successfully with {chunk_count} chunks",
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get all documents owned by the authenticated user."""
    documents = (
        db.query(Document).filter(Document.user_id == current_user.id).all()
    )
    return documents


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific document owned by the authenticated user."""
    document = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a document owned by the authenticated user."""
    document = (
        db.query(Document)
        .filter(Document.id == doc_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}
