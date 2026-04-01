import uuid
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.modules.database import Base
from datetime import datetime


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    doll_id: Mapped[str] = mapped_column(String, ForeignKey("dolls.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Assuming 1-hour slots as per requirements, but we can store end_time for convenience
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    doll: Mapped["Doll"] = relationship("Doll")
