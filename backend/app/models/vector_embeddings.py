from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    # Stored as JSON string vector for universal compatibility (SQLite/PostgreSQL)
    embedding_json = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="chunks")
