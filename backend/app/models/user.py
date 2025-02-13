import uuid

from sqlalchemy import JSON, UUID, Column, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    settings = Column(JSON, nullable=True)
    
    # Relationships
    chat_threads = relationship("ChatThread", back_populates="user")
    documents = relationship("Document", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user") 