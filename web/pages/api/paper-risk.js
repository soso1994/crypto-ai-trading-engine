export default async function handler(req, res) {
  const PAPER_URL = process.env.PAPER_URL || 'http://localhost:8090/paper'
  if (req.method !== 'GET') return res.status(405).json({ error: 'method not allowed' })
  try {
    const r = await fetch(`${PAPER_URL}/risk`)
    return res.status(r.ok ? 200 : 502).json(await r.json())
  } catch (err) {
    return res.status(200).json({ halted: false, max_order_notional_usdt: 1000, max_open_positions: 3, max_daily_loss_usdt: 3000, daily_loss_used_usdt: 0, open_positions: 0 })
  }
}
