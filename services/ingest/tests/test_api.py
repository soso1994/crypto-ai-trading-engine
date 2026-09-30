import pytest

from services.ingest.app import create_app
from services.ingest.binance import MarketDataError


@pytest.fixture
def candles():
    result = []
    for index in range(100):
        close = 100 + index + index**1.2 / 10
        result.append(
            {
                "time": index * 60_000,
                "open": close - 0.2,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": 10 + index,
            }
        )
    return result


@pytest.fixture
def client(candles):
    app = create_app(testing=True)
    app.config["KLINE_FETCHER"] = lambda symbol, interval: candles
    return app.test_client()


def test_health_endpoint_is_public_paper_only(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"mode": "paper", "status": "ok"}


def test_live_signal_response_matches_dashboard_contract(client):
    response = client.get("/live_signal?symbol=BTCUSDT&interval=15m")
    assert response.status_code == 200
    result = response.json
    assert {"signal", "confidence", "entry_price", "stop_loss", "take_profit", "atr", "timeframe"} <= result.keys()
    assert result["signal"] in {"BUY", "SELL", "HOLD"}
    assert result["symbol"] == "BTCUSDT"
    assert result["timeframe"] == "15m"
    assert result["mode"] == "paper"
    assert len(result["candles"]) == 60


@pytest.mark.parametrize(
    "query",
    [
        "?symbol=BTC/USDT",
        "?symbol=",
        "?symbol=BTCUSDT&interval=2m",
        "?symbol=BTCUSDT&interval=",
    ],
)
def test_live_signal_rejects_invalid_query_parameters(client, query):
    response = client.get(f"/live_signal{query}")
    assert response.status_code == 400
    assert "error" in response.json


def test_signal_endpoint_uses_binance_defaults(client):
    response = client.get("/live_signal")
    assert response.status_code == 200
    assert response.json["symbol"] == "BTCUSDT"
    assert response.json["timeframe"] == "15m"


def test_upstream_failures_are_reported_as_gateway_errors(candles):
    app = create_app(testing=True)

    def unavailable(*_):
        raise MarketDataError("Binance market data is unavailable")

    app.config["KLINE_FETCHER"] = unavailable
    response = app.test_client().get("/live_signal")
    assert response.status_code == 502
    assert response.json == {"error": "Market data is temporarily unavailable"}


def test_insufficient_candles_are_reported_as_gateway_errors():
    app = create_app(testing=True)
    app.config["KLINE_FETCHER"] = lambda *_: []
    response = app.test_client().get("/live_signal")
    assert response.status_code == 502
    assert response.json == {"error": "Market data is temporarily unavailable"}


def test_invalid_kline_shape_is_reported_by_signal_and_performance_routes(candles):
    invalid_candles = [{**candle, "close": "invalid"} for candle in candles]
    app = create_app(testing=True)
    app.config["KLINE_FETCHER"] = lambda *_: invalid_candles
    client = app.test_client()
    assert client.get("/live_signal").json == {"error": "Invalid market data"}
    assert client.get("/performance").json == {"error": "Invalid market data"}


def test_performance_rejects_invalid_query_parameters(client):
    response = client.get("/performance?symbol=BTCUSDT&interval=2m")
    assert response.status_code == 400
    assert response.json == {"error": "Unsupported interval"}


def test_default_binance_fetcher_is_used_when_no_test_override_is_set(monkeypatch, candles):
    monkeypatch.setattr("services.ingest.app.fetch_klines", lambda *_: candles)
    response = create_app(testing=True).test_client().get("/live_signal")
    assert response.status_code == 200
    assert response.json["symbol"] == "BTCUSDT"


def test_performance_endpoint_returns_paper_win_loss_statistics(client):
    response = client.get("/performance?symbol=ETHUSDT&interval=1h")
    assert response.status_code == 200
    assert response.json["mode"] == "paper_backtest"
    assert response.json["symbol"] == "ETHUSDT"
    assert response.json["sample_size"] == response.json["wins"] + response.json["losses"]
    assert 0 <= response.json["win_rate"] <= 100


def test_performance_endpoint_reports_upstream_errors():
    app = create_app(testing=True)
    app.config["KLINE_FETCHER"] = lambda *_: (_ for _ in ()).throw(
        MarketDataError("Binance market data is unavailable")
    )
    response = app.test_client().get("/performance")
    assert response.status_code == 502
    assert response.json == {"error": "Market data is temporarily unavailable"}


def test_cors_is_enabled_for_dashboard_origin(client):
    response = client.get("/live_signal", headers={"Origin": "http://localhost:3000"})
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
