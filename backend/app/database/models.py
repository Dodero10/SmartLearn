from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class ChatHistory(BaseModel):
    id: int
    thread_id: str
    question: str
    answer: str
    created_at: datetime = datetime.now()

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    stock: int
    specifications: dict
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Order(BaseModel):
    id: int
    user_id: str
    product_id: int
    quantity: int
    total_amount: Decimal
    status: str  # pending, confirmed, paid, cancelled
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class UserWallet(BaseModel):
    id: int
    user_id: str
    balance: Decimal
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now() 