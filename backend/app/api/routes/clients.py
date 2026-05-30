from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import client as crud_client
from app.db.session import get_db
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
async def list_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    return await crud_client.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    return await crud_client.create(db, payload)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),):
    obj = await crud_client.get(db, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    return obj


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: int, payload: ClientUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    obj = await crud_client.get(db, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    return await crud_client.update(db, obj, payload)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.ADMIN)),):
    obj = await crud_client.get(db, client_id)
    if not obj:
        raise HTTPException(404, "Client not found")
    await crud_client.delete(db, obj)