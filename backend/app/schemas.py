from __future__ import annotations

import pandas as pd
from pydantic import BaseModel


class MarketPayload(BaseModel):
    ticker: str
    company_name: str | None
    currency: str
    source: str
    analysis_history: pd.DataFrame
    daily_history: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True
