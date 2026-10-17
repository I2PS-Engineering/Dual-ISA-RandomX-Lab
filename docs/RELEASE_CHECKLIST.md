# Pre-release acceptance checklist

Do not mark the v0.4 product production ready until all conditions below are verified.

- [ ] I2PS license and commercial mining/developer-contribution policy reviewed and approved.
- [ ] User sees exact **two** authorization acknowledgments and the Dev Wallet payout disclosure.
- [ ] XMRig is fetched from official source with pinned checksum and separate third-party license compliance.
- [ ] Startup never launches mining unless the user explicitly authorizes it.
- [ ] Program works on supported actual hardware and Windows/Linux migration paths are documented honestly.
- [ ] 24 uninterrupted active hours measured with robust timekeeping; interruptions do not count as complete.
- [ ] Accurate Dev Wallet payout behavior verified against external pool evidence.
- [ ] Thread-profile selection compares sustained measured hashrate, not fake/demo values.
- [ ] User can stop mining immediately; process termination and cancellation audited.
- [ ] After benchmark, only user's public receiving address is requested; seed/private keys rejected.
- [ ] Dev Donate rate and implementation completed, disclosed, audited, and XMRig own donation preserved.
- [ ] CPU thermals, power, abnormal load, disconnects and failed downloads handled safely.
- [ ] Logs and reports scrubbed of wallet secrets, hostnames, IPs and miner credentials.
- [ ] Real screenshot captures and user guide reflect production functionality.
- [ ] Versioned release archives, SHA-256 checksums and legal notices attached to GitHub Releases.
