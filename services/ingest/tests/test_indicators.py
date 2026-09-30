import pytest

from services.ingest.indicators import atr, ema, macd, rsi


def test_ema_returns_deterministic_exponential_average():
    assert ema([10, 20, 30], 2) == pytest.approx([10, 16.6666667, 25.5555556])


def test_rsi_handles_rising_falling_and_flat_prices():
    assert rsi(list(range(16)), 14) == 100
    assert rsi(list(range(16, 0, -1)), 14) == 0
    assert rsi([5] * 15, 14) == 50


def test_macd_returns_line_signal_and_histogram():
    result = macd([100 + index**1.2 for index in range(50)])
    assert set(result) == {"macd", "signal", "histogram"}
    assert result["histogram"] > 0


def test_atr_uses_true_range_including_previous_close_gaps():
    assert atr([12, 15], [10, 13], [11, 14], 2) == pytest.approx(3)


@pytest.mark.parametrize(
    "calculate,arguments",
    [
        (lambda: ema([], 3), "values must contain finite numbers"),
        (lambda: ema([1, 2], 0), "period must be a positive integer"),
        (lambda: rsi([1, 2], 2), "at least 3 values are required"),
        (lambda: macd([1, 2, 3], 26, 12), "fast period must be less than slow period"),
        (lambda: atr([1], [0], [1], 2), "at least 2 candles are required"),
        (lambda: atr([2], [3], [2], 1), "high must be greater than or equal to low"),
        (lambda: atr([2], [1, 1], [2], 1), "highs, lows, and closes must have equal lengths"),
    ],
)
def test_indicators_validate_inputs(calculate, arguments):
    with pytest.raises(ValueError, match=arguments):
        calculate()
