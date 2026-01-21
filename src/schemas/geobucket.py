from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GeoBucketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    geohash6: str
    normalized_name: str
    coverage_radius_meters: int | None
    created_at: datetime
    updated_at: datetime
