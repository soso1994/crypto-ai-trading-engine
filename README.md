# Crypto AI Trading Engine

A paper-only cryptocurrency signal API and responsive React dashboard. The service reads public Binance candle data and displays deterministic technical signals; it never places or routes trades.

## Run locally

Requirements: Python 3.10+, Node.js 18+, and npm.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r services/ingest/requirements-dev.txt
python -m services.ingest.app
```

In another terminal:

```bash
npm ci --prefix web
npm run dev --prefix web
```

Open <http://localhost:3000>. The Vite development server proxies REST and WebSocket requests to the API at <http://localhost:5000>. No Binance API key or account is required.

## Docker Compose

```bash
docker compose up --build
```

The dashboard is available at <http://localhost:3000> and the API at <http://localhost:5000>. The production dashboard container serves a static React build with Nginx and proxies the API and WebSocket paths to Flask.

## API and safety

See [API.md](API.md) for REST and WebSocket routes, parameters, response fields, validation, and error behavior. `/performance` is a historical, next-candle paper backtest. It is not a record of executed trades and is not a prediction of future performance.

The application intentionally has no order execution, exchange credentials, or trading-account integration. Signals and ATR-derived stop/take-profit values are informational only, not financial advice.

## Tests

```bash
python -m pytest services/ingest/tests --cov=services.ingest --cov-report=term-missing --cov-fail-under=95
npm test --prefix web
npm run build --prefix web
```
