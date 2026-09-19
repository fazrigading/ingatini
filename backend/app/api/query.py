from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import QueryRequest, QueryResponse
from app.services.embedding_service import EmbeddingError
from app.services.errors import LLMError
from app.services.rag_service import RAGService

import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_documents(
    query: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Query the authenticated user's documents using the RAG pipeline."""
    started = time.monotonic()
    try:
        rag_service = RAGService(db)
        result = rag_service.query_documents(
            user_id=current_user.id,
            query_text=query.query_text,
            document_ids=query.document_ids,
            top_k=query.top_k,
        )
    except EmbeddingError:
        logger.exception("Embedding failed during query")
        raise HTTPException(status_code=502, detail="Embedding service unavailable")
    except LLMError:
        logger.exception("LLM generation failed during query")
        raise HTTPException(status_code=502, detail="AI service unavailable")
    except Exception:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail="Query failed")

    elapsed_ms = (time.monotonic() - started) * 1000
    return QueryResponse(
        query_text=result["query"],
        response=result["response"],
        retrieved_chunks=result["retrieved_chunks"],
        response_time_ms=round(elapsed_ms, 2),
    )


@router.get("/history")
def get_query_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get query history for the authenticated user."""
    limit = max(1, min(limit, 100))
    try:
        rag_service = RAGService(db)
        history = rag_service.get_query_history(current_user.id, limit=limit)
    except Exception:
        logger.exception("Failed to retrieve query history")
        raise HTTPException(status_code=500, detail="Failed to retrieve query history")
    return {"user_id": current_user.id, "history": history}
