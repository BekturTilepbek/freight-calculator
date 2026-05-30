from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


async def get(db: AsyncSession, client_id: int) -> Client | None:
    result = await db.execute(select(Client).where(Client.id == client_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Client]:
    result = await db.execute(
        select(Client).order_by(Client.id.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: ClientCreate) -> Client:
    obj = Client(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, obj: Client, data: ClientUpdate) -> Client:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, obj: Client) -> None:
    await db.delete(obj)
    await db.commit()