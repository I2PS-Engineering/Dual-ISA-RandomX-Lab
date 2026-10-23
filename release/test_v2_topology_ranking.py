"""V2 topology-ranking regression tests. Run against installed release module."""
import unittest
from ztm_surgical_runtime import candidate_profiles, choose_init_threads, _ranked_counts

class TopologyRanking(unittest.TestCase):
    def test_four_core_distinct(self):
        h={'logical_cpus':4,'physical_cores':4,'l3_cache_bytes':6*1024*1024}
        p=candidate_profiles(h,3,11)
        self.assertEqual(len(p),3)
        self.assertEqual(set(p),{1,2,4})
        self.assertEqual(p,candidate_profiles(h,3,11))
    def test_smt_prefers_physical_without_cache_penalty(self):
        h={'logical_cpus':16,'physical_cores':8,'l3_cache_bytes':32*1024*1024}
        p=candidate_profiles(h,8,11)
        self.assertEqual(len(p),10)
        self.assertEqual(len(set(p)),10)
        self.assertNotIn(8,p)
        self.assertLess(p.index(7),p.index(16))
    def test_initializer_not_random(self):
        h={'logical_cpus':16,'physical_cores':8,'l3_cache_bytes':32*1024*1024}
        self.assertEqual(choose_init_threads(h,8),8)
    def test_small_cache_penalty(self):
        h={'logical_cpus':8,'physical_cores':4,'l3_cache_bytes':4*1024*1024}
        p=candidate_profiles(h,2,11)
        self.assertEqual(len(p),7)
        self.assertEqual(len(set(p)),7)

if __name__=='__main__':
    unittest.main()
