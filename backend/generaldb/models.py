from datetime import datetime
from enum import Enum

from mongoengine import (BooleanField, DateTimeField, Document, EmailField,
                         EmbeddedDocument, EmbeddedDocumentField, EnumField,
                         IntField, ListField, ReferenceField, StringField,
                         connect)

from .config import DATABASE_NAME, MONGODB_URI


# Enum definitions
class Role(str, Enum):
    USER = "user"
    BOT = "bot"

class QuizStatus(str, Enum):
    PREPARING = "preparing"
    GENERATING = "generating"
    READY = "ready"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(int, Enum):
    TYPE_0 = 0
    TYPE_1 = 1
    TYPE_2 = 2

# Embedded documents
class Choice(EmbeddedDocument):
    index = IntField(required=True)
    text = StringField(required=True)

# Document definitions
class User(Document):
    user_id = IntField(primary_key=True)
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email'
        ]
    }

class Project(Document):
    user_id = ReferenceField(User, required=True)
    project_name = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    active = BooleanField(default=True)

class Chat(Document):
    project_id = ReferenceField(Project, required=True)
    title = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    active = BooleanField(default=True)

class Message(Document):
    chat_id = ReferenceField(Chat, required=True)
    role = EnumField(Role, required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)

class File(Document):
    chat_id = ReferenceField(Chat, required=True)
    file_name = StringField(required=True)
    file_type = StringField(required=True)
    size = IntField(required=True)
    upload_date = DateTimeField(default=datetime.utcnow)

class Quiz(Document):
    chat_id = ReferenceField(Chat, required=True)
    status = EnumField(QuizStatus, required=True, default=QuizStatus.PREPARING)
    created_at = DateTimeField(default=datetime.utcnow)
    question_count = IntField(required=True)
    difficulty = EnumField(Difficulty, required=True)

class QuizQuestion(Document):
    quiz_id = ReferenceField(Quiz, required=True)
    question_text = StringField(required=True)
    choices = ListField(EmbeddedDocumentField(Choice))
    correct_answer = ListField(IntField())
    explanation = StringField(required=True)
    type = EnumField(QuestionType, required=True)

class Setting(Document):
    user_id = ReferenceField(User, required=True)
    key = StringField(required=True)
    value = StringField(required=True)

    meta = {
        'indexes': [
            {'fields': ('user_id', 'key'), 'unique': True}
        ]
    }

# Thiết lập kết nối MongoDB
try:
    connect(db=DATABASE_NAME, host=MONGODB_URI)
    print("Kết nối MongoDB Atlas thành công!")
except Exception as e:
    print(f"Lỗi kết nối MongoDB Atlas: {e}") 