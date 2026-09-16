from flask import Flask, jsonify
import time
import random
import os
import yaml

app = Flask(__name__)

def load_symbols():
    cfg_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'markets.yaml')
    try:
        with open(cfg_path, 'r') as f:
            cfg = yaml.safe_load(f)
            markets = cfg.get('markets', []) if isinstance(cfg, dict) else []
            symbols = [m.get('symbol') for m in markets if m.get('symbol')]
            if symbols:
                return symbols
    except Exception as e:
        print('Could not load markets.yaml:', e)
    # fallback
    return ['BTCUSDT', 'ETHUSDT']

SYMBOLS = load_symbols()

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/mock_stream')
def mock_stream():
    # returns a small batch of mocked messages across configured symbols
    now_ts = int(time.time())
    data = []
    for sym in SYMBOLS:
        price = round(random.uniform(10.0, 50000.0), 6)
        data.append({"source": "mock", "symbol": sym, "ts": now_ts, "price": price})
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=8081)
