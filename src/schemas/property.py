from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.schemas.geobucket import GeoBucketRead


class PropertyCreate(BaseModel):
    title: str
    location_name: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    price: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None


class PropertyRead(BaseModel):
    id: UUID
    title: str
    location_name: str
    normalized_location_name: str | None
    lat: float
    lng: float
    price: int | None
    bedrooms: int | None
    bathrooms: int | None
    geo_bucket_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyWithBucket(BaseModel):
    property: PropertyRead
    bucket: GeoBucketRead
