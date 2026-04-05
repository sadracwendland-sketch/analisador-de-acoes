import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import streamlit as st
import requests

st.title("📈 Stock Analyzer")

response = requests.get(
    f"{https://stock-analyzer-api-9f95.onrender.com}/analyze",  # 🔥 corrigido
    params={"ticker": ticker},
    timeout=20  # reduz tempo de espera
)

ticker = st.text_input("Ticker", "PETR4.SA")

if st.button("Analisar"):
    try:
        with st.spinner("Buscando dados..."):
            response = requests.get(
                f"{API_URL}/api/analyze",
                params={
                    "ticker": ticker,
                    "period": "1y",
                    "capital": 100000,
                    "horizon": 7
                },
                timeout=60
            )

            # 👇 ESSENCIAL (evita erro silencioso)
            response.raise_for_status()

            data = response.json()

        st.success("Dados carregados com sucesso")
        st.json(data)

    except requests.exceptions.RequestException as e:
        st.error(f"Erro na API: {e}")

    except Exception as e:
        st.error(f"Erro inesperado: {e}")
