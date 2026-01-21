# ExpertListing Geo-Bucket Challenge

Async FastAPI backend for geo-bucketed property search with Postgres + PostGIS + pg_trgm.

## Prereqs
- Docker + docker compose

## Run Postgres + API (Docker)
```bash
docker compose up -d --build
```

Once running, open the FastAPI docs to create properties, search, and fetch bucket stats:
```text
http://localhost:8000/docs
```

Create test database:
```bash
docker compose exec db psql -U postgres -d expertlisting -c "CREATE DATABASE expertlisting_test;"
```

## Run migrations and seed data
Docker entrypoint runs `alembic upgrade head` and seeds if the `properties` table is empty.

To run manually:
```bash
docker compose exec api uv run alembic upgrade head
docker compose exec api uv run python seed.py
```

## Run tests
```bash
docker compose exec api uv run pytest
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
