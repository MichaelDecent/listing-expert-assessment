from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, TimestampMixin, UUIDMixin


class GeoBucketAlias(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "geo_bucket_aliases"

    geo_bucket_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_buckets.id"), index=True
    )
    normalized_alias: Mapped[str] = mapped_column(String, nullable=False)


Index(
    "ix_geo_bucket_aliases_normalized_alias_trgm",
    GeoBucketAlias.normalized_alias,
    postgresql_using="gin",
)
