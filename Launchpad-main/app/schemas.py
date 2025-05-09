

from pydantic import BaseModel, EmailStr 
from typing import Literal
from datetime import datetime

# -------- User Schemas -------- #

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str | None = "customer"

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str 

class TokenData(BaseModel):
    username: str | None = None


# -------- Category, Brand, Vendor Nested Schemas -------- #

class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }

class BrandOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }



# -------- Product Schemas -------- #

class ProductBase(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    quantity: int
    category_id: int
    brand: str | None = None

class ProductCreate(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    quantity: int
    category_id: int
    brand: str | None = None

class ProductUpdate(ProductBase):
    pass

class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    category_id: int
    brand: str | None=None        # changed from brand: Optional[str]

    model_config = {
        "from_attributes": True
    }


# -------- Order Schemas -------- #

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    

class OrderCreate(BaseModel):
    user_id: int
    total_price: float
    payment_method: str
    status: str | None = "PENDING"
    items: list[OrderItemCreate]

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
    model_config = {
        "from_attributes": True
    }
    
class OrderOut(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    payment_method: str | None = None
    items: list[OrderItemOut]
    model_config = {
        "from_attributes": True
    }

# -------- Wishlist Schemas -------- #
class WishlistBase(BaseModel):
    user_id: int
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(WishlistBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
