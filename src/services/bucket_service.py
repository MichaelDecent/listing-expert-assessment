from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from geoalchemy2 import Geography

from src.models.geobucket import GeoBucket
from src.services.normalize import normalize_location

BUCKET_PRECISION = 6
BUCKET_RADIUS_METERS = 300

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_encode(lat: float, lng: float, precision: int = BUCKET_PRECISION) -> str:
    lat_interval = [-90.0, 90.0]
    lng_interval = [-180.0, 180.0]
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = sum(lng_interval) / 2
            if lng > mid:
                ch |= bits[bit]
                lng_interval[0] = mid
            else:
                lng_interval[1] = mid
        else:
            mid = sum(lat_interval) / 2
            if lat > mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(_BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)


def _neighbor(hashcode: str, direction: str) -> str:
    neighbors = {
        "n": "p0r21436x8zb9dcf5h7kjnmqesgutwvy",
        "s": "14365h7k9dcfesgujnmqp0r2twvyx8zb",
        "e": "bc01fg45238967deuvhjyznpkmstqrwx",
        "w": "238967debc01fg45kmstqrwxuvhjyznp",
    }
    borders = {
        "n": "prxz",
        "s": "028b",
        "e": "bcfguvyz",
        "w": "0145hjnp",
    }

    last = hashcode[-1]
    parent = hashcode[:-1]
    if last in borders[direction] and parent:
        parent = _neighbor(parent, direction)
    index = neighbors[direction].find(last)
    return parent + _BASE32[index]


def geohash_neighbors(hashcode: str) -> Iterable[str]:
    n = _neighbor(hashcode, "n")
    s = _neighbor(hashcode, "s")
    e = _neighbor(hashcode, "e")
    w = _neighbor(hashcode, "w")
    return {
        n,
        s,
        e,
        w,
        _neighbor(n, "e"),
        _neighbor(n, "w"),
        _neighbor(s, "e"),
        _neighbor(s, "w"),
    }


async def assign_bucket(
    session: AsyncSession, *, location_name: str, lat: float, lng: float
) -> GeoBucket:
    geohash6 = geohash_encode(lat, lng, BUCKET_PRECISION)
    candidate_hashes = {geohash6, *geohash_neighbors(geohash6)}
    normalized = normalize_location(location_name)
    point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326).cast(Geography)

    stmt = select(GeoBucket).where(GeoBucket.geohash6.in_(candidate_hashes))
    result = await session.execute(stmt)
    buckets = result.scalars().all()

    for bucket in buckets:
        within = await session.execute(
            select(
                func.ST_DWithin(bucket.centroid, point, BUCKET_RADIUS_METERS)
            )
        )
        if within.scalar():
            return bucket

    bucket = GeoBucket(
        geohash6=geohash6,
        normalized_name=normalized,
        centroid=point,
        coverage_radius_meters=None,
    )
    session.add(bucket)
    await session.flush()
    return bucket
