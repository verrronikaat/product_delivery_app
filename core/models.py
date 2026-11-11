from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    phone: str = Field(index=True)
    address: str

    orders: List["Order"] = Relationship(back_populates="customer")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="new")  # new / paid / delivered / cancelled
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")

    customer: Optional[Customer] = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = Field(gt=0)

    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")