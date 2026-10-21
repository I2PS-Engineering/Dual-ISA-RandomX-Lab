# ZTM worker intelligence — implementation branch

This work is NOT the published ZTM-SRP1V2 package. It is a staged
foundation for the next release, so existing 24-hour mining behavior
is not modified before regression testing.

## Approved identity

Canonical display name: `ZTM-SRP1V3-L/X64-A7K92` (example).
The final five characters are the stable **ZTM ID**.
Version changes upon upgrade, but the ZTM ID persists.
Supported OS markers: L Linux, M macOS.
Supported architecture markers: X64 and ARM64.

The canonical slash is not assumed valid in all pool-worker fields.
`mining_safe_worker_name` uses an underscore for pool integrations until
a real protocol compatibility test confirms the slash is accepted.

The worker ID is a human-readable label and MUST NOT be used as authentication.
The backend must verify uniqueness and provision a separate credential.
If two independent installations generate the same ZTM ID, the service
must require conflict resolution before accepting submissions.

## Collection

Local SQLite queue, opt-in uploads, HTTPS, idempotency headers and
PostgreSQL schema are provided as building blocks. Reporting consent
is independent from mining consent. No upload is enabled by default.

`intelligence/ztm_identity.py` contains platform naming, local
identity and hardware inventory without serial numbers or MAC addresses.
`intelligence/ztm_reporting.py` contains a local queue and explicit
submission mechanism. `intelligence/schema.sql` is the starting DDL.

## Outstanding release blockers

1. Integrate identity with BOTH benchmark and personal-mining XMRig
   config generation, replacing the hardcoded `ZTM-RX1V2-L`.
2. Detect/respect provider naming character restrictions and test pool connection.
3. Expose automatic display scaling, magnifying-glass zoom and
   real, asynchronous network/XMRig/HashVault pre-checks in Tkinter.
4. Add hardware/result capture for every optimizer profile and link
   completed winners to the local queue.
5. Deploy a properly authenticated server API, registration uniqueness,
   consent management, PostgreSQL and administrator analytics.
6. Test installation upgrades, cloned-machine identities, UI display
   geometries, successful and interrupted 24-hour runs, miner shutdown.
7. Build reproducible .deb, installer and README-only ZIP; publish release
   only when validated. Do not retag or overwrite SRP1V2.

The six tables are an initial schema requiring migrations, endpoint
authorization, administrative governance and acceptance tests before production.
