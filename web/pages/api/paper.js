export default async function handler(req, res) {
  const PAPER_URL = process.env.PAPER_URL || 'http://localhost:8090/paper'

  if (req.method === 'GET' && req.query.account === '1') {
    try {
      const r = await fetch(`${PAPER_URL}/account`)
      if (!r.ok) return res.status(502).json({ error: 'Upstream error' })
      const data = await r.json()
      return res.status(200).json(data)
    } catch (err) {
      return res.status(200).json({
        mode: 'paper',
        cash_usdt: 100000,
        realized_pnl: 0,
        total_trades: 0,
        positions: [],
      })
    }
  }

  if (req.method === 'POST' && req.body) {
    try {
      const payload = req.body
      const r = await fetch(`${PAPER_URL}/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await r.json()
      if (!r.ok) return res.status(r.status).json(data)
      return res.status(200).json(data)
    } catch (err) {
      return res.status(500).json({ error: 'paper trading is unavailable' })
    }
  }

  return res.status(405).json({ error: 'method not allowed' })
}
