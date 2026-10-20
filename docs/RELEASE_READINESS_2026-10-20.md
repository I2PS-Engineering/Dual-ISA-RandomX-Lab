# I2PS Dual-ISA RandomX Lab — release readiness (20 October 2026)

**Status: NOT RELEASED. No GitHub-installable v0.4 application binary is available.**

The public repository has GitHub bootstrap scripts and installation instructions, but GitHub Releases currently contains no approved application ZIP. The bootstrap refuses to install when no approved stable release is found.

## Engineering prototype assembled locally today

- A separate v0.4 online-only XMRig subprocess controller, without the v0.3 offline benchmark endpoint
- The two exact acknowledgments and separate per-session PolyForm license acceptance
- An operator-configured PUBLIC Dev Wallet address, hidden from the GUI and absent from API responses; missing address prevents mining
- Operator-selected pool/TLS, 24-hour default active-run clock, automated thread candidates, XMRig-reported speed/share metrics, Stop
- Refusal to complete on interruption, miner early exit, zero accepted shares, or zero reported hashrate samples
- Consistent official cyan logo and fixed sidebar; remaining design PNGs explicitly marked previews
- Beginner documentation for installed Ubuntu and Windows-to-Ubuntu migration

## Tests completed

- 9 synthetic automated tests passed, zero failed; these do not mine
- Ordinary non-root Linux Quickstart dry-run completed in a Debian 13 container
- Chromium static authorization-page render inspected at 1448px: two acknowledgments, correct logo/sidebar, no horizontal overflow
- Local ZIP passed the existing GitHub installer archive safety validator and received a SHA-256 digest

**Not tested:** Real official XMRig downloads on a clean Ubuntu host; live pool connectivity and payout; full 24-hour run; thermal behavior; public GitHub release/installer; personal-mining Dev Donate.

## Actual prerequisites for public release

1. Operator supplies and verifies the public Dev Wallet receiving address; never private keys or seeds.
2. Approve pool/TLS beginner defaults or guided pool selection.
3. Finalize the compulsory post-benchmark Dev Donate policy and percentage.
4. Confirm license/payout disclosures and third-party GPLv3 notices.
5. Validate XMRig pool connection, share acceptance, stop/failure handling and full real-hardware 24-hour benchmark on supported Ubuntu hardware.
6. Approve final application binary and SHA256SUMS.txt, then publish an official GitHub stable release with real assets.
7. Test the official GitHub bootstrap on an independent clean Ubuntu machine. Film the actual result, not simulated metrics.

The locally assembled prototype is not uploaded to this public repository because it contains proprietary application source. Its presence on a local filesystem is not public distribution.

**Video guidance:** It is accurate to explain Ubuntu migration and future GitHub distribution. It is not accurate to claim that v0.4 can be downloaded today or that its full 24-hour benchmark has been validated.
