# ML Fraud Detection App

The repository is built as a full product, with the backend service living in `api/` and the dashboard frontend in `dashboard/`.

## What This Repo Uses

- Python `3.11+`
- Dependency management and virtualenv via [`uv`](https://docs.astral.sh/uv/)
- PostgreSQL `15`
- FastAPI + SQLAlchemy
- Optional Logfire telemetry

`requirements.txt` is no longer used. Use Dev Containers or `uv` workflows only.

## Project Layout

- `api/`: backend package and FastAPI service
  - `api/main.py`: FastAPI app setup and router wiring
  - `api/routers/transactions.py`: transaction and scoring endpoints
  - `api/core/`: exception handling, logging, and model loader logic
  - `api/database.py`: engine, session, and DB startup/shutdown helpers
  - `api/models.py`, `api/schemas.py`: ORM models and request/response schemas
- `dashboard/`: Next.js dashboard UI and client-side code
- `docker-compose.yml`: production-style compose services
- `docker-compose.dev.yml`: local development overrides for backend, dashboard, and test DB
- `.devcontainer/api/`: backend development container
- `.devcontainer/frontend/`: frontend/dashboard development container
- `tests/`: backend test suite
- `scripts/import_transactions.py`: CSV import helper
- `artifacts/model.joblib`: trained model bundle
- `deploy/nginx/default.conf`: local reverse proxy configuration

> Note: `dashboard/app/` is the frontend Next.js app root. The backend code is now under `api/`.

## Run Options

### Option 1: VS Code Dev Container (recommended)

Use the built-in devcontainer setup when you want backend and frontend development to run from the same repo root.

#### Backend development container

1. Open the repo in VS Code.
2. Run `Dev Containers: Reopen in Container`.
3. Choose the backend container from `.devcontainer/api`.
4. Inside the container, install and sync dependencies:

```bash
make venv
```

5. Start the backend service:

```bash
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

6. Open the backend OpenAPI docs at `http://localhost:8000/`.

#### Frontend development container

The dashboard development container is configured in `.devcontainer/frontend`.

- It starts the Next.js dashboard on port `3000`.
- It runs in the same repo root and can call the backend at `http://localhost:8000`.
- Open `.devcontainer/frontend` in VS Code and let the container build the frontend dependencies.

Both devcontainers are designed to work from the same repository and share the local compose stack.

For local Docker development without devcontainers, run:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### Option 2: Local machine with uv

Use this if you are **not** using devcontainers.

### Prerequisites

- Python `3.11+`
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL (local install or container)

### 1) Set up database

You can run only PostgreSQL from compose:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d web-db
```

If you run the DB outside Docker, create a database named `web` and a user/password that matches your URI.

### 2) Configure environment variables

Create a local `.env` (or export vars in your shell):

```bash
export DATABASE_URI="postgres://postgres:postgres@localhost:5432/web"
export MODEL_PATH="$(pwd)/artifacts/model.joblib"

# Optional observability
export LOG_LEVEL="WARNING"          # e.g. DEBUG, INFO, WARNING, ERROR
export LOGFIRE_TOKEN=""             # leave empty to disable cloud export
export LOGFIRE_SERVICE_NAME="ml-fraud-detection-app"
export LOGFIRE_ENVIRONMENT="development"
```

Note: inside containers the database hostname is `web-db`; on your host machine it is typically `localhost`.

### 3) Create/sync environment

```bash
make venv
```

(`make venv` runs `uv sync --frozen`.)

### 4) Start backend service

```bash
uv run uvicorn api.main:app --reload
```

### 5) Run tests and checks

```bash
make test
make check
```

## Makefile Commands

- `make venv`: sync dependencies with `uv.lock`
- `make test`: run tests with coverage
- `make lint`: lock check + Ruff format/check
- `make typecheck`: pyright + mypy
- `make check`: lint + typecheck
- `make fix`: auto-fix Ruff issues + format
- `make clean`: remove caches and virtualenv

## Backend API Reference

Base URL (local): `http://localhost:8000`

Interactive OpenAPI docs are served at: `GET /`

Current endpoints implemented in `api/routers/transactions.py`:

- `GET /transactions?limit=<n>&offset=<n>`: paginated transactions list
- `GET /transactions/count`: total transactions count
- `GET /transactions/scores?limit=<n>&offset=<n>`: paginated scores history
- `GET /transactions/scores/count`: total scores count
- `GET /transactions/{transaction_id}`: transaction details + prediction history
- `POST /transactions`: create and score a transaction
- `PUT /transactions/{transaction_id}`: update and rescore a transaction
- `POST /transactions/import`: import transactions from CSV upload

### 1) Score Transaction

- Method: `POST`
- Path: `/score`
- Purpose: score one transaction and persist a prediction

Example request:

```json
{
  "transaction_id": "tx_12345",
  "amount": 150.50,
  "transaction_hour": 14,
  "merchant_category": "Electronics",
  "foreign_transaction": false,
  "location_mismatch": false,
  "device_trust_score": 85,
  "velocity_last_24h": 3,
  "cardholder_age": 35
}
```

Allowed `merchant_category` values:

- `Electronics`
- `Travel`
- `Grocery`
- `Food`
- `Clothing`

cURL:

```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "tx_12345",
    "amount": 150.50,
    "transaction_hour": 14,
    "merchant_category": "Electronics",
    "foreign_transaction": false,
    "location_mismatch": false,
    "device_trust_score": 85,
    "velocity_last_24h": 3,
    "cardholder_age": 35
  }'
```

Example response (`200`):

```json
{
  "transaction_id": "tx_12345",
  "fraud_probability": 0.0234,
  "decision": 0,
  "threshold": 0.5,
  "model_version": "v1.0",
  "scored_at": "2024-01-15T10:30:00.000000+00:00"
}
```

Response fields:

- `transaction_id`: transaction identifier
- `fraud_probability`: value between `0` and `1`
- `decision`: binary model decision (`1` when probability is `>= threshold`)
- `threshold`: decision threshold used
- `model_version`: model metadata/version label
- `scored_at`: ISO-8601 UTC timestamp

### 2) List Transactions

- Method: `GET`
- Path: `/transactions`
- Query parameter `limit` (default `50`, max `100`)
- Query parameter `offset` (default `0`)

cURL:

```bash
curl "http://localhost:8000/transactions?limit=10&offset=0"
```

Example response (`200`):

```json
[
  {
    "id": 1,
    "transaction_id": "tx_12345",
    "amount": 150.5,
    "transaction_hour": 14,
    "merchant_category": "Electronics",
    "foreign_transaction": false,
    "location_mismatch": false,
    "device_trust_score": 85,
    "velocity_last_24h": 3,
    "cardholder_age": 35
  }
]
```

### 3) Get Transaction Details

- Method: `GET`
- Path: `/transactions/{transaction_id}`
- Purpose: transaction details plus prediction history

cURL:

```bash
curl "http://localhost:8000/transactions/tx_12345"
```

Success response (`200`):

```json
{
  "transaction": {
    "id": 1,
    "transaction_id": "tx_12345",
    "amount": 150.5,
    "transaction_hour": 14,
    "merchant_category": "Electronics",
    "foreign_transaction": false,
    "location_mismatch": false,
    "device_trust_score": 85,
    "velocity_last_24h": 3,
    "cardholder_age": 35
  },
  "predictions": [
    {
      "id": 1,
      "transaction_id": "tx_12345",
      "fraud_probability": 0.0234,
      "decision": "0",
      "model_version": "v1.0",
      "scored_at": "2024-01-15T10:30:00.000000+00:00"
    }
  ]
}
```

Not found response (`200`, current behavior):

```json
{
  "error": "Transaction not found"
}
```

## Validation and Error Notes

Common validation constraints:

- `amount > 0`
- `transaction_hour` in `[0, 23]`
- `device_trust_score` in `[0, 100]`
- `velocity_last_24h >= 0`
- `cardholder_age` in `[18, 100]`
- `merchant_category` must be one of the allowed literals

Validation failures return FastAPI `422` responses.

Model/runtime failures in scoring return `500` with:

```json
{
  "detail": "Scoring failed"
}
```

## Optional Data Import

You can import sample transactions from `resources/credit_card_fraud_10k.csv`:

```bash
uv run python scripts/import_transactions.py
```

Ensure `DATABASE_URI` is set before running import.
