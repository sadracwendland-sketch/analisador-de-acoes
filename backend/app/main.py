from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import SUPPORTED_PERIODS, settings
from app.schemas import AnalysisResponse
from app.services.pipeline import run_full_analysis

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/periods")
def periods() -> dict:
    return {"periods": SUPPORTED_PERIODS}


@app.get("/api/analyze", response_model=AnalysisResponse)
def analyze(
    ticker: str = Query(..., description="Ticker, ex: PETR4.SA, VALE3.SA, AAPL"),
    period: str = Query("1d", description="1m, 5m, 1h, 1d, 1y"),
    capital: float = Query(settings.default_capital, ge=1000),
    horizon: int = Query(settings.default_horizon, ge=5, le=10),
):
    try:
        return run_full_analysis(
            ticker=ticker,
            period=period,
            capital=capital,
            horizon=horizon,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Erro interno na análise") from exc


# =========================
# 🔧 FIX RENDER (CRÍTICO)
# =========================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # 👈 ESSENCIAL

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
