# Risk controls for paper trading

This patch adds the safe defaults and risk validation layer:

- max order notional: `1000 USDT`
- max open positions: `3`
- max daily loss: `3000 USDT`
- reject invalid side/size/price combinations
- reject order if loss limit is reached
- expose `/paper/risk` endpoint for the dashboard

No live funds or exchange access are involved.
