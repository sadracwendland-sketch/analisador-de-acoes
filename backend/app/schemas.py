from __future__ import annotations

from typing import Any, Literal
import pandas as pd

from pydantic import BaseModel, Field


class SignalModel(BaseModel):
    label: Literal["COMPRA", "VENDA", "ESPERAR"]
    emoji: str
    confidence: float
    score: float
    reasons: list[str]


class AnalysisResponse(BaseModel):
    ticker: str
    period: str
    currency: str = "USD"
    last_price: float
    price_change_pct: float
    company_name: str | None = None
    market_source: str
    price_history: list[dict[str, Any]]
    indicators: dict[str, Any]
    signal: SignalModel
    forecast: dict[str, Any]
    risk: dict[str, Any]
    backtest: dict[str, Any]
    benchmark: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)


class MarketPayload(BaseModel):
    ticker: str
    company_name: str | None
    currency: str
    source: str
    analysis_history: pd.DataFrame
    daily_history: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True
