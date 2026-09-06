Data feeds adapters

This directory contains lightweight adapters for live data ingestion.

- binance_ws.py: public websockets consumer skeleton
- adapter.py: file/db writer factories (placeholders)

How to run locally:

1) python -m venv venv && source venv/bin/activate
2) pip install -r requirements.txt (add websockets, asyncpg)
3) Run the sample consumer in binance_ws.py
