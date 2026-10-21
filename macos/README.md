# ZTM — Native macOS Preview P1

**Development branch:** `feature/macos-native`

The Ubuntu release `ZTM-SRP1V1` remains the approved Linux stable release.
This macOS port is independently built and must complete real-hardware validation before a macOS stable designation.

## Targets

- Apple Silicon macOS: native `arm64`, without Rosetta
- Intel macOS: native `x86_64`
- Official XMRig 6.26.0, using architecture-specific SHA-256-verified release binaries
- No Ubuntu APT, pkexec, MSR driver, kernel modifications, sudo authorization, or Linux executables

## Preserved workflow

1. User opens the ZTM GUI.
2. User authorizes downloading the official native XMRig binary, verified against the upstream SHA-256.
3. No mining starts during installation/preparation.
4. User reads and checks both approved benchmark authorizations.
5. User starts the fixed **24-hour online RandomX** benchmark, with **CPU Threads: Auto**.
6. The optimizer tests up to five alternative profiles plus the baseline and runs the selected tested configuration for the remainder of the 24-hour test.
7. A full, uninterrupted, pool-verified result unlocks Wallet and personal mining.
8. Personal mining requires a **public Monero receiving address only**, retains upstream XMRig and I2PS developer contributions, and provides a Stop control.

The benchmark reward destination is the configured development wallet until a qualifying test has completed; after qualification, personal mining uses the user's public address.

## Winning Configuration report

After the benchmark finishes, ZTM displays **WINNING CONFIGURATION** and writes both a JSON result and a separate text file in `~/ZTM-Results/`.

The winner report includes:
- Mac CPU model, architecture, logical CPU count and XMRig version
- Selected active CPU-thread count and automatic dataset initialization
- Search-window median, mean, minimum, maximum, optimizer score and stability coefficient
- Sustained winner measurements for the remainder of the 24-hour benchmark
- Accepted/rejected shares and elapsed time
- Ranked tested configurations with their exact measured scores
- The profile producing the **highest instantaneous hashrate**, clearly distinguished from the strongest sustained configuration
- Whether the full 24-hour benchmark qualified

If a benchmark is interrupted, any provisional profile remains explicitly **incomplete**, not a qualified result.

## Process safety

The native macOS guardian runs XMRig as the current logged-in user; it does not elevate privileges.
The benchmark/mining controller keeps a pipe open to the guardian. The worker also periodically verifies the GUI process ID and its macOS process start identity.
When the user stops work, the GUI exits unexpectedly, or the benchmark controller terminates, the guardian receives EOF, signals the XMRig process group, and waits for shutdown.
A separate real-hardware validation of stop/kill behavior is required before stable publication.

## GUI

The interface preserves the existing dark I2PS engineering palette, live terminal, benchmark, Wallet and Mining tabs.
The preview is identified as **macOS Intel / Apple Silicon · Preview P1**.
The Linux SRP1V1 GUI and package have not been changed.

## Packaging and verification

The GitHub Actions workflow `.github/workflows/build-macos-preview.yml` runs separately on native Apple Silicon and Intel macOS runners.
It performs Python compilation, fixed-duration checks, native XMRig checksum verification and a version test, then builds a `ZTM.app` bundle and an unnotarized testing `.dmg`.

**Gatekeeper:** These preview applications are not Developer ID-signed or notarized. On macOS, opening them may require the user to approve the specific application under System Settings > Privacy & Security. They should not be distributed as notarized stable releases.

**Caution:** A MacBook should remain on power, awake and adequately cooled for a 24-hour benchmark. Do not run simultaneous independent miner processes on the same machine.

## License

I2PS-owned ZTM components retain PolyForm Strict 1.0.0 licensing, and official XMRig is a separate GPLv3 project. A macOS preview does not broaden user redistribution, modification or commercial-use permissions.
