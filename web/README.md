# Web README additions

## Running with the ingest mock service (local)

To see the dashboard fetch live mock data, run the ingest mock service and the Next.js app in parallel.

1. Start ingest mock (from repo root):

   cd services/ingest
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m services.ingest.main

   The mock service will run on http://localhost:8081

2. Start web app:

   cd web
   npm ci
   npm run dev

3. Open http://localhost:3000/dashboard — the page will proxy metrics through /api/metrics to the ingest mock.

Notes:
- The Next.js API route `web/pages/api/metrics.js` proxies to `INGEST_URL` (defaults to http://localhost:8081/mock_stream). To change, set `INGEST_URL` environment variable when running Next.js.
- For production, replace the proxy with a secure metrics endpoint (Prometheus/Grafana) and add authentication.
