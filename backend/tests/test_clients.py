class TestClientsCRUD:
    async def test_create_client(self, client, dispatcher_headers):
        r = await client.post("/api/v1/clients", json={
            "name": "Acme Logistics",
            "contact_person": "John Doe",
            "email": "john@acme.com",
            "phone": "+1 555 1234",
        }, headers=dispatcher_headers)
        assert r.status_code == 201
        assert r.json()["name"] == "Acme Logistics"

    async def test_list_clients(self, client, dispatcher_headers):
        for i in range(3):
            await client.post("/api/v1/clients", json={
                "name": f"Client {i}",
            }, headers=dispatcher_headers)
        r = await client.get("/api/v1/clients", headers=dispatcher_headers)
        assert r.status_code == 200
        assert len(r.json()) == 3

    async def test_update_client(self, client, dispatcher_headers):
        created = (await client.post("/api/v1/clients", json={
            "name": "Old Name",
        }, headers=dispatcher_headers)).json()
        r = await client.patch(
            f"/api/v1/clients/{created['id']}",
            json={"name": "New Name"},
            headers=dispatcher_headers,
        )
        assert r.status_code == 200
        assert r.json()["name"] == "New Name"

    async def test_admin_can_delete_client(self, client, admin_headers, dispatcher_headers):
        created = (await client.post("/api/v1/clients", json={
            "name": "To Delete",
        }, headers=dispatcher_headers)).json()
        r = await client.delete(
            f"/api/v1/clients/{created['id']}",
            headers=admin_headers,
        )
        assert r.status_code == 204

    async def test_dispatcher_cannot_delete_client(self, client, dispatcher_headers):
        created = (await client.post("/api/v1/clients", json={
            "name": "Protected",
        }, headers=dispatcher_headers)).json()
        r = await client.delete(
            f"/api/v1/clients/{created['id']}",
            headers=dispatcher_headers,
        )
        assert r.status_code == 403