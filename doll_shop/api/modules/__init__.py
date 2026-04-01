from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


class BaseModule:
    def __init__(self, request: Request, db: AsyncSession):
        self.request = request
        self.db = db
