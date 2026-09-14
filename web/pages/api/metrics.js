export default async function handler(req, res) {
  // Proxy to local ingest mock service. In production, replace with Prometheus/Grafana proxy.
  const INGEST_URL = process.env.INGEST_URL || 'http://localhost:8081/mock_stream'
  try {
    const r = await fetch(INGEST_URL, { method: 'GET', timeout: 3000 })
    if (!r.ok) {
      return res.status(502).json({ error: 'Upstream error' })
    }
    const data = await r.json()
    // Transform into { time, rate } series for the chart if needed.
    // If upstream returns ticks, convert to simple time/rate mock.
    if (Array.isArray(data)) {
      const now = new Date()
      const series = data.map((d, idx) => ({ time: new Date(now.getTime() - (data.length - idx) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), rate: typeof d.rate === 'number' ? d.rate : Math.round((d.price || 0) % 200 + 80) }))
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
