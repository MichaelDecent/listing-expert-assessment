import pytest


async def _seed(async_client):
    payloads = [
        {"title": "A", "location_name": "Sangotedo", "lat": 6.4698, "lng": 3.6285},
        {"title": "B", "location_name": "Sangotedo, Ajah", "lat": 6.4720, "lng": 3.6301},
        {"title": "C", "location_name": "sangotedo lagos", "lat": 6.4705, "lng": 3.6290},
    ]
    for payload in payloads:
        res = await async_client.post("/api/properties", json=payload)
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_case_insensitive_search(async_client):
    await _seed(async_client)
    res = await async_client.get("/api/properties/search", params={"location": "SANGOTEDO"})
    assert res.status_code == 200
    assert len(res.json()) == 3


@pytest.mark.asyncio
async def test_typo_tolerance_search(async_client):
    await _seed(async_client)
    res = await async_client.get("/api/properties/search", params={"location": "sangotdeo"})
    assert res.status_code == 200
    assert len(res.json()) == 3
