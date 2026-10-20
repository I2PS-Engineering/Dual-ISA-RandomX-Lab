# ZTM v0.1.5-alpha6 Mining integration — engineering status

**Status: local Ubuntu .deb built and tested; NOT yet published as a GitHub one-command installation.**

Alpha5 remains the most recently published GitHub installer. Do **not** describe the existing `install-ztm-v5.sh` as installing alpha6.

## Surgical changes implemented in a local test build

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

**Publication gate:** GitHub installer and binary upload/verification remain pending. Preserve alpha5 as the default until verified.
