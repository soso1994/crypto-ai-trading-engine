from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/mock_stream')
def mock_stream():
    # returns a small batch of mocked messages
    data = [
        {"source": "binance", "symbol": "BTCUSDT", "ts": int(time.time()), "price": 27000.0},
        {"source": "bybit", "symbol": "BTCUSDT", "ts": int(time.time()), "price": 27010.5},
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=8081)
