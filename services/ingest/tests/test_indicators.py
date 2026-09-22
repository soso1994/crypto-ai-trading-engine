from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services' / 'ingest'))
from indicators import atr, build_signal, ema, macd, rsi

def candles(values):
    return [{"open": v, "high": v + 1, "low": v - 1, "close": v, "volume": 1} for v in values]

def test_indicators_are_deterministic():
    values = [float(100 + index) for index in range(50)]
    assert len(ema(values, 12)) == 39
    assert rsi(values) == 100.0
    assert macd(values)["histogram"] > 0
    assert atr(candles(values), 14) == 2.0

def test_signal_is_paper_only_and_has_risk_metrics():
    result = build_signal(candles([float(100 + index) for index in range(50)]))
    assert result["mode"] == "paper_only"
    assert result["signal"] in {"buy", "sell", "hold"}
    assert 0.5 <= result["confidence"] <= 0.99
    assert result["atr"] > 0

def test_signal_rejects_short_history():
    try:
        build_signal(candles([100 + index for index in range(20)]))
    except ValueError as exc:
        assert "35" in str(exc)
    else:
        raise AssertionError("short history was accepted")
