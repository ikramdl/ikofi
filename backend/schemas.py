from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class OrderItemCreate(BaseModel):
    item_id: int
    quantity :int

class MenuItemResponse(BaseModel):
    id: int
    name: str
    price: int

    model_config = ConfigDict(from_attributes=True)

class OrderItemResponse(BaseModel):
    id: int
    name: str
    price: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    grand_total: float
    status: str
    items: List[OrderItemCreate]

    model_config = ConfigDict(from_attributes=True)
