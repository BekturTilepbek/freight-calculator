from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum as SAEnum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, Enum):
    DRAFT = "draft"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Связи
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    broker_id: Mapped[int | None] = mapped_column(
        ForeignKey("brokers.id", ondelete="SET NULL"), nullable=True
    )
    dispatcher_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    # Маршрут
    origin_address: Mapped[str] = mapped_column(String(500))
    destination_address: Mapped[str] = mapped_column(String(500))
    distance_miles: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Финансы
    rate_per_mile: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Груз
    cargo_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    weight_lbs: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Даты
    pickup_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)

    # Статус и метаданные
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status"), default=OrderStatus.DRAFT, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    client: Mapped["Client | None"] = relationship(back_populates="orders")
    broker: Mapped["Broker | None"] = relationship(back_populates="orders")
    dispatcher: Mapped["User | None"] = relationship(
        back_populates="orders_as_dispatcher", foreign_keys=[dispatcher_id]
    )
    vehicle: Mapped["Vehicle | None"] = relationship(back_populates="orders")
    calculations: Mapped[list["Calculation"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )