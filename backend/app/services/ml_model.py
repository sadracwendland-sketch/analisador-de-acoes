import numpy as np


def forecast_with_lstm(series, horizon=5):
    # 🔥 fallback leve (remove deep learning pesado)
    values = series.values

    if len(values) < 10:
        return {"forecast": [], "trend": "NEUTRO"}

    trend = "ALTA" if values[-1] > values.mean() else "BAIXA"

    forecast = [float(values[-1]) for _ in range(horizon)]

    return {
        "forecast": forecast,
        "trend": trend
    }
