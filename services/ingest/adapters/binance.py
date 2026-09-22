"""Public Binance market-data adapter.

Only unauthenticated public endpoints are used. This module never places orders
or accesses account data.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "markets.yaml"
DEFAULT_BASE_URL = "https://api.binance.com"


def _safe_yaml_load(path: Path) -> Dict[str, Any]:
    try:
        import yaml
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle) or {}
        return value if isinstance(value, dict) else {}
    except (OSError, ImportError, ValueError):
        return {"markets": []}


def get_market_config(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    markets = _safe_yaml_load(CONFIG_PATH).get("markets", [])
    if not isinstance(markets, list):
        return []
    return [market for market in markets if isinstance(market, dict)
            and (symbol is None or str(market.get("symbol")).upper() == str(symbol).upper())]


def get_market_symbols() -> List[str]:
    return [str(market["symbol"]).upper() for market in get_market_config() if market.get("symbol")]


def _get_json(path: str, timeout: float = 5.0) -> Any:
    base_url = os.getenv("BINANCE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    request = Request(f"{base_url}{path}", headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_market_snapshot(symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
    configured = get_market_config(symbol)
    market = configured[0] if configured else {"symbol": symbol, "exchange": "binance"}
    normalized = str(market.get("symbol", symbol)).upper()
    error = None
    if price is None:
        try:
            price = float(_get_json(f"/api/v3/ticker/price?symbol={quote(normalized)}")["price"])
        except (HTTPError, URLError, KeyError, TypeError, ValueError, TimeoutError) as exc:
            error, price = str(exc), None
    payload = {"source": "binance_public" if error is None else "binance_unavailable",
               "exchange": market.get("exchange", "binance"), "symbol": normalized,
               "ts": int(time.time()), "price": price,
               "base": market.get("base"), "quote": market.get("quote")}
    if error is not None:
        payload["error"] = error
    return payload


def fetch_klines(symbol: str, interval: str = "15m", limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch normalized OHLCV candles from Binance's public spot endpoint."""
    symbol = str(symbol or "").upper()
    interval = str(interval or "15m")
    if not symbol or interval not in {"1m", "5m", "15m", "1h", "4h", "1d"}:
        raise ValueError("invalid symbol or interval")
    if not 1 <= int(limit) <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    rows = _get_json(f"/api/v3/klines?symbol={quote(symbol)}&interval={quote(interval)}&limit={int(limit)}")
    if not isinstance(rows, list):
        raise ValueError("Binance returned an invalid kline payload")
    candles = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 6:
            raise ValueError("Binance returned a malformed kline")
        candles.append({"open_time": int(row[0]), "open": float(row[1]), "high": float(row[2]),
                        "low": float(row[3]), "close": float(row[4]), "volume": float(row[5]),
                        "symbol": symbol, "interval": interval, "source": "binance_public"})
    return candles


def fetch_snapshots(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    symbols = [symbol] if symbol else get_market_symbols()
    return [fetch_market_snapshot(item) for item in symbols]
