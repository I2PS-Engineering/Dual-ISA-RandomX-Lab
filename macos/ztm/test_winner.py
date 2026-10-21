"""Unit tests for measured winning-configuration reporting."""
import unittest

from ztm_winner import build_winning_configuration, format_winning_configuration


def profile(label, threads, median, peak, score, accepted, rejected, seconds):
    return {
        "label": label,
        "threads_requested": threads,
        "threads_observed": threads,
        "median_hs": median,
        "mean_hs": median * 0.99,
        "min_hs": median * 0.94,
        "max_hs": peak,
        "stability_cv": 0.04,
        "score": score,
        "accepted_shares": accepted,
        "rejected_shares": rejected,
        "seconds": seconds,
    }


class WinnerTest(unittest.TestCase):
    def setUp(self):
        self.report = {
            "selected_threads": 5,
            "optimizer_profiles": [
                profile("xmrig-auto-baseline", 4, 820, 1200, 760, 7, 1, 120),
                profile("threads-5", 5, 960, 1000, 940, 10, 0, 120),
                profile("threads-6", 6, 910, 1100, 870, 9, 0, 120),
                profile("winner-sustained", 5, 945, 1010, 925, 250, 1, 85600),
            ],
            "cpu_model": "Example Core i5",
            "logical_cpus": 8,
            "architecture": "x86_64",
            "host_os": "macOS",
            "xmrig_version_target": "6.26.0",
            "pool": "pool.example.org:443",
            "tls": True,
            "elapsed_seconds": 86400,
            "actual_24_hour_benchmark": True,
            "status": "MEASURED_POOL_VERIFIED",
            "mean_hs": 942,
            "median_hs": 950,
            "min_hs": 600,
            "max_hs": 1200,
            "accepted_shares": 276,
            "rejected_shares": 2,
            "hashrate_samples": 2000,
        }

    def test_winner_selected_by_score_not_peak(self):
        result = build_winning_configuration(self.report)
        self.assertEqual(result["selected_active_threads"], 5)
        self.assertEqual(result["chosen_search_profile"]["median_hs"], 960)
        self.assertEqual(result["winner_sustained_profile"]["median_hs"], 945)
        self.assertEqual(result["highest_observed_peak"]["threads_observed"], 4)
        self.assertEqual(len(result["all_ranked_tested_profiles"]), 3)
        self.assertTrue(result["full_24_hour_qualified"])
        text = format_winning_configuration(result)
        for needle in ("WINNING CONFIGURATION", "960.00 H/s", "945.00 H/s",
                       "1,200.00 H/s", "TOP PROFILES", "5 threads", "Pool shares"):
            self.assertIn(needle, text)

    def test_incomplete_not_labelled_qualified(self):
        self.report["actual_24_hour_benchmark"] = False
        self.report["status"] = "STOPPED_OR_INCOMPLETE"
        result = build_winning_configuration(self.report)
        self.assertFalse(result["full_24_hour_qualified"])
        self.assertIn("NO", format_winning_configuration(result))

    def test_no_samples_no_fake_winner(self):
        self.report["optimizer_profiles"] = []
        self.report["selected_threads"] = None
        result = build_winning_configuration(self.report)
        self.assertIsNone(result["selected_active_threads"])
        self.assertIsNone(result["chosen_search_profile"])
        self.assertIn("insufficient measured data", format_winning_configuration(result))


if __name__ == "__main__":
    unittest.main()
