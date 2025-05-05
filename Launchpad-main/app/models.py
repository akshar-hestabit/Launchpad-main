# Module: app/models.py
# Brief: TODO - add description

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from passlib.context import CryptContext  # For password hashing

# Setup the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Primary key = already indexed
    username = Column(String, index=True, unique=True, nullable=False)  # Search/login
    email = Column(String, index=True, unique=True, nullable=False)     # Search/login
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    orders = relationship("Order", back_populates="user", cascade="all, delete")
    wishlist = relationship("Wishlist", back_populates="user", cascade="all, delete")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)  # Primary key
    name = Column(String, unique=True, index=True, nullable=False)  # Filter/search by category name

    products = relationship("Products", back_populates="category", cascade="all, delete")

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)  # Primary key
    name = Column(String, index=True, nullable=False)  # Search by product name
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    brand = Column(String, index=True, nullable=True)  # Filter by brand
    category_id = Column(Integer, ForeignKey("categories.id"), index=True, nullable=False)  # Filter by category

    category = relationship("Category", back_populates="products")
    wishlists = relationship("Wishlist", back_populates="product", cascade="all, delete")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # Look up by user
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)  # Look up by product
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="wishlist")
    product = relationship("Products", back_populates="wishlists")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)  # Filter by user
    total_price = Column(Float, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), index=True, server_default=func.now())  # Sort by date
    payment_method = Column(String, nullable=False, default="CARD")

    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete")
    user = relationship("User", back_populates="orders")    
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)  # Join/fetch invoice
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)  # Join/fetch product
    price_at_purchase = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")
    product = relationship("Products")
