from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User
from app.services.routing import calculate_full_route

router = APIRouter(prefix="/geo", tags=["geo"])


class RouteRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=500)
    destination: str = Field(..., min_length=2, max_length=500)


@router.post("/route")
async def build_route(
    payload: RouteRequest,
    current_user: User = Depends(get_current_user),
):
    """Геокодирует адреса и строит маршрут между ними."""
    try:
        return await calculate_full_route(payload.origin, payload.destination)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Внешний сервис недоступен: {e}")