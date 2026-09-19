from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class RegisterRequest(UserBase):
    """Schema for registering a new account."""

    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenResponse(BaseModel):
    """Schema for the login response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""

    filename: str = Field(..., min_length=1, max_length=255)


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


# Query Schemas
class QueryRequest(BaseModel):
    """Schema for a user query."""

    query_text: str = Field(..., min_length=1, max_length=2000)
    document_ids: Optional[List[int]] = None
    top_k: int = Field(5, ge=1, le=20)


class RetrievedChunk(BaseModel):
    """A chunk retrieved by vector search, with its similarity score."""

    id: int
    document_id: int
    chunk_index: int
    content: str
    token_count: Optional[int] = None
    similarity: float


class QueryResponse(BaseModel):
    """Schema for query response."""

    query_text: str
    response: str
    retrieved_chunks: list[RetrievedChunk]
    response_time_ms: float


# Upload Response
class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""

    id: int
    filename: str
    total_chunks: int
    message: str
