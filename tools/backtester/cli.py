#!/usr/bin/env python3
"""Simple CLI for running deterministic replay for a given symbol.

Usage:
  python -m tools.backtester.cli --symbol BTCUSDT --source http://localhost:8081/mock_stream

The CLI fetches data for the symbol (from a JSON endpoint or local file) and runs deterministic_replay.
"""
import argparse
import requests
import pandas as pd
import sys
import json
from backtester.replay import deterministic_replay


def fetch_from_endpoint(url, symbol):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        # data expected to be list of {symbol, ts, price}
        filtered = [d for d in data if str(d.get('symbol')) == str(symbol)]
        if not filtered:
            print(f'No data for symbol {symbol} at {url}', file=sys.stderr)
            return None
        df = pd.DataFrame(filtered)
        return df
    except Exception as e:
        print('Failed to fetch data:', e, file=sys.stderr)
        return None


def load_from_file(path, symbol):
    with open(path, 'r') as f:
        data = json.load(f)
    filtered = [d for d in data if str(d.get('symbol')) == str(symbol)]
    if not filtered:
        print(f'No data for symbol {symbol} in file {path}', file=sys.stderr)
        return None
    import pandas as pd
    return pd.DataFrame(filtered)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', required=True, help='Symbol to run replay for (e.g., BTCUSDT)')
    p.add_argument('--source', help='JSON endpoint or local file path to fetch ticks from')
    args = p.parse_args()

    symbol = args.symbol
    source = args.source or 'http://localhost:8081/mock_stream'

    df = None
    if source.startswith('http'):
        df = fetch_from_endpoint(source, symbol)
    else:
        df = load_from_file(source, symbol)

    if df is None or df.empty:
        print('No input data - exiting', file=sys.stderr)
        sys.exit(2)

    pnl = deterministic_replay(df)
    print(f'Replay for {symbol} produced PnL: {pnl}')


if __name__ == '__main__':
    main()
