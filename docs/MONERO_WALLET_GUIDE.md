# Monero wallet guide — public address only

After the **completed** online benchmark, users may configure personal mining using their **own Monero wallet**.

## What the app should request

**Only a public Monero receiving address**, which allows a pool to send earned payouts to the user's wallet.

| Item | Purpose | Enter in I2PS Lab? |
| --- | --- | --- |
| Public receiving address | Receives mining payouts | **Yes** |
| Public spend/view keys | Public cryptographic elements | **No — not needed** |
| Private spend key | Authorizes spending of wallet funds | **Never** |
| Private view key | Can reveal wallet incoming-transaction history | **Never** |
| Recovery seed / mnemonic | Can restore control over wallet funds | **Never** |
| Wallet password | Protects local wallet access | **Never** |

The receiving address is not identical to the private spend key. The software should validate a public address without requesting any secret.

## Do not have a wallet yet?

- Official Monero wallet downloads: https://www.getmonero.org/downloads/
- Official Monero user guides: https://www.getmonero.org/resources/user-guides/
- Official Monero website: https://www.getmonero.org/

Users should install wallet software from official sources, create a wallet, **back up their seed offline**, and copy **only the public receiving address** into the I2PS application's user-wallet form.

## Separate sessions

The initial 24-hour online benchmark is paid to the **Dev Wallet** with prior consent. Personal mining is a different session, using the user's entered public wallet, with the built-in and disclosed **Dev Donate** mechanism. The exact Dev Donate rate is **not yet finalized**; personal mining with that mechanism must not be released without full specification and verification.

Never publish wallet credentials, seeds or sensitive user identity information in benchmark logs or GitHub issues.
