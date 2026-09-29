"""History API routes.

History endpoints will be added after persistence support is introduced.
"""

from fastapi import APIRouter


router = APIRouter(
    prefix="/api/history",
    tags=["history"],
)
