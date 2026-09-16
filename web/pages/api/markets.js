// Serverless API to get available symbols from the ingest mock service.
// Proxies to INGEST_URL (defaults to http://localhost:8081/mock_stream) and extracts unique symbols.

export default async function handler(req, res) {
  const INGEST_URL = process.env.INGEST_URL || 'http://localhost:8081/mock_stream'
  try {
    const r = await fetch(INGEST_URL, { method: 'GET' })
    if (!r.ok) return res.status(502).json({ error: 'Upstream error' })
    const data = await r.json()
    const symbols = Array.isArray(data) ? Array.from(new Set(data.map(d => d.symbol).filter(Boolean))) : []
    return res.status(200).json({ symbols })
  } catch (err) {
    console.warn('markets proxy failed', err)
    return res.status(200).json({ symbols: ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'] })
  }
}
