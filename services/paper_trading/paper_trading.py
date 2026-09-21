"""Paper trading scaffold.

This module does not execute real orders. It simulates cash, positions, and PnL
based on a fixed starting balance and deterministic price snapshots. This is the
safest bridge between mock data and real live trading.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "paper_trading_state.json"


@dataclass
class Position:
    symbol: str
    side: str
    size: float
    entry_price: float
    created_at: str


@dataclass
class PaperTradingState:
    cash_usdt: float = 100000.0
    positions: List[Position] = field(default_factory=list)
    orders: List[Dict[str, object]] = field(default_factory=list)
    realized_pnl: float = 0.0
    total_trades: int = 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "cash_usdt": self.cash_usdt,
            "realized_pnl": self.realized_pnl,
            "total_trades": self.total_trades,
            "positions": [
                {
                    "symbol": p.symbol,
                    "side": p.side,
                    "size": p.size,
                    "entry_price": p.entry_price,
                    "created_at": p.created_at,
                }
                for p in self.positions
            ],
            "orders": self.orders,
        }

    @classmethod
    def load(cls) -> "PaperTradingState":
        if not STATE_PATH.exists():
            return cls()
        try:
            with STATE_PATH.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return cls()

        state = cls(
            cash_usdt=float(payload.get("cash_usdt", 100000.0)),
            realized_pnl=float(payload.get("realized_pnl", 0.0)),
            total_trades=int(payload.get("total_trades", 0)),
            positions=[
                Position(
                    symbol=str(item.get("symbol", "")),
                    side=str(item.get("side", "long")),
                    size=float(item.get("size", 0.0)),
                    entry_price=float(item.get("entry_price", 0.0)),
                    created_at=str(item.get("created_at", "")),
                )
                for item in payload.get("positions", [])
            ],
            orders=list(payload.get("orders", [])),
        )
        return state

    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATE_PATH.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)


def create_default_state() -> PaperTradingState:
    return PaperTradingState()


def get_state() -> PaperTradingState:
    return PaperTradingState.load()


def simulate_order(symbol: str, side: str, size: float, price: float, ts: Optional[str] = None) -> Dict[str, object]:
    """Simulate a paper order and update the virtual account state."""
    state = get_state()
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")
    if size <= 0 or price <= 0:
        raise ValueError("size and price must be positive")

    notional = size * price
    if side == "buy":
        if state.cash_usdt < notional:
            raise ValueError("insufficient paper cash")
        state.cash_usdt -= notional
    else:
        state.cash_usdt += notional

    state.total_trades += 1
    state.orders.append({
        "symbol": symbol,
        "side": side,
        "size": size,
        "price": price,
        "ts": ts or "now",
        "mode": "paper",
    })
    state.save()

    return {"status": "paper_simulated", "symbol": symbol, "side": side, "size": size, "price": price}
