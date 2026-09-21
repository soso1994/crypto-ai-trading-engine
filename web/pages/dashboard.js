import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const fallbackIngest = [
  { time: '10:00', rate: 120 },
  { time: '10:05', rate: 140 },
  { time: '10:10', rate: 110 },
  { time: '10:15', rate: 160 },
  { time: '10:20', rate: 135 },
]

export default function Dashboard() {
  const [data, setData] = useState(fallbackIngest)
  const [loading, setLoading] = useState(true)
  const [symbols, setSymbols] = useState([])
  const [selected, setSelected] = useState('BTCUSDT')
  const [account, setAccount] = useState({ mode: 'paper', cash_usdt: 100000, realized_pnl: 0, total_trades: 0, positions: [] })
  const [form, setForm] = useState({ symbol: 'BTCUSDT', side: 'buy', size: '0.1', price: '50000' })
  const [message, setMessage] = useState('')

  useEffect(() => {
    let mounted = true
    async function loadSymbols() {
      try {
        const res = await fetch('/api/markets')
        const json = await res.json()
        if (mounted && Array.isArray(json.symbols) && json.symbols.length) {
          setSymbols(json.symbols)
          setSelected(prev => json.symbols.includes(prev) ? prev : json.symbols[0])
        }
      } catch (e) {
        console.warn('failed to load symbols', e)
      }
    }
    loadSymbols()
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    let mounted = true
    async function fetchMetrics() {
      try {
        const res = await fetch(`/api/metrics?symbol=${encodeURIComponent(selected)}`)
        if (!res.ok) throw new Error('metrics fetch failed')
        const json = await res.json()
        if (mounted && Array.isArray(json) && json.length) setData(json)
      } catch (e) {
        console.warn('metrics fetch failed, using fallback', e)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    if (selected) {
      fetchMetrics()
      const interval = setInterval(fetchMetrics, 15 * 1000)
      return () => clearInterval(interval)
    }
    return () => { mounted = false }
  }, [selected])

  useEffect(() => {
    async function fetchAccount() {
      try {
        const res = await fetch('/api/paper?account=1')
        const json = await res.json()
        setAccount(json)
      } catch (e) {
        console.warn('paper account fetch failed', e)
      }
    }
    fetchAccount()
    const interval = setInterval(fetchAccount, 15 * 1000)
    return () => clearInterval(interval)
  }, [])

  const submitPaperOrder = async (e) => {
    e.preventDefault()
    setMessage('')
    try {
      const res = await fetch('/api/paper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: form.symbol,
          side: form.side,
          size: Number(form.size),
          price: Number(form.price),
        })
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error || 'order failed')
      setMessage(`Paper order simulated: ${json.side.toUpperCase()} ${json.size} ${json.symbol} @ ${json.price}`)
      const accountRes = await fetch('/api/paper?account=1')
      const accountJson = await accountRes.json()
      setAccount(accountJson)
    } catch (err) {
      setMessage(err.message)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="max-w-6xl mx-auto p-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Operations Dashboard</h1>
        <div>
          <label className="text-sm text-gray-600 mr-2">Symbol</label>
          <select className="border rounded px-2 py-1" value={selected} onChange={(e) => setSelected(e.target.value)}>
            {symbols.length ? symbols.map(s => <option key={s} value={s}>{s}</option>) : <option>BTCUSDT</option>}
          </select>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Ingest rate (msgs/s) — {selected}</h3>
          <div style={{ width: '100%', height: 200 }}>
            <ResponsiveContainer>
              <LineChart data={data}>
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="rate" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-xs text-gray-500">{loading ? 'Loading metrics...' : 'Metrics updated'}</div>
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Paper account</h3>
          <div className="text-sm text-gray-600">Mode: <span className="font-medium text-amber-600">{account.mode}</span></div>
          <div className="mt-2 text-sm text-gray-600">Cash: <span className="font-medium">{account.cash_usdt.toLocaleString()} USDT</span></div>
          <div className="mt-2 text-sm text-gray-600">Realized PnL: <span className="font-medium">{account.realized_pnl}</span></div>
          <div className="mt-2 text-sm text-gray-600">Trades: <span className="font-medium">{account.total_trades}</span></div>
          <div className="mt-2 text-sm text-gray-600">Open positions: <span className="font-medium">{account.positions.length}</span></div>
        </section>

        <section className="bg-white rounded shadow p-4 md:col-span-2">
          <h3 className="text-sm font-medium mb-2">Paper order simulator</h3>
          <form onSubmit={submitPaperOrder} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
            <div>
              <label className="block text-xs text-gray-600">Symbol</label>
              <select value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value })} className="border rounded px-2 py-1 w-full">
                {symbols.length ? symbols.map(s => <option key={s} value={s}>{s}</option>) : <option>BTCUSDT</option>}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-600">Side</label>
              <select value={form.side} onChange={(e) => setForm({ ...form, side: e.target.value })} className="border rounded px-2 py-1 w-full">
                <option value="buy">Buy</option>
                <option value="sell">Sell</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-600">Size</label>
              <input type="number" min="0.01" step="0.01" value={form.size} onChange={(e) => setForm({ ...form, size: e.target.value })} className="border rounded px-2 py-1 w-full" />
            </div>
            <div>
              <label className="block text-xs text-gray-600">Price</label>
              <input type="number" min="1" step="0.01" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} className="border rounded px-2 py-1 w-full" />
            </div>
            <div>
              <button type="submit" className="px-3 py-1 bg-blue-600 text-white rounded w-full">Simulate order</button>
            </div>
          </form>
          {message && <div className="mt-3 text-sm text-green-700">{message}</div>}
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Last replay — {selected}</h3>
          <div className="text-sm text-gray-600">Status: <span className="font-medium text-green-600">Success</span></div>
          <div className="mt-3 text-xs text-gray-500">Duration: 00:04:12</div>
          <div className="mt-4">
            <button className="px-3 py-1 bg-blue-600 text-white rounded">Run replay</button>
          </div>
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Alerts</h3>
          <ul className="text-sm text-gray-600">
            <li className="mb-2">No active alerts</li>
          </ul>
        </section>
      </main>
    </div>
  )
}
