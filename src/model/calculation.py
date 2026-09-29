"""Request and response models for the calculation API."""

from typing import Literal

from pydantic import BaseModel


class CalculateRequest(BaseModel):
    """Validate the JSON body accepted by the calculation endpoint."""

    expression: str


class CalculateResponse(BaseModel):
    """Describe a successful calculation response."""

    success: Literal[True] = True
    expression: str
    result: int | float


class CalculateErrorResponse(BaseModel):
    """Describe an expected client-input error response."""

    success: Literal[False] = False
    message: str
