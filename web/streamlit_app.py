from __future__ import annotations

import streamlit as st
st.write("🚀 App iniciando...")

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")

st.set_page_config(page_title="Stock Analyzer Pro", page_icon="📈", layout="wide", initial_sidebar_state="expanded")


@st.cache_data(ttl=180, show_spinner=False)
def load_analysis(ticker: str, period: str, capital: float, horizon: int) -> dict:
    if not API_BASE_URL:
        st.error("API_BASE_URL não configurada")
        st.stop()

    response = requests.get(
        f"{API_BASE_URL}/api/analyze",
        params={"ticker": ticker, "period": period, "capital": capital, "horizon": horizon},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    with st.sidebar:
        st.title("📈 Stock Analyzer Pro")
        dark_mode = st.toggle("Dark mode", value=True)
        ticker = st.text_input("Ticker", value="PETR4.SA")

        period_options = {
            "1mo": "1 mês",
            "3mo": "3 meses",
            "6mo": "6 meses",
            "1y": "1 ano",
            "5y": "5 anos"
        }

        period = st.selectbox(
            "Período",
            options=list(period_options.keys()),
            index=3,
            format_func=lambda x: f"{x} · {period_options[x]}"
        )

        capital = st.number_input("Capital", min_value=1000.0, value=100000.0)
        horizon = st.slider("Horizonte", 5, 10, 7)
        run = st.button("Analisar")

    if run:
        data = load_analysis(ticker, period, capital, horizon)
        st.success("Dados carregados com sucesso")
        st.json(data)


if __name__ == "__main__":
    main()
