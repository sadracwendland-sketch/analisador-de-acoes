from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Stock Analyzer Pro API"
    brapi_token: str | None = os.getenv("BRAPI_API_KEY")
    cors_origins: list[str] = None  # type: ignore[assignment]
    default_capital: float = float(os.getenv("DEFAULT_CAPITAL", "100000"))
    default_horizon: int = int(os.getenv("DEFAULT_FORECAST_HORIZON", "7"))

    def __post_init__(self):
        if self.cors_origins is None:
            object.__setattr__(
                self,
                "cors_origins",
                [
                    "*",
                ],
            )


settings = Settings()

SUPPORTED_PERIODS = {
    "1m": {"range": "7d", "interval": "1m", "label": "Intraday 1 minuto"},
    "5m": {"range": "60d", "interval": "5m", "label": "Intraday 5 minutos"},
    "1h": {"range": "730d", "interval": "1h", "label": "Intraday 1 hora"},
    "1d": {"range": "5y", "interval": "1d", "label": "Diário"},
    "1y": {"range": "10y", "interval": "1mo", "label": "Mensal / visão anual"},
}

LONG_HISTORY_PERIOD = "5y"
LONG_HISTORY_INTERVAL = "1d"
