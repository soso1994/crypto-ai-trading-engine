import { useEffect, useState } from "react";
import PriceChart from "./components/PriceChart";

const SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"];
const INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d"];

function formatPrice(value) {
  if (value == null || !Number.isFinite(Number(value))) return "—";
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function App() {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [interval, setInterval] = useState("15m");
  const [signal, setSignal] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [connection, setConnection] = useState("connecting");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    let socket;
    let reconnectTimer;

    const query = `symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}`;
    const loadSignal = async () => {
      try {
        const response = await fetch(`/live_signal?${query}`);
        if (!response.ok) throw new Error("Signal service is unavailable");
        const result = await response.json();
        if (active) {
          setSignal(result);
          setError("");
        }
      } catch (requestError) {
        if (active) setError(requestError.message);
      }
    };
    const loadPerformance = async () => {
      try {
        const response = await fetch(`/performance?${query}`);
        if (!response.ok) throw new Error("Performance data is unavailable");
        const result = await response.json();
        if (active) setPerformance(result);
      } catch {
        if (active) setPerformance(null);
      }
    };
    const connect = () => {
      if (!active || typeof WebSocket === "undefined") {
        setConnection("offline");
        return;
      }
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      socket = new WebSocket(`${protocol}//${window.location.host}/ws/signals?${query}`);
      socket.onopen = () => active && setConnection("live");
      socket.onmessage = (event) => {
        try {
          const result = JSON.parse(event.data);
          if (result.error) throw new Error(result.error);
          if (active) {
            setSignal(result);
            setError("");
          }
        } catch (messageError) {
          if (active) setError(messageError.message);
        }
      };
      socket.onerror = () => active && setConnection("reconnecting");
      socket.onclose = () => {
        if (active) {
          setConnection("reconnecting");
          reconnectTimer = window.setTimeout(connect, 5000);
        }
      };
    };

    setSignal(null);
    setPerformance(null);
    setError("");
    setConnection("connecting");
    loadSignal();
    loadPerformance();
    connect();
    const fallback = window.setInterval(loadSignal, 30000);
    const refreshStats = window.setInterval(loadPerformance, 60000);

    return () => {
      active = false;
      window.clearInterval(fallback);
      window.clearInterval(refreshStats);
      window.clearTimeout(reconnectTimer);
      if (socket) socket.close();
    };
  }, [symbol, interval]);

  const direction = signal?.signal?.toLowerCase() || "hold";
  const wins = performance?.wins ?? 0;
  const losses = performance?.losses ?? 0;

  return (
    <main className="dashboard">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Signal Desk home">
          <span className="brand-mark" aria-hidden="true">◈</span>
          <span>signal<span className="brand-light">desk</span></span>
        </a>
        <div className="topbar-right">
          <span className="mode-chip"><span className="mode-dot" /> PAPER MODE</span>
          <span className={`connection connection-${connection}`}>
            <span className="connection-dot" />
            {connection === "live" ? "Live feed" : connection}
          </span>
        </div>
      </header>

      <section className="intro">
        <div>
          <p className="eyebrow">MARKET OVERVIEW <span className="eyebrow-rule" /></p>
          <h1>Signal desk</h1>
          <p className="intro-copy">Clear, data-driven market context. No trades are ever placed.</p>
        </div>
        <div className="filters">
          <label>
            <span>MARKET</span>
            <select aria-label="Symbol" value={symbol} onChange={(event) => setSymbol(event.target.value)}>
              {SYMBOLS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>
            <span>TIMEFRAME</span>
            <select aria-label="Timeframe" value={interval} onChange={(event) => setInterval(event.target.value)}>
              {INTERVALS.map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
        </div>
      </section>

      {error && <div className="error-banner" role="alert">{error}. Retrying automatically.</div>}

      <section className="signal-grid" aria-label="Live market signal">
        <article className={`signal-card card signal-${direction}`}>
          <div className="card-topline">
            <span className="card-label">CURRENT SIGNAL</span>
            <span className="live-indicator"><span /> LIVE</span>
          </div>
          <h2>{symbol} <span>· {interval}</span></h2>
          <div className="signal-main">
            <div className="signal-badge" aria-label={`${signal?.signal || "HOLD"} signal`}>
              <span className="signal-icon" aria-hidden="true">{direction === "buy" ? "↗" : direction === "sell" ? "↘" : "↔"}</span>
              {signal?.signal || "HOLD"}
            </div>
            <div className="confidence">
              <div className="confidence-heading"><span>CONFIDENCE</span><strong>{signal ? `${signal.confidence}%` : "—"}</strong></div>
              <div className="confidence-track"><span style={{ width: `${signal?.confidence || 0}%` }} /></div>
              <p>Based on technical indicators</p>
            </div>
          </div>
          <div className="entry-price">
            <span>REFERENCE PRICE</span>
            <strong>${formatPrice(signal?.entry_price)}</strong>
          </div>
        </article>

        <article className="chart-card card">
          <div className="card-heading">
            <div><span className="card-label">PRICE ACTION</span><h2>{symbol}</h2></div>
            <span className="chart-range">{signal?.candles?.length ? `${signal.candles.length} candles` : "Loading"}</span>
          </div>
          <PriceChart candles={signal?.candles} symbol={symbol} />
          <div className="chart-labels"><span>Older</span><span>Latest</span></div>
        </article>
      </section>

      <section className="section">
        <div className="section-heading"><div><p className="eyebrow">TRADE PLANNING</p><h2>Risk levels</h2></div><span className="section-note">Indicative · ATR-based</span></div>
        <div className="metrics-grid">
          <Metric label="ENTRY PRICE" value={formatPrice(signal?.entry_price)} prefix="$" tone="neutral" />
          <Metric label="STOP LOSS" value={formatPrice(signal?.stop_loss)} prefix={signal?.stop_loss == null ? "" : "$"} tone="down" />
          <Metric label="TAKE PROFIT" value={formatPrice(signal?.take_profit)} prefix={signal?.take_profit == null ? "" : "$"} tone="up" />
          <Metric label="AVERAGE TRUE RANGE" value={formatPrice(signal?.atr)} prefix="$" tone="neutral" />
        </div>
      </section>

      <section className="section performance-section">
        <div className="section-heading"><div><p className="eyebrow">HISTORICAL CONTEXT</p><h2>Paper performance</h2></div><span className="section-note">Next-candle direction backtest · no executions</span></div>
        <div className="performance-card card">
          <div className="win-rate"><span>WIN RATE</span><strong>{performance ? formatPercent(performance.win_rate) : "—"}</strong><small>{performance?.sample_size ?? 0} directional signals evaluated</small></div>
          <div className="outcome-stat wins"><span>WINS</span><strong>{wins}</strong></div>
          <div className="outcome-stat losses"><span>LOSSES</span><strong>{losses}</strong></div>
          <div className="performance-disclaimer">Paper backtest results are historical context only and do not predict future performance.</div>
        </div>
      </section>

      <footer><span>Signal Desk <span className="footer-separator">/</span> Public market data</span><span>For information only · Not financial advice</span></footer>
    </main>
  );
}

function Metric({ label, value, prefix, tone }) {
  return (
    <article className="metric-card card">
      <span className="card-label">{label}</span>
      <strong className={`metric-value metric-${tone}`}>{prefix}{value}</strong>
      <span className="metric-subtitle">{tone === "down" ? "Risk boundary" : tone === "up" ? "Reward target" : "Market-derived"}</span>
    </article>
  );
}

export default App;
