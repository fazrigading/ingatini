from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Health check endpoint that verifies database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "service": "ingatini-api", "database": "ok"}
    except Exception:
        return {"status": "degraded", "service": "ingatini-api", "database": "unreachable"}
