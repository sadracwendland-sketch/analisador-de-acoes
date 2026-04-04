from __future__ import annotations

import pandas as pd

from app.services.backtest import run_backtest
from app.services.data_provider import DataProvider
from app.services.indicators import compute_indicators, generate_signal
from app.services.ml_model import forecast_with_lstm
from app.services.risk import calculate_risk_metrics

provider = DataProvider()


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume", "sma10", "sma30", "rsi14", "macd", "macd_signal", "macd_hist", "bb_upper", "bb_mid", "bb_lower"]
    existing = [c for c in cols if c in df.columns]
    records = []
    for idx, row in df[existing].dropna(how="all").iterrows():
        record = {"date": idx.isoformat()}
        for col in existing:
            value = row[col]
            record[col.lower().replace(" ", "_")] = None if pd.isna(value) else round(float(value), 6)
        records.append(record)
    return records


def run_full_analysis(ticker: str, period: str, capital: float, horizon: int) -> dict:
    payload = provider.get_market_data(ticker, period)
    analysis_df = compute_indicators(payload.analysis_history)
    signal = generate_signal(analysis_df.dropna()) if len(analysis_df.dropna()) >= 35 else {"label": "ESPERAR", "emoji": "⏸️", "confidence": 50.0, "score": 0.0, "reasons": ["Histórico insuficiente para gerar sinal confiável."]}
    forecast = forecast_with_lstm(compute_indicators(payload.daily_history)["close_used"], horizon=horizon)
    risk = calculate_risk_metrics(analysis_df.dropna(), capital=capital)
    ibov = provider.get_ibov_history(payload.daily_history.index.min(), payload.daily_history.index.max())
    cdi = provider.get_cdi_daily(payload.daily_history.index.min(), payload.daily_history.index.max())
    backtest = run_backtest(payload.daily_history, ibov, cdi)

    close_used = analysis_df["close_used"].dropna()
    last_price = float(close_used.iloc[-1])
    previous = float(close_used.iloc[-2]) if len(close_used) > 1 else last_price
    price_change = ((last_price / previous) - 1) * 100 if previous else 0.0

    return {
        "ticker": payload.ticker,
        "period": period,
        "currency": payload.currency,
        "last_price": round(last_price, 4),
        "price_change_pct": round(price_change, 2),
        "company_name": payload.company_name,
        "market_source": payload.source,
        "price_history": dataframe_to_records(analysis_df.tail(300)),
        "indicators": {
            "sma10": round(float(analysis_df["sma10"].iloc[-1]), 4),
            "sma30": round(float(analysis_df["sma30"].iloc[-1]), 4),
            "rsi14": round(float(analysis_df["rsi14"].iloc[-1]), 2),
            "macd": round(float(analysis_df["macd"].iloc[-1]), 4),
            "macd_signal": round(float(analysis_df["macd_signal"].iloc[-1]), 4),
            "macd_hist": round(float(analysis_df["macd_hist"].iloc[-1]), 4),
            "bb_upper": round(float(analysis_df["bb_upper"].iloc[-1]), 4),
            "bb_mid": round(float(analysis_df["bb_mid"].iloc[-1]), 4),
            "bb_lower": round(float(analysis_df["bb_lower"].iloc[-1]), 4),
            "atr14": round(float(analysis_df["atr14"].iloc[-1]), 4),
        },
        "signal": signal,
        "forecast": {
            "predictions": forecast.predictions,
            "trend": forecast.trend,
            "expected_return_pct": forecast.expected_return_pct,
            "horizon_days": forecast.horizon_days,
            "model_name": forecast.model_name,
            "note": forecast.note,
        },
        "risk": risk,
        "backtest": backtest,
        "benchmark": {
            "ibov_points": [{"date": idx.isoformat(), "close": round(float(val), 4)} for idx, val in ibov.tail(300).items()],
            "cdi_daily": [{"date": idx.isoformat(), "rate": round(float(val), 6)} for idx, val in cdi.tail(300).items()],
        },
        "meta": {
            "records_analysis": int(len(payload.analysis_history)),
            "records_daily": int(len(payload.daily_history)),
        },
    }
