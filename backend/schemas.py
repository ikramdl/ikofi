from pydantic import BaseModel
from typing import List
from datetime import datetime


class OrderItemCreate(BaseModel):
    item_id: int
    quantity :int

class MenuItemResponse(BaseModel):
    id: int
    name: str
    price: int

    class config:
        from_attributes: True

class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    grand_total: float
    status: str
    items: List[OrderItemCreate]

    class config:
        from_attributes: True
