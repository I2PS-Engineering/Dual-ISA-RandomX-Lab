# ZTM — Zero to Monero (Ubuntu Desktop alpha)

**20 October 2026: engineering alpha published to the repository downloads directory, with a signed manifest and a one-command verified Ubuntu bootstrap. It is not yet a GitHub Release or production v0.4.** This is not the completed I2PS RandomX v0.4 24-hour production benchmark.

## Actual first-user experience

- Existing Ubuntu Desktop x86-64: download the reviewed ZTM Debian installer, open the .deb in Ubuntu's package installer, choose Install, and launch **ZTM — Zero to Monero** in the applications menu.
- Migrating from Windows: back up files and install Ubuntu Desktop using official Ubuntu instructions first, then follow the identical ZTM installation path. ZTM does not modify disk partitions or distribute a custom Linux image.
- In ZTM click **Prepare Linux + Install XMRig**. The application shows the real terminal output of APT index refresh and package installation; optional full package upgrades require a separate opt-in checkbox. It then retrieves the official **XMRig 6.26.0** static Linux x64 release after verifying its hardcoded SHA-256 checksum.
- Enter a pool host:port, a **public** Monero receiving address, matching TLS setting, number of threads and test duration.
- Read both separate diagnostic acknowledgments and explicitly authorize online CPU mining. The **Start Benchmark** control remains disabled until preparation completes.
- Actual XMRig speed and share lines stream through the GUI, with STOP always available during the run. Results are JSON plus a redacted diagnostic log in `~/ZTM-Results`.
- A run without pool shares, or an interrupted run, is **not** reported as pool-verified.

## Test results, with evidence limits

- 11 local tests passed; no test failures.
- Real Tk GUI was launched in a virtual display and visually captured at 1090×760.
- A real Debian .deb package was built and inspected.
- **Not tested:** clean real Ubuntu install, graphical polkit/apt, online XMRig download, any real pool accepted share, 24 hours of hardware performance, and Dev Wallet payout.

## Critical distinction

ZTM alpha is a **short engineering diagnostic using the test operator's explicitly entered receiving address**. It is not the official v0.4 first-run 24-hour Dev Wallet benchmark, and **does not replace its approved payout and mandatory Dev Donate requirements**. Full production release remains blocked pending those validations and completed functionality.

The actual .deb, signed manifest and pinned bootstrap are hosted in the repository downloads directory and can be installed with the [single verified command](ZTM_ONE_COMMAND.md). This is still an alpha; do not describe an untested 24-hour benchmark as verified.

**Third party:** XMRig is fetched from the official upstream repository under its separate GPLv3 license; no XMRig executable is included in the Debian package.
