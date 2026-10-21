# ZTM Intelligence: Neon Free pilot

Deployment provider: **Neon**. Railway is parked.

## Live database infrastructure

- Neon project: `green-haze-50764096`
- Name: `i2ps-ztm-intelligence-eu`
- Branch: `br-solitary-snow-baqev50h` (production)
- Database: `ztm_intelligence`
- Region: Frankfurt / `aws-eu-central-1`
- 8 tables and 3 analytics views created and queried successfully on 2026-10-21.

## API/dashboard

`neon/index.mjs` is a dependency-free Neon Function implementation of:
`/health`, `/dashboard`, `/v1/admin/register`,
`/v1/admin/stats`, `/v1/admin/workers`, and `/v1/results`.

Admin actions require the `ZTM_ADMIN_BOOTSTRAP_TOKEN` secret in the
Neon Function environment. Worker submissions require a separate
registered bearer credential, and a valid 5-character ZTM ID. Results
are stored as UNVERIFIED until assessed independently.

**Not live:** The hosted Function deployment was blocked at the tool
invocation. No public function URL has been verified. GitHub Actions
passes syntax checks; this does not establish live database connectivity.

The function uses Neon's documented SQL-over-HTTPS proxy; test on the
actual Neon runtime before relying on it for production ingestion.
The account credential and Postgres connection string must never be
committed to the repository.

## Future blockers

- Deploy Function, verify `/health` database connectivity and secret management.
- Test auth denial, admin registration, credential conflict, accepted and
  duplicate event ingestion, and unauthorized access.
- Integrate identity/reporting and consent into the ZTM desktop GUI.
- Validate display scaling, network pre-check UI and miner shutdown.
- Implement more comprehensive collection privacy, rate limiting,
  retention and administrator login (SSO rather than bootstrap token).
- Complete controlled 24-hour RandomX pilot and compare profile statistics.

An earlier Neon project in `aws-us-west-2` exists but is not the
intended Functions-enabled deployment; do not use it for the ZTM API.
