import pytest_asyncio
from decimal import Decimal


@pytest_asyncio.fixture
async def assigned_order(db_session, driver_user, dispatcher_user):
    """Создает заявку, назначенную на ТС водителя."""
    from app.models.vehicle import Vehicle
    from app.models.order import Order, OrderStatus

    # Создаем ТС с водителем
    vehicle = Vehicle(
        plate_number="FRH-001",
        fuel_consumption_mpg=Decimal("6.5"),
        driver_id=driver_user.id,
    )
    db_session.add(vehicle)
    await db_session.flush()

    # Создаем заявку, назначенную на это ТС
    order = Order(
        order_number="FR-T999",
        origin_address="Chicago, IL",
        destination_address="Dallas, TX",
        distance_miles=Decimal("925"),
        rate_per_mile=Decimal("1.5"),
        vehicle_id=vehicle.id,
        dispatcher_id=dispatcher_user.id,
        status=OrderStatus.ASSIGNED,
    )
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order


class TestDriverWorkflow:
    async def test_driver_sees_own_orders(self, client, driver_headers, assigned_order):
        """Водитель видит заявку, привязанную к его ТС."""
        r = await client.get("/api/v1/orders/my/assigned", headers=driver_headers)
        assert r.status_code == 200
        orders = r.json()
        assert len(orders) == 1
        assert orders[0]["order_number"] == "FR-T999"

    async def test_driver_can_start_trip(self, client, driver_headers, assigned_order):
        """Водитель может перевести Назначен → В пути."""
        r = await client.patch(
            f"/api/v1/orders/{assigned_order.id}/status?new_status=in_transit",
            headers=driver_headers,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "in_transit"

    async def test_driver_cannot_skip_states(self, client, driver_headers, assigned_order):
        """Водитель не может прыгнуть Назначен → Доставлено, минуя В пути."""
        r = await client.patch(
            f"/api/v1/orders/{assigned_order.id}/status?new_status=delivered",
            headers=driver_headers,
        )
        assert r.status_code == 400  # state machine отвергает переход

    async def test_driver_without_vehicle_sees_empty_list(self, client, db_session):
        """Если у водителя нет ТС — список рейсов пуст."""
        from app.models.user import User, UserRole
        from app.core.security import hash_password

        new_driver = User(
            email="driver2@test.com",
            password_hash=hash_password("pass123"),
            full_name="Lonely Driver",
            role=UserRole.DRIVER,
        )
        db_session.add(new_driver)
        await db_session.commit()

        login = await client.post("/api/v1/auth/login", json={
            "email": "driver2@test.com", "password": "pass123",
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/orders/my/assigned", headers=headers)
        assert r.status_code == 200
        assert r.json() == []