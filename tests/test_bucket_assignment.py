import pytest


@pytest.mark.asyncio
async def test_nearby_properties_share_bucket(async_client):
    payload_a = {
        "title": "Near A",
        "location_name": "Ajah Near",
        "lat": 6.4698,
        "lng": 3.6285,
    }
    payload_b = {
        "title": "Near B",
        "location_name": "Ajah Near 2",
        "lat": 6.4700,
        "lng": 3.6287,
    }

    res_a = await async_client.post("/api/properties", json=payload_a)
    res_b = await async_client.post("/api/properties", json=payload_b)

    assert res_a.status_code == 200
    assert res_b.status_code == 200

    bucket_a = res_a.json()["bucket"]["id"]
    bucket_b = res_b.json()["bucket"]["id"]
    assert bucket_a == bucket_b
