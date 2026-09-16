import pandas as pd
from backtester.replay import deterministic_replay


def test_replay_simple():
    df = pd.DataFrame({
        'ts': [1,2,3],
        'price': [100.0, 105.0, 110.0]
    })
    pnl = deterministic_replay(df)
    assert abs(pnl - 10.0) < 1e-6


def test_replay_empty():
    df = pd.DataFrame({
        'ts': [],
        'price': []
    })
    pnl = deterministic_replay(df)
    assert pnl == 0.0


def test_replay_negative_prices():
    df = pd.DataFrame({
        'ts': [1,2],
        'price': [-50.0, -45.0]
    })
    pnl = deterministic_replay(df)
    assert abs(pnl - 5.0) < 1e-6
