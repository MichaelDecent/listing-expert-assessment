"""geo bucket aliases

Revision ID: 0002_bucket_aliases
Revises: 0001_initial
Create Date: 2026-01-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_bucket_aliases"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "geo_bucket_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geo_bucket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("normalized_alias", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["geo_bucket_id"], ["geo_buckets.id"]),
    )

    op.create_index(
        "ix_geo_bucket_aliases_geo_bucket_id",
        "geo_bucket_aliases",
        ["geo_bucket_id"],
    )
    op.create_index(
        "ix_geo_bucket_aliases_normalized_alias_trgm",
        "geo_bucket_aliases",
        ["normalized_alias"],
        postgresql_using="gin",
        postgresql_ops={"normalized_alias": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_geo_bucket_aliases_normalized_alias_trgm",
        table_name="geo_bucket_aliases",
    )
    op.drop_index(
        "ix_geo_bucket_aliases_geo_bucket_id",
        table_name="geo_bucket_aliases",
    )
    op.drop_table("geo_bucket_aliases")

