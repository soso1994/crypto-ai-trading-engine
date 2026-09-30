# Signals API

The Flask service listens on port `5000` and reads public Binance spot klines. All routes are unauthenticated and read-only. No endpoint submits, routes, or executes orders. CORS is enabled for the dashboard and local development.

## `GET /health`

Returns `{"status":"ok","mode":"paper"}` without contacting Binance.

## `GET /live_signal`

Query parameters:

| Name | Default | Accepted values |
| --- | --- | --- |
| `symbol` | `BTCUSDT` | 5–20 uppercase letters/digits, e.g. `ETHUSDT` |
| `interval` | `15m` | `1m`, `5m`, `15m`, `1h`, `4h`, `1d` |

Example: `GET /live_signal?symbol=BTCUSDT&interval=15m`

The JSON response includes:

```json
{
  "symbol": "BTCUSDT",
  "signal": "BUY",
  "confidence": 80,
  "entry_price": 64250.5,
  "stop_loss": 63800.0,
  "take_profit": 65150.0,
  "atr": 300.25,
  "timeframe": "15m",
  "mode": "paper",
  "indicators": {
    "ema_fast": 64100.0,
    "ema_slow": 63900.0,
    "rsi": 60.0,
    "macd": 25.0,
    "signal": 18.0,
    "histogram": 7.0
  },
  "candles": [
    {"time": 1720000000000, "open": 64200, "high": 64300, "low": 64100, "close": 64250.5, "volume": 123.4}
  ]
}
```

`signal` is `BUY`, `SELL`, or `HOLD`; stop loss and take profit are `null` for `HOLD`. Confidence is a deterministic score based on EMA(9/21), RSI(14), and MACD(12/26/9). Risk distances use ATR(14): 1.5 ATR for the stop and 3 ATR for the target.

## `GET /performance`

Uses the same query parameters. Reports `wins`, `losses`, `sample_size`, and `win_rate` from a paper-only historical next-candle direction check over fetched candles. `mode` is `paper_backtest`. This is a simple historical metric, not a simulated account or actual trade record.

## `GET /ws/signals`

Connect over WebSocket (for example, `ws://localhost:5000/ws/signals?symbol=BTCUSDT&interval=15m`). The server sends a JSON signal immediately and then every 15 seconds. Query validation and signal/error payloads match the REST API.

## Errors

- `400`: unsupported interval or malformed symbol.
- `502`: Binance is unavailable, returns an invalid response, or provides insufficient candle data.
- WebSocket clients receive JSON with an `error` field for invalid parameters or market-data failures.
