# ZTM_Benchmark — One-command installation (v0.1.7-alpha8-session)

**Engineering alpha.** This surgical revision preserves the alpha7 GUI, Benchmark/Wallet/Mining tabs, 24-hour unlock requirement, optimizer, and alpha7 miner-shutdown behavior.

## Step 1 — Stop the old version

Let an active benchmark finish; close the old application. Ensure no miner remains with `sudo pgrep -a -x xmrig` (no output means none).

## Step 2 — Install and open from GitHub

Run as your **normal Ubuntu Desktop x86-64 user**, not as root:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://raw.githubusercontent.com/I2PS-Engineering/ZTM_Benchmark/0ef289b5c11ca3a299e07721adbb645f79bd0dc1/install-ztm-v8.sh";b=urllib.request.urlopen(u,timeout=30).read();assert hashlib.sha256(b).hexdigest()=="33b50ef2d2fece6f084986d48b9b3921c0bbc4768486513984a62150ae3932c6","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

The pinned installer verifies its own SHA-256, downloads exactly eight package fragments from immutable commit `838a118a2723eaf65451bdd21a1a0350198ac5c9`, checks package size (**35,428 bytes**), package SHA-256 (`6df838427794da150f44b34fce5f37fbc1691a4f589ec440620a034a044ededf`), and Debian identity/version `0.1.7~alpha8session1` before calling APT and starting ZTM.

Ubuntu may ask for the administrator password when the **one-command installer** changes installed packages. This is separate from ZTM's subsequent **application session**.

## Step 3 — Authorize ZTM once

Click **PREPARE LINUX + INSTALL XMRIG** and approve the one Ubuntu administrator prompt. ZTM retains one narrowly scoped privileged helper *only for the lifetime of this open ZTM GUI session*. It performs fixed APT update/install/optional upgrade/MSR setup and starts verified XMRig mining jobs for the normal-user optimizer. It does not store passwords, disable password security, or install permanent passwordless sudo.

If you close and reopen ZTM, a new session may require a new authorization. If you already completed the 24-hour benchmark and start personal Mining before Prepare, the first Start Mining action establishes the same one-time session.

The privileged helper rechecks the official XMRig 6.26.0 release archive SHA-256 and executes a root-private extracted copy; it does not execute an arbitrary user-writable binary with administrator privileges.

## Step 4 — Run a benchmark

Use the unchanged UI, with CPU Threads: Auto. A 24-hour run must finish to unlock Wallet and Mining; partial runs do not unlock them. The elapsed timer and confirmed accepted shares are recorded in `~/ZTM-Results`. The existing STOP/close control terminates mining via alpha7's guardian.

## Testing status

Eight focused offline/synthetic tests passed, including a real Unix-socket session conversation and a simulated process launch/stop through the existing guardian. This is **not** proof of a live Ubuntu Polkit prompt or a completed real 24-hour run. Validate one-prompt preparation and automatic shutdown on the actual machine before the full run.

[Release notes](ZTM_ALPHA8_RELEASE_NOTES.md) · [Repository](https://github.com/I2PS-Engineering/ZTM_Benchmark)
