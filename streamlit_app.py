from __future__ import annotations

import json
import os
import sys
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# Na estrutura flat, 'app' está na raiz, então as importações diretas funcionam
# Configuração de períodos suportados (copiado do backend para evitar importação pesada)
SUPPORTED_PERIODS = {
    "1d": {"label": "1 Dia", "days": 1},
    "5d": {"label": "5 Dias", "days": 5},
    "1mo": {"label": "1 Mês", "days": 22},
    "3mo": {"label": "3 Meses", "days": 66},
    "6mo": {"label": "6 Meses", "days": 132},
    "1y": {"label": "1 Ano", "days": 252},
}

API_BASE_URL = os.getenv("API_BASE_URL", "https://stock-analyzer-api-9f95.onrender.com").rstrip("/")

st.set_page_config(page_title="Stock Analyzer Pro", page_icon="📈", layout="wide", initial_sidebar_state="expanded")


def inject_pwa_assets() -> None:
    # No Streamlit, arquivos em static/ são servidos via static/ (quando na raiz)
    manifest_url = "static/manifest.json"
    icon_192 = "static/icon-192.png"
    icon_512 = "static/icon-512.png"
    worker_js = """
      const swCode = `
        const CACHE_NAME = 'stock-analyzer-v1';
        self.addEventListener('install', event => { self.skipWaiting(); });
        self.addEventListener('activate', event => { event.waitUntil(self.clients.claim()); });
      `;
      if ('serviceWorker' in navigator) {
        const blob = new Blob([swCode], {type: 'text/javascript'});
        const url = URL.createObjectURL(blob);
        navigator.serviceWorker.register(url).catch(() => null);
      }
    """
    html = f"""
    <script>
      const ensureLink = (rel, href) => {{
        if (![...document.head.querySelectorAll(`link[rel='${{rel}}']`)].some(el => el.href.includes(href))) {{
          const link = document.createElement('link');
          link.rel = rel;
          link.href = href;
          document.head.appendChild(link);
        }}
      }};
      ensureLink('manifest', '{manifest_url}');
      const metaTheme = document.createElement('meta');
      metaTheme.name = 'theme-color';
      metaTheme.content = '#0f172a';
      document.head.appendChild(metaTheme);
      const icon = document.createElement('link');
      icon.rel = 'apple-touch-icon';
      icon.href = '{icon_192}';
      document.head.appendChild(icon);
      {worker_js}
    </script>
    """
    components.html(html, height=0)


def apply_css(dark_mode: bool) -> None:
    bg = "#020617" if dark_mode else "#f8fafc"
    fg = "#e2e8f0" if dark_mode else "#0f172a"
    card = "#0f172a" if dark_mode else "#ffffff"
    border = "rgba(148,163,184,0.2)"
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {bg}; color: {fg}; }}
          .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}
          .metric-card {{
              background: {card};
              border: 1px solid {border};
              border-radius: 18px;
              padding: 16px 18px;
              box-shadow: 0 10px 30px rgba(15,23,42,0.08);
              margin-bottom: 12px;
          }}
          .metric-title {{ font-size: 0.85rem; opacity: 0.8; margin-bottom: 6px; }}
          .metric-value {{ font-size: 1.55rem; font-weight: 700; }}
          .signal-buy {{ color: #22c55e; font-weight: 700; }}
          .signal-sell {{ color: #ef4444; font-weight: 700; }}
          .signal-wait {{ color: #f59e0b; font-weight: 700; }}
          .stButton > button {{ border-radius: 14px; min-height: 46px; font-weight: 600; }}
          .stTextInput > div > div > input, .stNumberInput input {{ border-radius: 12px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=180, show_spinner=False)
def load_analysis(ticker: str, period: str, capital: float, horizon: int) -> dict:
    # Sempre usar a API do Render para cálculos pesados (ML/LSTM)
    try:
        # Se o período for 1d ou 5d, pedimos 1mo para a API ter dados suficientes para indicadores
        api_period = "1mo" if period in ["1d", "5d"] else period
        
        response = requests.get(
            f"{API_BASE_URL}/api/analyze",
            params={"ticker": ticker, "period": api_period, "capital": capital, "horizon": horizon},
            timeout=180,
        )
        
        if response.status_code == 400:
            try:
                error_detail = response.json().get("detail", "Erro desconhecido")
            except:
                error_detail = response.text
            st.error(f"A API recusou o pedido (400): {error_detail}")
            return None
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao conectar com a API no Render: {str(e)}")
        st.info("Verifique se o seu serviço no Render está 'Active'.")
        return None


def metric_card(title: str, value: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-title'>{title}</div>
          <div class='metric-value'>{value}</div>
          <div style='opacity:0.75;font-size:0.85rem;margin-top:6px'>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_price_chart(data: dict, dark_mode: bool) -> go.Figure:
    df = pd.DataFrame(data["price_history"])
    df["date"] = pd.to_datetime(df["date"])
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.07)
    fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Preço"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["sma10"], name="SMA10", line=dict(color="#22c55e", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["sma30"], name="SMA30", line=dict(color="#38bdf8", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["bb_upper"], name="BB Upper", line=dict(color="#94a3b8", width=1, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["bb_lower"], name="BB Lower", line=dict(color="#94a3b8", width=1, dash="dot"), fill="tonexty", fillcolor="rgba(148,163,184,0.10)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["rsi14"], name="RSI(14)", line=dict(color="#f59e0b", width=2)), row=2, col=1)
    fig.add_hline(y=70, row=2, col=1, line_dash="dash", line_color="#ef4444")
    fig.add_hline(y=30, row=2, col=1, line_dash="dash", line_color="#22c55e")
    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly_white",
        height=720,
        margin=dict(l=8, r=8, t=30, b=8),
        xaxis_rangeslider_visible=False,
        legend_orientation="h",
    )
    return fig


def build_backtest_chart(data: dict, dark_mode: bool) -> go.Figure:
    df = pd.DataFrame(data["backtest"]["equity_curve"])
    df["date"] = pd.to_datetime(df["date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["strategy"], mode="lines", name="Estratégia", line=dict(color="#22c55e", width=3)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["ibov"], mode="lines", name="IBOV", line=dict(color="#38bdf8", width=2)))
    fig.add_trace(go.Scatter(x=df["date"], y=df["cdi"], mode="lines", name="CDI", line=dict(color="#f59e0b", width=2)))
    fig.update_layout(template="plotly_dark" if dark_mode else "plotly_white", height=420, margin=dict(l=8, r=8, t=30, b=8), legend_orientation="h")
    return fig


def build_forecast_chart(data: dict, dark_mode: bool) -> go.Figure:
    history = pd.DataFrame(data["price_history"]).tail(60)
    history["date"] = pd.to_datetime(history["date"])
    preds = pd.DataFrame(data["forecast"]["predictions"])
    last_date = history["date"].iloc[-1]
    preds["date"] = [last_date + pd.tseries.offsets.BDay(i) for i in range(1, len(preds) + 1)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["date"], y=history["close"], name="Histórico", line=dict(color="#38bdf8", width=3)))
    fig.add_trace(go.Scatter(x=preds["date"], y=preds["predicted_price"], name="LSTM Forecast", line=dict(color="#a855f7", width=3, dash="dash")))
    fig.update_layout(template="plotly_dark" if dark_mode else "plotly_white", height=360, margin=dict(l=8, r=8, t=30, b=8))
    return fig


def main() -> None:
    inject_pwa_assets()
    with st.sidebar:
        st.title("📈 Stock Analyzer Pro")
        dark_mode = st.toggle("Dark mode", value=True)
        
        # Normalização do Ticker no Frontend
        raw_ticker = st.text_input("Ticker", value="PETR4.SA")
        ticker = raw_ticker.strip().upper()
        if re.match(r'^[A-Z]{4}[0-9]{1,2}$', ticker):
            ticker = f"{ticker}.SA"
            
        period = st.selectbox("Período", options=list(SUPPORTED_PERIODS.keys()), index=3, format_func=lambda x: f"{x} · {SUPPORTED_PERIODS[x]['label']}")
        capital = st.number_input("Capital (R$ / US$)", min_value=1000.0, value=100000.0, step=1000.0)
        horizon = st.slider("Horizonte da previsão (dias)", min_value=5, max_value=10, value=7)
        run = st.button("Analisar agora", use_container_width=True, type="primary")
        st.caption("Se API_BASE_URL estiver vazio, o Streamlit executa a análise localmente.")

    apply_css(dark_mode)
    st.title("🔥 Dashboard de análise técnica, risco, ML e backtest")
    st.write("Dashboard responsivo para web/celular com FastAPI + Streamlit + Expo. Use o botão abaixo para recalcular os sinais.")

    if not run and "analysis_payload" not in st.session_state:
        run = True

    if run:
        with st.spinner("Buscando dados, calculando indicadores, treinando LSTM e rodando backtest..."):
            st.session_state["analysis_payload"] = load_analysis(ticker, period, capital, horizon)

    data = st.session_state.get("analysis_payload")
    if not data:
        st.stop()

    signal = data["signal"]
    signal_class = "signal-buy" if signal["label"] == "COMPRA" else "signal-sell" if signal["label"] == "VENDA" else "signal-wait"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Ticker", data["ticker"], data.get("company_name") or data["market_source"])
    with col2:
        metric_card("Último preço", f"{data['currency']} {data['last_price']:.2f}", f"Variação {data['price_change_pct']:.2f}%")
    with col3:
        metric_card("Sinal", f"<span class='{signal_class}'>{signal['emoji']} {signal['label']}</span>", f"Confiança {signal['confidence']:.1f}%")
    with col4:
        metric_card("Previsão {0}d".format(data["forecast"]["horizon_days"]), f"{data['forecast']['trend']}", f"Retorno esp. {data['forecast']['expected_return_pct']:.2f}%")

    st.plotly_chart(build_price_chart(data, dark_mode), use_container_width=True, config={"responsive": True, "displaylogo": False})

    tab1, tab2, tab3 = st.tabs(["📊 Técnico", "🤖 ML & Risco", "📈 Backtest"])
    with tab1:
        i1, i2, i3, i4 = st.columns(4)
        with i1:
            metric_card("SMA10 / SMA30", f"{data['indicators']['sma10']:.2f} / {data['indicators']['sma30']:.2f}")
        with i2:
            metric_card("RSI(14)", f"{data['indicators']['rsi14']:.2f}")
        with i3:
            metric_card("MACD", f"{data['indicators']['macd']:.4f}", f"Signal {data['indicators']['macd_signal']:.4f}")
        with i4:
            metric_card("Bollinger", f"{data['indicators']['bb_lower']:.2f} - {data['indicators']['bb_upper']:.2f}")
        st.subheader("Racional do sinal")
        for reason in signal["reasons"]:
            st.write(f"• {reason}")

    with tab2:
        st.plotly_chart(build_forecast_chart(data, dark_mode), use_container_width=True, config={"responsive": True, "displaylogo": False})
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            metric_card("Stop-loss dinâmico", f"{data['risk']['stop_loss_pct']:.2f}%", f"Preço: {data['risk']['stop_loss_price']:.2f}")
        with r2:
            metric_card("VaR 95%", f"{data['risk']['value_at_risk_95_pct']:.2f}%", f"Valor: {data['risk']['value_at_risk_95_amount']:.2f}")
        with r3:
            metric_card("Position sizing", f"{data['risk']['position_size_shares']} ações", f"Valor: {data['risk']['position_size_value']:.2f}")
        with r4:
            metric_card("Budget por trade", f"{data['risk']['risk_budget']:.2f}", "Regra de 2% do capital")
        st.caption(data['forecast']['note'])

    with tab3:
        st.plotly_chart(build_backtest_chart(data, dark_mode), use_container_width=True, config={"responsive": True, "displaylogo": False})
        stats = data["backtest"]["stats"]
        b1, b2, b3, b4, b5 = st.columns(5)
        with b1:
            metric_card("Strategy", f"{stats['strategy_return_pct']:.2f}%")
        with b2:
            metric_card("IBOV", f"{stats['ibov_return_pct']:.2f}%")
        with b3:
            metric_card("CDI", f"{stats['cdi_return_pct']:.2f}%")
        with b4:
            metric_card("Sharpe Ratio", f"{stats['sharpe_ratio']:.2f}")
        with b5:
            metric_card("Max Drawdown", f"{stats['max_drawdown_pct']:.2f}%")

    with st.expander("JSON bruto da análise"):
        st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")


if __name__ == "__main__":
    main()
