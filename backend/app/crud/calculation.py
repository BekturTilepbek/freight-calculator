from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calculation import Calculation


async def get_by_order(db: AsyncSession, order_id: int) -> list[Calculation]:
    result = await db.execute(
        select(Calculation)
        .where(Calculation.order_id == order_id)
        .order_by(Calculation.created_at.desc())
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, **data) -> Calculation:
    obj = Calculation(**data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj