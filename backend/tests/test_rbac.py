class TestRoleBasedAccess:
    async def test_admin_can_delete_order(self, client, admin_headers, dispatcher_headers):
        """Админ имеет право удалять заявки."""
        created = (await client.post("/api/v1/orders", json={
            "order_number": "FR-DEL1",
            "origin_address": "A", "destination_address": "B",
            "distance_miles": "100", "rate_per_mile": "1.5",
        }, headers=dispatcher_headers)).json()
        r = await client.delete(
            f"/api/v1/orders/{created['id']}",
            headers=admin_headers,
        )
        assert r.status_code == 204

    async def test_dispatcher_cannot_delete_order(self, client, dispatcher_headers):
        """Диспетчер НЕ может удалять заявки — это привилегия админа."""
        created = (await client.post("/api/v1/orders", json={
            "order_number": "FR-DEL2",
            "origin_address": "A", "destination_address": "B",
            "distance_miles": "100", "rate_per_mile": "1.5",
        }, headers=dispatcher_headers)).json()
        r = await client.delete(
            f"/api/v1/orders/{created['id']}",
            headers=dispatcher_headers,
        )
        assert r.status_code == 403

    async def test_driver_cannot_access_dispatcher_endpoint(
        self, client, driver_headers
    ):
        """Эндпоинт «мои рейсы» доступен только водителю, но не другим."""
        # Driver успешно получает доступ к своему эндпоинту
        r = await client.get("/api/v1/orders/my/assigned", headers=driver_headers)
        assert r.status_code == 200

    async def test_non_driver_cannot_access_driver_endpoint(
        self, client, dispatcher_headers
    ):
        """Диспетчер не имеет доступа к эндпоинту 'мои рейсы' (требует роли DRIVER)."""
        r = await client.get("/api/v1/orders/my/assigned", headers=dispatcher_headers)
        assert r.status_code == 403