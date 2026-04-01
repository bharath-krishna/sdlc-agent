from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.modules import BaseModule
from api.exceptions.api import APIError
from api.schemas.orders import Order, OrderItem
from api.schemas.dolls import Doll
from api.schemas.customers import Customer


class OrdersModule(BaseModule):

    async def list_orders(self):
        result = await self.db.execute(
            select(Order).options(selectinload(Order.items))
        )
        return result.scalars().all()

    async def get_order(self, order_id: str):
        result = await self.db.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        )
        order = result.scalar_one_or_none()
        if not order:
            raise APIError("not_found", field="order_id", value=order_id)
        return order

    async def create_order(self, body):
        # 1. Validate customer
        customer_result = await self.db.execute(
            select(Customer).where(Customer.id == body.customer_id)
        )
        if not customer_result.scalar_one_or_none():
            raise APIError("not_found", field="customer_id", value=body.customer_id)

        # 2. Process items and calculate total
        total_amount = 0.0
        order_items = []
        
        for item_req in body.items:
            # Check doll
            doll_result = await self.db.execute(
                select(Doll).where(Doll.id == item_req.doll_id)
            )
            doll = doll_result.scalar_one_or_none()
            if not doll:
                raise APIError("not_found", field="doll_id", value=item_req.doll_id)
            
            # Check stock
            if doll.stock_quantity < item_req.quantity:
                raise APIError("general_error", text=f"Insufficient stock for doll: {doll.name}")
            
            # Reduce stock
            doll.stock_quantity -= item_req.quantity
            
            item_price = doll.price * item_req.quantity
            total_amount += item_price
            
            order_items.append(OrderItem(
                doll_id=doll.id,
                quantity=item_req.quantity,
                unit_price=doll.price
            ))
        
        # 3. Create order
        order = Order(
            customer_id=body.customer_id,
            total_amount=total_amount,
            items=order_items
        )
        
        self.db.add(order)
        await self.db.commit()
        return await self.get_order(order.id)

    async def delete_order(self, order_id: str):
        order = await self.get_order(order_id)
        
        # 1. Restore stock
        for item in order.items:
            doll_result = await self.db.execute(
                select(Doll).where(Doll.id == item.doll_id)
            )
            doll = doll_result.scalar_one_or_none()
            if doll:
                doll.stock_quantity += item.quantity
        
        # 2. Delete order
        await self.db.delete(order)
        await self.db.commit()
        return order
