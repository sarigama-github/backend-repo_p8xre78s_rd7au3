"""
Database Schemas for Custom Creations Co.

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
- Product -> "product"
- Project -> "project"
- Order -> "order"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal

# Core domain schemas

Category = Literal["clothing", "vehicle", "gadgets"]

class Product(BaseModel):
    title: str = Field(..., description="Product name")
    description: Optional[str] = Field(None, description="Details about the product")
    price: float = Field(..., ge=0, description="Price in USD")
    category: Category = Field(..., description="Product category")
    image_url: Optional[str] = Field(None, description="Primary image URL")
    tags: Optional[List[str]] = Field(default_factory=list, description="Search tags")
    in_stock: bool = Field(True, description="Availability flag")

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    summary: Optional[str] = Field(None, description="Short project blurb")
    service: Category = Field(..., description="Service category represented")
    hero_image: Optional[str] = Field(None, description="Main showcase image")
    gallery: Optional[List[str]] = Field(default_factory=list, description="Additional images")
    client: Optional[str] = Field(None, description="Client or brand name")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced product ObjectId as string")
    quantity: int = Field(1, ge=1, description="Quantity ordered")

class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class Order(BaseModel):
    items: List[OrderItem]
    customer: CustomerInfo
    notes: Optional[str] = None
    status: Literal["pending", "confirmed", "in_progress", "completed", "cancelled"] = "pending"

# Simple health schema to keep example users/products from template if needed
class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    age: Optional[int] = None
    is_active: bool = True
