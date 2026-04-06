FROM python:3.11-slim

# Instalar pacotes de sistema do packages.txt
COPY packages.txt .
RUN apt-get update && apt-get install -y $(cat packages.txt | tr '\n' ' ') && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements do Streamlit
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar o backend para que o Streamlit possa importar os serviços
COPY backend /app/backend

# Copiar o Streamlit app e a pasta static
COPY streamlit_app.py .
COPY static ./static

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
