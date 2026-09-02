-- server/sql/schema.sql

-- trades_log table: records each executed trade (paper or live) and its outcome
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS signals_catalog (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id TEXT,
  decision_payload JSONB,
  confidence DOUBLE PRECISION,
  suggested_size DOUBLE PRECISION,
  duration_ms BIGINT,
  start_ts TIMESTAMP WITH TIME ZONE DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS trades_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  signal_id TEXT,
  model_version TEXT,
  symbol TEXT,
  timeframe TEXT,
  signal_type TEXT,
  start_ts TIMESTAMP WITH TIME ZONE,
  end_ts TIMESTAMP WITH TIME ZONE,
  entry_price DOUBLE PRECISION,
  exit_price DOUBLE PRECISION,
  pnl DOUBLE PRECISION,
  pnl_pct DOUBLE PRECISION,
  realized BOOLEAN,
  user_action TEXT,
  features JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_version TEXT,
  metrics JSONB,
  artifact_path TEXT,
  trained_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  notes TEXT
);
