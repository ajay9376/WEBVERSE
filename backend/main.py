from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize all database tables automatically on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="WEBVERSE — Your Life. One Connected Intelligence. Universal AI for Academics, Finance, and Life Admin.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow development frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "system": "WEBVERSE Intelligence Engine",
        "tagline": "Your Life. One Connected Intelligence.",
        "status": "ONLINE",
        "docs_url": "/docs",
        "dimensions": ["ACADEMICS", "FINANCE", "LIFE_ADMIN", "UNIVERSAL_AI"]
    }

@app.get("/health")
async def health():
    return {"status": "HEALTHY", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
