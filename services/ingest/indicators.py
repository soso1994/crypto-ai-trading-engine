from math import isfinite


def _values(values):
    result = [float(value) for value in values]
    if not result or not all(isfinite(value) for value in result):
        raise ValueError("values must contain finite numbers")
    return result


def _period(period):
    if not isinstance(period, int) or isinstance(period, bool) or period <= 0:
        raise ValueError("period must be a positive integer")


def ema(values, period):
    _period(period)
    prices = _values(values)
    alpha = 2 / (period + 1)
    result = [prices[0]]
    for price in prices[1:]:
        result.append((price * alpha) + (result[-1] * (1 - alpha)))
    return result


def rsi(values, period=14):
    _period(period)
    prices = _values(values)
    if len(prices) <= period:
        raise ValueError(f"at least {period + 1} values are required")
    changes = [current - previous for previous, current in zip(prices, prices[1:])]
    recent = changes[-period:]
    average_gain = sum(max(change, 0) for change in recent) / period
    average_loss = sum(max(-change, 0) for change in recent) / period
    if average_loss == 0:
        return 100.0 if average_gain else 50.0
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def macd(values, fast=12, slow=26, signal_period=9):
    for period in (fast, slow, signal_period):
        _period(period)
    if fast >= slow:
        raise ValueError("fast period must be less than slow period")
    prices = _values(values)
    fast_ema = ema(prices, fast)
    slow_ema = ema(prices, slow)
    line = [fast_value - slow_value for fast_value, slow_value in zip(fast_ema, slow_ema)]
    signal_line = ema(line, signal_period)
    return {
        "macd": line[-1],
        "signal": signal_line[-1],
        "histogram": line[-1] - signal_line[-1],
    }


def atr(highs, lows, closes, period=14):
    _period(period)
    high_values, low_values, close_values = map(_values, (highs, lows, closes))
    if not (len(high_values) == len(low_values) == len(close_values)):
        raise ValueError("highs, lows, and closes must have equal lengths")
    if len(close_values) < period:
        raise ValueError(f"at least {period} candles are required")
    true_ranges = []
    for index, (high, low) in enumerate(zip(high_values, low_values)):
        if high < low:
            raise ValueError("high must be greater than or equal to low")
        previous_close = close_values[index - 1] if index else close_values[index]
        true_ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
    return sum(true_ranges[-period:]) / period
