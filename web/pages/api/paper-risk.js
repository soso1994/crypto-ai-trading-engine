export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      const r = await fetch('http://localhost:8090/paper/risk')
      if (!r.ok) return res.status(502).json({ error: 'Upstream error' })
      const data = await r.json()
      return res.status(200).json(data)
    } catch (err) {
      return res.status(200).json({
        halted: false,
        max_order_notional_usdt: 1000,
        max_open_positions: 3,
        max_daily_loss_usdt: 3000,
        daily_loss_used_usdt: 0,
        open_positions: 0,
      })
    }
  }

  return res.status(405).json({ error: 'method not allowed' })
}
