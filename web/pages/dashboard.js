import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const mockIngest = [
  { time: '10:00', rate: 120 },
  { time: '10:05', rate: 140 },
  { time: '10:10', rate: 110 },
  { time: '10:15', rate: 160 },
  { time: '10:20', rate: 135 },
]

export default function Dashboard() {
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
              <LineChart data={mockIngest}>
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="rate" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">Last replay</h3>
          <div className="text-sm text-gray-600">Status: <span className="font-medium text-green-600">Success</span></div>
          <div className="mt-3 text-xs text-gray-500">Duration: 00:04:12</div>
          <div className="mt-4">
            <button className="px-3 py-1 bg-blue-600 text-white rounded">Run replay</button>
          </div>
        </section>

        <section className="bg-white rounded shadow p-4">
          <h3 className="text-sm font-medium mb-2">S3 export</h3>
          <div className="text-sm text-gray-600">Last export: 2 minutes ago</div>
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
