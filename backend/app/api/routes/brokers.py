from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.crud import broker as crud_broker
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.broker import BrokerCreate, BrokerUpdate, BrokerOut

router = APIRouter(prefix="/brokers", tags=["brokers"])


@router.get("", response_model=list[BrokerOut])
async def list_brokers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_broker.get_all(db)


@router.post("", response_model=BrokerOut, status_code=status.HTTP_201_CREATED)
async def create_broker(
    payload: BrokerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await crud_broker.create(db, payload)


@router.get("/{broker_id}", response_model=BrokerOut)
async def get_broker(
    broker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = await crud_broker.get(db, broker_id)
    if not obj:
        raise HTTPException(404, "Broker not found")
    return obj


@router.patch("/{broker_id}", response_model=BrokerOut)
async def update_broker(
    broker_id: int,
    payload: BrokerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = await crud_broker.get(db, broker_id)
    if not obj:
        raise HTTPException(404, "Broker not found")
    return await crud_broker.update(db, obj, payload)


@router.delete("/{broker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_broker(
    broker_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    obj = await crud_broker.get(db, broker_id)
    if not obj:
        raise HTTPException(404, "Broker not found")
    await crud_broker.delete(db, obj)