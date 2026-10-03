# Fraud Detection Dashboard

A full-stack AI fraud detection website built with:
- FastAPI backend
- React + Vite frontend
- Gemini-powered fraud analysis with safe fallback logic

## Folder structure

- `backend/` — Python API
- `frontend/` — React app

## Run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open the frontend in your browser: http://localhost:5173

## Optional AI setup

Set a Gemini API key if you want live AI analysis:

```bash
export GEMINI_API_KEY="your-api-key"
```

If no API key is set, the app falls back to a deterministic fraud verdict.
