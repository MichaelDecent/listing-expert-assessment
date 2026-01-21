from __future__ import annotations

from typing import Sequence

from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.models.geobucket import GeoBucket
from src.models.geobucket_alias import GeoBucketAlias
from src.models.property import Property
from src.services.normalize import normalize_location

TRIGRAM_THRESHOLD = 0.3
CANDIDATE_LIMIT = 10


async def search_properties(session: AsyncSession, *, location: str) -> Sequence[Property]:
    normalized = normalize_location(location)

    bucket_similarity = func.similarity(GeoBucket.normalized_name, normalized).label(
        "score"
    )
    bucket_trigram_match = GeoBucket.normalized_name.op("%")
    bucket_matches = select(GeoBucket.id.label("bucket_id"), bucket_similarity).where(
        or_(bucket_similarity > TRIGRAM_THRESHOLD, bucket_trigram_match(normalized))
    )

    alias_similarity = func.similarity(
        GeoBucketAlias.normalized_alias, normalized
    ).label("score")
    alias_trigram_match = GeoBucketAlias.normalized_alias.op("%")
    alias_matches = select(
        GeoBucketAlias.geo_bucket_id.label("bucket_id"), alias_similarity
    ).where(or_(alias_similarity > TRIGRAM_THRESHOLD, alias_trigram_match(normalized)))

    unioned = bucket_matches.union_all(alias_matches).subquery("candidates")
    stmt = (
        select(unioned.c.bucket_id)
        .group_by(unioned.c.bucket_id)
        .order_by(desc(func.max(unioned.c.score)))
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
