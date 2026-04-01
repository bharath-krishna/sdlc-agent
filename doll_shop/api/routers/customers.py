from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from api.modules.customers import CustomersModule
from api.modules.database import get_db
from api.models.auth import require_user
from api.models.customers import CustomerRequest, CustomerUpdate, CustomerModel

router = APIRouter()


@router.get(
    '/customers',
    tags=['Customers'],
    summary='List Customers',
    response_model=List[CustomerModel],
)
async def list_customers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = CustomersModule(request, db)
    return await module.list_customers()


@router.get(
    '/customers/{customer_id}',
    tags=['Customers'],
    summary='Get Customer',
    response_model=CustomerModel,
)
async def get_customer(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = CustomersModule(request, db)
    return await module.get_customer(customer_id)


@router.post(
    '/customers',
    tags=['Customers'],
    summary='Create Customer',
    response_model=CustomerModel,
)
async def create_customer(
    request: Request,
    body: CustomerRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = CustomersModule(request, db)
    return await module.create_customer(body)


@router.put(
    '/customers/{customer_id}',
    tags=['Customers'],
    summary='Update Customer',
    response_model=CustomerModel,
)
async def update_customer(
    request: Request,
    customer_id: str,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = CustomersModule(request, db)
    return await module.update_customer(customer_id, body)


@router.delete(
    '/customers/{customer_id}',
    tags=['Customers'],
    summary='Delete Customer',
    response_model=CustomerModel,
)
async def delete_customer(
    request: Request,
    customer_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    module = CustomersModule(request, db)
    return await module.delete_customer(customer_id)
