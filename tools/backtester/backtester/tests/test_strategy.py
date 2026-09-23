from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services' / 'ingest'))
sys.path.insert(0, str(ROOT / 'tools' / 'backtester'))
from indicators import build_signal
from backtester.strategy import BacktestConfig, backtest


def candles(values):
    return [{"open": v, "high": v + 1, "low": v - 1, "close": v, "volume": 1} for v in values]


def test_backtest_returns_validation_metrics():
    result = backtest(candles([100 + ((i % 8) * 2) for i in range(80)]), build_signal, BacktestConfig(fee_rate=0, slippage_rate=0))
    assert result["mode"] == "paper_only"
    assert 0 <= result["win_rate"] <= 1
    assert result["completed_trades"] >= 0
    assert 0 <= result["max_drawdown"] <= 1
    assert len(result["equity_curve"]) > 1


def test_backtest_includes_costs():
    data = candles([100 + i for i in range(80)])
    free = backtest(data, build_signal, BacktestConfig(fee_rate=0, slippage_rate=0))
    costly = backtest(data, build_signal, BacktestConfig(fee_rate=.01, slippage_rate=.01))
    assert costly["final_equity"] <= free["final_equity"]


def test_backtest_rejects_short_history():
    try:
        backtest(candles(range(35)), build_signal)
    except ValueError as exc:
        assert "36" in str(exc)
    else:
        raise AssertionError("short history was accepted")
