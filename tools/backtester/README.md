# Backtester

This directory contains the deterministic replay package and a symbol-aware CLI.

## Run tests

```bash
cd tools/backtester
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

## Run a replay

Start the mock ingest service first, then run:

```bash
cd tools/backtester
python cli.py --symbol BTCUSDT --source http://localhost:8081/mock_stream
```

The CLI accepts a JSON endpoint or a local JSON file containing objects with
`symbol`, `ts`, and `price`. It never places real orders.
