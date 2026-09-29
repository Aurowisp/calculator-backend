"""Pydantic response models for calculation history APIs."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HistoryResponse(BaseModel):
    """Describe one persisted calculation history record."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    expression: str
    result: int | float
    created_at: datetime


class DeleteHistoryResponse(BaseModel):
    """Describe a successful history deletion."""

    success: Literal[True] = True
    message: str = "History record deleted"


class HistoryErrorResponse(BaseModel):
    """Describe a history API error."""

    success: Literal[False] = False
    message: str
