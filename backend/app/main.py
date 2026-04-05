from fastapi import FastAPI
from app.pipeline import run_pipeline

app = FastAPI()


@app.get("/analyze")
def analyze(ticker: str, period: str = "3mo"):
    return run_pipeline(ticker.upper(), period)
