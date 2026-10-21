"""Eligibility for ZTM personal mining: measured, uninterrupted 24h pool-verified benchmark."""
from __future__ import annotations
import json
from pathlib import Path

SECONDS_REQUIRED = 24 * 60 * 60


def valid_benchmark_report(report: dict) -> bool:
    """Require full requested and elapsed online benchmark with accepted pool shares."""
    if not isinstance(report, dict) or report.get('status') != 'MEASURED_POOL_VERIFIED':
        return False
    try:
        return (int(report.get('requested_seconds', 0)) >= SECONDS_REQUIRED and
                float(report.get('elapsed_seconds', 0)) >= SECONDS_REQUIRED and
                int(report.get('accepted_shares', 0)) > 0 and
                int(report.get('rejected_shares', 0)) >= 0 and
                int(report.get('hashrate_samples', 0)) > 0 and
                report.get('actual_24_hour_benchmark') is True and
                isinstance(report.get('selected_threads'), int) and
                report['selected_threads'] > 0 and
                bool(report.get('optimizer_profiles')))
    except (ValueError, TypeError):
        return False


def latest_qualified_report(results: Path | None = None) -> dict | None:
    """Find one complete 24-hour, pool-verified run; shorter runs cannot be combined.

    Local file is evidence of completion, not a cryptographically protected attestation.
    """
    results = Path(results or (Path.home() / 'ZTM-Results'))
    if not results.is_dir() or results.is_symlink():
        return None
    for path in sorted(results.glob('run_*.json'), reverse=True):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            if path.stat().st_size > 500_000:
                continue
            report = json.loads(path.read_text(encoding='utf-8'))
            if valid_benchmark_report(report):
                return report
        except (OSError, ValueError, UnicodeError):
            continue
    return None


def eligible(results: Path | None = None) -> bool:
    return latest_qualified_report(results) is not None
