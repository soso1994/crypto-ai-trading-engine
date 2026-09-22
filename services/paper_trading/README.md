# Paper-trading risk controls

Safe defaults:

- maximum order notional: `1000 USDT`
- maximum open positions: `3`
- maximum daily loss: `3000 USDT`

The service also provides:

- `GET /paper/account` — account and risk state
- `GET /paper/risk` — current limits and daily loss usage
- `GET /paper/history` — local paper order journal
- `POST /paper/reset` — reset virtual cash, positions, and journal
- `POST /paper/order` — simulate an order

The daily realized PnL and risk halt reset automatically when the UTC trading
day changes. All data remains local; no exchange or live funds are accessed.
