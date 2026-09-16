import pytest
import yaml
import pandas as pd
from backtester.replay import deterministic_replay
from pathlib import Path

CFG = Path(__file__).resolve().parents[4] / 'config' / 'markets.yaml'

with open(CFG, 'r') as f:
    cfg = yaml.safe_load(f)
    symbols = [m.get('symbol') for m in cfg.get('markets', [])][:5]

@pytest.mark.parametrize('symbol', symbols)
def test_replay_parametrized(symbol):
    # simple constructed DataFrame for deterministic_replay per symbol
    df = pd.DataFrame({'ts': [1,2,3], 'price': [100.0, 102.0, 110.0], 'symbol': [symbol]*3})
    pnl = deterministic_replay(df)
    assert isinstance(pnl, float)
