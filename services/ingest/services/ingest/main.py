"""Config-driven ingest service with read-only public Binance support."""
from flask import Flask, jsonify, request
import os, random, sys, time
ADAPTER_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if ADAPTER_ROOT not in sys.path: sys.path.insert(0, ADAPTER_ROOT)
from adapters.binance import fetch_klines, fetch_snapshots, get_market_symbols
from indicators import build_signal
app = Flask(__name__)
SYMBOLS = get_market_symbols() or ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
@app.route('/health')
def health(): return jsonify({"status": "ok", "mode": "read_only", "symbols": SYMBOLS})
@app.route('/symbols')
def symbols_route(): return jsonify({"symbols": SYMBOLS})
@app.route('/mock_stream')
def mock_stream():
    now_ts = int(time.time())
    return jsonify([{"source": "mock", "symbol": s, "ts": now_ts, "price": round(random.uniform(10.0, 50000.0), 6)} for s in SYMBOLS])
@app.route('/live_snapshot')
def live_snapshot():
    symbol = request.args.get('symbol')
    if symbol and symbol.upper() not in SYMBOLS: return jsonify({"error": "unsupported symbol", "symbol": symbol}), 400
    snapshots = fetch_snapshots(symbol.upper() if symbol else None)
    unavailable = [item for item in snapshots if item.get("price") is None]
    return jsonify({"source": "binance_public", "snapshots": snapshots, "available": len(snapshots) - len(unavailable), "unavailable": len(unavailable)}), 502 if unavailable else 200
@app.route('/live_klines')
def live_klines():
    symbol, interval = request.args.get('symbol', 'BTCUSDT').upper(), request.args.get('interval', '15m')
    try:
        if symbol not in SYMBOLS: return jsonify({"error": "unsupported symbol", "symbol": symbol}), 400
        candles = fetch_klines(symbol, interval, int(request.args.get('limit', 100)))
        return jsonify({"source": "binance_public", "symbol": symbol, "interval": interval, "candles": candles})
    except (TypeError, ValueError) as exc: return jsonify({"error": str(exc)}), 400
    except Exception as exc: return jsonify({"error": "Binance public data unavailable", "detail": str(exc)}), 502
@app.route('/live_signal')
def live_signal():
    symbol, interval = request.args.get('symbol', 'BTCUSDT').upper(), request.args.get('interval', '15m')
    try:
        if symbol not in SYMBOLS: return jsonify({"error": "unsupported symbol", "symbol": symbol}), 400
        signal = build_signal(fetch_klines(symbol, interval, 100))
        return jsonify({"symbol": symbol, "interval": interval, "candles_used": 100, **signal})
    except (TypeError, ValueError) as exc: return jsonify({"error": str(exc)}), 400
    except Exception as exc: return jsonify({"error": "signal data unavailable", "detail": str(exc)}), 502
if __name__ == '__main__': app.run(port=8081)
