# ZTM Wallet: Existing wallet or Create wallet

**20 October 2026 — implemented in local ZTM alpha 0.1.1, now deployed in the separately pinned signed alpha2 installer.**

On opening the ZTM Wallet tab the user sees ONLY two routes: **I have an existing wallet** and **I do not have a wallet — create one**.

## Existing wallet

1. Copy the PUBLIC Monero receiving address from the official wallet into ZTM.
2. Optionally select an existing local Monero wallet file (reference path only). ZTM never reads, decrypts or copies the wallet file.
3. Confirm the format and select **Use this public address**. ZTM saves the public address and optional file path in ~/.local/share/ztm/wallet-public.json with 0600 permissions. ZTM never stores a password, seed, secret spend key or private view key.

## Create wallet

1. Select **Create wallet** in ZTM.
2. Click **Open official Monero wallet**. If an official monero-wallet-gui executable is installed locally, ZTM launches it separately; if missing, the user can open https://www.getmonero.org/downloads/ . This alpha does NOT download or install a wallet binary automatically.
3. Inside the OFFICIAL Monero GUI, choose Create a new wallet, choose a wallet name and local folder, choose and confirm a strong password, and BACK UP the recovery seed offline.
4. Official Monero wallet software creates the encrypted wallet files (generally wallet and wallet.keys) on the computer. ZTM never handles wallet cryptography or secret keys.
5. Click **Wallet created — recovery instructions** in ZTM to display the detailed recovery-information page, then continue to enter only the public address for the benchmark.

## Mandatory recovery-information page

- **File path:** In the official Monero wallet, locate the wallet folder through Settings / Info (Wallet path; menu labels may vary). The cache and .keys files belong to the user.
- **Public receiving address:** Copy from the official wallet's Receive / Account section; it is not a secret key.
- **Wallet password:** Unlocks the encrypted local file; separate from mnemonic recovery seed. ZTM cannot retrieve or reset it.
- **Recovery seed and private keys:** In the official GUI, Settings → Wallet → Show seed & keys (menu labels vary). Keep the recovery seed securely OFFLINE; NEVER type it into ZTM, chats or websites.
- **Recover lost wallet:** Use official Restore from seed. A local wallet password alone is not sufficient to restore a missing wallet file.
- **Responsibility:** User controls wallet, file location, password, recovery information and funds. I2PS does not receive, store or recover secrets and cannot guarantee recovery.

Official restore resources: https://www.getmonero.org/resources/user-guides/restore_account.html and https://www.getmonero.org/resources/user-guides/restore_from_keys.html

## Verification and release status

Seventeen automated tests passed locally, including existing ZTM diagnostic tests and six wallet storage/launch safeguards. Wallet screens were rendered from the actual Tk GUI at 1090x760; overlap on the Create view was corrected and rerendered. These are UI and synthetic tests, not a live official Monero-wallet creation or hardware benchmark test.

**The wallet change is available in the published 0.1.1-alpha2 engineering `.deb` and via the signed [one-command Ubuntu installer](ZTM_ONE_COMMAND.md). This is not a production release.** No claim of full in-app Monero key generation is made: creation is performed by the separately installed official Monero GUI.
