# Risk controls for paper trading

from __future__ import annotations

from app import app


def test_paper_risk_endpoint():
    client = app.test_client()
    response = client.get('/paper/risk')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'max_order_notional_usdt' in payload
    assert 'max_open_positions' in payload
    assert 'max_daily_loss_usdt' in payload


def test_paper_account_returns_risk_block():
    client = app.test_client()
    response = client.get('/paper/account')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['mode'] == 'paper'
    assert 'risk' in payload
    assert 'halted' in payload['risk']


def test_paper_order_rejects_large_notional():
    client = app.test_client()
    response = client.post('/paper/order', json={
        'symbol': 'BTCUSDT',
        'side': 'buy',
        'size': 20,
        'price': 100000,
    })
    assert response.status_code == 400
    payload = response.get_json()
    assert 'error' in payload
    assert 'risk limit' in payload['error'].lower()
