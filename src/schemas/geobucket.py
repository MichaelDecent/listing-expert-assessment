from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GeoBucketRead(BaseModel):
    id: UUID
    geohash6: str
    normalized_name: str
    coverage_radius_meters: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
