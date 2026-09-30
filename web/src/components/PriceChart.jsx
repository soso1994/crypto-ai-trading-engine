export default function PriceChart({ candles = [], symbol = "BTCUSDT" }) {
  const points = candles.map((candle) => Number(candle.close)).filter(Number.isFinite);
  if (points.length < 2) {
    return <div className="chart-empty">Waiting for enough market data…</div>;
  }

  const low = Math.min(...points);
  const high = Math.max(...points);
  const range = high - low || 1;
  const coordinates = points.map((price, index) => {
    const x = 8 + (index / (points.length - 1)) * 984;
    const y = 12 + ((high - price) / range) * 176;
    return `${x},${y}`;
  });

  return (
    <svg
      className="price-chart"
      viewBox="0 0 1000 200"
      role="img"
      aria-label={`${symbol} price chart`}
      preserveAspectRatio="none"
    >
      {[48, 96, 144].map((y) => (
        <line key={y} x1="0" x2="1000" y1={y} y2={y} className="chart-grid" />
      ))}
      <polyline points={coordinates.join(" ")} className="chart-line" />
      <circle cx="992" cy={coordinates.at(-1).split(",")[1]} r="4" className="chart-dot" />
    </svg>
  );
}
