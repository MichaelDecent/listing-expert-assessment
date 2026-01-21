from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(title="ExpertListing Geo-Bucket Challenge")
app.include_router(router, prefix="/api")
