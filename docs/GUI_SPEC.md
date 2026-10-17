# GUI specification — approved v0.4 wording

**Status: authorization preview constructed; full application screens pending implementation.**

## Visual identity

Dark navy/black interface with cyan accents and the **exact official I2PS Engineering crown-and-star logo** in cyan. Sidebar should not extend unnecessarily below content; keep the authorization controls comfortably visible. Do not substitute generic company logos.

## Authorization screen

Main heading: **Online Benchmark Authorization**.

- The planned application performs online RandomX work on the real CPU for at least 24 continuous active hours.
- **No offline benchmark is available.** Do **not** append a version qualifier to this sentence.
- The initial benchmark mines to the **Dev Wallet**, benefiting I2PS Engineering.
- Warn about CPU, electricity and cooling implications.
- User's own Monero wallet is requested only after the 24-hour benchmark is complete.
- Do **not** display the Dev Wallet address, any secret key, or a fake/example payout address.
- **Dev Wallet** is the label, not **I2PS Dev Wallet**.

Place this explanatory copy directly alongside the **Dev Wallet** label:

> This contributes in the development of the software, of its future versions, and keeping it alive and always free, as it was first intended.

## Terms and Authorization — EXACTLY TWO acknowledgments

1. “I understand this benchmark uses my CPU continuously for approximately 24 hours so I can get the best result running my own RandomX miner.”
2. “I understand the terms and conditions of using I2PS RandomX CPU Benchmark software.”

There must be no additional acknowledgment checkbox. Both must be checked before enabling the authorization action. **Authorization is separate from dependency installation.**

## Other target screens

Setup Assistant → Live 24-hour benchmarking → Benchmark results → Wallet education and entry → Personal mining (Dev Donate disclosure) → Methodology.

**Stop Mining** must remain available; screenshots cannot be treated as verification of process-control functionality.
