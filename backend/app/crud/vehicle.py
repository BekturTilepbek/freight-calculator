from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


async def get(db: AsyncSession, vehicle_id: int) -> Vehicle | None:
    result = await db.execute(
        select(Vehicle)
        .options(selectinload(Vehicle.driver))
        .where(Vehicle.id == vehicle_id)
    )
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> list[Vehicle]:
    result = await db.execute(
        select(Vehicle)
        .options(selectinload(Vehicle.driver))
        .order_by(Vehicle.id.desc())
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, data: VehicleCreate) -> Vehicle:
    obj = Vehicle(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj, ["driver"])
    return obj


async def update(db: AsyncSession, obj: Vehicle, data: VehicleUpdate) -> Vehicle:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj, ["driver"])
    return obj


async def delete(db: AsyncSession, obj: Vehicle) -> None:
    await db.delete(obj)
    await db.commit()