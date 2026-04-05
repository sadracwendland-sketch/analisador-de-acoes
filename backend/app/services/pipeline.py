from app.services.data_provider import DataProvider
from app.services.indicators import compute_indicators, generate_signal
from app.services.ml_model import forecast_with_lstm
from app.services.risk import calculate_risk_metrics
from app.services.backtest import run_backtest

provider = DataProvider()


def run_pipeline(ticker: str, period: str = "3mo", horizon: int = 5):
    payload = provider.get_market_data(ticker, period)

    analysis_df = compute_indicators(payload.analysis_history)

    clean_df = analysis_df.dropna(subset=["close_used"])

    if clean_df.empty:
        raise ValueError("Dados insuficientes")

    # 🔥 EVITA TRAVAMENTO
    series = clean_df["close_used"].tail(60)

    try:
        forecast = forecast_with_lstm(series, horizon=horizon)
    except Exception:
        forecast = {
            "forecast": [],
            "trend": "NEUTRO"
        }

    signal = generate_signal(clean_df)
    risk = calculate_risk_metrics(clean_df)
    backtest = run_backtest(clean_df)

    return {
        "ticker": ticker,
        "signal": signal,
        "risk": risk,
        "forecast": forecast,
        "backtest": backtest,
    }
