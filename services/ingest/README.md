# Ingest service (mock)

This is a lightweight ingest service scaffold. It provides a local mock that simulates streaming messages for development and testing.

How to run (dev):

1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. python -m services.ingest.main

Notes:
- This is a mock used for local development. Replace message producers with real connectors (Binance/Bybit) when creds are available.
