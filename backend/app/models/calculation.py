from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Calculation(Base):
    """
    Сохраненный расчет стоимости рейса.

    Зачем хранить историю отдельной таблицей: цена топлива меняется,
    ставки пересматриваются. Расчет от прошлого месяца должен оставаться
    неизменным как исторический документ.
    """
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Входные параметры (на момент расчета)
    distance_miles: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    rate_per_mile: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    fuel_consumption_mpg: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    fuel_price_per_gallon: Mapped[Decimal] = mapped_column(Numeric(5, 3))

    # Результаты
    gross_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    fuel_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    extra_costs_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    total_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    net_profit: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    margin_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))

    # Детализация в JSON: позволяет хранить произвольное число статей расходов
    # без отдельной таблицы. Для отчетов и PDF-накладных
    breakdown: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped["Order | None"] = relationship(back_populates="calculations")