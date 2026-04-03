# AI-Powered Personal Finance Advisor

Production-shaped SaaS starter for personal finance tracking, expense prediction, overspending detection, anomaly detection, and AI-assisted savings and investment guidance.

## Stack

- Frontend: React, Vite, Tailwind CSS, Recharts, Axios
- Backend: FastAPI, SQLAlchemy, Alembic, JWT auth
- Database: PostgreSQL
- Cache: Redis
- AI/ML: pandas, NumPy, scikit-learn, joblib
- DevOps: Docker, Docker Compose

## Project Structure

```text
frontend/
backend/
  app/
  ml/
  alembic/
  tests/
database/
docker/
docker-compose.yml
```

## Features

- JWT authentication with register, login, and current-user lookup
- Income and expense tracking with categories and transaction history
- Summary dashboard with income, expenses, savings rate, anomaly count, and trends
- Expense prediction via RandomForest regressor
- Overspending classification via RandomForest classifier
- Unusual transaction detection via IsolationForest plus category-threshold fallback
- Budget, emergency fund, and investment recommendations
- Redis caching for summary and recommendation-heavy views

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ml.pipelines.train_models
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment

Copy `.env.example` to `.env` and adjust values as needed.

## Docker Setup

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## API Summary

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/login/json`
- `GET /api/v1/auth/me`

### Transactions and Finance

- `GET /api/v1/transactions/categories`
- `POST /api/v1/transactions`
- `GET /api/v1/transactions`
- `GET /api/v1/finance/summary`

### AI

- `POST /api/v1/ai/predict-expense`
- `POST /api/v1/ai/detect-anomaly`
- `POST /api/v1/ai/analyze-spending`
- `GET /api/v1/ai/recommend-budget`
- `GET /api/v1/ai/recommendations`

## ML Pipeline Overview

Training assets live under `backend/ml/`.

- Seed dataset: `backend/ml/data/monthly_spending_dataset_2020_2025.csv`
- Trainer: `backend/ml/pipelines/train_models.py`
- Artifacts: `backend/ml/artifacts/`

Models:

- `expense_regressor.joblib`
- `overspending_classifier.joblib`
- `anomaly_detector.joblib`
- `model_metadata.joblib`

The app uses shared trained models for baseline inference, then personalizes output using the authenticated user’s recent transaction history.

## Testing

```bash
cd backend
pytest
```

## Screenshots

- Dashboard screenshot placeholder
- Analytics screenshot placeholder
- Recommendations screenshot placeholder

## Notes

- The bundled seed dataset treats `Savings` separately from `Total Expenditure`.
- Redis gracefully falls back to an in-memory cache if Redis is unavailable during local development.
- This is a modular-monolith v1 that is structured so Finance, ML, and Recommendation services can be split out later.
