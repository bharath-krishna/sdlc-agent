from sqlalchemy import select, and_, or_
from api.modules import BaseModule
from api.exceptions.api import APIError
from api.schemas.reservations import Reservation
from api.schemas.dolls import Doll
from datetime import datetime, timedelta


class ReservationsModule(BaseModule):

    async def list_reservations(self):
        result = await self.db.execute(select(Reservation))
        return result.scalars().all()

    async def create_reservation(self, body):
        # 1. Check if doll exists
        doll_result = await self.db.execute(select(Doll).where(Doll.id == body.doll_id))
        doll = doll_result.scalar_one_or_none()
        if not doll:
            raise APIError("not_found", field="doll_id", value=body.doll_id)

        # 2. Check if reservation time is in the future
        if body.start_time <= datetime.utcnow():
            raise APIError("invalid_reservation_time")

        # 3. Calculate end time (1 hour slot)
        end_time = body.start_time + timedelta(hours=1)

        # 4. Check for overlapping reservations
        # Overlap if: existing_start < new_end AND existing_end > new_start
        overlap_query = select(Reservation).where(
            and_(
                Reservation.doll_id == body.doll_id,
                Reservation.start_time < end_time,
                Reservation.end_time > body.start_time
            )
        )
        overlap_result = await self.db.execute(overlap_query)
        if overlap_result.scalars().first():
            raise APIError("reservation_overlap")

        # 5. Create reservation
        reservation = Reservation(
            doll_id=body.doll_id,
            start_time=body.start_time,
            end_time=end_time
        )
        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation

    async def cancel_reservation(self, res_id: str):
        result = await self.db.execute(select(Reservation).where(Reservation.id == res_id))
        reservation = result.scalar_one_or_none()
        if not reservation:
            raise APIError("not_found", field="res_id", value=res_id)
        
        await self.db.delete(reservation)
        await self.db.commit()
        return reservation
