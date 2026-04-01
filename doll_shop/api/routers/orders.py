from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.orders import OrdersModule
from api.modules.database import get_db
from api.models.auth import require_user
from api.models.orders import OrderRequest, OrderModel

router = APIRouter()


@router.get(
    '/orders',
    tags=['Orders'],
    summary='List Orders',
    response_model=List[OrderModel],
)
async def list_orders(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = OrdersModule(request, db)
    return await module.list_orders()


@router.get(
    '/orders/{order_id}',
    tags=['Orders'],
    summary='Get Order',
    response_model=OrderModel,
)
async def get_order(
    request: Request,
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = OrdersModule(request, db)
    return await module.get_order(order_id)


@router.post(
    '/orders',
    tags=['Orders'],
    summary='Create Order',
    response_model=OrderModel,
)
async def create_order(
    request: Request,
    body: OrderRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = OrdersModule(request, db)
    return await module.create_order(body)


@router.delete(
    '/orders/{order_id}',
    tags=['Orders'],
    summary='Delete Order',
    response_model=OrderModel,
)
async def delete_order(
    request: Request,
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = OrdersModule(request, db)
    return await module.delete_order(order_id)
