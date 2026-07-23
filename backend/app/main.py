import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import engine, Base
import app.models  # noqa: F401

# ── Import routers directly from their files ──────────────────────────────────
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("efficiency_v")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating PostgreSQL tables asynchronously via asyncpg...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL DB ready. Server is up.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routes ───────────────────────────────────────────────────────────
# /api/v1/auth/login, /api/v1/auth/register, /api/v1/auth/me
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)

from app.api.v1.triage import router as triage_router
app.include_router(triage_router, prefix=settings.API_V1_STR)

from app.api.v1.predict import router as predict_router
app.include_router(predict_router, prefix=settings.API_V1_STR)


# app.include_router(chat_router, prefix=settings.API_V1_STR)  ← chat baad mein


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
