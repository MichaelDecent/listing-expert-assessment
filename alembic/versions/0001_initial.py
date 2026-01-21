"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geography
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "geo_buckets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geohash6", sa.String(), nullable=False),
        sa.Column("normalized_name", sa.String(), nullable=False),
        sa.Column("centroid", Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("coverage_radius_meters", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_geo_buckets_geohash6", "geo_buckets", ["geohash6"])
    op.create_index(
        "ix_geo_buckets_centroid", "geo_buckets", ["centroid"], postgresql_using="gist"
    )
    op.create_index(
        "ix_geo_buckets_normalized_name_trgm",
        "geo_buckets",
        ["normalized_name"],
        postgresql_using="gin",
        postgresql_ops={"normalized_name": "gin_trgm_ops"},
    )

    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("location_name", sa.String(), nullable=False),
        sa.Column("normalized_location_name", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("point", Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("price", sa.Numeric(), nullable=True),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Integer(), nullable=True),
        sa.Column("geo_bucket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["geo_bucket_id"], ["geo_buckets.id"]),
    )

    op.create_index("ix_properties_geo_bucket_id", "properties", ["geo_bucket_id"])
    op.create_index("ix_properties_point", "properties", ["point"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("ix_properties_point", table_name="properties")
    op.drop_index("ix_properties_geo_bucket_id", table_name="properties")
    op.drop_table("properties")

    op.drop_index("ix_geo_buckets_normalized_name_trgm", table_name="geo_buckets")
    op.drop_index("ix_geo_buckets_centroid", table_name="geo_buckets")
    op.drop_index("ix_geo_buckets_geohash6", table_name="geo_buckets")
    op.drop_table("geo_buckets")
