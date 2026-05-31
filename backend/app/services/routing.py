"""
Геокодирование адресов и построение маршрутов.
Использует открытые сервисы OpenStreetMap: Nominatim (геокодинг) и OSRM (роутинг).
"""
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

# Nominatim требует User-Agent (требование fair use policy)
USER_AGENT = "FreightFlow/1.0 (diploma-project)"


async def geocode(address: str) -> dict | None:
    """Преобразование адреса в координаты."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            NOMINATIM_URL,
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
        )
    results = r.json()
    if not results:
        return None
    item = results[0]
    return {
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "display_name": item["display_name"],
    }


async def get_route(o_lat: float, o_lon: float, d_lat: float, d_lon: float) -> dict | None:
    """Построение маршрута между двумя точками."""
    coords = f"{o_lon},{o_lat};{d_lon},{d_lat}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{OSRM_URL}/{coords}",
            params={"overview": "full", "geometries": "geojson"},
        )
    data = r.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        return None
    route = data["routes"][0]
    meters_to_miles = 1 / 1609.34
    return {
        "distance_meters": route["distance"],
        "distance_miles": round(route["distance"] * meters_to_miles, 2),
        "duration_minutes": round(route["duration"] / 60),
        "geometry": route["geometry"],  # GeoJSON LineString
    }


async def calculate_full_route(origin_addr: str, dest_addr: str) -> dict:
    """Полный пайплайн: геокод обоих адресов + построение маршрута."""
    origin = await geocode(origin_addr)
    if not origin:
        raise ValueError(f"Адрес не найден: {origin_addr}")

    destination = await geocode(dest_addr)
    if not destination:
        raise ValueError(f"Адрес не найден: {dest_addr}")

    route = await get_route(
        origin["lat"], origin["lon"],
        destination["lat"], destination["lon"],
    )
    if not route:
        raise ValueError("Не удалось построить маршрут между точками")

    return {
        "origin": origin,
        "destination": destination,
        "distance_miles": route["distance_miles"],
        "duration_minutes": route["duration_minutes"],
        "geometry": route["geometry"],
    }