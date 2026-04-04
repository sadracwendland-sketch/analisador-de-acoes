from functools import lru_cache

@lru_cache(maxsize=32)
def _cached_yf_history(ticker: str, period: str, interval: str):
    tk = yf.Ticker(ticker)
    return tk.history(period=period, interval=interval, auto_adjust=False, prepost=False)


def _fetch_yfinance(self, ticker: str, period: str) -> MarketPayload | None:
    config = SUPPORTED_PERIODS[period]

    analysis_df = _cached_yf_history(ticker, config["range"], config["interval"])
    daily_df = _cached_yf_history(ticker, LONG_HISTORY_PERIOD, LONG_HISTORY_INTERVAL)

    analysis_df = self._clean_history(analysis_df)
    daily_df = self._clean_history(daily_df)

    if analysis_df.empty or daily_df.empty:
        return None

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
