# ZTM-SRP1V1 — macOS port

This is a separate macOS engineering port of the released Ubuntu ZTM-SRP1V1 package.

Targets: macOS Intel (x86_64) and Apple Silicon (arm64), with native upstream XMRig 6.26.0 for each architecture.

Approved behavior retained: 24-hour fixed online RandomX benchmark, automatic CPU profile selection, both authorization acknowledgements, pool measurement, safe stop and qualification, public-address-only wallet, and existing developer-contribution policy.

macOS-specific adaptations: no apt, pkexec, /proc, Linux MSR drivers or root-owned mining process. Native miner runs under the signed-in user with lifecycle supervision. The application must not start mining on launch or preparation.

The Linux stable tag and Debian package remain untouched.

Mac packages will be labelled **technical preview** until their native installation, stop handling, benchmark, and wallet/mining paths have been exercised on physical Macs.

Official XMRig v6.26.0:
- Apple Silicon archive: xmrig-6.26.0-macos-arm64.tar.gz; SHA-256 6ae4eb4216e99a201ae9a3d2c3a7c275207c5165cfc25da1f3d735d6c4829c18
- Intel archive: xmrig-6.26.0-macos-x64.tar.gz; SHA-256 1da924b358c0089e361540c4a9e6f8b09538b29efeafa2379590e0f6db358ff4

These checksums are from the official XMRig release page.
