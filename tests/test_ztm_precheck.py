import unittest
from unittest.mock import patch
from ztm_precheck import (check_https_source, check_pool_tcp, suggested_zoom,
                          effective_font_zoom, clamp_manual_multiplier)


class PrecheckTests(unittest.TestCase):
    def test_bad_url_rejected(self):
        self.assertEqual(check_https_source("http://example.org").state, "unavailable")
    def test_invalid_pool_port(self):
        self.assertEqual(check_pool_tcp("127.0.0.1", "invalid").state, "offline")
    def test_zoom_rules(self):
        self.assertEqual(suggested_zoom(1366, 768), 1.35)
        self.assertEqual(suggested_zoom(1920, 1080), 1.20)
        self.assertEqual(clamp_manual_multiplier(50), 2.0)
        self.assertEqual(effective_font_zoom(1.20, 1.25), 1.5)


if __name__ == "__main__":
    unittest.main()
