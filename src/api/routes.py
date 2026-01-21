from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography

from src.db.session import get_session
from src.models.geobucket import GeoBucket
from src.models.property import Property
from src.schemas.property import PropertyCreate, PropertyRead, PropertyWithBucket
from src.schemas.geobucket import GeoBucketRead
from src.services.bucket_service import assign_bucket
from src.services.normalize import normalize_location
from src.services.search_service import search_properties

router = APIRouter()


@router.post("/properties", response_model=PropertyWithBucket)
async def create_property(
    payload: PropertyCreate, session: AsyncSession = Depends(get_session)
) -> PropertyWithBucket:
    bucket = await assign_bucket(
        session, location_name=payload.location_name, lat=payload.lat, lng=payload.lng
    )
    point = func.ST_SetSRID(func.ST_MakePoint(payload.lng, payload.lat), 4326).cast(
        Geography
    )
    prop = Property(
        title=payload.title,
        location_name=payload.location_name,
        normalized_location_name=normalize_location(payload.location_name),
        lat=payload.lat,
        lng=payload.lng,
        point=point,
        price=payload.price,
        bedrooms=payload.bedrooms,
        bathrooms=payload.bathrooms,
        geo_bucket_id=bucket.id,
    )
    session.add(prop)
    await session.commit()
    await session.refresh(prop)
    await session.refresh(bucket)
    return PropertyWithBucket(
        property=PropertyRead.model_validate(prop),
        bucket=GeoBucketRead.model_validate(bucket),
    )


@router.get("/properties/search", response_model=List[PropertyRead])
async def search(location: str = Query(..., min_length=2), session: AsyncSession = Depends(get_session)):
    props = await search_properties(session, location=location)
    return [PropertyRead.model_validate(prop) for prop in props]


@router.get("/geo-buckets/stats")
async def bucket_stats(session: AsyncSession = Depends(get_session)):
    distance = func.ST_Distance(GeoBucket.centroid, Property.point)
    stmt = (
        select(
            GeoBucket.id.label("bucket_id"),
            func.count(Property.id).label("property_count"),
            func.coalesce(func.max(distance), 0).label("coverage_radius_meters"),
        )
        .outerjoin(Property, Property.geo_bucket_id == GeoBucket.id)
        .group_by(GeoBucket.id)
    )
    result = await session.execute(stmt)
    rows = result.mappings().all()
    return {
        "total_buckets": len(rows),
        "buckets": [
            {
                "bucket_id": row["bucket_id"],
                "property_count": row["property_count"],
                "coverage_radius_meters": int(row["coverage_radius_meters"] or 0),
            }
            for row in rows
        ],
    }
