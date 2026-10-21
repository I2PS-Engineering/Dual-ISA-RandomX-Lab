"""Tests for no-cost local ZTM intelligence ingestion and dashboard."""
import json
import tempfile
import unittest
from pathlib import Path
from ztm_local_admin import database, import_report, import_path, dashboard_data, normalize

def sample(run_id="trial-001", worker_id="A7K92"):
    return {
        "worker":{"ztm_id":worker_id,"version":"SRP1V3","os":"L","architecture":"X64"},
        "hardware":{"cpu_model":"Intel Core i3-8100","ram_bytes":8589934592},
        "benchmark":{"run_id":run_id,"qualifying":True},
        "profiles":[{"threads":1},{"threads":2}],
        "winner":{"threads":2,"sustained_mean_hs":938.9,
            "sustained_median_hs":932.5,"highest_recorded_hs":1120},
        "accepted_shares":1524,"rejected_shares":4
    }

class DashboardDataTests(unittest.TestCase):
    def test_import_deduplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            with database(Path(folder)/"admin.db") as conn:
                self.assertTrue(import_report(conn,sample()))
                self.assertFalse(import_report(conn,sample()))
                self.assertEqual(dashboard_data(conn)["summary"]["runs"],1)
                self.assertEqual(dashboard_data(conn)["summary"]["workers"],1)
                self.assertEqual(dashboard_data(conn)["runs"][0]["active_threads"],2)

    def test_multiple_runs_same_worker(self):
        with tempfile.TemporaryDirectory() as folder:
            with database(Path(folder)/"admin.db") as conn:
                import_report(conn,sample("first"))
                import_report(conn,sample("second"))
                self.assertEqual(dashboard_data(conn)["summary"]["runs"],2)
                self.assertEqual(dashboard_data(conn)["summary"]["workers"],1)
                self.assertEqual(dashboard_data(conn)["summary"]["qualified"],2)

    def test_import_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder); data=base/"reports";data.mkdir()
            (data/"first.json").write_text(json.dumps(sample()))
            (data/"second.json").write_text(json.dumps(sample("second")))
            (data/"broken.json").write_text("{broken")
            with database(base/"admin.db") as conn:
                summary=import_path(conn,data)
                self.assertEqual(summary,{"imported":2,"duplicates":0,"invalid":1})

    def test_invalid_id_and_negative_shares(self):
        with self.assertRaises(ValueError):
            normalize(sample(worker_id="BAD!"))
        document=sample()
        document["rejected_shares"]=-1
        with self.assertRaises(ValueError):normalize(document)

    def test_legacy_report_stays_unverified_identity(self):
        report={"cpu_model":"Intel(R) Core i3","winning_configuration":{"threads":2},
                "actual_24_hour_benchmark":True,"runid":"legacy-1"}
        parsed=normalize(report)
        self.assertEqual(parsed["worker_id"],"LEGACY")
        self.assertEqual(parsed["active_threads"],2)

if __name__=="__main__":unittest.main()
