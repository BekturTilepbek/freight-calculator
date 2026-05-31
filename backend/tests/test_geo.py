import pytest
from unittest.mock import patch, AsyncMock


class TestGeoEndpoint:
    @patch("app.api.routes.geo.calculate_full_route", new_callable=AsyncMock)   # ← путь изменен
    async def test_route_endpoint_returns_distance(
        self, mock_route, client, dispatcher_headers
    ):
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
        mock_route.assert_called_once_with("Chicago, IL", "Dallas, TX")

    @patch("app.api.routes.geo.calculate_full_route", new_callable=AsyncMock)   # ← путь изменен
    async def test_route_endpoint_handles_invalid_address(
        self, mock_route, client, dispatcher_headers
    ):
        mock_route.side_effect = ValueError("Адрес не найден: Atlantis")
        r = await client.post(
            "/api/v1/geo/route",
            json={"origin": "Atlantis", "destination": "Dallas, TX"},
            headers=dispatcher_headers,
        )
        assert r.status_code == 400

    async def test_route_endpoint_requires_auth(self, client):
        r = await client.post("/api/v1/geo/route", json={
            "origin": "Chicago, IL", "destination": "Dallas, TX",
        })
        assert r.status_code == 401

    async def test_route_endpoint_validates_input(self, client, dispatcher_headers):
        r = await client.post(
            "/api/v1/geo/route",
            json={"origin": "X", "destination": "Y"},
            headers=dispatcher_headers,
        )
        assert r.status_code == 422