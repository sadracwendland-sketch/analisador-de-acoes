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

    clean_df = analysis_df.dropna()

    # =========================
    # 🔧 SIGNAL (mantido)
    # =========================
    signal = generate_signal(clean_df) if len(clean_df) >= 35 else {
        "label": "ESPERAR",
        "emoji": "⏸️",
        "confidence": 50.0,
        "score": 0.0,
        "reasons": ["Histórico insuficiente para gerar sinal confiável."]
    }

    # =========================
    # 🔧 FORECAST (corrigido)
    # =========================
    try:
        forecast = forecast_with_lstm(
            compute_indicators(payload.daily_history)["close_used"],
            horizon=horizon
        )
    except Exception as e:
        print(f"Erro forecast: {e}")
        forecast = type("ForecastFallback", (), {
            "predictions": [],
            "trend": "neutro",
            "expected_return_pct": 0.0,
            "horizon_days": horizon,
            "model_name": "fallback",
            "note": "Erro no modelo LSTM"
        })()

    # =========================
    # 🔧 RISK (corrigido)
    # =========================
    try:
        risk = calculate_risk_metrics(clean_df, capital=capital)
    except Exception as e:
        print(f"Erro risk: {e}")
        risk = {}

    # =========================
    # 🔧 BACKTEST (corrigido)
    # =========================
    try:
        ibov = provider.get_ibov_history(payload.daily_history.index.min(), payload.daily_history.index.max())
        cdi = provider.get_cdi_daily(payload.daily_history.index.min(), payload.daily_history.index.max())
        backtest = run_backtest(payload.daily_history, ibov, cdi)
    except Exception as e:
        print(f"Erro backtest: {e}")
        ibov = pd.Series(dtype=float)
        cdi = pd.Series(dtype=float)
        backtest = {
            "stats": {},
            "trades": [],
            "equity_curve": []
        }

    # =========================
    # 🔧 PREÇO (corrigido)
    # =========================
    close_used = analysis_df.get("close_used")

    if close_used is None or close_used.dropna().empty:
        raise ValueError("Sem dados de preço válidos")

    close_used = close_used.dropna()

    last_price = float(close_used.iloc[-1])
    previous = float(close_used.iloc[-2]) if len(close_used) > 1 else last_price
    price_change = ((last_price / previous) - 1) * 100 if previous else 0.0

    # =========================
    # 🔧 SAFE INDICATORS
    # =========================
    def safe_get(df, col, default=0.0, precision=4):
        try:
            return round(float(df[col].iloc[-1]), precision)
        except:
            return default

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
            "sma10": safe_get(analysis_df, "sma10"),
            "sma30": safe_get(analysis_df, "sma30"),
            "rsi14": safe_get(analysis_df, "rsi14", precision=2),
            "macd": safe_get(analysis_df, "macd"),
            "macd_signal": safe_get(analysis_df, "macd_signal"),
            "macd_hist": safe_get(analysis_df, "macd_hist"),
            "bb_upper": safe_get(analysis_df, "bb_upper"),
            "bb_mid": safe_get(analysis_df, "bb_mid"),
            "bb_lower": safe_get(analysis_df, "bb_lower"),
            "atr14": safe_get(analysis_df, "atr14"),
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
