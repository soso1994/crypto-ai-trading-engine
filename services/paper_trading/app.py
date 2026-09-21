"""Paper trading API entrypoint.

This is intentionally read-write only in memory/JSON state and never touches real
funds or real exchange APIs.
"""

from flask import Flask, jsonify, request

from paper_trading import get_state, simulate_order

app = Flask(__name__)


@app.route('/paper/account')
def paper_account():
    state = get_state()
    return jsonify({
        "mode": "paper",
        "cash_usdt": state.cash_usdt,
        "realized_pnl": state.realized_pnl,
        "total_trades": state.total_trades,
        "positions": [
            {
                "symbol": p.symbol,
                "side": p.side,
                "size": p.size,
                "entry_price": p.entry_price,
                "created_at": p.created_at,
            }
            for p in state.positions
        ],
    })


@app.route('/paper/order', methods=['POST'])
def paper_order():
    payload = request.get_json(silent=True) or {}
    symbol = payload.get('symbol')
    side = payload.get('side')
    size = float(payload.get('size', 0))
    price = float(payload.get('price', 0))
    if not symbol or not side:
        return jsonify({"error": "symbol and side are required"}), 400
    try:
        result = simulate_order(symbol, side, size, price)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route('/paper/summary')
def paper_summary():
    state = get_state()
    return jsonify({
        "mode": "paper",
        "cash_usdt": state.cash_usdt,
        "positions": len(state.positions),
        "total_trades": state.total_trades,
        "realized_pnl": state.realized_pnl,
    })


if __name__ == '__main__':
    app.run(port=8090)
