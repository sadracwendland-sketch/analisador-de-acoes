from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from app.config import LONG_HISTORY_INTERVAL, LONG_HISTORY_PERIOD, SUPPORTED_PERIODS, settings


@dataclass
class MarketPayload:
    ticker: str
    company_name: str | None
    currency: str
    source: str
    analysis_history: pd.DataFrame
    daily_history: pd.DataFrame


class DataProvider:
    def __init__(self) -> None:
        self.session = requests.Session()

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        ticker = ticker.strip().upper()
        if ticker.endswith(".SA"):
            return ticker
        return ticker

    @staticmethod
    def _brapi_symbol(ticker: str) -> str:
        return ticker.replace(".SA", "")

    @staticmethod
    def _clean_history(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        df.columns = [str(c).title() for c in df.columns]
        rename_map = {"Adj Close": "Adj Close", "Close": "Close", "Open": "Open", "High": "High", "Low": "Low", "Volume": "Volume"}
        df = df.rename(columns=rename_map)
        for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
            if col not in df.columns:
                if col == "Adj Close" and "Close" in df.columns:
                    df[col] = df["Close"]
                elif col == "Volume":
                    df[col] = 0.0
                else:
                    df[col] = np.nan
        if hasattr(df.index, "tz") and df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        df = df.sort_index()
        df = df.dropna(subset=["Close"])
        return df

    def _fetch_yfinance(self, ticker: str, period: str) -> MarketPayload | None:
        config = SUPPORTED_PERIODS[period]
        tk = yf.Ticker(ticker)
        analysis_df = tk.history(period=config["range"], interval=config["interval"], auto_adjust=False, prepost=False)
        daily_df = tk.history(period=LONG_HISTORY_PERIOD, interval=LONG_HISTORY_INTERVAL, auto_adjust=False, prepost=False)
        analysis_df = self._clean_history(analysis_df)
        daily_df = self._clean_history(daily_df)
        if analysis_df.empty or daily_df.empty:
            return None
        info = {}
        try:
            info = tk.fast_info or {}
        except Exception:
            info = {}
        company_name = None
        currency = info.get("currency", "USD") if isinstance(info, dict) else "USD"
        return MarketPayload(
            ticker=ticker,
            company_name=company_name,
            currency=currency,
            source="yfinance",
            analysis_history=analysis_df,
            daily_history=daily_df,
        )

    def _fetch_brapi(self, ticker: str, period: str) -> MarketPayload | None:
        if not ticker.endswith(".SA"):
            return None
        symbol = self._brapi_symbol(ticker)
        config = SUPPORTED_PERIODS[period]
        url = f"https://brapi.dev/api/quote/{symbol}"
        headers = {}
        if settings.brapi_token:
            headers["Authorization"] = f"Bearer {settings.brapi_token}"
        params = {"range": config["range"], "interval": config["interval"]}
        resp = self.session.get(url, headers=headers, params=params, timeout=20)
        if resp.status_code >= 400:
            return None
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None
        item = results[0]
        hist = item.get("historicalDataPrice", [])
        if not hist:
            return None
        analysis_df = pd.DataFrame(hist)
        analysis_df["date"] = pd.to_datetime(analysis_df["date"], unit="s")
        analysis_df = analysis_df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "adjustedClose": "Adj Close",
                "volume": "Volume",
            }
        ).set_index("date")
        analysis_df = self._clean_history(analysis_df)

        long_params = {"range": LONG_HISTORY_PERIOD, "interval": LONG_HISTORY_INTERVAL}
        long_resp = self.session.get(url, headers=headers, params=long_params, timeout=20)
        long_item = long_resp.json().get("results", [{}])[0] if long_resp.ok else {}
        long_hist = long_item.get("historicalDataPrice", hist)
        daily_df = pd.DataFrame(long_hist)
        daily_df["date"] = pd.to_datetime(daily_df["date"], unit="s")
        daily_df = daily_df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "adjustedClose": "Adj Close",
                "volume": "Volume",
            }
        ).set_index("date")
        daily_df = self._clean_history(daily_df)
        if analysis_df.empty or daily_df.empty:
            return None
        return MarketPayload(
            ticker=ticker,
            company_name=item.get("longName") or item.get("shortName"),
            currency=item.get("currency", "BRL"),
            source="brapi.dev",
            analysis_history=analysis_df,
            daily_history=daily_df,
        )

    def get_market_data(self, ticker: str, period: str) -> MarketPayload:
        ticker = self._normalize_ticker(ticker)
        if period not in SUPPORTED_PERIODS:
            raise ValueError(f"Período inválido: {period}")
        payload = self._fetch_yfinance(ticker, period)
        if payload is not None:
            return payload
        payload = self._fetch_brapi(ticker, period)
        if payload is not None:
            return payload
        raise ValueError(f"Não foi possível carregar dados para {ticker}")

    def get_ibov_history(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
        ibov = yf.download("^BVSP", start=start.date(), end=(end + timedelta(days=1)).date(), progress=False, auto_adjust=True)
        if ibov.empty:
            return pd.Series(dtype=float)
        if isinstance(ibov.columns, pd.MultiIndex):
            ibov.columns = [c[0] for c in ibov.columns]
        series = ibov["Close"].copy()
        if hasattr(series.index, "tz") and series.index.tz is not None:
            series.index = series.index.tz_convert(None)
        return series.sort_index()

    def get_cdi_daily(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados"
        params = {
            "formato": "json",
            "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": end.strftime("%d/%m/%Y"),
        }
        try:
            resp = self.session.get(url, params=params, timeout=12)
            if not resp.ok:
                return pd.Series(dtype=float)
            rows = resp.json()
            if not rows:
                return pd.Series(dtype=float)
            df = pd.DataFrame(rows)
            df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce") / 100.0
            df = df.dropna()
            return df.set_index("data")["valor"].sort_index()
        except Exception:
            return pd.Series(dtype=float)
