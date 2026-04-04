from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

try:
    import torch
    from torch import nn
except Exception:  # pragma: no cover
    torch = None
    nn = None


@dataclass
class ForecastResult:
    predictions: list[dict]
    trend: str
    expected_return_pct: float
    horizon_days: int
    model_name: str
    note: str


if nn is not None:
    class LSTMRegressor(nn.Module):
        def __init__(self, input_size: int = 1, hidden_size: int = 32, num_layers: int = 2, dropout: float = 0.2):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers, dropout=dropout, batch_first=True)
            self.linear = nn.Linear(hidden_size, 1)

        def forward(self, x):
            output, _ = self.lstm(x)
            return self.linear(output[:, -1, :])
else:
    class LSTMRegressor:  # pragma: no cover
        pass


def _minmax_scale(values: np.ndarray) -> tuple[np.ndarray, float, float]:
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    scale = vmax - vmin if vmax != vmin else 1.0
    return (values - vmin) / scale, vmin, scale


def _inverse_scale(values: np.ndarray, vmin: float, scale: float) -> np.ndarray:
    return values * scale + vmin


def forecast_with_lstm(close_series: pd.Series, horizon: int = 7, epochs: int = 15, seq_len: int = 60) -> ForecastResult:
    series = close_series.dropna().astype(float)
    if len(series) < seq_len + 20 or torch is None or nn is None:
        last = float(series.iloc[-1])
        preds = []
        for i in range(1, horizon + 1):
            preds.append({"step": i, "predicted_price": round(last, 4)})
        return ForecastResult(
            predictions=preds,
            trend="LATERAL",
            expected_return_pct=0.0,
            horizon_days=horizon,
            model_name="Fallback Naive",
            note="Torch indisponível ou histórico insuficiente; usando fallback ingênuo.",
        )

    values = series.values.reshape(-1, 1).astype(np.float32)
    scaled, vmin, scale = _minmax_scale(values)
    X, y = [], []
    for i in range(seq_len, len(scaled)):
        X.append(scaled[i - seq_len : i])
        y.append(scaled[i])
    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y, dtype=np.float32)

    device = "cpu"
    X_tensor = torch.tensor(X_arr, dtype=torch.float32, device=device)
    y_tensor = torch.tensor(y_arr, dtype=torch.float32, device=device)

    model = LSTMRegressor().to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        pred = model(X_tensor)
        loss = loss_fn(pred, y_tensor)
        loss.backward()
        optimizer.step()

    rolling_window = scaled[-seq_len:].copy()
    preds_scaled = []
    model.eval()
    with torch.no_grad():
        for _ in range(horizon):
            tensor_window = torch.tensor(rolling_window.reshape(1, seq_len, 1), dtype=torch.float32, device=device)
            next_pred = model(tensor_window).cpu().numpy().flatten()[0]
            preds_scaled.append(next_pred)
            rolling_window = np.vstack([rolling_window[1:], [[next_pred]]])

    preds = _inverse_scale(np.array(preds_scaled).reshape(-1, 1), vmin, scale).flatten()
    last_price = float(series.iloc[-1])
    expected_return = float((preds[-1] / last_price - 1) * 100)
    trend = "ALTA" if expected_return > 1 else "BAIXA" if expected_return < -1 else "LATERAL"
    result = [{"step": idx + 1, "predicted_price": round(float(price), 4)} for idx, price in enumerate(preds)]
    return ForecastResult(
        predictions=result,
        trend=trend,
        expected_return_pct=round(expected_return, 2),
        horizon_days=horizon,
        model_name="PyTorch LSTM",
        note="Modelo treinado com janela deslizante de preços de fechamento ajustados.",
    )
