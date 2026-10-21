"""Local public-wallet selection for ZTM; NEVER generates or receives secret keys.

New encrypted Monero wallets are created by official monero-wallet-gui. This module
only stores the public receiving address in a user-owned file, not a password,
mnemonic, private spend/view key, or a copy of the .keys wallet file.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

OFFICIAL_WALLET_URL = 'https://www.getmonero.org/downloads/'
OFFICIAL_RESTORE_URL = 'https://www.getmonero.org/resources/user-guides/restore_account.html'
OFFICIAL_KEYS_URL = 'https://www.getmonero.org/resources/user-guides/restore_from_keys.html'


class WalletError(ValueError):
    pass


def public_record_path(home=None):
    return Path(home or Path.home()) / 'Library' / 'Application Support' / 'I2PS' / 'ZTM' / 'wallet-public.json'


def write_public_record(address, chosen_wallet_file='', *, destination=None):
    """Create a private-permissions record of PUBLIC data only (never secret material).

    The wallet file path is a reference to the encrypted Monero wallet produced by
    official software. ZTM does not read, copy or modify that file.
    """
    from ztm_engine import validate_address, BenchError
    try:
        address = validate_address(address)
    except BenchError as exc:
        raise WalletError(str(exc)) from exc
    chosen_wallet_file = str(chosen_wallet_file).strip()
    if chosen_wallet_file:
        candidate = Path(chosen_wallet_file).expanduser()
        if not candidate.is_file():
            raise WalletError('Choose an existing local Monero wallet file, or leave this field empty.')
        # never store reference to unencrypted backup, seed, or a random file
        if candidate.suffix in ('.txt', '.json', '.seed', '.pem', '.log'):
            raise WalletError('Do not select seed backups, password files or logs.')
        chosen_wallet_file = str(candidate.resolve())
    target = Path(destination) if destination is not None else public_record_path()
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.parent.is_symlink():
        raise WalletError('Refusing public-wallet storage through a symbolic-link directory.')
    try:
        target.parent.chmod(0o700)
    except OSError:
        pass
    data = {'public_address': address, 'local_wallet_file': chosen_wallet_file,
            'notice': 'NO PRIVATE KEYS, PASSWORDS OR SEEDS ARE STORED BY ZTM'}
    fd, name = tempfile.mkstemp(prefix='.public-wallet-', dir=target.parent)
    temp = Path(name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
    return target


def read_public_record(*, destination=None):
    target = Path(destination) if destination is not None else public_record_path()
    if not target.is_file() or target.is_symlink():
        return None
    try:
        data = json.loads(target.read_text(encoding='utf-8'))
        from ztm_engine import validate_address, BenchError
        try:
            data['public_address'] = validate_address(data['public_address'])
        except BenchError:
            return None
        return {key: data.get(key, '') for key in ('public_address', 'local_wallet_file')}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def find_monero_gui():
    """Locate the official wallet application locally; never examine wallet secrets."""
    candidates = [
        Path('/Applications/Monero GUI Wallet.app/Contents/MacOS/monero-wallet-gui'),
        Path('/Applications/monero-wallet-gui.app/Contents/MacOS/monero-wallet-gui'),
        Path.home() / 'Applications' / 'Monero GUI Wallet.app' / 'Contents' / 'MacOS' / 'monero-wallet-gui',
        shutil.which('monero-wallet-gui'),
    ]
    for candidate in candidates:
        if candidate is not None and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return Path(candidate)
    return None


def launch_monero_gui(executable=None):
    """Launch official wallet software separately; ZTM cannot see its password/seed."""
    path = Path(executable) if executable is not None else find_monero_gui()
    if path is None:
        raise WalletError('Official Monero GUI Wallet is not installed yet.')
    if not path.is_file() or not os.access(path, os.X_OK):
        raise WalletError('Selected Monero wallet program cannot be executed.')
    return subprocess.Popen([str(path)], stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
