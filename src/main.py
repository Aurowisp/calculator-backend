"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.calculator_controller import router as calculator_router
from src.controller.history_controller import router as history_router
from src.database.database import initialize_database


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
    allow_origins=["http://localhost:5500"],
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
