import json
import re
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sock import Sock

from services.ingest.binance import MarketDataError, fetch_klines
from services.ingest.signals import generate_signal, paper_performance


SUPPORTED_INTERVALS = {"1m", "5m", "15m", "1h", "4h", "1d"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def create_app(testing=False):
    app = Flask(__name__)
    app.config.update(TESTING=testing, WS_INTERVAL_SECONDS=15)
    CORS(app)
    sock = Sock(app)

    def query_parameters():
        symbol = request.args.get("symbol", "BTCUSDT").upper()
        interval = request.args.get("interval", "15m")
        if not SYMBOL_PATTERN.fullmatch(symbol):
            return None, (jsonify(error="Invalid symbol"), 400)
        if interval not in SUPPORTED_INTERVALS:
            return None, (jsonify(error="Unsupported interval"), 400)
        return (symbol, interval), None

    def get_candles(symbol, interval):
        fetcher = app.config.get("KLINE_FETCHER", fetch_klines)
        candles = fetcher(symbol, interval)
        if len(candles) < 35:
            raise MarketDataError("Binance returned insufficient candle data")
        return candles

    @app.get("/health")
    def health():
        return jsonify(status="ok", mode="paper")

    @app.get("/live_signal")
    def live_signal():
        parameters, error = query_parameters()
        if error:
            return error
        symbol, interval = parameters
        try:
            result = generate_signal(get_candles(symbol, interval), symbol, interval)
        except MarketDataError as exception:
            return jsonify(error=str(exception)), 502
        except (KeyError, TypeError, ValueError):
            return jsonify(error="Invalid market data"), 502
        return jsonify(result)

    @app.get("/performance")
    def performance():
        parameters, error = query_parameters()
        if error:
            return error
        symbol, interval = parameters
        try:
            result = paper_performance(get_candles(symbol, interval), symbol, interval)
        except MarketDataError as exception:
            return jsonify(error=str(exception)), 502
        except (KeyError, TypeError, ValueError):
            return jsonify(error="Invalid market data"), 502
        return jsonify(result)

    @sock.route("/ws/signals")
    def signal_updates(websocket):
        parameters, error = query_parameters()
        if error:
            websocket.send(json.dumps(error[0].get_json()))
            return
        symbol, interval = parameters
        while True:
            try:
                result = generate_signal(get_candles(symbol, interval), symbol, interval)
                websocket.send(json.dumps(result))
                time.sleep(app.config["WS_INTERVAL_SECONDS"])
            except Exception:
                return

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
