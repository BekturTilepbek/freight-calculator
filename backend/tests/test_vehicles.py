import pytest_asyncio
from app.models.vehicle import Vehicle


@pytest_asyncio.fixture
async def existing_vehicle(db_session, driver_user):
    """Создаем ТС с привязкой к водителю напрямую через ORM."""
    from decimal import Decimal
    v = Vehicle(
        plate_number="TEST-001",
        make="Freightliner",
        model="Cascadia",
        fuel_consumption_mpg=Decimal("6.5"),
        driver_id=driver_user.id,
        is_active=True,
    )
    db_session.add(v)
    await db_session.commit()
    await db_session.refresh(v)
    return v


class TestVehiclesCRUD:
    async def test_create_vehicle(self, client, dispatcher_headers):
        r = await client.post("/api/v1/vehicles", json={
            "plate_number": "ABC-1234",
            "make": "Volvo",
            "model": "VNL 860",
            "fuel_consumption_mpg": 6.5,
        }, headers=dispatcher_headers)
        assert r.status_code == 201
        assert r.json()["plate_number"] == "ABC-1234"

    async def test_create_vehicle_with_driver(self, client, dispatcher_headers, driver_user):
        r = await client.post("/api/v1/vehicles", json={
            "plate_number": "DRV-001",
            "driver_id": driver_user.id,
        }, headers=dispatcher_headers)
        assert r.status_code == 201
        # В ответе должна быть инфа о водителе
        assert r.json()["driver"] is not None
        assert r.json()["driver"]["full_name"] == "Test Driver"

    async def test_update_vehicle_fuel_consumption(self, client, dispatcher_headers, existing_vehicle):
        r = await client.patch(
            f"/api/v1/vehicles/{existing_vehicle.id}",
            json={"fuel_consumption_mpg": 7.2},
            headers=dispatcher_headers,
        )
        assert r.status_code == 200
        assert float(r.json()["fuel_consumption_mpg"]) == 7.2

    async def test_deactivate_vehicle(self, client, dispatcher_headers, existing_vehicle):
        r = await client.patch(
            f"/api/v1/vehicles/{existing_vehicle.id}",
            json={"is_active": False},
            headers=dispatcher_headers,
        )
        assert r.status_code == 200
        assert r.json()["is_active"] is False