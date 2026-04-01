from sqlalchemy import select
from api.modules import BaseModule
from api.exceptions.api import APIError
from api.schemas.dolls import Doll


class DollsModule(BaseModule):

    async def list_dolls(self, type: str = None):
        query = select(Doll)
        if type:
            query = query.where(Doll.type == type)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_doll(self, doll_id: str):
        result = await self.db.execute(
            select(Doll).where(Doll.id == doll_id)
        )
        doll = result.scalar_one_or_none()
        if not doll:
            raise APIError("not_found", field="doll_id", value=doll_id)
        return doll

    async def create_doll(self, body):
        doll = Doll(
            name=body.name,
            description=body.description,
            price=body.price,
            type=body.type,
            weight=body.weight,
            stock_quantity=body.stock_quantity,
        )
        self.db.add(doll)
        await self.db.commit()
        await self.db.refresh(doll)
        return doll

    async def update_doll(self, doll_id: str, body):
        doll = await self.get_doll(doll_id)
        if body.name is not None:
            doll.name = body.name
        if body.description is not None:
            doll.description = body.description
        if body.price is not None:
            doll.price = body.price
        if body.type is not None:
            doll.type = body.type
        if body.weight is not None:
            doll.weight = body.weight
        if body.stock_quantity is not None:
            doll.stock_quantity = body.stock_quantity
        
        await self.db.commit()
        await self.db.refresh(doll)
        return doll

    async def delete_doll(self, doll_id: str):
        doll = await self.get_doll(doll_id)
        await self.db.delete(doll)
        await self.db.commit()
        return doll
