from unittest.mock import Mock

import pytest
import requests

from services.ingest.binance import MarketDataError, fetch_klines


def test_fetch_klines_normalizes_public_binance_response(monkeypatch):
    rows = [[index, "1", "3", "0.5", "2", "4"] for index in range(40)]
    response = Mock()
    response.json.return_value = rows
    response.raise_for_status.return_value = None
    request = Mock(return_value=response)
    monkeypatch.setattr("services.ingest.binance.requests.get", request)

    result = fetch_klines("BTCUSDT", "15m")

    request.assert_called_once()
    assert result[0] == {
        "time": 0,
        "open": 1.0,
        "high": 3.0,
        "low": 0.5,
        "close": 2.0,
        "volume": 4.0,
    }


@pytest.mark.parametrize("payload", [[], {"error": "bad"}, [[0, "bad"]]])
def test_fetch_klines_rejects_invalid_responses(monkeypatch, payload):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    monkeypatch.setattr("services.ingest.binance.requests.get", Mock(return_value=response))
    with pytest.raises(MarketDataError):
        fetch_klines("BTCUSDT", "15m")


def test_fetch_klines_translates_network_errors(monkeypatch):
    monkeypatch.setattr(
        "services.ingest.binance.requests.get",
        Mock(side_effect=requests.Timeout),
    )
    with pytest.raises(MarketDataError, match="unavailable"):
        fetch_klines("BTCUSDT", "15m")
