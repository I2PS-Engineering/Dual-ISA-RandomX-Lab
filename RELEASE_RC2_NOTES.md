# ZTM-SRP1V2-RC2 — verified benchmark crash fix and pre-GUI miner cleanup

RC2 replaces the broken RC1 **test release**, not the existing public stable V2.
- Fix local candidate_profiles name shadowing which crashed the 24-hour optimizer.
- Always use authorized all-owner recognized XMRig cleanup before GUI appears, including installer auto-launch and Desktop shortcut.
- Re-check for immediate miner service restarts; refuse GUI if privilege denied or competing XMRig persists.
- Preserve previous V2 24-hour consent, wallet rules, huge-page preparation, optimizer candidate testing, and subsequent miner checks.
- No arbitrary renamed process detection or system service disabling.
- CI tests are not real 24-hour HashVault or physical Worker 14 validation.
