from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # allows reading from ORM objects
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductBase(BaseModel):
    name: str
    description: str = ""
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    image_url: str | None = None
    category_id: int | None = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    shipping_address: str
    items: list[OrderItemIn] = Field(min_length=1)

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total: Decimal
    shipping_address: str
    created_at: datetime
    items: list[OrderItemOut]

class CategoriesBase(BaseModel):
    name: str

class CategoriesCreate(CategoriesBase):
    pass

class CategoriesOut(CategoriesBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class CategoriesUpdate(CategoriesBase):
    name: str | None = None