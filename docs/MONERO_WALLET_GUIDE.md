# Monero wallet safety — ZTM-SRP1V1

After a qualifying 24-hour benchmark, ZTM can use the user's **public Monero receiving address** for personal mining.

## What ZTM needs

| Item | Needed by ZTM? |
| --- | --- |
| Public receiving address | **Yes** |
| Recovery seed / mnemonic | **Never** |
| Wallet password | **Never** |
| Private spend key | **Never** |
| Private view key | **Never** |

A public receiving address allows mining payouts to be directed to the user's wallet. It does not give ZTM authority to spend the user's funds.

## Creating or restoring a wallet

Use wallet software you trust and obtain it from its official source.

Official Monero resources:

- https://www.getmonero.org/downloads/
- https://www.getmonero.org/resources/user-guides/

Back up recovery information securely and offline.

Do not paste a recovery seed or private key into ZTM, a GitHub issue, an email support request or a chat.

## ZTM wallet workflow

The Wallet section remains gated until a qualifying 24-hour benchmark completes.

When the user proceeds to personal mining, ZTM stores/uses only the public-address information required for that workflow.

ZTM does not recover lost wallets and cannot retrieve a forgotten wallet password or recovery seed.
