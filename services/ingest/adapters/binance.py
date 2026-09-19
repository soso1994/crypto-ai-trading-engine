"""Public Binance market-data adapter.

Only public endpoints are used here: no API key, secret, account access, or
order placement. Set BINANCE_BASE_URL to use Binance's testnet-compatible
endpoint when appropriate. The adapter is deliberately small so it can later
be replaced by a WebSocket stream without changing the ingest payload shape.
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
    if symbol is None:
        return [market for market in markets if isinstance(market, dict)]
    return [market for market in markets
            if isinstance(market, dict) and str(market.get("symbol")) == str(symbol)]


def get_market_symbols() -> List[str]:
    return [str(market["symbol"]) for market in get_market_config()
            if market.get("symbol")]


def _get_json(path: str, timeout: float = 5.0) -> Any:
    base_url = os.getenv("BINANCE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    request = Request(f"{base_url}{path}", headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_market_snapshot(symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
    """Return a normalized snapshot; use the public ticker when price is omitted."""
    configured = get_market_config(symbol)
    market = configured[0] if configured else {"symbol": symbol, "exchange": "binance"}
    normalized = str(market.get("symbol", symbol)).upper()
    error = None

    if price is None:
        try:
            ticker = _get_json(f"/api/v3/ticker/price?symbol={quote(normalized)}")
            price = float(ticker["price"])
        except (HTTPError, URLError, KeyError, TypeError, ValueError, TimeoutError) as exc:
            error = str(exc)
            price = None

    payload: Dict[str, Any] = {
        "source": "binance_public" if error is None else "binance_unavailable",
        "exchange": market.get("exchange", "binance"),
        "symbol": normalized,
        "ts": int(time.time()),
        "price": price,
        "base": market.get("base"),
        "quote": market.get("quote"),
    }
    if error is not None:
        payload["error"] = error
    return payload


def fetch_snapshots(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    symbols = [symbol] if symbol else get_market_symbols()
    return [fetch_market_snapshot(item) for item in symbols]
