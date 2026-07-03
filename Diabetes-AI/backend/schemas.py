"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthInput(BaseModel):
    """Clinical input payload used for prediction."""

    Pregnancies: float = Field(ge=0, le=20)
    Glucose: float = Field(ge=0, le=300)
    BloodPressure: float = Field(ge=0, le=200)
    SkinThickness: float = Field(ge=0, le=100)
    Insulin: float = Field(ge=0, le=900)
    BMI: float = Field(ge=0, le=70)
    DiabetesPedigreeFunction: float = Field(ge=0, le=3)
    Age: float = Field(ge=1, le=120)


class PredictionResponse(BaseModel):
    """Prediction output sent to frontend."""

    risk_level: str
    probability: float
    probability_percent: float
    prediction: int
    explanation: str
    top_contributors: list[tuple[str, float]]
    disclaimer: str


class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str = Field(min_length=1)
    prediction_context: str | None = None
    history: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Chat response payload."""

    response: str


class HistoryEntry(BaseModel):
    """Prediction history entry."""

    timestamp: datetime
    data: dict[str, Any]

