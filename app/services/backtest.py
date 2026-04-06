from __future__ import annotations

import numpy as np
import pandas as pd


from app.services.indicators import compute_indicators


def _strategy_positions(df: pd.DataFrame) -> pd.Series:
    pos = pd.Series(0.0, index=df.index)
    bullish = (df["sma10"] > df["sma30"]) & (df["macd"] > df["macd_signal"]) & (df["rsi14"] < 70)
    bearish = (df["sma10"] < df["sma30"]) & (df["macd"] < df["macd_signal"]) & (df["rsi14"] > 30)
    pos[bullish] = 1.0
    pos[bearish] = 0.0
    pos = pos.where(pos != 0.0).ffill().fillna(0.0)
    return pos


def _max_drawdown(cumulative: pd.Series) -> float:
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    return float(drawdown.min()) if not drawdown.empty else 0.0


def _sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    std = returns.std()
    if std == 0 or pd.isna(std):
        return 0.0
    return float(np.sqrt(periods_per_year) * returns.mean() / std)


def run_backtest(asset_daily: pd.DataFrame, ibov_close: pd.Series, cdi_daily: pd.Series) -> dict:
    data = compute_indicators(asset_daily).dropna().copy()
    if data.empty:
        return {
            "stats": {"sharpe_ratio": 0.0, "max_drawdown_pct": 0.0, "strategy_return_pct": 0.0, "ibov_return_pct": 0.0, "cdi_return_pct": 0.0},
            "equity_curve": [],
        }

    positions = _strategy_positions(data)
    asset_returns = data["close_used"].pct_change().fillna(0)
    strategy_returns = positions.shift(1).fillna(0) * asset_returns

    ibov = ibov_close.reindex(data.index).ffill().bfill()
    ibov_returns = ibov.pct_change(fill_method=None).fillna(0) if not ibov.empty else pd.Series(0, index=data.index, dtype=float)

    cdi = cdi_daily.reindex(data.index).ffill().fillna(0)
    cdi_returns = cdi if not cdi.empty else pd.Series(0, index=data.index, dtype=float)

    strat_curve = (1 + strategy_returns).cumprod()
    ibov_curve = (1 + ibov_returns).cumprod()
    cdi_curve = (1 + cdi_returns).cumprod()

    equity_curve = []
    for idx in data.index:
        equity_curve.append(
            {
                "date": idx.isoformat(),
                "strategy": round(float(strat_curve.loc[idx]), 6),
                "ibov": round(float(ibov_curve.loc[idx]), 6) if idx in ibov_curve.index else None,
                "cdi": round(float(cdi_curve.loc[idx]), 6) if idx in cdi_curve.index else None,
            }
        )

    return {
        "stats": {
            "sharpe_ratio": round(_sharpe(strategy_returns), 4),
            "max_drawdown_pct": round(_max_drawdown(strat_curve) * 100, 2),
            "strategy_return_pct": float(round((strat_curve.iloc[-1] - 1) * 100, 2)),
            "ibov_return_pct": float(round((ibov_curve.iloc[-1] - 1) * 100, 2)) if not ibov_curve.empty else 0.0,
            "cdi_return_pct": float(round((cdi_curve.iloc[-1] - 1) * 100, 2)) if not cdi_curve.empty else 0.0,
        },
        "equity_curve": equity_curve,
    }
