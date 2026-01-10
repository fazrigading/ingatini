from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""

    filename: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    """Schema for uploading a document."""

    user_id: int


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    id: int
    user_id: int
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    total_chunks: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chunk Schemas
class ChunkResponse(BaseModel):
    """Schema for chunk response."""

    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for a user query."""

    user_id: int
    query_text: str = Field(..., min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    """Schema for query response."""

    query_text: str
    response: str
    retrieved_chunks: list[ChunkResponse]
    response_time_ms: float

    class Config:
        from_attributes = True


class QueryLogResponse(BaseModel):
    """Schema for query log."""

    id: int
    user_id: int
    query_text: str
    response: Optional[str] = None
    retrieved_chunks_count: int
    response_time_ms: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Upload Response
class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""

    id: int
    filename: str
    total_chunks: int
    message: str
