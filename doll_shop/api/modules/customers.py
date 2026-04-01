from sqlalchemy import select
from api.modules import BaseModule
from api.exceptions.api import APIError
from api.schemas.customers import Customer


class CustomersModule(BaseModule):

    async def list_customers(self):
        result = await self.db.execute(select(Customer))
        return result.scalars().all()

    async def get_customer(self, customer_id: str):
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise APIError("not_found", field="customer_id", value=customer_id)
        return customer

    async def create_customer(self, body):
        # Check if email exists
        result = await self.db.execute(
            select(Customer).where(Customer.email == body.email)
        )
        if result.scalar_one_or_none():
            raise APIError("duplicated_resource", value=body.email)

        customer = Customer(
            name=body.name,
            email=body.email,
            phone=body.phone,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update_customer(self, customer_id: str, body):
        customer = await self.get_customer(customer_id)
        
        if body.email is not None and body.email != customer.email:
            result = await self.db.execute(
                select(Customer).where(Customer.email == body.email)
            )
            if result.scalar_one_or_none():
                raise APIError("duplicated_resource", value=body.email)
            customer.email = body.email

        if body.name is not None:
            customer.name = body.name
        if body.phone is not None:
            customer.phone = body.phone
        
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def delete_customer(self, customer_id: str):
        customer = await self.get_customer(customer_id)
        await self.db.delete(customer)
        await self.db.commit()
        return customer
