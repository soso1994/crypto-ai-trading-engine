import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useEffect, useState } from 'react'

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
  const [lastExport, setLastExport] = useState('2 minutes ago')
  const [replayStatus, setReplayStatus] = useState({ status: 'Success', duration: '00:04:12' })

  useEffect(() => {
    let mounted = true
    async function fetchMetrics() {
      try {
        const res = await fetch('/api/metrics')
        if (!res.ok) throw new Error('metrics fetch failed')
        const json = await res.json()
        // Expecting array of { time, rate }
        if (mounted && Array.isArray(json) && json.length) {
          setData(json)
        }
      } catch (e) {
        // keep fallback
        console.warn('metrics fetch failed, using fallback', e)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 15 * 1000) // refresh every 15s
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="max-w-6xl mx-auto p-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Operations Dashboard</h1>
      </header>
      <main className="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Ingest rate (msgs/s)</h3>
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
          <h3 className="text-sm font-medium mb-2">Last replay</h3>
          <div className="text-sm text-gray-600">Status: <span className={`font-medium ${replayStatus.status === 'Success' ? 'text-green-600' : 'text-red-600'}`}>{replayStatus.status}</span></div>
          <div className="mt-3 text-xs text-gray-500">Duration: {replayStatus.duration}</div>
          <div className="mt-4">
            <button className="px-3 py-1 bg-blue-600 text-white rounded">Run replay</button>
          </div>
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">S3 export</h3>
          <div className="text-sm text-gray-600">Last export: {lastExport}</div>
          <div className="mt-3 text-xs text-gray-500">Bucket: mock-bucket</div>
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
