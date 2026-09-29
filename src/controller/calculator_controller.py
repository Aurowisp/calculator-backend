"""Calculator API routes.

Calculation endpoints will be added in a later development phase.
"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/api",
    tags=["calculator"],
)
