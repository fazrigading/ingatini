from datetime import datetime, timezone
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """User data model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    documents = relationship("Document", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Document(Base):
    """Document metadata model."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    content_type = Column(String(100), nullable=True)
    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"


class Chunk(Base):
    """Text chunk extracted from documents with embeddings."""

    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)  # Approximate token count
    embedding = Column(Vector(768), nullable=True)  # gemini-embedding-001 @ 768-d
    embedding_model = Column(String(100), default="gemini-embedding-001")
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id})>"


class QueryLog(Base):
    """Log of user queries for analytics and debugging."""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    retrieved_chunks_count = Column(Integer, default=0)
    response_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    def __repr__(self):
        return f"<QueryLog(id={self.id}, user_id={self.user_id})>"
