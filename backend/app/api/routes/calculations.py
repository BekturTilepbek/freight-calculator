from decimal import Decimal
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.cost_calculator import (
    calculate_trip_cost, RouteData, CostComponent
)

router = APIRouter(prefix="/calculations", tags=["calculations"])


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


@router.post("/estimate", response_model=CalculationResponse)
async def estimate_trip_cost(payload: CalculationRequest):
    route = RouteData(
        distance_miles=payload.distance_miles,
        rate_per_mile=payload.rate_per_mile,
        fuel_consumption_mpg=payload.fuel_consumption_mpg,
        fuel_price_per_gallon=payload.fuel_price_per_gallon,
        extra_costs=[CostComponent(name=ec.name, amount=ec.amount) for ec in payload.extra_costs],
    )
    return calculate_trip_cost(route)