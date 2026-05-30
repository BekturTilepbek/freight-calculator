from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import order as crud_order, calculation as crud_calc
from app.db.session import get_db
from app.schemas.calculation import CalculationOut
from app.services.cost_calculator import (
    calculate_trip_cost, RouteData, CostComponent
)
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/calculations", tags=["calculations"])


# --- Схемы ---

class ExtraCostIn(BaseModel):
    name: str
    amount: Decimal = Field(gt=0)


class CalculationRequest(BaseModel):
    distance_miles: Decimal = Field(gt=0)
    rate_per_mile: Decimal = Field(gt=0)
    fuel_consumption_mpg: Decimal = Field(gt=0, default=Decimal("6.5"))
    fuel_price_per_gallon: Decimal = Field(gt=0, default=Decimal("3.80"))
    extra_costs: List[ExtraCostIn] = []


class CostComponentOut(BaseModel):
    name: str
    amount: Decimal
    description: str


class CalculationResponse(BaseModel):
    gross_revenue: Decimal
    fuel_cost: Decimal
    extra_costs_total: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    margin_percent: Decimal
    breakdown: List[CostComponentOut]


class SaveAsOrderRequest(BaseModel):
    """Сохранение расчета как новой заявки."""
    calculation: CalculationRequest
    origin_address: str = Field(..., max_length=500)
    destination_address: str = Field(..., max_length=500)
    cargo_type: str | None = None
    client_id: int | None = None
    broker_id: int | None = None


# --- Helpers ---

def _do_calculation(payload: CalculationRequest):
    route = RouteData(
        distance_miles=payload.distance_miles,
        rate_per_mile=payload.rate_per_mile,
        fuel_consumption_mpg=payload.fuel_consumption_mpg,
        fuel_price_per_gallon=payload.fuel_price_per_gallon,
        extra_costs=[
            CostComponent(name=ec.name, amount=ec.amount)
            for ec in payload.extra_costs
        ],
    )
    return calculate_trip_cost(route)


async def _generate_order_number(db: AsyncSession) -> str:
    """Простая генерация номера заявки. В проде стоит делать через sequence."""
    from sqlalchemy import select, func
    from app.models.order import Order

    result = await db.execute(select(func.count(Order.id)))
    count = result.scalar() or 0
    return f"FR-{1000 + count + 1}"


# --- Endpoints ---

@router.post("/estimate", response_model=CalculationResponse)
async def estimate_trip_cost(payload: CalculationRequest, current_user: User = Depends(get_current_user),):
    """Предварительный расчет — без сохранения."""
    return _do_calculation(payload)


@router.post("/save-as-order", response_model=CalculationOut)
async def save_as_order(
    payload: SaveAsOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создает новую заявку и сохраняет расчет, привязанный к ней."""
    from app.models.order import Order, OrderStatus

    # 1. Делаем расчет
    result = _do_calculation(payload.calculation)

    # 2. Создаем заявку
    order_number = await _generate_order_number(db)
    order = Order(
        order_number=order_number,
        origin_address=payload.origin_address,
        destination_address=payload.destination_address,
        distance_miles=payload.calculation.distance_miles,
        rate_per_mile=payload.calculation.rate_per_mile,
        cargo_type=payload.cargo_type,
        client_id=payload.client_id,
        broker_id=payload.broker_id,
        status=OrderStatus.DRAFT,
    )
    db.add(order)
    await db.flush()

    # 3. Сохраняем расчет
    breakdown_serialized = [
        {"name": c.name, "amount": str(c.amount), "description": c.description}
        for c in result.breakdown
    ]
    calc = await crud_calc.create(
        db,
        order_id=order.id,
        distance_miles=payload.calculation.distance_miles,
        rate_per_mile=payload.calculation.rate_per_mile,
        fuel_consumption_mpg=payload.calculation.fuel_consumption_mpg,
        fuel_price_per_gallon=payload.calculation.fuel_price_per_gallon,
        gross_revenue=result.gross_revenue,
        fuel_cost=result.fuel_cost,
        extra_costs_total=result.extra_costs_total,
        total_expenses=result.total_expenses,
        net_profit=result.net_profit,
        margin_percent=result.margin_percent,
        breakdown=breakdown_serialized,
    )
    return calc