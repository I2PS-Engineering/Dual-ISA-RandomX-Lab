# ZTM-SRP1V2 FAQ

### What is the current release?

**ZTM-SRP1V2 — Stable Release V1.2**.

### What operating system is supported?

The current stable package targets **Ubuntu Desktop x86-64**.

### Is ZTM open source?

No.

I2PS-owned ZTM software is distributed under **PolyForm Strict License 1.0.0** for permitted noncommercial use.

### Is the benchmark simulated?

No.

ZTM runs real RandomX CPU work through XMRig and connects to a real mining pool.

### Can I choose a shorter benchmark?

No.

ZTM-SRP1V2 is locked to **24 hours**. The duration selector was removed, and the engine rejects shorter benchmark durations.

### Can I choose CPU threads manually?

Not for the stable benchmark.

The benchmark uses **CPU Threads: Auto** and evaluates the supported tested profiles automatically.

### What happens if I stop before 24 hours?

The CPU work stops, but that run does not qualify as a completed 24-hour benchmark and does not unlock the qualified Wallet/Mining workflow.

### What do the two benchmark checkboxes say?

1. **I authorize real CPU work for 24 hours, including electricity use and heat.**
2. **I understand this online benchmark uses both XMRig and I2PS dev contribution.**

### Does ZTM need my wallet seed or private keys?

No.

ZTM only needs a **public Monero receiving address** for the user's personal-mining workflow.

Never enter a recovery seed, wallet password, private spend key or private view key into ZTM.

### Does ZTM store my Ubuntu administrator password?

No.

The privileged preparation uses a per-session authorization mechanism. ZTM does not store the password or install a permanent passwordless sudo rule.

### Does XMRig have its own developer contribution?

XMRig is independent software and retains its own upstream behavior and GPLv3 licensing. ZTM's I2PS contribution is separate.

### Does ZTM guarantee a particular hashrate?

No.

Hashrate is measured on the actual machine and depends on the CPU, memory, thermals, system state, pool conditions and tested profile.

### Where do I download the stable release?

https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/tag/ZTM-SRP1V2

### Where do I report a problem?

General technical reports: **engineering@i2psolutions.com**

Security reports: follow [SECURITY.md](../SECURITY.md).

### Does ZTM show the winning configuration after 24 hours?

Yes. A qualifying completed run displays the selected active threads, winning profile, optimization score, sustained and peak hashrates, pool shares, and a JSON report. **Highest peak** and **best sustained configuration** are distinguished.

### How can I enlarge the interface?

ZTM-SRP1V2 starts at 165% font scaling. The A− and A+ buttons in the top bar adjust interface text between 125% and 200%.
