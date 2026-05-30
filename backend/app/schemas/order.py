from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from app.models.order import OrderStatus


class OrderBase(BaseModel):
    order_number: str = Field(..., max_length=50)
    origin_address: str
    destination_address: str
    distance_miles: Decimal = Field(gt=0)
    rate_per_mile: Decimal = Field(gt=0)
    cargo_type: str | None = None
    weight_lbs: Decimal | None = None
    pickup_date: date | None = None
    delivery_date: date | None = None
    client_id: int | None = None
    broker_id: int | None = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    vehicle_id: int | None = None
    cargo_type: str | None = None
    weight_lbs: Decimal | None = None


class OrderListItem(BaseModel):
    """Краткое представление для списка/таблицы."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    origin_address: str
    destination_address: str
    distance_miles: Decimal
    rate_per_mile: Decimal
    status: OrderStatus
    created_at: datetime


class OrderOut(OrderListItem):
    """Полное представление с дополнительными полями."""
    cargo_type: str | None
    weight_lbs: Decimal | None
    pickup_date: date | None
    delivery_date: date | None
    client_id: int | None
    broker_id: int | None
    dispatcher_id: int | None
    vehicle_id: int | None