from fastapi import FastAPI

app = FastAPI(title="Kalshi Arbitrage Bot API", verison="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

