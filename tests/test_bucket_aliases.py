import pytest


@pytest.mark.asyncio
async def test_bucket_alias_allows_searching_variant_name(async_client):
    res_a = await async_client.post(
        "/api/properties",
        json={
            "title": "Ikoyi Prop",
            "location_name": "Ikoyi",
            "lat": 6.4540,
            "lng": 3.4340,
        },
    )
    assert res_a.status_code == 200

    res_b = await async_client.post(
        "/api/properties",
        json={
            "title": "Ebute Prop",
            "location_name": "Ebute",
            "lat": 6.4545,
            "lng": 3.4342,
        },
    )
    assert res_b.status_code == 200

    bucket_a = res_a.json()["bucket"]["id"]
    bucket_b = res_b.json()["bucket"]["id"]
    assert bucket_a == bucket_b

    res = await async_client.get("/api/properties/search", params={"location": "Ebute"})
    assert res.status_code == 200
    titles = {p["title"] for p in res.json()}
    assert titles == {"Ikoyi Prop", "Ebute Prop"}

