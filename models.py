from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    mobile: str = Field(unique=True)
    address: str
    password: str
    role: str = Field(default="BUYER")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    seller_id: int = Field(foreign_key="user.id")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="user.id")
    seller_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(gt=0)
    price: float
    total_amount: float
    order_status: str = Field(default="SUCCESS")
    created_at: datetime = Field(default_factory=datetime.utcnow)
