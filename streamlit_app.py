import streamlit as st
import requests

st.title("📈 Stock Analyzer")

API_URL = "https://SEU-APP-RENDER.onrender.com"

ticker = st.text_input("Ticker", "PETR4.SA")

if st.button("Analisar"):
    try:
        response = requests.get(
            f"{API_URL}/api/analyze",
            params={"ticker": ticker, "period": "1y", "capital": 100000, "horizon": 7},
            timeout=60
        )

        data = response.json()

        st.success("Dados carregados")
        st.json(data)

    except Exception as e:
        st.error(f"Erro: {e}")
