from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import order as crud_order
from app.db.session import get_db
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderListItem
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderListItem])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: OrderStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_order.get_all(db, skip=skip, limit=limit, status=status_filter)


@router.get("/stats")
async def orders_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    return await crud_order.get_stats(db)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    return await crud_order.create(db, payload)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    obj = await crud_order.get(db, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    return obj


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: int, payload: OrderUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    obj = await crud_order.get(db, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    return await crud_order.update(db, obj, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN)),):
    obj = await crud_order.get(db, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    await crud_order.delete(db, obj)


from app.crud import calculation as crud_calc
from app.schemas.calculation import CalculationOut


@router.get("/{order_id}/calculations", response_model=list[CalculationOut])
async def get_order_calculations(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    """История расчетов по заявке."""
    obj = await crud_order.get(db, order_id)
    if not obj:
        raise HTTPException(404, "Order not found")
    return await crud_calc.get_by_order(db, order_id)