# ZTM 0.1.4-alpha5-optimizer

Surgical backend update over 0.1.3-alpha4-surgical. The visible GUI is unchanged.

## What changed

- **CPU Threads: Auto** now performs an internal RandomX thread-profile search instead of measuring only XMRig's first automatic profile.
- ZTM keeps one privileged XMRig process running and uses XMRig's watched configuration to switch active RandomX thread profiles without restarting the miner.
- The initial XMRig automatic profile is measured as the baseline.
- Alternate active-thread counts are tested within the selected benchmark duration.
- Each profile is scored from sustained median H/s, stability, and accepted/rejected share quality rather than peak H/s alone.
- The best measured profile is selected and used for the remainder of the benchmark.
- Accepted/rejected share totals continue across profile changes.
- The selected thread count and all tested-profile statistics are written to the JSON result.
- The benchmark still stops automatically at the selected duration.
- Closing ZTM still stops its XMRig child process through the existing GUI close/stop path.

## Search budget

- Under 5 minutes: connectivity/measurement only; no profile search.
- 5–15 minutes: up to 3 total profiles, 60 seconds each.
- 15–60 minutes: up to 5 total profiles, 90 seconds each.
- 60 minutes or more: up to 6 total profiles, 120 seconds each.

On a 4-logical-CPU machine with a 30-minute benchmark, ZTM can measure the XMRig Auto baseline plus the remaining sensible thread counts and then run the winner for the remaining time.

## Unchanged from alpha4

GUI source, Wallet source, I2PS logo, embedded pool/payout/TLS behavior, dedicated HashVault worker identity `ZTM-Zero-to-Monero`, MSR/huge-page preparation, both authorization checkboxes, and the visible Duration/CPU Threads controls are unchanged.

## Verification

Synthetic end-to-end optimizer testing passed: one simulated miner process hot-switched 2 → 1 → 3 → 4 threads, retained cumulative share accounting, selected the controlled 2-thread winner, continued on that winner, and stopped at the configured deadline.

The alpha4 and alpha5 GUI files have identical SHA-256:
`5a6468dce872ecf61242659849d90f7f602f7c1e84722584f9d42fb686565516`.

The alpha5 Debian package SHA-256 is:
`ef41146e5de18201bb5f0a92d2729006c9b00bdff9b851ce2fd5a66884c52daf`.

Real hardware validation of the profile-selection logic is still required; the current successful alpha4 live HashVault run does not by itself validate alpha5's optimizer.
