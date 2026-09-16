# Contributing

Thanks for contributing to the Crypto AI Trading Engine repository. This guide describes how to run the web dashboard locally, run tests, and open a PR for review.

Running locally
----------------
- Web (Next.js)
  1. cd web
  2. npm ci
  3. npm run dev
  4. Open http://localhost:3000/dashboard

- Ingest mock (Flask)
  1. cd services/ingest
  2. python -m venv .venv
  3. source .venv/bin/activate
  4. pip install -r requirements.txt
  5. python -m services.ingest.main
  6. Ingest mock will be available at http://localhost:8081/mock_stream

- Backtester tests
  1. cd tools/backtester
  2. python -m venv .venv
  3. source .venv/bin/activate
  4. pip install -r requirements.txt
  5. pytest -q

How to open a PR
----------------
1. Ensure your branch is pushed (feat/web-dashboard). The PR body template is available at `.github/prs/feat-web-dashboard-pr.md`.
2. Open the repository on GitHub and click "Compare & pull request" for the feat/web-dashboard branch, paste the PR title and body if necessary, assign reviewers and labels, then create the PR.

Coding standards
----------------
- JavaScript/React: follow ESLint rules included (`npm run lint`).
- Python: keep tests in `tools/backtester` and use pytest. Use type hints where helpful.

Secrets and deployment
----------------------
- For Vercel automated deploys set `VERCEL_TOKEN` in the repository secrets. The deploy workflow is present but will fail if the secret is missing.
- For metrics integration provide `INGEST_URL` (for local development this defaults to http://localhost:8081/mock_stream) or PROMETHEUS/GRAFANA endpoints for production.

If you need help, tag @soso1994 in a GitHub issue.
