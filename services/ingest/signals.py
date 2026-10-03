from services.ingest.indicators import atr, ema, macd, rsi


def generate_signal(candles, symbol, timeframe):
    if len(candles) < 35:
        raise ValueError("at least 35 candles are required")

    closes = [candle["close"] for candle in candles]
    entry_price = closes[-1]
    average_true_range = atr(
        [candle["high"] for candle in candles],
        [candle["low"] for candle in candles],
        closes,
    )
    fast_average = ema(closes, 9)[-1]
    slow_average = ema(closes, 21)[-1]
    momentum = macd(closes)
    relative_strength = rsi(closes)

    bullish_score = sum(
        (
            fast_average > slow_average,
            momentum["histogram"] > 0,
            50 <= relative_strength < 70,
        )
    )
    bearish_score = sum(
        (
            fast_average < slow_average,
            momentum["histogram"] < 0,
            30 < relative_strength <= 50,
        )
    )
    score = bullish_score if bullish_score > bearish_score else -bearish_score
    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    distance = average_true_range * 1.5
    if signal == "BUY":
        stop_loss, take_profit = entry_price - distance, entry_price + (distance * 2)
    elif signal == "SELL":
        stop_loss, take_profit = entry_price + distance, entry_price - (distance * 2)
    else:
        stop_loss = take_profit = None

    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": min(95, 50 + abs(score) * 15),
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "atr": average_true_range,
        "timeframe": timeframe,
        "mode": "paper",
        "indicators": {
            "ema_fast": fast_average,
            "ema_slow": slow_average,
            "rsi": relative_strength,
            **momentum,
        },
        "candles": candles[-60:],
    }


def paper_performance(candles, symbol, timeframe):
    wins = losses = 0
    for index in range(35, len(candles)):
        signal = generate_signal(candles[:index], symbol, timeframe)["signal"]
        previous_close = candles[index - 1]["close"]
        next_close = candles[index]["close"]
        if signal == "BUY":
            wins += next_close > previous_close
            losses += next_close <= previous_close
        elif signal == "SELL":
            wins += next_close < previous_close
            losses += next_close >= previous_close
    sample_size = wins + losses
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "mode": "paper_backtest",
        "wins": wins,
        "losses": losses,
        "sample_size": sample_size,
        "win_rate": (wins / sample_size * 100) if sample_size else 0,
    }
