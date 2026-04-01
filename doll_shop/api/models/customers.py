from pydantic import BaseModel, ConfigDict
from typing import Optional


class CustomerRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class CustomerModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    phone: Optional[str]
