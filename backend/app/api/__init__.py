from fastapi import APIRouter

from app.api import auth, documents, health, query

# Create main router
api_router = APIRouter()

# Include all routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(query.router)

__all__ = ["api_router"]
