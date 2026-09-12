# PR: feat(web-dashboard) — Operations Dashboard scaffold

Summary
-------
This PR adds a lightweight Next.js + Tailwind scaffold for an Operations Dashboard for the Crypto AI Trading Engine project. Widgets are mocked and include ingest rate, last replay status, S3 export status and alerts. A CI workflow is included to run lint and build on the feat/web-dashboard branch.

What this PR contains
---------------------
- New `web/` directory containing a Next.js app scaffold
  - pages: `/` (landing) and `/dashboard` (ops dashboard)
  - Tailwind CSS configuration and global styles
  - Recharts-based mocked chart for ingest rate
- CI workflow: `.github/workflows/ci.yml` for building and linting the web app on this branch
- README with run instructions

Acceptance criteria
-------------------
- [ ] `web` builds successfully in CI (GitHub Action on feat/web-dashboard)
- [ ] `npm run dev` runs locally and dashboard accessible at `http://localhost:3000`
- [ ] Dashboard pages render mocked widgets (ingest chart, replay status, S3 export, alerts)
- [ ] README includes local run instructions

Testing steps
-------------
1. Checkout branch: `git fetch && git checkout feat/web-dashboard`
2. Install dependencies: `cd web && npm ci`
3. Run locally: `npm run dev` and open `http://localhost:3000`
4. Verify the `/dashboard` page shows the mocked ingest rate chart and status panels
5. Confirm CI workflow runs on this branch and completes the `Build` job

Notes & next actions
--------------------
- The current widgets use mocked data. To connect real metrics, provide PROMETHEUS_URL or GRAFANA_URL (and API key if private) and I will update the API stubs to proxy real endpoints.
- For automated deployment to Vercel, add `VERCEL_TOKEN` as a GitHub Secret and I can add a deploy step.
- If you want me to open the Pull Request in the GitHub UI, tell me and I will prepare a PR body text for quick paste OR I can save this PR description as a file (already added) for you to use.

Reviewer checklist
------------------
- [ ] Review component structure and styles
- [ ] Confirm CI workflow location and behavior
- [ ] Confirm LICENSE / repo policies compliance for adding a web app directory

Path to PR description file
---------------------------
.github/prs/feat-web-dashboard-pr.md

If you want me to proceed and open the PR body text here for easy copy/paste into GitHub’s “Create pull request” UI, answer “open PR body” and I’ll paste the prepared PR body text.