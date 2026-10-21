# ZTM-SRP1V1 architecture

## Stable workflow

```text
ZTM GUI
  |
  +-- Ubuntu preparation
  |     +-- one authorized privileged session
  |     +-- prerequisites
  |     +-- verified XMRig preparation
  |
  +-- 24-hour Benchmark
  |     +-- fixed duration: 86400 seconds
  |     +-- CPU Threads: Auto
  |     +-- real RandomX workload
  |     +-- live pool connection
  |     +-- tested thread-profile evaluation
  |     +-- hashrate and share telemetry
  |     +-- Stop / shutdown handling
  |     +-- persistent result record
  |
  +-- Qualification gate
  |     +-- full 24-hour completion
  |     +-- pool verification
  |     +-- selected tested profile
  |
  +-- Wallet
  |     +-- public Monero receiving address only
  |
  +-- Personal Mining
        +-- qualified CPU thread result
        +-- user public wallet
        +-- developer-contribution behavior
        +-- explicit Start / Stop
```

## Privileged operations

ZTM requests Ubuntu administrator authorization for preparation through a per-application-session privileged broker.

The password is handled by the operating-system authorization flow. ZTM does not store it.

The privileged session ends with the application session.

## Benchmark engine

The stable GUI does not expose benchmark duration or manual thread selection.

The engine is also locked to the stable 24-hour duration. This prevents a hidden command-line duration change from turning a short run into a qualifying stable benchmark.

## XMRig

XMRig is an independent GPLv3 project.

ZTM prepares a verified supported XMRig binary and controls it as the RandomX execution engine. XMRig licensing and upstream developer contribution remain separate from I2PS-owned ZTM behavior.

## Wallet boundary

ZTM does not implement custody of private Monero wallet secrets.

The user supplies only a public receiving address for the personal-mining path. Seeds, wallet passwords and private keys stay outside ZTM.

## Result boundary

ZTM reports measured performance from the machine and configurations actually tested.

It does not claim an untested universal optimum or guaranteed profitability.
