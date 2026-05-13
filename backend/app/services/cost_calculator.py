from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class CostComponent:
    """Одна статья расходов в итоговом расчете."""
    name: str
    amount: Decimal
    description: str = ""


@dataclass
class RouteData:
    """Входные данные по маршруту."""
    distance_miles: Decimal
    rate_per_mile: Decimal
    fuel_consumption_mpg: Decimal
    fuel_price_per_gallon: Decimal
    extra_costs: List[CostComponent] = field(default_factory=list)
    company_margin_percent: Decimal = Decimal("0")


@dataclass
class CalculationResult:
    """Результат расчета — детализированный, не одно число."""
    gross_revenue: Decimal
    fuel_cost: Decimal
    extra_costs_total: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    margin_percent: Decimal
    breakdown: List[CostComponent]


def calculate_trip_cost(route: RouteData) -> CalculationResult:
    """
    Универсальный расчет стоимости рейса.
    Каждая статья считается отдельно и складывается в breakdown —
    удобно и для UI, и для генерации PDF-накладной.
    """
    # 1. Выручка по договоренности диспетчера с брокером
    gross_revenue = route.distance_miles * route.rate_per_mile

    # 2. Расчет топлива
    gallons_needed = route.distance_miles / route.fuel_consumption_mpg
    fuel_cost = gallons_needed * route.fuel_price_per_gallon

    # 3. Дополнительные расходы
    extra_costs_total = sum(
        (item.amount for item in route.extra_costs),
        Decimal("0"),
    )

    # 4. Итоги
    total_expenses = fuel_cost + extra_costs_total
    net_profit = gross_revenue - total_expenses
    margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else Decimal("0")

    # 5. Детализация для отображения
    breakdown = [
        CostComponent(
            name="Выручка по ставке",
            amount=gross_revenue,
            description=f"{route.distance_miles} миль × ${route.rate_per_mile}/милю",
        ),
        CostComponent(
            name="Топливо",
            amount=fuel_cost,
            description=f"{gallons_needed:.2f} галлонов × ${route.fuel_price_per_gallon}",
        ),
        *route.extra_costs,
    ]

    return CalculationResult(
        gross_revenue=gross_revenue.quantize(Decimal("0.01")),
        fuel_cost=fuel_cost.quantize(Decimal("0.01")),
        extra_costs_total=extra_costs_total.quantize(Decimal("0.01")),
        total_expenses=total_expenses.quantize(Decimal("0.01")),
        net_profit=net_profit.quantize(Decimal("0.01")),
        margin_percent=margin.quantize(Decimal("0.01")),
        breakdown=breakdown,
    )