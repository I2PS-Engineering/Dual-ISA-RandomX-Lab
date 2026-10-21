import unittest
from unittest.mock import patch
from ztm_heartbeat import Heartbeat,send_heartbeat


class HeartbeatTests(unittest.TestCase):
    def test_payload(self):
        heartbeat=Heartbeat("A7K92","mining",hashrate_hs=1234.5,cpu_percent=70)
        self.assertEqual(heartbeat.as_payload()["hashrate_hs"],1234.5)
        self.assertNotIn("temperature_c",heartbeat.as_payload())
    def test_invalid(self):
        with self.assertRaises(ValueError):
            Heartbeat("A7K92","mining",cpu_percent=120).as_payload()
    def test_refuse_unapproved_reporting(self):
        with self.assertRaises(PermissionError):
            send_heartbeat("https://example.test","x"*64,Heartbeat("A7K92","idle"),consent=False)
    def test_refuse_insecure_endpoint(self):
        with self.assertRaises(ValueError):
            send_heartbeat("http://example.test","x"*64,Heartbeat("A7K92","idle"),consent=True)


if __name__=="__main__":
    unittest.main()
