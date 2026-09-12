import Link from 'next/link'
export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="max-w-6xl mx-auto p-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Crypto AI Trading Engine — Dashboard</h1>
        <nav>
          <Link href="/dashboard"><a className="text-blue-600 hover:underline">Open Dashboard</a></Link>
        </nav>
      </header>
      <main className="max-w-4xl mx-auto p-6">
        <section className="bg-white rounded shadow p-6">
          <h2 className="text-xl font-medium mb-2">Overview</h2>
          <p className="text-sm text-gray-600">This is a lightweight scaffold for the operations dashboard. Widgets are mocked locally. Connect Prometheus/Grafana or the real API endpoints later.</p>
        </section>
      </main>
    </div>
  )
}
