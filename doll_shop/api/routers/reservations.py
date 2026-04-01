from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.reservations import ReservationsModule
from api.modules.database import get_db
from api.models.auth import require_user
from api.models.reservations import ReservationRequest, ReservationModel

router = APIRouter()


@router.get(
    '/reservations',
    tags=['Reservations'],
    summary='List Reservations',
    response_model=List[ReservationModel],
)
async def list_reservations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = ReservationsModule(request, db)
    return await module.list_reservations()


@router.post(
    '/reservations',
    tags=['Reservations'],
    summary='Create Reservation',
    response_model=ReservationModel,
)
async def create_reservation(
    request: Request,
    body: ReservationRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = ReservationsModule(request, db)
    return await module.create_reservation(body)


@router.delete(
    '/reservations/{res_id}',
    tags=['Reservations'],
    summary='Cancel Reservation',
    response_model=ReservationModel,
)
async def cancel_reservation(
    request: Request,
    res_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = ReservationsModule(request, db)
    return await module.cancel_reservation(res_id)
