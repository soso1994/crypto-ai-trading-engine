#!/usr/bin/env python3
"""
Autolabel worker: reads trades_log from Postgres, computes simple labels and writes labeled_trades.csv
This is a scaffold: adjust rules and thresholds to your needs.
"""
import os
import csv
import psycopg2
import psycopg2.extras
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')
OUT_CSV = os.getenv('OUT_CSV', 'labeled_trades.csv')
PNL_PCT_THRESHOLD = float(os.getenv('PNL_PCT_THRESHOLD', '0.005'))  # default 0.5%

if not DATABASE_URL:
    raise SystemExit('DATABASE_URL env var is required')

conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
cur = conn.cursor()

cur.execute("""
SELECT t.*, s.duration_ms
FROM trades_log t
LEFT JOIN signals_catalog s ON t.signal_id = s.signal_id
WHERE t.end_ts IS NOT NULL
ORDER BY t.end_ts ASC
""")
rows = cur.fetchall()

out_rows = []
for r in rows:
    # compute label rules
    pnl_pct = r.get('pnl_pct')
    user_action = r.get('user_action') or ''

    label = 0
    # user can override
    if user_action and user_action.lower() in ('accepted', 'success', 'win'):
        label = 1
    else:
        if pnl_pct is not None:
            try:
                if float(pnl_pct) >= PNL_PCT_THRESHOLD:
                    label = 1
            except Exception:
                label = 0
        # fallback: if duration_ms exists and trade lasted at least that long and pnl positive
        if label == 0 and r.get('duration_ms') and r.get('start_ts'):
            try:
                start = r.get('start_ts')
                end = r.get('end_ts')
                if isinstance(start, str):
                    start = datetime.fromisoformat(start)
                if isinstance(end, str):
                    end = datetime.fromisoformat(end)
                elapsed_ms = (end - start).total_seconds() * 1000
                if elapsed_ms >= int(r.get('duration_ms')) and r.get('pnl') and float(r.get('pnl')) > 0:
                    label = 1
            except Exception:
                pass

    out_rows.append({
        'id': r.get('id'),
        'signal_id': r.get('signal_id'),
        'model_version': r.get('model_version'),
        'symbol': r.get('symbol'),
        'timeframe': r.get('timeframe'),
        'start_ts': r.get('start_ts'),
        'end_ts': r.get('end_ts'),
        'entry_price': r.get('entry_price'),
        'exit_price': r.get('exit_price'),
        'pnl': r.get('pnl'),
        'pnl_pct': r.get('pnl_pct'),
        'label': label,
        'features': r.get('features')
    })

# write CSV
with open(OUT_CSV, 'w', newline='') as csvfile:
    fieldnames = ['id','signal_id','model_version','symbol','timeframe','start_ts','end_ts','entry_price','exit_price','pnl','pnl_pct','label','features']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for orow in out_rows:
        # ensure features serialized as JSON string
        if orow['features'] is None:
            orow['features'] = ''
        writer.writerow(orow)

print(f'Wrote {len(out_rows)} labeled rows to {OUT_CSV}')
cur.close()
conn.close()
