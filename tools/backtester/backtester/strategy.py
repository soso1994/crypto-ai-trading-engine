"""Candle-based paper backtester with fees, slippage, and validation metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass(frozen=True)
class BacktestConfig:
    initial_cash: float = 10000.0
    fee_rate: float = 0.001
    slippage_rate: float = 0.0005
    position_fraction: float = 0.25

    def validate(self) -> None:
        if self.initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        if self.fee_rate < 0 or self.slippage_rate < 0:
            raise ValueError("fee and slippage rates cannot be negative")
        if not 0 < self.position_fraction <= 1:
            raise ValueError("position_fraction must be between 0 and 1")


def _price(candle: Dict[str, Any]) -> float:
    try:
        value = float(candle["close"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("each candle must contain a numeric close") from exc
    if value <= 0:
        raise ValueError("candle close must be positive")
    return value


def _signal(candles: Sequence[Dict[str, Any]], indicator_fn):
    return indicator_fn(candles)["signal"]


def backtest(candles: Sequence[Dict[str, Any]], indicator_fn, config: BacktestConfig | None = None) -> Dict[str, Any]:
    """Run a long-only signal backtest; signals use candles available before execution."""
    config = config or BacktestConfig()
    config.validate()
    if len(candles) < 36:
        raise ValueError("at least 36 candles are required for backtest")

    cash = config.initial_cash
    units = 0.0
    entry_value = 0.0
    equity = [cash]
    trades: List[Dict[str, Any]] = []
    for index in range(35, len(candles)):
        current = _price(candles[index])
        action = _signal(candles[:index], indicator_fn)
        if action == "buy" and units == 0:
            gross = cash * config.position_fraction
            fill = current * (1 + config.slippage_rate)
            fee = gross * config.fee_rate
            units = max(0.0, (gross - fee) / fill)
            cash -= gross
            entry_value = gross
            trades.append({"side": "buy", "price": fill, "fee": fee, "index": index})
        elif action == "sell" and units > 0:
            fill = current * (1 - config.slippage_rate)
            gross = units * fill
            fee = gross * config.fee_rate
            cash += gross - fee
            trades.append({"side": "sell", "price": fill, "fee": fee, "index": index})
            units = 0.0
            entry_value = 0.0
        equity.append(cash + units * current)

    if units > 0:
        current = _price(candles[-1])
        fill = current * (1 - config.slippage_rate)
        gross = units * fill
        fee = gross * config.fee_rate
        cash += gross - fee
        trades.append({"side": "sell", "price": fill, "fee": fee, "index": len(candles) - 1, "forced": True})
        units = 0.0
        equity[-1] = cash

    wins = 0
    completed = 0
    for buy, sell in zip(trades, trades[1:]):
        if buy["side"] == "buy" and sell["side"] == "sell":
            completed += 1
            wins += int(sell["price"] > buy["price"])
    profits = [sell["price"] - buy["price"] for buy, sell in zip(trades, trades[1:]) if buy["side"] == "buy" and sell["side"] == "sell"]
    gross_profit = sum(value for value in profits if value > 0)
    gross_loss = abs(sum(value for value in profits if value < 0))
    peak = equity[0]
    max_drawdown = 0.0
    for value in equity:
        peak = max(peak, value)
        max_drawdown = max(max_drawdown, (peak - value) / peak if peak else 0.0)
    final_equity = equity[-1]
    return {"initial_cash": config.initial_cash, "final_equity": final_equity,
            "net_pnl": final_equity - config.initial_cash, "return_pct": (final_equity / config.initial_cash - 1) * 100,
            "trades": trades, "completed_trades": completed, "win_rate": wins / completed if completed else 0.0,
            "profit_factor": gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else 0.0),
            "max_drawdown": max_drawdown, "equity_curve": equity, "mode": "paper_only"}
