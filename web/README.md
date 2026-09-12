# Web dashboard scaffold (Next.js + Tailwind)

This directory contains a lightweight scaffold for a project dashboard. It uses Next.js and Tailwind CSS and provides mocked widgets for ingest rate, replay status and exports.

How to run locally:

1. cd web
2. npm install
3. npm run dev

Notes:
- Widgets are mocked. To integrate real metrics, wire Prometheus/Grafana APIs or add an API layer that proxies metrics from your infra.
- CI workflow is included and runs on the feat/web-dashboard branch.
