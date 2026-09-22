# Paper-trading risk controls

Paper mode now enforces local safety limits:

- maximum order notional: `PAPER_MAX_ORDER_NOTIONAL_USDT` (default `10000`)
- maximum open positions: `PAPER_MAX_OPEN_POSITIONS` (default `5`)
- maximum daily realized loss: `PAPER_MAX_DAILY_LOSS_USDT` (default `1000`)
- sells cannot exceed an existing paper position
- account and risk status are available through `/paper/account`,
  `/paper/summary`, and `/paper/risk`

These controls apply only to virtual paper state. No exchange or live account is
accessed.
