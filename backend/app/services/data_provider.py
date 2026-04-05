from __future__ import annotations

import yfinance as yf
import pandas as pd
from functools import lru_cache

from app.schemas import MarketPayload
from app.config import SUPPORTED_PERIODS


@lru_cache(maxsize=32)
def _cached_yf_history(ticker: str, period: str, interval: str):
    return yf.download(ticker, period=period, interval=interval, progress=False)


class DataProvider:

    def _clean_history(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        df = df.copy()
        df.columns = [c.strip() for c in df.columns]

        if "Close" in df.columns:
            df["close_used"] = df["Close"]

        return df.dropna(how="all")

def _fetch_yfinance(self, ticker: str, period: str) -> MarketPayload | None:
    try:
        config = SUPPORTED_PERIODS.get(period)

        if not config:
            raise ValueError(f"Período inválido: {period}")

        df = _cached_yf_history(ticker, config["range"], config["interval"])

        if df is None or df.empty:
            print(f"[ERRO] yfinance vazio para {ticker}")
            return None

        df = self._clean_history(df)

        if df is None or df.empty:
            print(f"[ERRO] Dados limpos vazios para {ticker}")
            return None

        # 🔥 GARANTIA CRÍTICA
        if "Close" not in df.columns and "Adj Close" not in df.columns:
            print(f"[ERRO] Sem coluna de preço")
            return None

        tk = yf.Ticker(ticker)

        currency = "USD"
        company_name = None

        try:
            info = tk.fast_info or {}
            if isinstance(info, dict):
                currency = info.get("currency", "USD")
        except Exception:
            pass

        return MarketPayload(
            ticker=ticker,
            company_name=company_name,
            currency=currency,
            source="yfinance",
            analysis_history=df,
            daily_history=df.copy(),
        )

    except Exception as e:
        print(f"[ERRO CRÍTICO YFINANCE] {e}")
        return None
        

    def get_market_data(self, ticker: str, period: str) -> MarketPayload:
        data = self._fetch_yfinance(ticker, period)

        if data is None:
            raise ValueError("Falha ao obter dados de mercado")

        return data

    def get_ibov_history(self, start, end):
        df = yf.download("^BVSP", start=start, end=end, progress=False)
        return df["Close"]

    def get_cdi_daily(self, start, end):
        # simplificado (placeholder)
        return pd.Series([0.0001] * len(pd.date_range(start, end)), index=pd.date_range(start, end))
