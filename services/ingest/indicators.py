"""Deterministic technical indicators and paper-only signal generation."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


def _closes(candles: Sequence[Dict[str, Any]]) -> List[float]:
    try:
        values = [float(candle["close"]) for candle in candles]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("candles must contain numeric close values") from exc
    if not values or any(value <= 0 for value in values):
        raise ValueError("candles must contain positive close values")
    return values


def ema(values: Sequence[float], period: int) -> List[float]:
    if period < 1 or len(values) < period:
        raise ValueError("not enough values for EMA period")
    multiplier = 2 / (period + 1)
    result = [sum(values[:period]) / period]
    for value in values[period:]:
        result.append((value - result[-1]) * multiplier + result[-1])
    return result


def rsi(values: Sequence[float], period: int = 14) -> float:
    if period < 1 or len(values) <= period:
        raise ValueError("not enough values for RSI period")
    gains, losses = [], []
    for previous, current in zip(values, values[1:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period
    for gain, loss in zip(gains[period:], losses[period:]):
        average_gain = ((average_gain * (period - 1)) + gain) / period
        average_loss = ((average_loss * (period - 1)) + loss) / period
    if average_loss == 0:
        return 100.0 if average_gain else 50.0
    return 100 - (100 / (1 + average_gain / average_loss))


def macd(values: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
    if len(values) < slow + signal - 1:
        raise ValueError("not enough values for MACD")
    fast_values = ema(values, fast)
    slow_values = ema(values, slow)
    offset = slow - fast
    line = [fast_values[index + offset] - slow_value for index, slow_value in enumerate(slow_values)]
    signal_line = ema(line, signal)
    return {"macd": line[-1], "signal": signal_line[-1], "histogram": line[-1] - signal_line[-1]}


def atr(candles: Sequence[Dict[str, Any]], period: int = 14) -> float:
    if period < 1 or len(candles) <= period:
        raise ValueError("not enough candles for ATR period")
    try:
        true_ranges = []
        previous_close = float(candles[0]["close"])
        for candle in candles[1:]:
            high, low = float(candle["high"]), float(candle["low"])
            true_ranges.append(max(high - low, abs(high - previous_close), abs(low - previous_close)))
            previous_close = float(candle["close"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("candles must contain numeric high, low, and close values") from exc
    return sum(true_ranges[:period]) / period


def build_signal(candles: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    values = _closes(candles)
    if len(values) < 35:
        raise ValueError("at least 35 candles are required for a signal")
    fast, slow = ema(values, 12)[-1], ema(values, 26)[-1]
    current_rsi, current_macd, current_atr = rsi(values, 14), macd(values), atr(candles, 14)
    score = (1 if fast > slow else -1) + (1 if current_macd["histogram"] > 0 else -1)
    score += 1 if 50 < current_rsi < 70 else (-1 if current_rsi > 70 or current_rsi < 30 else 0)
    action = "buy" if score >= 2 else "sell" if score <= -2 else "hold"
    return {"signal": action, "confidence": round(min(0.99, 0.5 + abs(score) / 6), 3), "score": score,
            "price": values[-1], "ema_fast": fast, "ema_slow": slow, "rsi": current_rsi,
            "macd": current_macd, "atr": current_atr, "mode": "paper_only", "source": "binance_public"}
