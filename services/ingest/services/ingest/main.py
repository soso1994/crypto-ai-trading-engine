"""Binance adapter scaffold.

This module is intentionally safe: it does not place real orders and does not
require API keys for the mock, config-driven mode. It exposes a minimal market
schema that can later be swapped with the real Binance REST/WebSocket client.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "markets.yaml"


def _safe_yaml_load(path: Path) -> Dict[str, Any]:
    try:
        import yaml
    except Exception:
        return {"markets": []}

    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {"markets": []}


def get_market_config(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    cfg = _safe_yaml_load(CONFIG_PATH)
    markets = cfg.get("markets", [])
    if not isinstance(markets, list):
        return []
    if symbol is None:
        return markets
    filtered = [m for m in markets if str(m.get("symbol")) == str(symbol)]
    return filtered


def get_market_symbols() -> List[str]:
    markets = get_market_config()
    symbols = [str(m.get("symbol")) for m in markets if m.get("symbol")]
    return symbols


def fetch_market_snapshot(symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
    """Return a safe, config-aligned snapshot for a symbol."""
    cfg = get_market_config(symbol)
    market = cfg[0] if cfg else {"symbol": symbol, "exchange": "binance"}
    now = int(time.time())
    if price is None:
        # deterministic pseudo-price based on symbol hash to keep mock behavior stable
        safe_seed = sum(ord(ch) for ch in str(symbol))
        price = 100.0 + (safe_seed % 5000)
    return {
        "source": "binance",
        "symbol": market.get("symbol", symbol),
        "exchange": market.get("exchange", "binance"),
        "ts": now,
        "price": float(price),
        "base": market.get("base"),
        "quote": market.get("quote"),
    }


def list_market_payloads() -> List[Dict[str, Any]]:
    symbols = get_market_symbols()
    return [fetch_market_snapshot(symbol) for symbol in symbols]
