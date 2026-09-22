export default async function handler(req, res) {
  const PAPER_URL = process.env.PAPER_URL || 'http://localhost:8090/paper'

  if (req.method === 'GET' && req.query.account === '1') {
    try {
      const r = await fetch(`${PAPER_URL}/account`)
      if (!r.ok) return res.status(502).json({ error: 'Upstream error' })
      return res.status(200).json(await r.json())
    } catch (err) {
      return res.status(200).json({ mode: 'paper', cash_usdt: 100000, realized_pnl: 0, total_trades: 0, positions: [] })
    }
  }

  if (req.method === 'GET' && req.query.history === '1') {
    try {
      const r = await fetch(`${PAPER_URL}/history`)
      if (!r.ok) return res.status(502).json({ error: 'Upstream error' })
      return res.status(200).json(await r.json())
    } catch (err) {
      return res.status(200).json({ mode: 'paper', orders: [] })
    }
  }

  if (req.method === 'POST' && req.query.reset === '1') {
    try {
      const r = await fetch(`${PAPER_URL}/reset`, { method: 'POST' })
      const data = await r.json()
      return res.status(r.ok ? 200 : r.status).json(data)
    } catch (err) {
      return res.status(503).json({ error: 'paper trading is unavailable' })
    }
  }

  if (req.method === 'POST' && req.body) {
    try {
      const r = await fetch(`${PAPER_URL}/order`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req.body),
      })
      const data = await r.json()
      return res.status(r.ok ? 200 : r.status).json(data)
    } catch (err) {
      return res.status(500).json({ error: 'paper trading is unavailable' })
    }
  }

  return res.status(405).json({ error: 'method not allowed' })
}
