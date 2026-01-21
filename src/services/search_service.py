from __future__ import annotations

from typing import Sequence

from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.models.geobucket import GeoBucket
from src.models.property import Property
from src.services.normalize import normalize_location

TRIGRAM_THRESHOLD = 0.3
CANDIDATE_LIMIT = 10


async def search_properties(session: AsyncSession, *, location: str) -> Sequence[Property]:
    normalized = normalize_location(location)

    similarity = func.similarity(GeoBucket.normalized_name, normalized)
    trigram_match = GeoBucket.normalized_name.op("%")
    stmt = (
        select(GeoBucket.id)
        .where(or_(similarity > TRIGRAM_THRESHOLD, trigram_match(normalized)))
        .order_by(desc(similarity))
        .limit(CANDIDATE_LIMIT)
    )

    result = await session.execute(stmt)
    bucket_ids = [row[0] for row in result.all()]
    if not bucket_ids:
        return []

    prop_stmt = (
        select(Property)
        .where(Property.geo_bucket_id.in_(bucket_ids))
        .order_by(desc(Property.created_at), desc(Property.id))
    )
    prop_result = await session.execute(prop_stmt)
    return prop_result.scalars().all()
