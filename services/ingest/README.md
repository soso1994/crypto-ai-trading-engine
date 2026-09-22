# Stage 2: indicators and paper-only signals

The read-only ingest service computes EMA, RSI, MACD, and ATR from public
Binance Spot candles. `GET /live_signal?symbol=BTCUSDT&interval=15m` returns a
`buy`, `sell`, or `hold` signal with confidence and volatility metrics.

Signals are informational and marked `mode: paper_only`; this stage cannot place
orders and does not use API credentials. Technical signals are not guarantees of
future performance.
