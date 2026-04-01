from pydantic import BaseModel, ConfigDict
from typing import Optional


class DollRequest(BaseModel):
    name: str
    description: str
    price: float
    type: str
    weight: float
    stock_quantity: int


class DollUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    type: Optional[str] = None
    weight: Optional[float] = None
    stock_quantity: Optional[int] = None


class DollModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    price: float
    type: str
    weight: float
    stock_quantity: int


class DollPriceCheck(BaseModel):
    price: float
    weight: float
    shipping_category: str
