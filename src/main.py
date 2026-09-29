"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.calculator_controller import router as calculator_router
from src.controller.history_controller import router as history_router


app = FastAPI(
    title="Calculator Backend",
    description="Backend API for the calculator course project.",
    version="0.1.0",
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
