# ZTM v0.1.7-alpha8-session — surgical single-authentication update

Base: working v0.1.6-alpha7-guard.

## Unchanged

The visible Benchmark, Wallet, Mining tabs, logo, colors, layout, optimizer profile selection, embedded HashVault settings, 24-hour eligibility gate, terms and donation percentages, and original alpha7 stop guardian.

## Changed (backend only)

- First **Prepare Linux** operation starts one authenticated desktop session using Polkit (`pkexec`).
- A narrow privileged helper lives only while the authorized ZTM GUI remains open, and serves the approved APT refresh, selected optional package upgrade, prerequisite installation, MSR module setup, and XMRig guardian operations through a private Unix socket.
- Users who completed a prior 24-hour benchmark can begin personal mining first; that first mining action starts the same one-time authorized session.
- No passwords are saved or cached by ZTM; no `NOPASSWD` sudoers changes and no global/root GUI.
- The privileged helper verifies the official XMRig 6.26.0 archive against its pinned SHA-256 and launches the checked miner binary from a root-private temporary path. It does not invoke arbitrary shell commands or directly elevate a user-modifiable executable.
- The unchanged alpha7 guardian terminates the miner when the controller requests Stop, exits, or disappears.

## Package integrity

- Package: `downloads/ZTM-Zero-to-Monero_0.1.7-alpha8-session_amd64.deb.b64.part00` through `.part07`, pinned to commit `838a118a2723eaf65451bdd21a1a0350198ac5c9`
- Base64 fragment sizes: 6000 × 7 and 5240 bytes.
- Decoded Debian package size: **35,428 bytes**.
- Debian version: `0.1.7~alpha8session1`.
- SHA-256: `6df838427794da150f44b34fce5f37fbc1691a4f589ec440620a034a044ededf`
- Pinned bootstrap: [install-ztm-v8.sh](../install-ztm-v8.sh), commit `0ef289b5c11ca3a299e07721adbb645f79bd0dc1`
- Bootstrap SHA-256: `33b50ef2d2fece6f084986d48b9b3921c0bbc4768486513984a62150ae3932c6`.

## Test boundary

Eight focused offline tests passed. They include a Unix-socket request lifecycle, command allowlist rejection, owner identity/mode checks and a simulated XMRig child stopped through the original guardian with no remaining process. **Not yet verified**: real Ubuntu authentication UI, live mining after the change, or uninterrupted 24-hour mining. Keep the currently working alpha7 run intact until it finishes.

See [one-command install instructions](ZTM_ONE_COMMAND.md).
