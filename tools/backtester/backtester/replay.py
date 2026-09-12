import pandas as pd

def deterministic_replay(trade_df: pd.DataFrame):
    """Simple deterministic replay: returns cumulative PnL for price series using naive strategy"""
    if trade_df.empty:
        return 0.0
    # assume a single long 1-unit position at first row price, exit at last row price
    entry = trade_df.iloc[0]['price']
    exit_p = trade_df.iloc[-1]['price']
    pnl = exit_p - entry
    return float(pnl)
