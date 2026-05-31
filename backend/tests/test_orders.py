class TestOrdersCRUD:
    async def test_create_order(self, client, dispatcher_headers):
        r = await client.post("/api/v1/orders", json={
            "order_number": "FR-T001",
            "origin_address": "Chicago, IL",
            "destination_address": "Dallas, TX",
            "distance_miles": "925",
            "rate_per_mile": "1.5",
        }, headers=dispatcher_headers)
        assert r.status_code == 201
        assert r.json()["order_number"] == "FR-T001"
        assert r.json()["status"] == "draft"

    async def test_list_orders_returns_all(self, client, dispatcher_headers):
        # Создаем 3 заявки
        for i in range(3):
            await client.post("/api/v1/orders", json={
                "order_number": f"FR-T{100+i}",
                "origin_address": "A", "destination_address": "B",
                "distance_miles": "100", "rate_per_mile": "1.5",
            }, headers=dispatcher_headers)
        r = await client.get("/api/v1/orders", headers=dispatcher_headers)
        assert r.status_code == 200
        assert len(r.json()) == 3

    async def test_get_order_by_id(self, client, dispatcher_headers):
        created = (await client.post("/api/v1/orders", json={
            "order_number": "FR-T200",
            "origin_address": "A", "destination_address": "B",
            "distance_miles": "100", "rate_per_mile": "1.5",
        }, headers=dispatcher_headers)).json()
        r = await client.get(f"/api/v1/orders/{created['id']}", headers=dispatcher_headers)
        assert r.status_code == 200
        assert r.json()["order_number"] == "FR-T200"

    async def test_get_nonexistent_order_returns_404(self, client, dispatcher_headers):
        r = await client.get("/api/v1/orders/99999", headers=dispatcher_headers)
        assert r.status_code == 404

    async def test_update_order_status(self, client, dispatcher_headers):
        created = (await client.post("/api/v1/orders", json={
            "order_number": "FR-T300",
            "origin_address": "A", "destination_address": "B",
            "distance_miles": "100", "rate_per_mile": "1.5",
        }, headers=dispatcher_headers)).json()
        r = await client.patch(
            f"/api/v1/orders/{created['id']}",
            json={"status": "assigned"},
            headers=dispatcher_headers,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "assigned"


class TestCalculatorEndpoint:
    async def test_estimate_endpoint_returns_correct_values(self, client, dispatcher_headers):
        r = await client.post("/api/v1/calculations/estimate", json={
            "distance_miles": "1000",
            "rate_per_mile": "1.5",
            "fuel_consumption_mpg": "6.5",
            "fuel_price_per_gallon": "3.80",
        }, headers=dispatcher_headers)
        assert r.status_code == 200
        data = r.json()
        assert float(data["gross_revenue"]) == 1500.00
        assert float(data["net_profit"]) > 900