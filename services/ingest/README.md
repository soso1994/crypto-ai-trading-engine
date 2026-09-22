# Ingest service

The service supports mock data and read-only Binance Spot public data:

- `GET /mock_stream`
- `GET /live_snapshot?symbol=BTCUSDT`
- `GET /live_klines?symbol=BTCUSDT&interval=15m&limit=100`

No API key, secret, account access, or order placement is used. The kline route
normalizes Binance OHLCV rows for the later indicator and backtest stages.

```bash
pip install -r services/ingest/requirements.txt
python services/ingest/services/ingest/main.py
curl 'http://localhost:8081/live_klines?symbol=BTCUSDT&interval=15m&limit=10'
```
