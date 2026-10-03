from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.fraud_logic import build_analysis, default_chat_history, default_history
from app.models import TransactionInput

app = FastAPI(title="Fraud Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_transaction(tx: TransactionInput):
    analysis = build_analysis(
        flagged_tx=tx.model_dump(),
        history=default_history(),
        chat_history=default_chat_history(),
    )
    return analysis


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
