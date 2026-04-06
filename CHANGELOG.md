# Changelog

Todas as mudanças relevantes deste projeto serão documentadas aqui.

Este formato é inspirado em **Keep a Changelog** e versionamento semântico.

---

## [1.0.0] - 2026-04-01

### Added
- backend FastAPI com endpoint `/api/analyze`
- ingestão de dados com `yfinance` + fallback `brapi.dev`
- cálculo de SMA10/30, RSI(14), MACD e Bollinger Bands
- motor de sinal com `COMPRA`, `VENDA` e `ESPERAR`
- módulo de risco com stop-loss, VaR 95% e position sizing
- módulo de backtesting contra IBOV e CDI
- forecast com LSTM em PyTorch e fallback seguro
- dashboard web responsivo em Streamlit + Plotly
- suporte inicial a PWA com `manifest.json`
- app mobile nativo com Expo/React Native
- estrutura inicial de deploy com Docker Compose, Render e Streamlit Cloud
- kit profissional de repositório GitHub
