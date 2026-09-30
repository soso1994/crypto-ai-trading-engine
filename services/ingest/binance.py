import requests


BASE_URL = "https://api.binance.com/api/v3/klines"
KLINE_LIMIT = 100
MIN_CANDLES = 35


class MarketDataError(Exception):
    pass


def fetch_klines(symbol, interval, limit=KLINE_LIMIT):
    try:
        response = requests.get(
            BASE_URL,
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise MarketDataError("Binance market data is unavailable") from error

    if not isinstance(payload, list) or len(payload) < MIN_CANDLES:
        raise MarketDataError("Binance returned insufficient candle data")

    try:
        candles = [
            {
                "time": int(row[0]),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
            }
            for row in payload
        ]
    except (IndexError, TypeError, ValueError) as error:
        raise MarketDataError("Binance returned invalid candle data") from error
    return candles
