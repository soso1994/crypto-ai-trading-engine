# Stage 3: historical validation

The backtester now evaluates the paper-only signal strategy on candle history.
It accounts for configurable fees and slippage and reports final equity, net PnL,
return, win rate, profit factor, maximum drawdown, trades, and an equity curve.

Example:

```python
from backtester.strategy import backtest
from indicators import build_signal
result = backtest(candles, build_signal)
```

This is research tooling only. Results are not a promise of future returns and
no live orders are sent.
