from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    url="postgresql+asyncpg://postgres:YuWlNvrGs@localhost:5432/testtask",
    echo=True,
)

async_session_factory = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
