# ZTM v0.1.5-alpha6 Mining integration — engineering status

**Status: alpha6 package and pinned one-command installer published on the renamed GitHub repository; real 24-hour live validation pending.**

Alpha5 remains available for rollback. The new [`install-ztm-v6.sh`](../install-ztm-v6.sh) and [one-command instructions](ZTM_ONE_COMMAND.md) install alpha6, and the package is stored as SHA-256-verified GitHub fragments.

## Surgical changes implemented in the published alpha6 engineering build

- Original alpha5 benchmark GUI, wallet backend, official I2PS logo and source mining engine behavior retained. An added third **Mining** navigation tab does not redesign the benchmark layout.
- Before a qualifying **24-hour uninterrupted, pool-verified** RandomX benchmark, both **Wallet** and **Mining** navigation entries are greyed out. Clicking them displays the 24-hour requirement rather than opening a tab.
- Backend requires one qualifying `~/ZTM-Results/run_*.json` record for a 24-hour session with accepted shares, performance samples, and a selected optimizer profile. Incomplete/short reports do not unlock personal mining.
- After unlock: user enters existing PUBLIC Monero receiving address or creates a wallet with the official local Monero GUI; both lead to **Mining**. ZTM never handles recovery seeds or private keys.
- Mining connects to HashVault with the user's address and the selected qualified thread profile. Personal mining must be initiated explicitly; Start/Stop controls and live speed/share readings are shown.
- XMRig keeps its own `donate-level: 1` developer contribution. A separate schedule changes XMRig's watched configuration to the I2PS public receiving address for **60 seconds per 6,000 seconds** of mining time. The two schedules are independent; actual contribution shares/rewards may vary.
- Terms and the 1% + 1% policy are in a README and one Mining Terms & Conditions acknowledgment, not recurring in-app warnings.
- No changes to existing benchmark payout routing or benchmark two-checkbox authorization.

## Local validation

19 automated tests passed, including the existing alpha5 optimizer tests and synthetic 24h gate, mining donation schedule, unchanged assets and headless GUI navigation. Debian metadata and archive inventory were inspected. The expected local alpha6 package metadata is `ztm-zero-to-monero`, Debian version `0.1.5~alpha6mining1`, architecture `amd64`.

**Not validated:** a full real 24-hour benchmark unlocking tabs, live personal mining/donation payouts, or full process shutdown on actual Ubuntu hardware. Results stored locally are evidence of completion but not cryptographically signed.

**Publication verification:** Seven GitHub-hosted package fragments were retrieved from pinned commit `6d0568aa93631199338cf016b5dc8473b2ab7673` and exactly matched the locally tested 30,380-byte Debian package (SHA-256 `86262258c70707ad15a4154935175f8394bc3b5d98c4f305b692e90fac4109cd`). The pinned new GitHub installer is in `install-ztm-v6.sh`. This does not establish that a real Ubuntu installation or mining-cycle test passed.
