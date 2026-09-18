"""Flask mock ingest service.

This service intentionally stays in mock mode until real market-data credentials
and a production adapter are configured. It reads the config-based symbols and
emits mock payloads for them, while offering a safe gateway for future Binance
adapter integration.
"""

from flask import Flask, jsonify
import time
import random
import os
import yaml

try:
    from adapters.binance import get_market_symbols
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from adapters.binance import get_market_symbols

app = Flask(__name__)


def load_symbols():
    symbols = get_market_symbols()
    if symbols:
        return symbols
    # fallback safe list
    return ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']


SYMBOLS = load_symbols()


@app.route('/health')
def health():
    return jsonify({"status": "ok", "symbols": SYMBOLS})


@app.route('/mock_stream')
def mock_stream():
    """Return mock price payloads for all configured symbols."""
    now_ts = int(time.time())
    data = []
    for sym in SYMBOLS:
        price = round(random.uniform(10.0, 50000.0), 6)
        data.append({"source": "mock", "symbol": sym, "ts": now_ts, "price": price})
    return jsonify(data)


@app.route('/symbols')
def symbols_route():
    return jsonify({"symbols": SYMBOLS})


if __name__ == '__main__':
    app.run(port=8081)
