from fastapi import APIRouter

from app.api import documents, health, query, users

# Create main router
api_router = APIRouter()

# Include all routers
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(documents.router)
api_router.include_router(query.router)

__all__ = ["api_router"]
