from functools import lru_cache
import yfinance as yf

from app.schemas.market import MarketPayload  # 👈 USE ESSE (MAIS SEGURO)
from app.config import SUPPORTED_PERIODS


@lru_cache(maxsize=32)
def _cached_yf_history(ticker: str, period: str, interval: str):
    return yf.download(ticker, period=period, interval=interval, progress=False)


def _fetch_yfinance(self, ticker: str, period: str) -> MarketPayload | None:
    try:
        config = SUPPORTED_PERIODS[period]

        analysis_df = _cached_yf_history(ticker, config["range"], config["interval"])
        analysis_df = self._clean_history(analysis_df)

        if analysis_df is None or analysis_df.empty:
            return None

        daily_df = analysis_df.copy()

        tk = yf.Ticker(ticker)

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

    except Exception as e:
        print(f"Erro yfinance: {e}")
        return None
