"""Validated signal contract for external, human-reviewed execution.

This module creates actionable-looking LONG/SHORT/FLAT instructions from live
public market data, but never places orders. Consumers must validate and execute
these signals separately.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class SignalContract:
    symbol: str
    side: str
    signal: str
    confidence: float
    entry_price: float
    stop_loss: float | None
    take_profit: float | None
    atr: float
    generated_at: str
    timeframe: str
    source: str = "binance_public"
    mode: str = "signal_only"
    execution_required: bool = False
    strategy_version: str = "ema-rsi-macd-atr-v1"

    def validate(self) -> None:
        if not self.symbol or self.side not in {"LONG", "SHORT", "FLAT"}:
            raise ValueError("invalid signal identity")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.entry_price <= 0 or self.atr <= 0:
            raise ValueError("entry price and ATR must be positive")
        if self.side == "LONG":
            if self.stop_loss is None or self.take_profit is None or not (self.stop_loss < self.entry_price < self.take_profit):
                raise ValueError("long signal must have SL < entry < TP")
        elif self.side == "SHORT":
            if self.stop_loss is None or self.take_profit is None or not (self.take_profit < self.entry_price < self.stop_loss):
                raise ValueError("short signal must have TP < entry < SL")
        elif self.stop_loss is not None or self.take_profit is not None:
            raise ValueError("flat signal cannot have targets")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)


def build_signal_contract(symbol: str, timeframe: str, indicators: Dict[str, Any],
                          stop_atr: float = 1.5, target_atr: float = 3.0) -> Dict[str, Any]:
    """Convert indicator output into a human-reviewable signal contract."""
    if stop_atr <= 0 or target_atr <= 0:
        raise ValueError("ATR multipliers must be positive")
    action = str(indicators.get("signal", "hold")).lower()
    side = {"buy": "LONG", "sell": "SHORT", "hold": "FLAT"}.get(action)
    if side is None:
        raise ValueError("unsupported signal action")
    entry = float(indicators["price"])
    volatility = float(indicators["atr"])
    confidence = float(indicators["confidence"])
    stop = target = None
    if side == "LONG":
        stop, target = entry - stop_atr * volatility, entry + target_atr * volatility
    elif side == "SHORT":
        stop, target = entry + stop_atr * volatility, entry - target_atr * volatility
    contract = SignalContract(
        symbol=str(symbol).upper(), side=side, signal=action, confidence=confidence,
        entry_price=entry, stop_loss=stop, take_profit=target, atr=volatility,
        generated_at=datetime.now(timezone.utc).isoformat(), timeframe=str(timeframe),
    )
    return contract.to_dict()
