"""Config-driven ingest service with safe public Binance snapshot support."""

from flask import Flask, jsonify, request
import os
import random
import sys
import time

# The repository layout keeps the Flask entrypoint below services/ingest while
# the adapter package lives directly under services/ingest/adapters.
ADAPTER_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if ADAPTER_ROOT not in sys.path:
    sys.path.insert(0, ADAPTER_ROOT)
from adapters.binance import fetch_market_snapshot, fetch_snapshots, get_market_symbols

app = Flask(__name__)
SYMBOLS = get_market_symbols() or ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


@app.route('/health')
def health():
    return jsonify({"status": "ok", "mode": "mock", "symbols": SYMBOLS})


@app.route('/symbols')
def symbols_route():
    return jsonify({"symbols": SYMBOLS})


@app.route('/mock_stream')
def mock_stream():
    now_ts = int(time.time())
    return jsonify([
        {"source": "mock", "symbol": symbol, "ts": now_ts,
         "price": round(random.uniform(10.0, 50000.0), 6)}
        for symbol in SYMBOLS
    ])


@app.route('/live_snapshot')
def live_snapshot():
    """Read public Binance ticker data; never places orders."""
    symbol = request.args.get('symbol')
    if symbol and symbol.upper() not in SYMBOLS:
        return jsonify({"error": "unsupported symbol", "symbol": symbol}), 400
    snapshots = fetch_snapshots(symbol.upper() if symbol else None)
    unavailable = [item for item in snapshots if item.get("price") is None]
    status = 502 if unavailable else 200
    return jsonify({"source": "binance_public", "snapshots": snapshots,
                    "available": len(snapshots) - len(unavailable),
                    "unavailable": len(unavailable)}), status


if __name__ == '__main__':
    app.run(port=8081)
