import pandas as pd


class MarketPayload(BaseModel):
    ticker: str
    company_name: str | None
    currency: str
    source: str
    analysis_history: pd.DataFrame
    daily_history: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True
