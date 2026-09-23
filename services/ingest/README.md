# Real signal schema

`GET /live_signal?symbol=BTCUSDT&interval=15m` now returns two explicit layers:

- `indicators`: raw EMA/RSI/MACD/ATR strategy output;
- `signal_contract`: normalized human-reviewable `LONG`, `SHORT`, or `FLAT` signal.

Example contract shape:

```json
{
  "symbol": "BTCUSDT",
  "side": "LONG",
  "signal": "buy",
  "confidence": 0.833,
  "entry_price": 61000,
  "stop_loss": 60400,
  "take_profit": 62200,
  "atr": 400,
  "timeframe": "15m",
  "source": "binance_public",
  "mode": "signal_only",
  "execution_required": false,
  "strategy_version": "ema-rsi-macd-atr-v1"
}
```

`LONG`/`SHORT` are recommendations for human review, not orders. The service
never sends orders, stores exchange credentials, or accesses account funds.
Targets use configurable ATR multiples (default SL 1.5x, TP 3x). Confidence is
model output, not a probability guarantee.
