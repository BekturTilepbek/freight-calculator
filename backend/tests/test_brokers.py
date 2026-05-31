class TestBrokersCRUD:
    async def test_create_broker_with_mc_number(self, client, dispatcher_headers):
        r = await client.post("/api/v1/brokers", json={
            "company_name": "TQL Logistics",
            "mc_number": "MC-123456",
            "contact_person": "Jane Smith",
            "email": "jane@tql.com",
        }, headers=dispatcher_headers)
        assert r.status_code == 201
        assert r.json()["mc_number"] == "MC-123456"

    async def test_create_broker_without_optional_fields(self, client, dispatcher_headers):
        r = await client.post("/api/v1/brokers", json={
            "company_name": "Minimal Broker",
        }, headers=dispatcher_headers)
        assert r.status_code == 201

    async def test_list_brokers(self, client, dispatcher_headers):
        for i in range(2):
            await client.post("/api/v1/brokers", json={
                "company_name": f"Broker {i}",
            }, headers=dispatcher_headers)
        r = await client.get("/api/v1/brokers", headers=dispatcher_headers)
        assert r.status_code == 200
        assert len(r.json()) == 2

    async def test_get_nonexistent_broker_returns_404(self, client, dispatcher_headers):
        r = await client.get("/api/v1/brokers/99999", headers=dispatcher_headers)
        assert r.status_code == 404