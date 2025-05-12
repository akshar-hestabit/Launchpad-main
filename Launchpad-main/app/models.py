# Module: app/models.py


from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from passlib.context import CryptContext  #


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  
    username = Column(String, index=True, unique=True, nullable=False)  
    email = Column(String, index=True, unique=True, nullable=True)     
    hashed_password = Column(String, nullable=True)
    role = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="user", cascade="all, delete")
    wishlist = relationship("Wishlist", back_populates="user", cascade="all, delete")
    addresses = relationship("Address", back_populates="user")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String, unique=True, index=True, nullable=False)  

    products = relationship("Products", back_populates="category", cascade="all, delete")

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)  
    name = Column(String, index=True, nullable=False)  
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    brand = Column(String, index=True, nullable=True)  
    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False) 

    category = relationship("Category", back_populates="products")
    wishlists = relationship("Wishlist", back_populates="product", cascade="all, delete")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="wishlist")
    product = relationship("Products", back_populates="wishlists")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  
    total_price = Column(Float, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())  
    payment_method = Column(String, nullable=False, default="CARD")

    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete")
    user = relationship("User", back_populates="orders")    
    items = relationship("OrderItem", back_populates="order",overlaps="order_items")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)  
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)  
    price_at_purchase = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Products")

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    user = relationship("User", back_populates="addresses")


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)