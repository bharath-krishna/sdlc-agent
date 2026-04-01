from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ReservationRequest(BaseModel):
    doll_id: str
    start_time: datetime


class ReservationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doll_id: str
    start_time: datetime
    end_time: datetime
