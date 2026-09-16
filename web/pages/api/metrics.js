export default async function handler(req, res) {
  // Proxy to local ingest mock service. Filter by ?symbol= if provided.
  const INGEST_URL = process.env.INGEST_URL || 'http://localhost:8081/mock_stream'
  const symbol = req.query.symbol
  try {
    const r = await fetch(INGEST_URL, { method: 'GET' })
    if (!r.ok) {
      return res.status(502).json({ error: 'Upstream error' })
    }
    const data = await r.json()
    if (Array.isArray(data)) {
      const now = new Date()
      // If upstream returned objects with symbol/price, filter by requested symbol
      let filtered = data
      if (symbol) filtered = data.filter(d => String(d.symbol) === String(symbol))
      const series = filtered.map((d, idx) => ({ time: new Date(now.getTime() - (filtered.length - idx) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), rate: typeof d.price === 'number' ? Math.round(d.price % 200 + 80) : Math.round((d.price || 0) % 200 + 80) }))
      return res.status(200).json(series)
    }
    return res.status(200).json(data)
  } catch (err) {
    console.warn('metrics proxy failed', err)
    // Fallback series
    return res.status(200).json([
      { time: '10:00', rate: 120 },
      { time: '10:05', rate: 140 },
      { time: '10:10', rate: 110 },
      { time: '10:15', rate: 160 },
      { time: '10:20', rate: 135 },
    ])
  }
}
