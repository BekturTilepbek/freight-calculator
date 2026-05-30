from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class CalculationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int | None
    distance_miles: Decimal
    rate_per_mile: Decimal
    fuel_consumption_mpg: Decimal
    fuel_price_per_gallon: Decimal
    gross_revenue: Decimal
    fuel_cost: Decimal
    extra_costs_total: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    margin_percent: Decimal
    breakdown: list[dict]
    created_at: datetime