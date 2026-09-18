"""Adapters package for external market-data providers."""

from .binance import get_market_config, get_market_symbols, fetch_market_snapshot

__all__ = ["get_market_config", "get_market_symbols", "fetch_market_snapshot"]
