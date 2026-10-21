# ZTM-SRP1V1 user guide

## What ZTM does

ZTM measures real RandomX performance on the physical CPU of an Ubuntu x86-64 computer.

It uses a real XMRig workload and a real mining-pool connection.

The goal is to identify a strong **tested** CPU thread configuration and measure sustained behavior over a full 24-hour benchmark.

## 1. Prepare the machine

Open ZTM and select:

**1 PREPARE LINUX + INSTALL XMRIG**

Ubuntu requests administrator authorization for the preparation operations.

ZTM uses one privileged authorization session while the application remains open. It does not store the password.

Preparation does not begin mining automatically.

## 2. Review the benchmark setup

ZTM-SRP1V1 has no duration selector.

The benchmark is always:

**24 hours**

CPU thread control is:

**Auto**

The two required acknowledgements are:

1. **I authorize real CPU work for 24 hours, including electricity use and heat.**
2. **I understand this online benchmark uses both XMRig and I2PS dev contribution.**

## 3. Start the benchmark

Select:

**START 24-HOUR RANDOMX BENCHMARK**

ZTM starts real RandomX CPU work through XMRig.

The live terminal shows benchmark/miner activity. ZTM records hashrate and pool-share behavior and evaluates the supported thread profiles.

A short peak is not treated as the final result. The objective is sustained measured performance.

You can stop the benchmark. A stopped or incomplete run does not qualify as a completed 24-hour benchmark.

## 4. Result and qualification

A qualifying run must complete the full 24-hour requirement and satisfy the pool-verification conditions used by ZTM.

The result records information including the selected thread profile, elapsed time, hashrate samples and accepted/rejected share behavior.

Wallet and Mining remain gated until the qualifying benchmark completes.

## 5. Wallet

For personal mining, ZTM requires only a **public Monero receiving address**.

Never enter into ZTM:

- recovery seed;
- wallet password;
- private spend key;
- private view key.

Wallet creation and recovery are performed using wallet software, not ZTM.

## 6. Personal mining

After qualification, ZTM uses the tested CPU configuration for the personal-mining workflow.

The user's public receiving address is the payout destination for the user's mining path.

The developer-contribution behavior remains part of the software, while XMRig also retains its own independent upstream contribution behavior.

## 7. Stop and close

The Stop control must terminate active CPU work.

Closing the ZTM session also closes the privileged authorization session.

## Performance interpretation

Hashrate depends on the actual CPU, memory behavior, thermal state, operating environment, pool conditions and tested thread profile.

ZTM does not guarantee profitability or a universal best hashrate.
