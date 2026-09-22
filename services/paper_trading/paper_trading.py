"""Safe paper-trading engine with configurable risk controls.

This module never calls an exchange. Orders only change the local virtual state.
Risk limits can be configured with environment variables for paper experiments:
PAPER_MAX_ORDER_NOTIONAL_USDT, PAPER_MAX_OPEN_POSITIONS, and
PAPER_MAX_DAILY_LOSS_USDT.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "paper_trading_state.json"


@dataclass(frozen=True)
class RiskLimits:
    max_order_notional_usdt: float = 10_000.0
    max_open_positions: int = 5
    max_daily_loss_usdt: float = 1_000.0

    @classmethod
    def from_environment(cls) -> "RiskLimits":
        return cls(
            max_order_notional_usdt=float(os.getenv("PAPER_MAX_ORDER_NOTIONAL_USDT", "10000")),
            max_open_positions=int(os.getenv("PAPER_MAX_OPEN_POSITIONS", "5")),
            max_daily_loss_usdt=float(os.getenv("PAPER_MAX_DAILY_LOSS_USDT", "1000")),
        )

    def validate(self) -> None:
        if self.max_order_notional_usdt <= 0:
            raise ValueError("max order notional must be positive")
        if self.max_open_positions < 1:
            raise ValueError("max open positions must be at least 1")
        if self.max_daily_loss_usdt <= 0:
            raise ValueError("max daily loss must be positive")


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
    daily_realized_pnl: float = 0.0
    risk_halted: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "cash_usdt": self.cash_usdt,
            "realized_pnl": self.realized_pnl,
            "daily_realized_pnl": self.daily_realized_pnl,
            "risk_halted": self.risk_halted,
            "total_trades": self.total_trades,
            "positions": [vars(p) for p in self.positions],
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
        return cls(
            cash_usdt=float(payload.get("cash_usdt", 100000.0)),
            realized_pnl=float(payload.get("realized_pnl", 0.0)),
            daily_realized_pnl=float(payload.get("daily_realized_pnl", 0.0)),
            risk_halted=bool(payload.get("risk_halted", False)),
            total_trades=int(payload.get("total_trades", 0)),
            positions=[Position(**{key: item.get(key, "") for key in
                ("symbol", "side", "size", "entry_price", "created_at")})
                for item in payload.get("positions", [])],
            orders=list(payload.get("orders", [])),
        )

    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATE_PATH.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)


def get_state() -> PaperTradingState:
    return PaperTradingState.load()


def risk_status(state: Optional[PaperTradingState] = None, limits: Optional[RiskLimits] = None) -> Dict[str, object]:
    state = state or get_state()
    limits = limits or RiskLimits.from_environment()
    limits.validate()
    loss_used = max(0.0, -state.daily_realized_pnl)
    return {
        "halted": state.risk_halted or loss_used >= limits.max_daily_loss_usdt,
        "max_order_notional_usdt": limits.max_order_notional_usdt,
        "max_open_positions": limits.max_open_positions,
        "max_daily_loss_usdt": limits.max_daily_loss_usdt,
        "daily_loss_used_usdt": loss_used,
        "open_positions": len(state.positions),
    }


def simulate_order(symbol: str, side: str, size: float, price: float, ts: Optional[str] = None) -> Dict[str, object]:
    state = get_state()
    limits = RiskLimits.from_environment()
    limits.validate()
    symbol = str(symbol or "").upper()
    side = str(side or "").lower()
    if not symbol:
        raise ValueError("symbol is required")
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")
    if size <= 0 or price <= 0:
        raise ValueError("size and price must be positive")
    notional = size * price
    if notional > limits.max_order_notional_usdt:
        raise ValueError("risk limit: order notional is too large")
    if state.risk_halted or max(0.0, -state.daily_realized_pnl) >= limits.max_daily_loss_usdt:
        state.risk_halted = True
        state.save()
        raise ValueError("risk limit: paper trading is halted for the daily loss limit")

    existing = next((p for p in state.positions if p.symbol == symbol), None)
    if side == "buy":
        if state.cash_usdt < notional:
            raise ValueError("insufficient paper cash")
        if existing is None and len(state.positions) >= limits.max_open_positions:
            raise ValueError("risk limit: maximum open positions reached")
        state.cash_usdt -= notional
        if existing:
            total_size = existing.size + size
            existing.entry_price = ((existing.size * existing.entry_price) + notional) / total_size
            existing.size = total_size
        else:
            state.positions.append(Position(symbol, "long", size, price, ts or datetime.now(timezone.utc).isoformat()))
    else:
        if existing is None or existing.size < size:
            raise ValueError("cannot sell more than the open paper position")
        state.cash_usdt += notional
        pnl = (price - existing.entry_price) * size
        state.realized_pnl += pnl
        state.daily_realized_pnl += pnl
        existing.size -= size
        if existing.size <= 1e-12:
            state.positions.remove(existing)

    state.total_trades += 1
    state.orders.append({"symbol": symbol, "side": side, "size": size, "price": price,
                         "ts": ts or datetime.now(timezone.utc).isoformat(), "mode": "paper"})
    state.save()
    return {"status": "paper_simulated", "symbol": symbol, "side": side, "size": size, "price": price}
