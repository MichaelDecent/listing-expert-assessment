from sqlalchemy import Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geography

from src.models.base import Base, TimestampMixin, UUIDMixin


class GeoBucket(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "geo_buckets"

    geohash6: Mapped[str] = mapped_column(String, index=True)
    normalized_name: Mapped[str] = mapped_column(String)
    centroid: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    coverage_radius_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)


Index("ix_geo_buckets_centroid", GeoBucket.centroid, postgresql_using="gist")
Index("ix_geo_buckets_normalized_name_trgm", GeoBucket.normalized_name, postgresql_using="gin")
