import enum
import uuid

from sqlalchemy import (JSON, UUID, Boolean, Column, Enum, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class QuestionType(enum.Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    open_ended = "open_ended"

class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    settings = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    explanation = Column(Text)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="question")

class Option(Base, TimestampMixin):
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    user_answers = relationship("UserAnswer", back_populates="selected_option")

class QuizAttempt(Base, TimestampMixin):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score = Column(Integer)
    total_questions = Column(Integer)
    duration = Column(Integer)  # in seconds
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")
    answers = relationship("UserAnswer", back_populates="attempt", cascade="all, delete-orphan")

class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"))
    is_correct = Column(Boolean)
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("Question", back_populates="user_answers")
    selected_option = relationship("Option", back_populates="user_answers") 