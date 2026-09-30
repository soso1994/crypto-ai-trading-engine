import json
import threading

import pytest
from services.ingest.binance import MarketDataError
from simple_websocket import Client
from werkzeug.serving import make_server

from services.ingest.app import create_app


@pytest.fixture
def websocket_server():
    candles = []
    for index in range(40):
        close = 100 + index + index**1.2 / 10
        candles.append(
            {
                "time": index,
                "open": close,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": 1,
            }
        )
    app = create_app(testing=True)
    failure = {"enabled": False}

    def fetcher(*_):
        if failure["enabled"]:
            raise MarketDataError("Binance market data is unavailable")
        return candles

    app.config.update(KLINE_FETCHER=fetcher, WS_INTERVAL_SECONDS=0.01)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_port, failure
    server.shutdown()
    thread.join(timeout=2)


def test_websocket_sends_realtime_signal_payload(websocket_server):
    socket = Client.connect(
        f"ws://127.0.0.1:{websocket_server[0]}/ws/signals?symbol=BTCUSDT&interval=15m"
    )
    try:
        result = json.loads(socket.receive(timeout=2))
    finally:
        socket.close()
    assert result["symbol"] == "BTCUSDT"
    assert result["signal"] in {"BUY", "SELL", "HOLD"}
    assert result["mode"] == "paper"


def test_websocket_rejects_unsupported_interval(websocket_server):
    socket = Client.connect(
        f"ws://127.0.0.1:{websocket_server[0]}/ws/signals?symbol=BTCUSDT&interval=2m"
    )
    try:
        result = json.loads(socket.receive(timeout=2))
    finally:
        socket.close()
    assert result == {"error": "Unsupported interval"}


def test_websocket_reports_market_data_errors(websocket_server):
    port, failure = websocket_server
    socket = Client.connect(f"ws://127.0.0.1:{port}/ws/signals?symbol=BTCUSDT&interval=15m")
    try:
        assert json.loads(socket.receive(timeout=2))["mode"] == "paper"
        failure["enabled"] = True
        result = json.loads(socket.receive(timeout=2))
    finally:
        if socket.connected:
            socket.close()
    assert result == {"error": "Binance market data is unavailable"}
