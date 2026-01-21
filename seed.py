import asyncio

from src.db.session import AsyncSessionLocal
from src.models.property import Property
from src.services.bucket_service import assign_bucket
from src.services.normalize import normalize_location
from sqlalchemy.sql import func
from geoalchemy2 import Geography


SEED_PROPERTIES = [
    {
        "title": "Sangotedo",
        "location_name": "Sangotedo",
        "lat": 6.4698,
        "lng": 3.6285,
        "price": 120,
        "bedrooms": 3,
        "bathrooms": 2,
    },
    {
        "title": "Sangotedo Ajah",
        "location_name": "Sangotedo, Ajah",
        "lat": 6.4720,
        "lng": 3.6301,
        "price": 130,
        "bedrooms": 3,
        "bathrooms": 2,
    },
    {
        "title": "Sangotedo Lagos",
        "location_name": "sangotedo lagos",
        "lat": 6.4705,
        "lng": 3.6290,
        "price": 110,
        "bedrooms": 2,
        "bathrooms": 2,
    },
    {
        "title": "Lekki Phase 1",
        "location_name": "Lekki Phase 1",
        "lat": 6.4474,
        "lng": 3.4725,
        "price": 250,
        "bedrooms": 4,
        "bathrooms": 3,
    },
    {
        "title": "Victoria Island",
        "location_name": "Victoria Island",
        "lat": 6.4281,
        "lng": 3.4219,
        "price": 300,
        "bedrooms": 4,
        "bathrooms": 4,
    },
    {
        "title": "Ikoyi Central",
        "location_name": "Ikoyi",
        "lat": 6.4540,
        "lng": 3.4340,
        "price": 280,
        "bedrooms": 3,
        "bathrooms": 3,
    },
    {
        "title": "Ikorodu Ebute",
        "location_name": "Ikorodu Ebute",
        "lat": 6.4545,
        "lng": 3.4342,
        "price": 240,
        "bedrooms": 2,
        "bathrooms": 2,
    },
    {
        "title": "Yaba Tech",
        "location_name": "Yaba",
        "lat": 6.5100,
        "lng": 3.3820,
        "price": 180,
        "bedrooms": 2,
        "bathrooms": 1,
    },
    {
        "title": "Ikorodu Garage",
        "location_name": "Ikorodu Garage",
        "lat": 6.5010,
        "lng": 3.3560,
        "price": 170,
        "bedrooms": 2,
        "bathrooms": 2,
    },
    {
        "title": "Ikeja GRA",
        "location_name": "Ikeja GRA",
        "lat": 6.6050,
        "lng": 3.3490,
        "price": 260,
        "bedrooms": 4,
        "bathrooms": 3,
    },
]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        for item in SEED_PROPERTIES:
            bucket = await assign_bucket(
                session,
                location_name=item["location_name"],
                lat=item["lat"],
                lng=item["lng"],
            )
            point = func.ST_SetSRID(func.ST_MakePoint(item["lng"], item["lat"]), 4326).cast(
                Geography
            )
            prop = Property(
                title=item["title"],
                location_name=item["location_name"],
                normalized_location_name=normalize_location(item["location_name"]),
                lat=item["lat"],
                lng=item["lng"],
                point=point,
                price=item["price"],
                bedrooms=item["bedrooms"],
                bathrooms=item["bathrooms"],
                geo_bucket_id=bucket.id,
            )
            session.add(prop)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
