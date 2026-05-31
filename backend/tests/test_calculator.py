from decimal import Decimal
from app.services.cost_calculator import (
    calculate_trip_cost, RouteData, CostComponent
)


class TestCostCalculator:
    """Unit-тесты бизнес-логики калькулятора стоимости."""

    def test_basic_calculation_from_diploma_example(self):
        """Пример заказчика: 1000 миль × $1.5/милю с топливом."""
        route = RouteData(
            distance_miles=Decimal("1000"),
            rate_per_mile=Decimal("1.5"),
            fuel_consumption_mpg=Decimal("6.5"),
            fuel_price_per_gallon=Decimal("3.80"),
        )
        result = calculate_trip_cost(route)

        assert result.gross_revenue == Decimal("1500.00")
        # 1000 / 6.5 * 3.80 ≈ 584.62
        assert result.fuel_cost == Decimal("584.62")
        assert result.net_profit == Decimal("915.38")
        assert result.margin_percent == Decimal("61.03")

    def test_zero_distance_returns_zero_revenue(self):
        """Нулевая дистанция — никакой выручки и расходов на топливо."""
        route = RouteData(
            distance_miles=Decimal("0"),
            rate_per_mile=Decimal("1.5"),
            fuel_consumption_mpg=Decimal("6.5"),
            fuel_price_per_gallon=Decimal("3.80"),
        )
        result = calculate_trip_cost(route)
        assert result.gross_revenue == Decimal("0.00")
        assert result.fuel_cost == Decimal("0.00")
        assert result.margin_percent == Decimal("0.00")

    def test_extra_costs_are_added(self):
        """Дополнительные расходы корректно вычитаются из прибыли."""
        route = RouteData(
            distance_miles=Decimal("500"),
            rate_per_mile=Decimal("2.0"),
            fuel_consumption_mpg=Decimal("6.5"),
            fuel_price_per_gallon=Decimal("3.80"),
            extra_costs=[
                CostComponent(name="Платная дорога", amount=Decimal("50")),
                CostComponent(name="Погрузка", amount=Decimal("100")),
            ],
        )
        result = calculate_trip_cost(route)
        assert result.extra_costs_total == Decimal("150.00")
        assert result.total_expenses > result.fuel_cost

    def test_breakdown_includes_all_components(self):
        """В детализации присутствуют выручка, топливо и доп. расходы."""
        route = RouteData(
            distance_miles=Decimal("100"),
            rate_per_mile=Decimal("2.0"),
            fuel_consumption_mpg=Decimal("6.5"),
            fuel_price_per_gallon=Decimal("3.80"),
            extra_costs=[
                CostComponent(name="Toll", amount=Decimal("25")),
            ],
        )
        result = calculate_trip_cost(route)
        names = [c.name for c in result.breakdown]
        assert "Выручка по ставке" in names
        assert "Топливо" in names
        assert "Toll" in names

    def test_unprofitable_trip_has_negative_profit(self):
        """Рейс с низкой ставкой и большими расходами — убыточен."""
        route = RouteData(
            distance_miles=Decimal("1000"),
            rate_per_mile=Decimal("0.3"),  # очень низкая ставка
            fuel_consumption_mpg=Decimal("5.0"),
            fuel_price_per_gallon=Decimal("4.50"),
        )
        result = calculate_trip_cost(route)
        # Выручка 300, топливо 900 → убыток 600
        assert result.net_profit < Decimal("0")
        assert result.margin_percent < Decimal("0")

    def test_decimal_precision_not_lost(self):
        """Все суммы корректно округлены до 2 знаков."""
        route = RouteData(
            distance_miles=Decimal("333"),
            rate_per_mile=Decimal("1.27"),
            fuel_consumption_mpg=Decimal("6.5"),
            fuel_price_per_gallon=Decimal("3.83"),
        )
        result = calculate_trip_cost(route)
        # Проверяем, что все значения имеют не более 2 знаков после запятой
        for value in [result.gross_revenue, result.fuel_cost, result.net_profit]:
            sign, digits, exponent = value.as_tuple()
            assert exponent >= -2, f"Слишком много знаков в {value}"