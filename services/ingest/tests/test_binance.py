from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services' / 'ingest'))

from adapters import binance


def test_fetch_klines_normalizes_public_payload(monkeypatch):
    monkeypatch.setattr(binance, '_get_json', lambda path: [[
        1700000000000, '100.0', '110.0', '90.0', '105.0', '12.5'
    ]])
    result = binance.fetch_klines('BTCUSDT', '15m', 1)
    assert result == [{
        'open_time': 1700000000000, 'open': 100.0, 'high': 110.0,
        'low': 90.0, 'close': 105.0, 'volume': 12.5,
        'symbol': 'BTCUSDT', 'interval': '15m', 'source': 'binance_public'
    }]


def test_fetch_klines_rejects_invalid_limit():
    try:
        binance.fetch_klines('BTCUSDT', '15m', 0)
    except ValueError as exc:
        assert 'limit' in str(exc)
    else:
        raise AssertionError('invalid limit was accepted')


def test_fetch_klines_rejects_malformed_payload(monkeypatch):
    monkeypatch.setattr(binance, '_get_json', lambda path: [[1, 2]])
    try:
        binance.fetch_klines('BTCUSDT')
    except ValueError as exc:
        assert 'malformed' in str(exc)
    else:
        raise AssertionError('malformed payload was accepted')
