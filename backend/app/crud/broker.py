from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker import Broker
from app.schemas.broker import BrokerCreate, BrokerUpdate


async def get(db: AsyncSession, broker_id: int) -> Broker | None:
    result = await db.execute(select(Broker).where(Broker.id == broker_id))
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession, skip: int = 0, limit: int = 200) -> list[Broker]:
    result = await db.execute(
        select(Broker).order_by(Broker.id.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: BrokerCreate) -> Broker:
    obj = Broker(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, obj: Broker, data: BrokerUpdate) -> Broker:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, obj: Broker) -> None:
    await db.delete(obj)
    await db.commit()