import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
async def query_documents(
    query: QueryRequest,
    document_ids: Optional[List[int]] = None,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    """Query documents using RAG pipeline.
    
    Performs vector similarity search and generates LLM-augmented responses.
    """
    try:
        rag_service = RAGService(db)
        result = rag_service.query_documents(
            user_id=query.user_id,
            query_text=query.query_text,
            document_ids=document_ids,
            top_k=top_k,
        )
        
        return QueryResponse(
            query_text=result["query"],
            response=result["response"],
            retrieved_chunks=result["retrieved_chunks"],
            response_time_ms=0.0,  # TODO: Add timing
        )
    except ValueError as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except ImportError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail="RAG service not configured")
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/history/{user_id}")
async def get_query_history(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """Get query history for a user."""
    try:
        rag_service = RAGService(db)
        history = rag_service.get_query_history(user_id, limit=limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve query history")
