from __future__ import annotations

import numpy as np
import pandas as pd


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    close = data["Adj Close"].fillna(data["Close"])
    data["sma10"] = close.rolling(10).mean()
    data["sma30"] = close.rolling(30).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    data["rsi14"] = 100 - (100 / (1 + rs))
    data["rsi14"] = data["rsi14"].fillna(50)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    data["macd"] = ema12 - ema26
    data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()
    data["macd_hist"] = data["macd"] - data["macd_signal"]

    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    data["bb_mid"] = bb_mid
    data["bb_upper"] = bb_mid + 2 * bb_std
    data["bb_lower"] = bb_mid - 2 * bb_std

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (data["High"] - data["Low"]).abs(),
            (data["High"] - prev_close).abs(),
            (data["Low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    data["atr14"] = tr.rolling(14).mean()
    data["return"] = close.pct_change().fillna(0)
    data["close_used"] = close
    return data


def generate_signal(data: pd.DataFrame) -> dict:
    row = data.iloc[-1]
    prev = data.iloc[-2] if len(data) > 1 else row
    close = float(row["close_used"])
    score = 0.0
    reasons: list[str] = []

    bullish_cross = row["sma10"] > row["sma30"] and prev["sma10"] <= prev["sma30"]
    bearish_cross = row["sma10"] < row["sma30"] and prev["sma10"] >= prev["sma30"]
    if bullish_cross:
        score += 0.35
        reasons.append("SMA10 cruzou acima da SMA30")
    elif bearish_cross:
        score -= 0.35
        reasons.append("SMA10 cruzou abaixo da SMA30")
    elif row["sma10"] > row["sma30"]:
        score += 0.15
        reasons.append("SMA10 permanece acima da SMA30")
    else:
        score -= 0.15
        reasons.append("SMA10 permanece abaixo da SMA30")

    rsi = float(row["rsi14"])
    if rsi < 30:
        score += 0.2
        reasons.append("RSI indica sobrevenda")
    elif rsi > 70:
        score -= 0.2
        reasons.append("RSI indica sobrecompra")
    else:
        reasons.append("RSI em região neutra")

    if row["macd"] > row["macd_signal"] and prev["macd"] <= prev["macd_signal"]:
        score += 0.25
        reasons.append("MACD cruzou para cima")
    elif row["macd"] < row["macd_signal"] and prev["macd"] >= prev["macd_signal"]:
        score -= 0.25
        reasons.append("MACD cruzou para baixo")
    elif row["macd"] > row["macd_signal"]:
        score += 0.1
        reasons.append("MACD está positivo")
    else:
        score -= 0.1
        reasons.append("MACD está negativo")

    if close <= float(row["bb_lower"]):
        score += 0.2
        reasons.append("Preço encostou na banda inferior de Bollinger")
    elif close >= float(row["bb_upper"]):
        score -= 0.2
        reasons.append("Preço encostou na banda superior de Bollinger")
    else:
        reasons.append("Preço dentro das bandas de Bollinger")

    confidence = round(min(99.0, 50 + abs(score) * 60), 2)
    if score >= 0.25:
        return {"label": "COMPRA", "emoji": "🟢", "confidence": confidence, "score": round(score, 4), "reasons": reasons}
    if score <= -0.25:
        return {"label": "VENDA", "emoji": "🔴", "confidence": confidence, "score": round(score, 4), "reasons": reasons}
    return {"label": "ESPERAR", "emoji": "⏸️", "confidence": confidence, "score": round(score, 4), "reasons": reasons}
