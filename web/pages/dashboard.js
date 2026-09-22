import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const fallbackIngest = [{ time: '10:00', rate: 120 }, { time: '10:05', rate: 140 }, { time: '10:10', rate: 110 }]
const initialAccount = { mode: 'paper', cash_usdt: 100000, realized_pnl: 0, total_trades: 0, positions: [], risk: { halted: false, daily_loss_used_usdt: 0, max_daily_loss_usdt: 3000, open_positions: 0, max_open_positions: 3 } }

export default function Dashboard() {
  const [data, setData] = useState(fallbackIngest); const [loading, setLoading] = useState(true)
  const [symbols, setSymbols] = useState([]); const [selected, setSelected] = useState('BTCUSDT')
  const [account, setAccount] = useState(initialAccount); const [history, setHistory] = useState([])
  const [form, setForm] = useState({ symbol: 'BTCUSDT', side: 'buy', size: '0.01', price: '50000' }); const [message, setMessage] = useState('')

  const refreshPaper = async () => {
    const [accountRes, historyRes] = await Promise.all([fetch('/api/paper?account=1'), fetch('/api/paper?history=1')])
    if (accountRes.ok) setAccount(await accountRes.json())
    if (historyRes.ok) setHistory((await historyRes.json()).orders || [])
  }
  useEffect(() => { fetch('/api/markets').then(r => r.json()).then(j => { if (j.symbols?.length) { setSymbols(j.symbols); setSelected(j.symbols[0]); setForm(f => ({ ...f, symbol: j.symbols[0] })) } }).catch(() => {}) }, [])
  useEffect(() => { async function load() { try { const r = await fetch(`/api/metrics?symbol=${encodeURIComponent(selected)}`); const j = await r.json(); if (Array.isArray(j) && j.length) setData(j) } finally { setLoading(false) } } load(); const id = setInterval(load, 15000); return () => clearInterval(id) }, [selected])
  useEffect(() => { refreshPaper().catch(() => {}); const id = setInterval(() => refreshPaper().catch(() => {}), 15000); return () => clearInterval(id) }, [])

  const submit = async (e) => { e.preventDefault(); setMessage(''); const r = await fetch('/api/paper', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, size: Number(form.size), price: Number(form.price) }) }); const j = await r.json(); setMessage(r.ok ? `Simulated ${j.side.toUpperCase()} ${j.size} ${j.symbol} @ ${j.price}` : j.error); if (r.ok) refreshPaper() }
  const reset = async () => { if (!window.confirm('Reset the paper account and delete its local history?')) return; const r = await fetch('/api/paper?reset=1', { method: 'POST' }); if (r.ok) { setMessage('Paper account reset'); refreshPaper() } }

  return <div className="min-h-screen bg-gray-50 text-gray-900"><header className="max-w-6xl mx-auto p-6 flex justify-between"><h1 className="text-2xl font-semibold">Operations Dashboard</h1><select className="border rounded px-2 py-1" value={selected} onChange={e => setSelected(e.target.value)}>{(symbols.length ? symbols : ['BTCUSDT']).map(s => <option key={s}>{s}</option>)}</select></header>
    <main className="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <section className="bg-white rounded shadow p-4"><h3 className="font-medium mb-2">Market metrics — {selected}</h3><div style={{ width: '100%', height: 200 }}><ResponsiveContainer><LineChart data={data}><XAxis dataKey="time" /><YAxis /><Tooltip /><Line type="monotone" dataKey="rate" stroke="#3b82f6" /></LineChart></ResponsiveContainer></div><small>{loading ? 'Loading...' : 'Updated'}</small></section>
      <section className="bg-white rounded shadow p-4"><h3 className="font-medium mb-2">Paper account</h3><p>Mode: <b className="text-amber-600">{account.mode}</b></p><p>Cash: <b>{Number(account.cash_usdt).toLocaleString()} USDT</b></p><p>Realized PnL: <b>{Number(account.realized_pnl).toFixed(2)} USDT</b></p><p>Trades: <b>{account.total_trades}</b> · Positions: <b>{account.positions.length}</b></p><p className={account.risk?.halted ? 'text-red-600 font-semibold' : 'text-green-600'}>{account.risk?.halted ? 'Risk halted' : 'Risk controls active'} — daily loss {account.risk?.daily_loss_used_usdt}/{account.risk?.max_daily_loss_usdt} USDT</p><button onClick={reset} className="mt-2 px-3 py-1 border rounded">Reset paper account</button></section>
      <section className="bg-white rounded shadow p-4 md:col-span-2"><h3 className="font-medium mb-2">Paper order simulator</h3><form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">{[['symbol','Symbol'],['side','Side'],['size','Size'],['price','Price']].map(([key,label]) => <div key={key}><label className="block text-xs">{label}</label>{key === 'symbol' ? <select className="border rounded px-2 py-1 w-full" value={form.symbol} onChange={e => setForm({ ...form, symbol: e.target.value })}>{(symbols.length ? symbols : ['BTCUSDT']).map(s => <option key={s}>{s}</option>)}</select> : key === 'side' ? <select className="border rounded px-2 py-1 w-full" value={form.side} onChange={e => setForm({ ...form, side: e.target.value })}><option value="buy">Buy</option><option value="sell">Sell</option></select> : <input className="border rounded px-2 py-1 w-full" type="number" min="0.01" step="0.01" value={form[key]} onChange={e => setForm({ ...form, [key]: e.target.value })} />}</div>)}<button className="px-3 py-1 bg-blue-600 text-white rounded">Simulate order</button></form>{message && <p className="mt-3 text-sm">{message}</p>}</section>
      <section className="bg-white rounded shadow p-4 md:col-span-2"><h3 className="font-medium mb-2">Trade journal</h3>{history.length ? <div className="overflow-auto"><table className="w-full text-sm"><thead><tr><th className="text-left">Time</th><th className="text-left">Symbol</th><th className="text-left">Side</th><th className="text-left">Size</th><th className="text-left">Price</th></tr></thead><tbody>{history.slice().reverse().map((o, i) => <tr key={`${o.ts}-${i}`}><td>{o.ts}</td><td>{o.symbol}</td><td>{o.side}</td><td>{o.size}</td><td>{o.price}</td></tr>)}</tbody></table></div> : <p className="text-sm text-gray-500">No paper trades yet.</p>}</section>
    </main></div>
}
