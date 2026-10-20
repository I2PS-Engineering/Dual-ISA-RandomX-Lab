# ZTM 0.1.3-alpha4-surgical

Surgical update over 0.1.2-alpha3-surgical. The visible GUI is unchanged.

Changes:
- Prepare Linux installs `kmod` and `msr-tools` and loads the Linux `msr` kernel module.
- The verified XMRig process is elevated through `pkexec` so XMRig can apply its own Linux RandomX huge-page allocation and MSR preset automatically.
- XMRig pool password and `rig-id` are both fixed to `ZTM-Zero-to-Monero` so HashVault can show a dedicated ZTM worker identity instead of an anonymous/default worker.
- Existing pool, payout, TLS, Auto CPU threads, 24-hour default duration, authorization controls, Wallet tab, terminal, and visual layout are otherwise unchanged.

Important dashboard distinction: using the same receiving address as the existing fleet means HashVault will still show the ZTM worker under that wallet's dashboard and include it in that wallet's worker total. The dedicated name separates it visually. A completely separate HashVault wallet dashboard requires a different receiving address.

Live validation still required on Ubuntu: confirm XMRig reports successful MSR application, non-zero/100% huge pages, worker name `ZTM-Zero-to-Monero`, and at least one accepted pool share.
