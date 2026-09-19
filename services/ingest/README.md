# Ingest service

The service has two intentionally separate modes:

- `GET /mock_stream` emits deterministic-shape mock ticks for all configured
  symbols.
- `GET /live_snapshot?symbol=BTCUSDT` reads the public Binance ticker endpoint.

The live endpoint is read-only. It does not require API credentials and cannot
place orders. Set `BINANCE_BASE_URL` to a compatible endpoint for testing.

Run locally from the repository root:

```bash
pip install -r services/ingest/requirements.txt
python services/ingest/services/ingest/main.py
curl http://localhost:8081/live_snapshot?symbol=BTCUSDT
```
