# Architecture and design boundaries

## Components

**Target v0.4 architecture (not yet fully implemented)**

```text
I2PS local interface (official cyan I2PS branding)
    |
    +-- License and online benchmark authorization
    +-- Setup Assistant / verified XMRig installer
    +-- Online 24-hour session controller
    |      +-- CPU / architecture and thread-profile discovery
    |      +-- Separate verified XMRig subprocess
    |      +-- Live mining-pool connection
    |      +-- Time, share and hashrate telemetry
    |      +-- Stop, failure handling and result persistence
    |      +-- Initial rewards -> Dev Wallet
    |
    +-- Completed run report / tested profile ranking
    +-- Post-benchmark public wallet address education
    +-- Separate explicitly authorized personal mining
           +-- User wallet + defined built-in Dev Donate
```

## Platform compatibility

- x86-64 machines (Intel and AMD): primary initial validation targets on Ubuntu/Debian.
- ARM64/Apple Silicon: comparison target, requires supported OS-specific XMRig and verification.
- Different RandomX variants and workloads must not be pooled into one unqualified performance comparison.

## Security boundaries

- No password, mnemonic or private spend/view keys are ever required.
- Payout address is configured internally for the initial Dev Wallet session; the beneficiary must nonetheless be explicitly disclosed.
- The local web application must not expose process-control APIs to a public interface.
- Download official XMRig only with pinned integrity verification and maintain its separate license obligations.
- Automatic installation is distinct from authorization to mine; consent and explicit Start are mandatory.
- Prevent unintended persistence or automatic relaunch of mining when the user's Stop command is used.

## Current implementation gap

The available development backend is from **v0.3.1** and includes an offline benchmark plus an independent mining interface. The **v0.4 online-only continuous 24-hour benchmark**, profile controller and payout logic have not yet been implemented.
