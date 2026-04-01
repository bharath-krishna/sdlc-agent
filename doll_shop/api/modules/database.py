from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from api.configurations.base import config

class Base(DeclarativeBase):
    pass

async def get_db():
    engine = create_async_engine(config.database_url, echo=config.debug)
    session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_local() as session:
        yield session
    await engine.dispose()
