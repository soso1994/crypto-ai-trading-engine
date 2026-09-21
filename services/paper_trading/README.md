# Paper trading scaffold

This module creates a safe simulation loop for virtual cash and paper positions.
No live funds are used.

Run locally:

```bash
python services/paper_trading/app.py
curl http://localhost:8090/paper/account
```

Then a sample order:

```bash
curl -X POST http://localhost:8090/paper/order \
  -H 'Content-Type: application/json' \
  -d '{"symbol":"BTCUSDT","side":"buy","size":0.1,"price":52000}'
```
