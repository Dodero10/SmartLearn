import enum
import uuid

from sqlalchemy import UUID, Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class FunctionType(enum.Enum):
    tutor = "tutor"
    video = "video"
    quiz = "quiz"

class ModelType(enum.Enum):
    gpt4 = "gpt-4"
    gpt35 = "gpt-3.5-turbo"
    claude3 = "claude-3"

class ChatThread(Base, TimestampMixin):
    __tablename__ = "chat_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    function_type = Column(Enum(FunctionType), nullable=False, default=FunctionType.tutor)
    model_type = Column(Enum(ModelType), nullable=False, default=ModelType.gpt4)
    
    # Relationships
    user = relationship("User", back_populates="chat_threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=False)
    
    # Relationships
    thread = relationship("ChatThread", back_populates="messages") 