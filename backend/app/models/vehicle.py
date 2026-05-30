from decimal import Decimal

from sqlalchemy import String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(50), unique=True)
    make: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fuel_consumption_mpg: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("6.5")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )

    driver: Mapped["User | None"] = relationship(back_populates="vehicle")
    orders: Mapped[list["Order"]] = relationship(back_populates="vehicle")