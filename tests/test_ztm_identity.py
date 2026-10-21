import json
import tempfile
import unittest
from pathlib import Path
from ztm_identity import load_or_create, worker_name, mining_safe_worker_name, hardware_snapshot


class IdentityTests(unittest.TestCase):
    def test_persistence_and_permissions(self):
        with tempfile.TemporaryDirectory() as d:
            a = load_or_create(d)
            b = load_or_create(d)
            self.assertEqual(a, b)
            self.assertEqual(len(a["ztm_id"]), 5)
            self.assertEqual(Path(d, "worker_identity.json").stat().st_mode & 0o777, 0o600)
    def test_os_arch_and_version(self):
        data = {"ztm_id": "A7K92"}
        self.assertEqual(worker_name("SRP1V3", data, "L", "X64"),
                         "ZTM-SRP1V3-L/X64-A7K92")
        self.assertEqual(worker_name("SRP1V3", data, "M", "ARM64"),
                         "ZTM-SRP1V3-M/ARM64-A7K92")
        self.assertEqual(mining_safe_worker_name("SRP1V3", data, "M", "ARM64"),
                         "ZTM-SRP1V3-M_ARM64-A7K92")
    def test_inventory_excludes_secrets(self):
        encoded = json.dumps(hardware_snapshot())
        for secret_field in ("wallet", "password", "serial_number", "mac_address", "ip_address"):
            self.assertNotIn('"' + secret_field + '"', encoded)


if __name__ == "__main__":
    unittest.main()
