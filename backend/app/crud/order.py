from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate


async def get(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalar_one_or_none()


async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: OrderStatus | None = None,
) -> list[Order]:
    query = select(Order).order_by(Order.created_at.desc())
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create(db: AsyncSession, data: OrderCreate) -> Order:
    obj = Order(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, obj: Order, data: OrderUpdate) -> Order:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, obj: Order) -> None:
    await db.delete(obj)
    await db.commit()


async def get_stats(db: AsyncSession) -> dict:
    """Сводная статистика для дашборда."""
    # Активные заявки
    active_q = select(func.count(Order.id)).where(
        Order.status.in_([OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT])
    )
    active = (await db.execute(active_q)).scalar() or 0

    # Общий пробег
    distance_q = select(func.coalesce(func.sum(Order.distance_miles), 0))
    total_distance = (await db.execute(distance_q)).scalar() or 0

    # Общая выручка (грубо: distance * rate)
    revenue_q = select(
        func.coalesce(func.sum(Order.distance_miles * Order.rate_per_mile), 0)
    )
    total_revenue = (await db.execute(revenue_q)).scalar() or 0

    # Всего заявок
    total_q = select(func.count(Order.id))
    total = (await db.execute(total_q)).scalar() or 0

    return {
        "active_orders": int(active),
        "total_orders": int(total),
        "total_distance_miles": float(total_distance),
        "total_revenue": float(total_revenue),
    }

async def get_for_driver(db: AsyncSession, driver_user_id: int) -> list[Order]:
    """
    Возвращает рейсы, назначенные на ТС текущего водителя.
    Цепочка: User → Vehicle (driver_id) → Order (vehicle_id).
    """
    from sqlalchemy.orm import selectinload
    from app.models.vehicle import Vehicle

    # Находим ТС водителя
    v_result = await db.execute(
        select(Vehicle.id).where(Vehicle.driver_id == driver_user_id)
    )
    vehicle_id = v_result.scalar_one_or_none()
    if not vehicle_id:
        return []

    # Все заявки на это ТС
    result = await db.execute(
        select(Order)
        .where(Order.vehicle_id == vehicle_id)
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())