import yfinance as yf
import pandas as pd
from functools import lru_cache
from typing import Optional
from app.models.schemas import MarketPayload

SUPPORTED_PERIODS = {
    "1mo": {"range": "1mo", "interval": "1d"},
    "3mo": {"range": "3mo", "interval": "1d"},
    "6mo": {"range": "6mo", "interval": "1d"},
}


@lru_cache(maxsize=32)
def _cached_yf_history(ticker: str, range_: str, interval: str):
    try:
        df = yf.download(ticker, period=range_, interval=interval, progress=False)
        return df
    except Exception:
        return None


class DataProvider:

    def _clean_history(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip() for c in df.columns]

        if "Adj Close" in df.columns:
            df["close_used"] = df["Adj Close"]
        elif "Close" in df.columns:
            df["close_used"] = df["Close"]
        else:
            return pd.DataFrame()

        return df.dropna()

    def _fetch_yfinance(self, ticker: str, period: str) -> Optional[MarketPayload]:
        try:
            config = SUPPORTED_PERIODS.get(period)

            if not config:
                raise ValueError(f"Período inválido: {period}")

            df = _cached_yf_history(ticker, config["range"], config["interval"])

            if df is None or df.empty:
                return None

            df = self._clean_history(df)

            if df.empty:
                return None

            tk = yf.Ticker(ticker)

            currency = "USD"
            try:
                info = tk.fast_info or {}
                if isinstance(info, dict):
                    currency = info.get("currency", "USD")
            except Exception:
                pass

            return MarketPayload(
                ticker=ticker,
                company_name=None,
                currency=currency,
                source="yfinance",
                analysis_history=df,
                daily_history=df.copy(),
            )

        except Exception:
            return None

    def get_market_data(self, ticker: str, period: str) -> MarketPayload:
        data = self._fetch_yfinance(ticker, period)

        if data is None:
            raise ValueError(f"Falha ao obter dados para {ticker}")

        return data
