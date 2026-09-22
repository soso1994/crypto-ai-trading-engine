"""Paper trading API; all orders remain local simulations."""

from flask import Flask, jsonify, request

from paper_trading import get_state, reset_state, risk_status, simulate_order

app = Flask(__name__)


def account_payload():
    state = get_state()
    return {
        "mode": "paper",
        "cash_usdt": state.cash_usdt,
        "realized_pnl": state.realized_pnl,
        "total_trades": state.total_trades,
        "positions": [vars(position) for position in state.positions],
        "risk": risk_status(state),
    }


@app.route('/paper/account')
def paper_account():
    return jsonify(account_payload())


@app.route('/paper/risk')
def paper_risk():
    return jsonify(risk_status())


@app.route('/paper/history')
def paper_history():
    return jsonify({"mode": "paper", "orders": get_state().orders})


@app.route('/paper/reset', methods=['POST'])
def paper_reset():
    return jsonify({
        "mode": "paper",
        "cash_usdt": reset_state().cash_usdt,
        "realized_pnl": 0.0,
        "total_trades": 0,
        "positions": [],
        "risk": risk_status(),
    })


@app.route('/paper/order', methods=['POST'])
def paper_order():
    payload = request.get_json(silent=True) or {}
    try:
        result = simulate_order(
            payload.get('symbol'),
            payload.get('side'),
            float(payload.get('size', 0)),
            float(payload.get('price', 0)),
        )
        return jsonify(result), 200
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc), "mode": "paper"}), 400


@app.route('/paper/summary')
def paper_summary():
    state = get_state()
    return jsonify({
        "mode": "paper",
        "cash_usdt": state.cash_usdt,
        "positions": len(state.positions),
        "total_trades": state.total_trades,
        "realized_pnl": state.realized_pnl,
        "risk": risk_status(state),
    })


if __name__ == '__main__':
    app.run(port=8090)
