"""Base service class for business logic."""
from abc import ABC


class BaseService(ABC):
    """Base service class with common functionality."""

    def __init__(self, db):
        """Initialize service with database session."""
        self.db = db

    def commit_and_refresh(self, obj):
        """Commit changes and refresh object."""
        self.db.commit()
        self.db.refresh(obj)
        return obj
