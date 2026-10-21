# Railway deployment — ZTM Intelligence API

**Not deployed by committing this folder.**

1. Provision Railway PostgreSQL, with a private `DATABASE_URL` attached to the API service.
2. Apply `intelligence/schema.sql` then `deployment/server.sql` to PostgreSQL.
3. Create a Railway service from this repository's development branch.
4. Set Dockerfile path to `deployment/Dockerfile`.
5. Set `ZTM_ADMIN_BOOTSTRAP_TOKEN` to a long random secret (never commit it).
6. Expose only the API HTTPS domain; PostgreSQL must not be publicly accessible.
7. Verify `GET /health` returns `{"status":"ok","database":"connected"}`.
8. Provision worker credentials through the admin registration endpoint, then
   submit consented reports using per-worker bearer token and Idempotency-Key.
9. Test collision rejection, invalid tokens, duplicate submission and DB outage.
10. Before real users, add administrator SSO, token rotation, stricter JSON
    validation, rate limiting, retention policy and dashboard integration.

Deployment does not automatically collect worker reports: production ZTM
client integration and user opt-in are still required. Uploaded results are
UNVERIFIED observations until server-side validation.
