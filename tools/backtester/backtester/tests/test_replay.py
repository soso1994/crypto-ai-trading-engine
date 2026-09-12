import pandas as pd
from backtester.replay import deterministic_replay

def test_replay_simple():
    df = pd.DataFrame({
        'ts': [1,2,3],
        'price': [100.0, 105.0, 110.0]
    })
    pnl = deterministic_replay(df)
    assert abs(pnl - 10.0) < 1e-6
