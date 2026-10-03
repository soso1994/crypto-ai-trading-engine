# Crypto AI Trading Engine

A paper-only cryptocurrency signal API and responsive React dashboard. The service reads public Binance candle data and displays deterministic technical signals; it never places or routes trades.

## Run on your laptop (recommended)

Install Docker Desktop (Windows/macOS) or Docker Engine with the Compose plugin (Linux), then download the project by cloning it:

```bash
git clone https://github.com/soso1994/crypto-ai-trading-engine.git
cd crypto-ai-trading-engine
docker compose up --build
```

On Windows, run the same commands in PowerShell after installing Git and Docker Desktop. You can also download the repository ZIP from GitHub, extract it, open a terminal in the extracted `crypto-ai-trading-engine` folder, and run `docker compose up --build`.

The first launch downloads dependencies and builds the services, so it may take a few minutes. Keep the terminal and Docker Desktop open while using the app. Open <http://localhost:3000> for the dashboard; the API is at <http://localhost:5000>. To stop the app, press `Ctrl+C` and run `docker compose down` from the project folder.

No Binance API key or account is required. The laptop must have an internet connection to download dependencies and fetch public Binance market data.

## Run without Docker (development)

Requirements: Python 3.10+, Node.js 18+, and npm. Start the API in one terminal from the project folder:

```sh
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r services/ingest/requirements-dev.txt
python -m services.ingest.app
```

Leave that terminal running. Open a second terminal in the same project folder and start the dashboard:

```sh
npm ci --prefix web
npm run dev --prefix web
```

Then open <http://localhost:3000>. The dashboard forwards API and WebSocket requests to the API on port `5000`.

## API and safety

See [API.md](API.md) for REST and WebSocket routes, parameters, response fields, validation, and error behavior. `/performance` is a historical, next-candle paper backtest. It is not a record of executed trades and is not a prediction of future performance.

The application intentionally has no order execution, exchange credentials, or trading-account integration. Signals and ATR-derived stop/take-profit values are informational only, not financial advice.

## Tests

```bash
python -m pytest services/ingest/tests --cov=services.ingest --cov-report=term-missing --cov-fail-under=95
npm test --prefix web
npm run build --prefix web
```
