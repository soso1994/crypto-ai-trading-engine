import pool from "./db";

export async function logSignal(signal: {
  signal_id: string;
  payload: any;
  confidence?: number;
  size?: number;
  durationMs?: number | null;
}) {
  const query = `INSERT INTO signals_catalog(signal_id, decision_payload, confidence, suggested_size, duration_ms, start_ts)
    VALUES($1, $2, $3, $4, $5, now())`;
  const params = [signal.signal_id, signal.payload, signal.confidence ?? null, signal.size ?? null, signal.durationMs ?? null];
  await pool.query(query, params);
}

export async function logTradeOutcome(trade: {
  signal_id: string;
  model_version?: string;
  symbol: string;
  timeframe: string;
  signal_type: string;
  start_ts?: string | Date;
  end_ts?: string | Date;
  entry_price?: number;
  exit_price?: number;
  pnl?: number;
  pnl_pct?: number;
  realized?: boolean;
  user_action?: string;
  features?: any;
}) {
  const query = `INSERT INTO trades_log(
    signal_id, model_version, symbol, timeframe, signal_type, start_ts, end_ts, entry_price, exit_price, pnl, pnl_pct, realized, user_action, features, created_at
  ) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14, now())`;

  const params = [
    trade.signal_id,
    trade.model_version ?? null,
    trade.symbol,
    trade.timeframe,
    trade.signal_type,
    trade.start_ts ?? null,
    trade.end_ts ?? null,
    trade.entry_price ?? null,
    trade.exit_price ?? null,
    trade.pnl ?? null,
    trade.pnl_pct ?? null,
    trade.realized ?? null,
    trade.user_action ?? null,
    trade.features ? JSON.stringify(trade.features) : null,
  ];

  await pool.query(query, params);
}
