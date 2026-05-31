from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class VehicleBase(BaseModel):
    plate_number: str = Field(..., max_length=50)
    make: str | None = None
    model: str | None = None
    fuel_consumption_mpg: Decimal = Field(default=Decimal("6.5"), gt=0, le=50)
    driver_id: int | None = None
    is_active: bool = True


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    plate_number: str | None = None
    make: str | None = None
    model: str | None = None
    fuel_consumption_mpg: Decimal | None = None
    driver_id: int | None = None
    is_active: bool | None = None


class DriverInfo(BaseModel):
    """Краткая инфа о водителе для отображения в карточке ТС."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str


class VehicleOut(VehicleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    driver: DriverInfo | None = None