from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String(100), nullable = False)
    price = Column(Numeric(10, 2), nullable = False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key = True, index = True)
    created_at = Column(DateTime, default=datetime.utcnow)
    grand_total  = Column(Numeric(10,2), nullable = False)
    satus = Column(String(50), default = "Confirmed")

    items = relationship("OrderItem", back_populates = "order", cascade = "all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=False)
    item_id = Column(Integer, ForeignKey("menu_items.id"), index=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")