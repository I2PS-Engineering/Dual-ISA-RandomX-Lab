"""Summarize measured benchmark winners without treating a peak as a sustained result.

A winning configuration is selected from actual tested optimizer profiles.
The highest instantaneous sample is reported separately for engineering context.
"""
from __future__ import annotations


def _numeric(value, default=0.0):
    try:
        return float(value) if value is not None else float(default)
    except (ValueError, TypeError, OverflowError):
        return float(default)


def _integer(value, default=0):
    try:
        return int(value) if value is not None else int(default)
    except (ValueError, TypeError, OverflowError):
        return int(default)


def _profile_fields(item):
    return {
        "label": str(item.get("label") or ""),
        "threads_requested": item.get("threads_requested"),
        "threads_observed": item.get("threads_observed"),
        "median_hs": item.get("median_hs"),
        "mean_hs": item.get("mean_hs"),
        "min_hs": item.get("min_hs"),
        "max_hs": item.get("max_hs"),
        "score": item.get("score"),
        "stability_cv": item.get("stability_cv"),
        "accepted_shares": item.get("accepted_shares", 0),
        "rejected_shares": item.get("rejected_shares", 0),
        "hashrate_samples": item.get("hashrate_samples"),
        "measured_seconds": item.get("seconds"),
        "reload_generation": item.get("reload_generation"),
    }


def build_winning_configuration(report: dict) -> dict:
    profiles = [p for p in report.get("optimizer_profiles", []) if isinstance(p, dict)]
    evaluated = [p for p in profiles if p.get("label") != "winner-sustained"]
    tested = [p for p in evaluated if _numeric(p.get("median_hs")) > 0 and
              _integer(p.get("threads_observed")) > 0]
    ranked = sorted(tested, key=lambda p: (
        _numeric(p.get("score")), _numeric(p.get("median_hs")),
        -_numeric(p.get("stability_cv"), 1.0)
    ), reverse=True)

    selected_threads = _integer(report.get("selected_threads"))
    selected_profile = next(
        (p for p in ranked if _integer(p.get("threads_observed")) == selected_threads),
        None
    )
    sustained = next(
        (p for p in profiles if p.get("label") == "winner-sustained" and
         _integer(p.get("threads_observed")) == selected_threads), None
    )
    peak = max((p for p in profiles if _numeric(p.get("max_hs")) > 0),
               key=lambda p: _numeric(p.get("max_hs")), default=None)

    # Never fabricate a winner when no valid measured search profile exists.
    return {
        "selection_basis": "Measured optimizer score: sustained median, variability and share quality; NOT a single peak",
        "selected_active_threads": selected_threads if selected_profile is not None else None,
        "randomx_dataset_init_threads": "XMRig automatic",
        "chosen_search_profile": _profile_fields(selected_profile) if selected_profile else None,
        "winner_sustained_profile": _profile_fields(sustained) if sustained else None,
        "highest_observed_peak": _profile_fields(peak) if peak else None,
        "all_ranked_tested_profiles": [_profile_fields(p) for p in ranked],
        "cpu_model": report.get("cpu_model"),
        "logical_cpus": report.get("logical_cpus"),
        "host_os": report.get("host_os"),
        "architecture": report.get("architecture"),
        "xmrig_version": report.get("xmrig_version_target"),
        "pool": report.get("pool"),
        "tls": report.get("tls"),
        "elapsed_seconds": report.get("elapsed_seconds"),
        "full_24_hour_qualified": report.get("actual_24_hour_benchmark") is True,
        "overall_mean_hs": report.get("mean_hs"),
        "overall_median_hs": report.get("median_hs"),
        "overall_min_hs": report.get("min_hs"),
        "overall_max_hs": report.get("max_hs"),
        "overall_accepted_shares": report.get("accepted_shares", 0),
        "overall_rejected_shares": report.get("rejected_shares", 0),
        "overall_hashrate_samples": report.get("hashrate_samples", 0),
        "qualification_status": report.get("status"),
    }


def format_winning_configuration(result: dict) -> str:
    def speed(value):
        return f"{_numeric(value):,.2f} H/s" if value is not None else "not measured"

    def signed(value):
        return str(value) if value is not None else "not measured"

    chosen = result.get("chosen_search_profile")
    sustained = result.get("winner_sustained_profile")
    peak = result.get("highest_observed_peak")
    lines = [
        "=" * 69,
        "ZTM — WINNING CONFIGURATION",
        "=" * 69,
        f"Status:                {result.get('qualification_status') or 'UNKNOWN'}",
        f"Full 24h qualified:    {'YES' if result.get('full_24_hour_qualified') else 'NO'}",
        f"CPU model:             {result.get('cpu_model') or 'Unknown'}",
        f"Logical CPUs:          {signed(result.get('logical_cpus'))}",
        f"Architecture:          {result.get('architecture') or 'Unknown'}",
        f"Host OS:               {result.get('host_os') or 'Unknown'}",
        f"XMRig:                 {result.get('xmrig_version') or 'Unknown'}",
        f"Pool:                  {result.get('pool') or 'Unknown'}",
        f"TLS:                   {'enabled' if result.get('tls') else 'disabled'}",
        f"Selected active threads: {signed(result.get('selected_active_threads'))}",
        f"Dataset initialization:  {result.get('randomx_dataset_init_threads')}",
        f"Profiles tested:       {len(result.get('all_ranked_tested_profiles') or [])}",
        "Selection method:     highest measured optimizer score",
    ]
    if chosen is not None:
        lines.extend([
            "",
            "WINNING SEARCH PROFILE (MEASURED)",
            f"  Test label:           {chosen.get('label')}",
            f"  Selected threads:     {signed(chosen.get('threads_observed'))}",
            f"  Median:               {speed(chosen.get('median_hs'))}",
            f"  Mean:                 {speed(chosen.get('mean_hs'))}",
            f"  Minimum:              {speed(chosen.get('min_hs'))}",
            f"  Peak:                 {speed(chosen.get('max_hs'))}",
            f"  Stability CV:         {signed(chosen.get('stability_cv'))}",
            f"  Optimizer score:      {signed(chosen.get('score'))}",
            f"  Pool shares:          {signed(chosen.get('accepted_shares'))} accepted / {signed(chosen.get('rejected_shares'))} rejected",
            f"  Measured seconds:     {signed(chosen.get('measured_seconds'))}",
        ])
    else:
        lines.extend(["", "NO VERIFIED WINNING SEARCH PROFILE — insufficient measured data."])
    if sustained is not None:
        lines.extend([
            "",
            "WINNER DURING REMAINDER OF BENCHMARK",
            f"  Median:               {speed(sustained.get('median_hs'))}",
            f"  Mean:                 {speed(sustained.get('mean_hs'))}",
            f"  Peak:                 {speed(sustained.get('max_hs'))}",
            f"  Stability CV:         {signed(sustained.get('stability_cv'))}",
            f"  Pool shares:          {signed(sustained.get('accepted_shares'))} accepted / {signed(sustained.get('rejected_shares'))} rejected",
            f"  Measured seconds:     {signed(sustained.get('measured_seconds'))}",
        ])
    lines.extend([
        "",
        "FULL RUN",
        f"  Median hashrate:      {speed(result.get('overall_median_hs'))}",
        f"  Mean hashrate:        {speed(result.get('overall_mean_hs'))}",
        f"  Lowest sample:        {speed(result.get('overall_min_hs'))}",
        f"  Highest sample:       {speed(result.get('overall_max_hs'))}",
        f"  Accepted / rejected:  {signed(result.get('overall_accepted_shares'))} / {signed(result.get('overall_rejected_shares'))}",
        f"  Duration (seconds):   {signed(result.get('elapsed_seconds'))}",
        "",
        "TOP PROFILES BY OPTIMIZER SCORE",
    ])
    for index, profile in enumerate(result.get("all_ranked_tested_profiles", []), start=1):
        lines.append(
            f"  {index}. {signed(profile.get('threads_observed'))} threads"
            f" | median {speed(profile.get('median_hs'))}"
            f" | peak {speed(profile.get('max_hs'))}"
            f" | score {signed(profile.get('score'))}"
            f" | accepted {signed(profile.get('accepted_shares'))}"
            f" | rejected {signed(profile.get('rejected_shares'))}"
        )
    if peak is not None:
        lines.extend([
            "",
            "HIGHEST MOMENTARY SAMPLE (NOT THE SELECTION CRITERION)",
            f"  Profile:              {peak.get('label')}",
            f"  Active threads:       {signed(peak.get('threads_observed'))}",
            f"  Peak:                 {speed(peak.get('max_hs'))}",
        ])
    lines.extend([
        "",
        "The winning configuration is the highest-scoring tested profile.",
        "A short-term peak alone is not a reliable sustained performance result.",
        "=" * 69,
    ])
    return "\n".join(lines) + "\n"
