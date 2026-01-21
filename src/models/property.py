from sqlalchemy import Integer, Numeric, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from src.models.base import Base, TimestampMixin, UUIDMixin


class Property(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "properties"

    title: Mapped[str] = mapped_column(String)
    location_name: Mapped[str] = mapped_column(String)
    normalized_location_name: Mapped[str | None] = mapped_column(String, nullable=True)
    lat: Mapped[float]
    lng: Mapped[float]
    point: Mapped[str] = mapped_column(Geography(geometry_type="POINT", srid=4326))
    price: Mapped[int | None] = mapped_column(Numeric, nullable=True)
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geo_bucket_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("geo_buckets.id"))

    bucket = relationship("GeoBucket")


Index("ix_properties_point", Property.point, postgresql_using="gist")
Index("ix_properties_geo_bucket_id", Property.geo_bucket_id)
