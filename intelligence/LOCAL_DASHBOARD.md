# ZTM Intelligence — free local dashboard

This works on Linux and macOS using the Python standard library. It does
not require a cloud database, a paid service, a subscription, or a card.
It is a standalone administrator-side component on the development branch;
it is **not yet bundled inside the released SRP1V2 .deb**.

## Launch

From the cloned repository root:

```bash
python3 intelligence/local_admin.py --import /path/to/ztm/results --serve
```

Replace `/path/to/ztm/results` with the directory containing saved ZTM
`run_*.json` reports. The script prints a local access URL such as
`http://127.0.0.1:8765/#token=<random-token>`; open that on the same
machine. The token changes every launch. Never publish or forward it.

To view the previously imported data later:

```bash
python3 intelligence/local_admin.py --serve
```

The SQLite database is saved under
`~/.local/share/ztm/intelligence.db`. Imports are deduplicated by worker ID
and benchmark run ID. Old SRP1V2 reports with the shared rig name are marked
`LEGACY` and are **not** credited with unique per-installation identity.

## Available dashboard functions

- Number of imported benchmark runs, worker IDs, CPU models and claimed
  24-hour runs
- CPU model comparison by number of observations
- Searchable history with winning thread configuration, median/peak
  hashrate, accepted and rejected shares
- CSV export of filtered observations
- No third-party JavaScript dependencies, telemetry or cloud hosting

Reports are unverified user/worker submissions, even if a report claims a
qualifying run. Central I2PS validation is a separate future step.

## Isolation and security

- The HTTP service binds **only** to `127.0.0.1`.
- Dashboard data endpoint requires a fresh random bearer token.
- The access token remains in the browser fragment and is removed from
  browser history immediately by the dashboard.
- No remote administrative access is provided by this implementation.
- Back up `intelligence.db` yourself when preserving benchmark data.

## Future server migration

We can later run authenticated PostgreSQL remotely using the same report
structure when a truly free provider is connected. A local dashboard is
the starting point, not a substitute for authenticated cross-machine
registration and remote submission.

## Test

```bash
PYTHONPATH=intelligence python3 -m unittest discover -s tests -p 'test_ztm_*.py' -v
```
