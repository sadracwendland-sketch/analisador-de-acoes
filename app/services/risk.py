from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_risk_metrics(df: pd.DataFrame, capital: float, confidence: float = 0.95) -> dict:
    close = float(df["close_used"].iloc[-1])
    atr = float(df["atr14"].iloc[-1]) if not pd.isna(df["atr14"].iloc[-1]) else close * 0.03
    stop_loss_pct = min(0.05, max(0.02, (atr / close) * 1.5))
    stop_price = close * (1 - stop_loss_pct)

    returns = df["return"].dropna()
    if returns.empty:
        var_pct = 0.0
    else:
        var_pct = float(abs(np.quantile(returns, 1 - confidence)))
    risk_budget = capital * 0.02
    risk_per_share = max(close - stop_price, close * 0.0001)
    shares = int(max(0, risk_budget // risk_per_share))
    position_value = shares * close

    return {
        "capital_base": float(round(capital, 2)),
        "risk_budget": round(risk_budget, 2),
        "stop_loss_pct": round(stop_loss_pct * 100, 2),
        "stop_loss_price": round(stop_price, 4),
        "value_at_risk_95_pct": round(var_pct * 100, 2),
        "value_at_risk_95_amount": round(position_value * var_pct, 2),
        "position_size_shares": shares,
        "position_size_value": round(position_value, 2),
        "risk_per_share": round(risk_per_share, 4),
    }
