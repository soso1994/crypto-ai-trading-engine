import pytest

from services.ingest.signals import generate_signal, paper_performance


def make_candles(closes):
    return [
        {
            "time": index,
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": 1,
        }
        for index, close in enumerate(closes)
    ]


def test_generate_signal_builds_directional_buy_and_sell_risk_levels():
    rising = make_candles([100 + index + index**1.2 / 10 for index in range(60)])
    falling = make_candles([200 - index - index**1.2 / 10 for index in range(60)])

    buy = generate_signal(rising, "BTCUSDT", "15m")
    sell = generate_signal(falling, "BTCUSDT", "15m")

    assert buy["signal"] == "BUY"
    assert buy["stop_loss"] < buy["entry_price"] < buy["take_profit"]
    assert sell["signal"] == "SELL"
    assert sell["take_profit"] < sell["entry_price"] < sell["stop_loss"]


def test_generate_signal_holds_flat_prices_without_risk_levels():
    result = generate_signal(make_candles([100] * 40), "BTCUSDT", "15m")
    assert result["signal"] == "HOLD"
    assert result["stop_loss"] is None
    assert result["take_profit"] is None


def test_generate_signal_requires_sufficient_candles():
    with pytest.raises(ValueError, match="at least 35 candles"):
        generate_signal(make_candles([100] * 34), "BTCUSDT", "15m")


def test_paper_performance_counts_both_wins_and_losses(monkeypatch):
    closes = [100] * 35 + [101, 100, 99]
    candles = make_candles(closes)
    signals = iter(("BUY", "SELL", "BUY"))
    monkeypatch.setattr(
        "services.ingest.signals.generate_signal",
        lambda *_: {"signal": next(signals)},
    )

    result = paper_performance(candles, "BTCUSDT", "15m")

    assert result["wins"] == 2
    assert result["losses"] == 1
    assert result["sample_size"] == 3
    assert result["win_rate"] == pytest.approx(200 / 3)


def test_paper_performance_returns_zero_for_no_directional_signals(monkeypatch):
    candles = make_candles([100] * 37)
    monkeypatch.setattr(
        "services.ingest.signals.generate_signal",
        lambda *_: {"signal": "HOLD"},
    )
    result = paper_performance(candles, "BTCUSDT", "15m")
    assert result["sample_size"] == 0
    assert result["win_rate"] == 0
