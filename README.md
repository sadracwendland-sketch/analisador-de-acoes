# Stock Analyzer Pro

<p align="center">
  <b>Plataforma full stack de análise de bolsa para Web + Mobile</b><br>
  FastAPI · Streamlit · React Native Expo · Plotly · PyTorch LSTM
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-Web-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img alt="Expo" src="https://img.shields.io/badge/Expo-Mobile-000020?style=for-the-badge&logo=expo&logoColor=white">
  <img alt="Plotly" src="https://img.shields.io/badge/Plotly-Charts-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">
  <img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-LSTM-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white">
</p>

<p align="center">
  <a href="#-visão-geral">Visão geral</a> •
  <a href="#-destaques">Destaques</a> •
  <a href="#-stack">Stack</a> •
  <a href="#-arquitetura">Arquitetura</a> •
  <a href="#-rodando-localmente">Rodando localmente</a> •
  <a href="#-deploy-e-publicação">Deploy</a> •
  <a href="#-publicação-no-github">GitHub</a>
</p>

---

## ✨ Visão geral

O **Stock Analyzer Pro** é um app de análise de ações desenhado para funcionar em **desktop, tablet e celular**, com um backend central em **FastAPI**, um dashboard **Streamlit** para web responsiva e um app mobile nativo em **React Native com Expo**.

A proposta do projeto é oferecer, em uma única experiência:

- consulta de ativos como `PETR4.SA`, `VALE3.SA` e `AAPL`
- leitura técnica automatizada
- sinal operacional claro com confiança percentual
- gestão de risco por operação
- backtesting comparativo com benchmarks
- forecast de curto prazo com **LSTM**
- deploy simples e reaproveitável

> Ideal para portfólio, demonstração técnica, MVP de fintech, estudos quantitativos e evolução para produto SaaS.

---

## 🚀 Destaques

### 📊 Análise técnica automática
- SMA 10 / SMA 30 crossover
- RSI (14)
- MACD
- Bollinger Bands
- racional do sinal exibido para o usuário

### 🟢 Sinal operacional objetivo
- **COMPRA**
- **VENDA**
- **ESPERAR**
- score interno + confiança percentual

### 🤖 Forecast com Machine Learning
- LSTM implementado em **PyTorch**
- previsão de **5 a 10 dias** à frente
- classificação de tendência: `ALTA`, `BAIXA`, `LATERAL`
- fallback seguro quando ambiente ML não estiver disponível

### 🛡️ Gestão de risco
- stop-loss dinâmico com base em volatilidade/ATR
- VaR 95%
- position sizing com regra de 2% do capital por trade

### 📈 Backtesting
- rentabilidade da estratégia
- comparação contra **IBOV** e **CDI**
- métricas de **Sharpe Ratio** e **Max Drawdown**

### 🌐 Web + 📱 Mobile
- dashboard Streamlit responsivo
- gráficos Plotly interativos
- dark/light mode
- PWA com `manifest.json`
- app mobile Expo usando o mesmo backend

---

## 🧩 Stack

### Backend
- **FastAPI** para API REST
- **Pydantic** para schema e validação
- **Pandas / NumPy** para engine analítica
- **PyTorch** para LSTM
- **yfinance** como fonte principal
- **brapi.dev** como fallback B3

### Frontend Web
- **Streamlit**
- **Plotly**
- cache de dados com `st.cache_data`
- static serving habilitado para assets da PWA

### Mobile
- **React Native**
- **Expo**
- **EAS Build** para geração de binários

### Deploy
- **Docker / Docker Compose** para execução local
- **Render** para backend FastAPI
- **Streamlit Community Cloud** para web app
- **Expo EAS** para publicação mobile

---

## 🏗️ Arquitetura

```text
                 ┌─────────────────────────────┐
                 │        React Native         │
                 │         Expo App            │
                 └──────────────┬──────────────┘
                                │
                                │ HTTP / JSON
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                         FastAPI API                           │
│                     /health  /api/analyze                     │
│                                                               │
│  Indicators  ·  Signal Engine  ·  Risk  ·  LSTM  · Backtest  │
└───────────────┬───────────────────────────────┬───────────────┘
                │                               │
                │                               │
      ┌─────────▼─────────┐           ┌────────▼────────┐
      │     yfinance      │           │    brapi.dev    │
      │ principal source  │           │ fallback B3     │
      └───────────────────┘           └─────────────────┘
                │
                │
      ┌─────────▼─────────┐
      │ BCB / benchmark   │
      │ CDI + IBOV        │
      └───────────────────┘
                ▲
                │
┌───────────────┴────────────────┐
│        Streamlit Dashboard      │
│      Web responsiva + PWA       │
└──────────────────────────────────┘
```

---

## 🗂️ Estrutura do projeto

```text
stock-analyzer-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── backtest.py
│   │       ├── data_provider.py
│   │       ├── indicators.py
│   │       ├── ml_model.py
│   │       ├── pipeline.py
│   │       └── risk.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── web/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .streamlit/config.toml
│   ├── .env.example
│   └── static/
│       ├── manifest.json
│       ├── icon-192.png
│       └── icon-512.png
├── mobile/
│   ├── App.tsx
│   ├── app.json
│   ├── eas.json
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## 🔍 Funcionalidades detalhadas

### 1) Input de mercado
O usuário informa:

- `ticker`
- `period`
- `capital`
- `horizon`

Períodos suportados:

- `1m`
- `5m`
- `1h`
- `1d`
- `1y`

### 2) Engine técnica
A engine calcula:

- cruzamento de médias móveis
- força relativa do ativo via RSI
- momento via MACD
- envelopes de preço via Bollinger Bands

### 3) Motor de sinal
A API combina os indicadores em um score e devolve:

- label do sinal
- confiança
- motivos do sinal

### 4) Gestão de risco
A resposta inclui:

- stop-loss percentual
- stop-loss em preço
- VaR 95%
- orçamento de risco
- quantidade sugerida de ações

### 5) Forecast
O módulo de forecast entrega:

- sequência de preços previstos
- tendência estimada
- retorno esperado no horizonte
- observação sobre o modelo usado

### 6) Backtest
O backtest retorna:

- equity curve da estratégia
- curva do IBOV
- curva do CDI
- Sharpe Ratio
- Max Drawdown
- retorno acumulado

---

## 📡 Fontes de dados

- **yfinance**: principal fonte de histórico e preços
- **brapi.dev**: fallback para ativos da B3
- **Banco Central do Brasil**: série de CDI
- **Yahoo Finance / ^BVSP**: benchmark do IBOV

> Para produção real, mantenha o token da **brapi.dev** apenas no backend.

---

## 🔐 Variáveis de ambiente

### Backend — `backend/.env.example`

```env
BRAPI_API_KEY=
DEFAULT_CAPITAL=100000
DEFAULT_FORECAST_HORIZON=7
```

### Web — `web/.env.example`

```env
API_BASE_URL=http://localhost:8000
```

### Mobile — `mobile/.env.example`

```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## ▶️ Rodando localmente

## Opção rápida com Docker Compose

```bash
docker compose up --build
```

A aplicação sobe com:

- API: `http://localhost:8000`
- Streamlit: `http://localhost:8501`

---

## Backend manual

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Teste:

```bash
curl http://localhost:8000/health
```

---

## Web manual

```bash
cd web
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run streamlit_app.py
```

---

## Mobile manual

```bash
cd mobile
npm install
npx expo start
```

Para testar no celular físico, aponte para o IP local da sua máquina:

```bash
export EXPO_PUBLIC_API_BASE_URL=http://SEU_IP_LOCAL:8000
```

---

## 🧪 Exemplo de uso da API

### Request

```bash
curl "http://localhost:8000/api/analyze?ticker=PETR4.SA&period=1d&capital=100000&horizon=7"
```

### Exemplo de resposta

```json
{
  "ticker": "PETR4.SA",
  "period": "1d",
  "last_price": 31.10,
  "signal": {
    "label": "COMPRA",
    "emoji": "🟢",
    "confidence": 78.5
  },
  "forecast": {
    "trend": "ALTA",
    "horizon_days": 7
  },
  "risk": {
    "stop_loss_pct": 3.2,
    "value_at_risk_95_pct": 2.1
  }
}
```

---

## 🚀 Deploy e publicação

## 1. Backend FastAPI no Render

O projeto já inclui:

- `backend/Dockerfile`
- `render.yaml`

### Passo a passo
1. publique o projeto no GitHub
2. conecte o repositório no Render
3. crie um **Web Service**
4. use o `render.yaml` ou a pasta `backend/`
5. configure as env vars:
   - `BRAPI_API_KEY`
   - `DEFAULT_CAPITAL`
   - `DEFAULT_FORECAST_HORIZON`
6. faça o deploy

### Teste após publicar

```bash
curl "https://SEU_BACKEND.onrender.com/api/analyze?ticker=AAPL&period=1d&capital=100000&horizon=7"
```

---

## 2. Web app no Streamlit Community Cloud

### Passo a passo
1. suba o projeto no GitHub
2. entre no Streamlit Community Cloud
3. conecte seu repositório
4. selecione o arquivo principal:

```text
web/streamlit_app.py
```

5. adicione a variável/secreto:

```toml
API_BASE_URL = "https://SEU_BACKEND_PUBLICO"
```

6. clique em **Deploy**

### Observações
- `web/requirements.txt` será usado no build
- `web/static/` contém os assets da PWA
- `.streamlit/config.toml` já habilita static serving

---

## 3. Mobile app com Expo / EAS

### Setup inicial

```bash
cd mobile
npm install
npm install -g eas-cli
eas login
eas build:configure
```

### Configurar API pública

```env
EXPO_PUBLIC_API_BASE_URL=https://SEU_BACKEND_PUBLICO
```

### Build

```bash
eas build --platform android
eas build --platform ios
```

### Distribuição
- Android: Google Play ou distribuição interna
- iOS: App Store / TestFlight

---

## 🌐 Publicação no GitHub

### 1. Criar o repositório
Crie um repositório, por exemplo:

```text
stock-analyzer-pro
```

### 2. Inicializar Git

```bash
git init
git add .
git commit -m "feat: initial portfolio version"
```

### 3. Conectar ao remoto

```bash
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 4. Boas práticas
Nunca publique:

- `.env`
- tokens
- chaves privadas
- credenciais de produção

Use `.env.example` como template.

---

## 🖼️ Sugestões para deixar o portfólio ainda mais forte

Você pode melhorar este README adicionando:

- screenshots do dashboard web
- GIF de navegação no app mobile
- link da demo publicada
- arquitetura em imagem SVG
- benchmark de performance
- roadmap do produto
- seção de desafios técnicos resolvidos

Exemplo de seção de demo:

```md
## Demo
- Web: https://seu-app.streamlit.app
- API: https://seu-backend.onrender.com/docs
- Mobile: link do APK / TestFlight
```

---

## 🛣️ Roadmap

- [ ] autenticação de usuários
- [ ] watchlist persistente
- [ ] alertas por e-mail / push
- [ ] scanner multiativos
- [ ] sentimento de notícias
- [ ] integração com corretora
- [ ] banco de dados para histórico de consultas
- [ ] CI/CD com GitHub Actions
- [ ] testes automatizados
- [ ] observabilidade e métricas de produção

---

## 🛡️ Segurança e observações

- `BRAPI_API_KEY` deve ficar apenas no backend
- `yfinance` é excelente para prototipagem e pesquisa, mas produção crítica pode exigir fontes dedicadas
- o módulo LSTM já está estruturado no projeto, com fallback para ambientes sem dependências completas
- em produção, vale separar inferência, persistir modelos e adicionar cache dedicado

---

## 📚 Links úteis

- FastAPI: https://fastapi.tiangolo.com/
- Streamlit: https://docs.streamlit.io/
- Streamlit Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Expo: https://docs.expo.dev/
- brapi.dev: https://brapi.dev/docs
- yfinance: https://ranaroussi.github.io/yfinance/

---

## 🧰 Kit profissional do repositório GitHub

Este repositório agora inclui um kit completo de governança e colaboração:

- `LICENSE`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `.editorconfig`
- `.github/CODEOWNERS`
- templates de issue
- template de pull request
- workflow de CI
- workflow de health check do repositório
- configuração do Dependabot

Isso deixa o projeto mais forte para portfólio, colaboração open source e demonstração de maturidade de engenharia.

---

## 🤝 Contribuição

Contribuições são bem-vindas.

Se quiser evoluir o projeto:

1. faça um fork
2. crie uma branch
3. implemente a melhoria
4. abra um pull request

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT**.

Consulte o arquivo [`LICENSE`](./LICENSE).

---

## 👨‍💻 Autor

Substitua pelos seus dados:

```text
Sadrac Wendland
GitHub: https://github.com/sadracwendland-sketch
LinkedIn: https://www.linkedin.com/in/sadracwendland/
```
