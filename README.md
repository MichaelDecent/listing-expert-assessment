# ExpertListing Geo-Bucket Challenge

Async FastAPI backend for geo-bucketed property search with Postgres + PostGIS + pg_trgm.

## Prereqs
- Docker + docker-compose
- Python 3.11

## Run Postgres + PostGIS
```bash
docker-compose up -d
```

Create test database:
```bash
psql postgresql://postgres:postgres@localhost:5432/expertlisting -c "CREATE DATABASE expertlisting_test;"
```

## Install Python deps (uv)
```bash
uv sync
```

## Run migrations
```bash
alembic upgrade head
```

## Seed data
```bash
python seed.py
```

## Run API
```bash
uv run uvicorn src.main:app --reload
```

## Run tests
```bash
uv run pytest
```

## Example cURL
Create a property:
```bash
curl -X POST http://localhost:8000/api/properties \
  -H "Content-Type: application/json" \
  -d '{"title":"Sangotedo","location_name":"Sangotedo","lat":6.4698,"lng":3.6285,"price":120,"bedrooms":3,"bathrooms":2}'
```

Search:
```bash
curl "http://localhost:8000/api/properties/search?location=sangotedo"
```

Bucket stats:
```bash
curl "http://localhost:8000/api/geo-buckets/stats"
```

## Notes
- Set `DATABASE_URL` and `DATABASE_URL_SYNC` to override default connections.
- BUCKET_RADIUS_METERS is 300m; geohash precision is 6.
