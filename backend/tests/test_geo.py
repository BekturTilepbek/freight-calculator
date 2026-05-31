import pytest
from unittest.mock import patch, AsyncMock


class TestGeoEndpoint:
    @patch("app.services.routing.calculate_full_route", new_callable=AsyncMock)
    async def test_route_endpoint_returns_distance(
        self, mock_route, client, dispatcher_headers
    ):
        """Эндпоинт корректно возвращает данные маршрута."""
        # Мокируем ответ внешнего сервиса
        mock_route.return_value = {
            "origin": {"lat": 41.85, "lon": -87.65, "display_name": "Chicago, IL, USA"},
            "destination": {"lat": 32.78, "lon": -96.80, "display_name": "Dallas, TX, USA"},
            "distance_miles": 925.14,
            "duration_minutes": 836,
            "geometry": {"type": "LineString", "coordinates": [[-87.65, 41.85], [-96.80, 32.78]]},
        }

        r = await client.post(
            "/api/v1/geo/route",
            json={"origin": "Chicago, IL", "destination": "Dallas, TX"},
            headers=dispatcher_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["distance_miles"] == 925.14
        assert data["duration_minutes"] == 836
        assert "geometry" in data
        # Проверяем, что внешний сервис был вызван
        mock_route.assert_called_once_with("Chicago, IL", "Dallas, TX")

    @patch("app.services.routing.calculate_full_route", new_callable=AsyncMock)
    async def test_route_endpoint_handles_invalid_address(
        self, mock_route, client, dispatcher_headers
    ):
        """Если адрес не найден, возвращается 400."""
        mock_route.side_effect = ValueError("Адрес не найден: Atlantis")
        r = await client.post(
            "/api/v1/geo/route",
            json={"origin": "Atlantis", "destination": "Dallas, TX"},
            headers=dispatcher_headers,
        )
        assert r.status_code == 400
        assert "Атлантид" in r.json()["detail"] or "Atlantis" in r.json()["detail"]

    async def test_route_endpoint_requires_auth(self, client):
        """Эндпоинт защищен от анонимного доступа."""
        r = await client.post("/api/v1/geo/route", json={
            "origin": "Chicago, IL", "destination": "Dallas, TX",
        })
        assert r.status_code == 401

    async def test_route_endpoint_validates_input(self, client, dispatcher_headers):
        """Слишком короткие адреса отклоняются валидатором."""
        r = await client.post(
            "/api/v1/geo/route",
            json={"origin": "X", "destination": "Y"},  # min_length=2
            headers=dispatcher_headers,
        )
        assert r.status_code == 422