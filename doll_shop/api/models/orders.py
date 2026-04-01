from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class OrderItemRequest(BaseModel):
    doll_id: str
    quantity: int


class OrderRequest(BaseModel):
    customer_id: str
    items: List[OrderItemRequest]


class OrderItemModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doll_id: str
    quantity: int
    unit_price: float


class OrderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    created_at: datetime
    total_amount: float
    items: List[OrderItemModel]
