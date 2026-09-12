<!-- Pull Request template for feature branches -->

## Summary
<!-- Short description of the change -->


## What it does
- 


## Acceptance criteria
- [ ] CI builds on feat/web-dashboard
- [ ] Local dev instructions validated
- [ ] Reviewers: @soso1994


## How to test locally
1. git fetch && git checkout feat/web-dashboard
2. cd web && npm ci && npm run dev
3. Open http://localhost:3000 and visit /dashboard


## Notes
- For Vercel automatic deploys set `VERCEL_TOKEN` in repository secrets.
- To connect metrics provide PROMETHEUS_URL or GRAFANA_URL and API key if private.
