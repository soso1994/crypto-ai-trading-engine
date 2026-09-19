#!/usr/bin/env python3
"""Validate the market symbol configuration.

This script ensures the repo's config/markets.yaml follows the minimum contract
required by the ingest and dashboard layers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required to validate config: {exc}")


DEFAULT_CONFIG = Path(__file__).resolve().parent / "markets.yaml"


def _require_mapping(value: Any, context: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping/object")
    return value


def validate_markets_config(path: str | Path = DEFAULT_CONFIG) -> List[Dict[str, Any]]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    config = _require_mapping(data, f"config at {config_path}")
    markets = config.get("markets")
    if not isinstance(markets, list):
        raise ValueError(f"{config_path} must contain a 'markets' list")
    if not markets:
        raise ValueError(f"{config_path} must include at least one market")

    normalized: List[Dict[str, Any]] = []
    seen: set[str] = set()

    for index, market in enumerate(markets, start=1):
        item = _require_mapping(market, f"market #{index}")
        symbol = str(item.get("symbol") or "").strip()
        base = str(item.get("base") or "").strip()
        quote = str(item.get("quote") or "").strip()
        exchange = str(item.get("exchange") or "").strip()
        tick_size = item.get("tick_size")
        lot_size = item.get("lot_size")

        if not symbol:
            raise ValueError(f"market #{index} is missing 'symbol'")
        if symbol != symbol.upper():
            raise ValueError(f"market #{index} symbol must be uppercase: {symbol}")
        if not base or not quote:
            raise ValueError(f"market {symbol} is missing base/quote")
        if not exchange:
            raise ValueError(f"market {symbol} is missing exchange")
        if tick_size is None or lot_size is None:
            raise ValueError(f"market {symbol} is missing tick_size or lot_size")
        if symbol in seen:
            raise ValueError(f"duplicate symbol detected: {symbol}")

        try:
            float(tick_size)
            float(lot_size)
        except (TypeError, ValueError):
            raise ValueError(f"market {symbol} has invalid numeric tick_size/lot_size")

        seen.add(symbol)
        normalized.append({
            "symbol": symbol,
            "exchange": exchange,
            "base": base,
            "quote": quote,
            "tick_size": float(tick_size),
            "lot_size": float(lot_size),
        })

    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate market config")
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG), help="Path to markets YAML file")
    args = parser.parse_args()

    try:
        markets = validate_markets_config(args.config)
    except Exception as exc:  # pragma: no cover - CLI only
        print(f"Config validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Validated {len(markets)} markets successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
