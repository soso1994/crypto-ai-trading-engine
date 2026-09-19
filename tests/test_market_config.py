from pathlib import Path

from config.validate_config import validate_markets_config


def test_config_has_unique_uppercase_symbols():
    markets = validate_markets_config(Path(__file__).resolve().parents[1] / 'config' / 'markets.yaml')
    symbols = [market['symbol'] for market in markets]
    assert len(symbols) == len(set(symbols))
    assert all(sym == sym.upper() for sym in symbols)


def test_config_has_required_fields_per_market():
    markets = validate_markets_config(Path(__file__).resolve().parents[1] / 'config' / 'markets.yaml')
    for market in markets:
        assert market['symbol']
        assert market['exchange']
        assert market['base']
        assert market['quote']
        assert market['tick_size'] > 0
        assert market['lot_size'] > 0


def test_config_has_20_markets():
    markets = validate_markets_config(Path(__file__).resolve().parents[1] / 'config' / 'markets.yaml')
    assert len(markets) == 20
