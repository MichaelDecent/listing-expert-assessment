import pytest


async def _create_property(client, title, location_name, lat, lng):
    payload = {
        "title": title,
        "location_name": location_name,
        "lat": lat,
        "lng": lng,
        "price": 100,
        "bedrooms": 2,
        "bathrooms": 2,
    }
    res = await client.post("/api/properties", json=payload)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_sangotedo_variants_returned(async_client):
    await _create_property(async_client, "A", "Sangotedo", 6.4698, 3.6285)
    await _create_property(async_client, "B", "Sangotedo, Ajah", 6.4720, 3.6301)
    await _create_property(async_client, "C", "sangotedo lagos", 6.4705, 3.6290)

    res = await async_client.get("/api/properties/search", params={"location": "sangotedo"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
