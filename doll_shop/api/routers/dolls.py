from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.dolls import DollsModule
from api.modules.database import get_db
from api.models.auth import require_user
from api.models.dolls import DollRequest, DollUpdate, DollModel, DollPriceCheck

router = APIRouter()


@router.get(
    '/dolls',
    tags=['Dolls'],
    summary='List Dolls',
    response_model=List[DollModel],
)
async def list_dolls(
    request: Request,
    type: str = None,
    db: AsyncSession = Depends(get_db),
):
    module = DollsModule(request, db)
    return await module.list_dolls(type=type)


@router.get(
    '/dolls/{doll_id}',
    tags=['Dolls'],
    summary='Get Doll',
    response_model=DollModel,
)
async def get_doll(
    request: Request,
    doll_id: str,
    db: AsyncSession = Depends(get_db),
):
    module = DollsModule(request, db)
    return await module.get_doll(doll_id)


@router.post(
    '/dolls',
    tags=['Dolls'],
    summary='Create Doll',
    response_model=DollModel,
)
async def create_doll(
    request: Request,
    body: DollRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = DollsModule(request, db)
    return await module.create_doll(body)


@router.put(
    '/dolls/{doll_id}',
    tags=['Dolls'],
    summary='Update Doll',
    response_model=DollModel,
)
async def update_doll(
    request: Request,
    doll_id: str,
    body: DollUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = DollsModule(request, db)
    return await module.update_doll(doll_id, body)


@router.delete(
    '/dolls/{doll_id}',
    tags=['Dolls'],
    summary='Delete Doll',
    response_model=DollModel,
)
async def delete_doll(
    request: Request,
    doll_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = DollsModule(request, db)
    return await module.delete_doll(doll_id)


@router.get(
    '/dolls/{doll_id}/price-check',
    tags=['Dolls'],
    summary='Price Check',
    response_model=DollPriceCheck,
)
async def price_check(
    request: Request,
    doll_id: str,
    db: AsyncSession = Depends(get_db),
):
    module = DollsModule(request, db)
    doll = await module.get_doll(doll_id)
    
    # Simple shipping category logic
    if doll.weight < 1.0:
        shipping_category = "Standard"
    elif doll.weight < 5.0:
        shipping_category = "Heavy"
    else:
        shipping_category = "Oversized"
        
    return {
        "price": doll.price,
        "weight": doll.weight,
        "shipping_category": shipping_category
    }
