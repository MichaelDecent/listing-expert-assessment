# ExpertListing Geo-Bucket Challenge - Design

## Geo-bucket strategy
We use a hybrid approach: a geohash6 bucket key for fast spatial bucketing and a PostGIS distance check for precision.

- Geohash precision: 6 (approx 1.2km x 0.6km cells).
- Bucket radius: 300 meters.

Assignment flow:
1. Compute geohash6 for the property coordinate.
2. Look up buckets with the same geohash and its 8 neighbors.
3. Reuse an existing bucket if `ST_DWithin(bucket.centroid, property.point, 300)` is true.
4. Otherwise create a new bucket centered on the property point.

Tradeoffs:
- Geohash provides fast candidate lookup via a B-tree index.
- Distance check prevents incorrect grouping at geohash borders.
- Buckets are stable and reused without scanning the properties table.

## Schema and indexes
Tables:
- `geo_buckets`: stores geohash6, normalized name, centroid point, optional cached coverage radius.
- `properties`: stores property metadata and a FK to `geo_buckets`.

Indexes:
- B-tree on `geo_buckets.geohash6` for candidate lookup.
- GiST on `geo_buckets.centroid` for spatial ops.
- GIN trigram on `geo_buckets.normalized_name` for similarity search.
- GiST on `properties.point` for spatial aggregation.
- B-tree on `properties.geo_bucket_id` for fast bucket lookup.

## Location matching logic
We normalize all location strings in Python:
- lowercase
- punctuation removal
- comma to space
- collapse whitespace

Search flow:
1. Normalize query in Python.
2. Use `pg_trgm` similarity (`%` operator + `similarity()` score) to find candidate buckets.
3. Rank by similarity and take top N candidates.
4. Fetch properties using bucket FK (indexed) and return results.

This avoids full table scans and keeps matching typo-tolerant while still anchored on bucket-level indexing.

## ASCII flow diagram

User query
   |
   v
Normalize string
   |
   v
Trigram bucket lookup (GIN index)
   |
   v
Bucket IDs -> properties lookup (FK index)
   |
   v
Return property list

## Scaling for 500,000 properties
- Bucket lookup keeps search bounded to a small candidate set.
- Trigram index avoids sequential scans on `geo_buckets`.
- FK lookup by `geo_bucket_id` scales linearly with bucket size, not total property count.
- Limit candidate buckets (default 10) to cap work per query.
- Use connection pooling and async I/O for high concurrency.

## Assumptions
- `BUCKET_RADIUS_METERS = 300`.
- Trigram similarity threshold `0.3` to tolerate minor typos.
