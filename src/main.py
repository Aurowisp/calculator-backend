"""FastAPI application entry point."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.calculator_controller import router as calculator_router
from src.controller.history_controller import router as history_router
from src.database.database import initialize_database


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5500",
    "http://127.0.0.1:5500",
)


def parse_cors_origins(configured_origins: str | None) -> list[str]:
    """Parse comma-separated origins or return local development defaults."""
    if configured_origins is None:
        return list(DEFAULT_CORS_ORIGINS)

    origins = [
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys(origins)) or list(DEFAULT_CORS_ORIGINS)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize database tables when the application starts."""
    initialize_database()
    yield


app = FastAPI(
    title="Calculator Backend",
    description="Backend API for the calculator course project.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(os.getenv("CORS_ORIGINS")),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator_router)
app.include_router(history_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Return the backend availability message."""
    return {"message": "Calculator Backend Running"}


@app.get("/health")
async def read_health() -> dict[str, str]:
    """Return a side-effect-free health check response."""
    return {"status": "ok"}
