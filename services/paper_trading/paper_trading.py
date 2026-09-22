"""Paper trading state and risk controls.

This module never calls an exchange. Orders only update local virtual state.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "paper_trading_state.json"


def current_trading_day() -> str:
    return datetime.now(timezone.utc).date().isoformat()


@dataclass(frozen=True)
class RiskLimits:
    max_order_notional_usdt: float = 1000.0
    max_open_positions: int = 3
    max_daily_loss_usdt: float = 3000.0

    @classmethod
    def from_environment(cls) -> "RiskLimits":
        return cls(
            float(os.getenv("PAPER_MAX_ORDER_NOTIONAL_USDT", "1000")),
            int(os.getenv("PAPER_MAX_OPEN_POSITIONS", "3")),
            float(os.getenv("PAPER_MAX_DAILY_LOSS_USDT", "3000")),
        )

    def validate(self) -> None:
        if self.max_order_notional_usdt <= 0 or self.max_daily_loss_usdt <= 0:
            raise ValueError("risk limits must be positive")
        if self.max_open_positions < 1:
            raise ValueError("max open positions must be at least 1")


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
    trading_day: str = field(default_factory=current_trading_day)

    def to_dict(self) -> Dict[str, object]:
        return {**self.__dict__, "positions": [vars(p) for p in self.positions]}

    @classmethod
    def load(cls) -> "PaperTradingState":
        if not STATE_PATH.exists():
            return cls()
        try:
            payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return cls()
        positions = []
        for item in payload.get("positions", []):
            try:
                positions.append(Position(
                    symbol=str(item["symbol"]), side=str(item.get("side", "long")),
                    size=float(item["size"]), entry_price=float(item["entry_price"]),
                    created_at=str(item.get("created_at", "")),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        state = cls(
            cash_usdt=float(payload.get("cash_usdt", 100000.0)),
            positions=positions,
            orders=list(payload.get("orders", [])),
            realized_pnl=float(payload.get("realized_pnl", 0.0)),
            total_trades=int(payload.get("total_trades", 0)),
            daily_realized_pnl=float(payload.get("daily_realized_pnl", 0.0)),
            risk_halted=bool(payload.get("risk_halted", False)),
            trading_day=str(payload.get("trading_day", current_trading_day())),
        )
        if state.ensure_current_day():
            state.save()
        return state

    def ensure_current_day(self) -> bool:
        today = current_trading_day()
        if self.trading_day == today:
            return False
        self.trading_day = today
        self.daily_realized_pnl = 0.0
        self.risk_halted = False
        return True

    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def get_state() -> PaperTradingState:
    state = PaperTradingState.load()
    if state.ensure_current_day():
        state.save()
    return state


def reset_state() -> PaperTradingState:
    state = PaperTradingState()
    state.save()
    return state


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
        "trading_day": state.trading_day,
    }


def simulate_order(symbol: str, side: str, size: float, price: float, ts: Optional[str] = None) -> Dict[str, object]:
    state = get_state()
    limits = RiskLimits.from_environment()
    limits.validate()
    symbol, side = str(symbol or "").upper(), str(side or "").lower()
    if not symbol:
        raise ValueError("symbol is required")
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")
    if size <= 0 or price <= 0:
        raise ValueError("size and price must be positive")
    notional = size * price
    if notional > limits.max_order_notional_usdt:
        raise ValueError("risk limit: order notional is too large")
    if state.risk_halted or -state.daily_realized_pnl >= limits.max_daily_loss_usdt:
        state.risk_halted = True
        state.save()
        raise ValueError("risk limit: paper trading is halted for the daily loss limit")

    position = next((p for p in state.positions if p.symbol == symbol), None)
    now = ts or datetime.now(timezone.utc).isoformat()
    if side == "buy":
        if state.cash_usdt < notional:
            raise ValueError("insufficient paper cash")
        if position is None and len(state.positions) >= limits.max_open_positions:
            raise ValueError("risk limit: maximum open positions reached")
        state.cash_usdt -= notional
        if position:
            total = position.size + size
            position.entry_price = ((position.size * position.entry_price) + notional) / total
            position.size = total
        else:
            state.positions.append(Position(symbol, "long", size, price, now))
    else:
        if position is None or position.size < size:
            raise ValueError("cannot sell more than the open paper position")
        state.cash_usdt += notional
        pnl = (price - position.entry_price) * size
        state.realized_pnl += pnl
        state.daily_realized_pnl += pnl
        position.size -= size
        if position.size <= 1e-12:
            state.positions.remove(position)

    state.total_trades += 1
    state.orders.append({"symbol": symbol, "side": side, "size": size, "price": price, "ts": now, "mode": "paper"})
    state.save()
    return {"status": "paper_simulated", "symbol": symbol, "side": side, "size": size, "price": price}
