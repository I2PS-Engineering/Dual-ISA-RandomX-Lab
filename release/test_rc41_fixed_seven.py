"""Fixed seven-profile and XMRig affinity regression tests for RC4.1."""
import unittest
from ztm_affinity_profiles import (
    ProfilePlanError, generate_affinity_profiles, parse_cpu_list,
    set_xmrig_affinity_config, _ranking
)


class FixedSevenProfiles(unittest.TestCase):
    @staticmethod
    def four():
        return {
            'allowed_cpu_ids':[0,1,2,3], 'logical_cpus':4, 'physical_cores':2,
            'core_groups':[[0,2],[1,3]],
            'l3_cache_bytes':6*1024*1024,
            'l3_domains':[{'cpu_ids':[0,1,2,3], 'size_bytes':6*1024*1024}],
            'l2_domains':[{'cpu_ids':[0,2], 'size_bytes':256*1024},
                          {'cpu_ids':[1,3], 'size_bytes':256*1024}],
            'numa_cpu_groups':[[0,1,2,3]]
        }

    def test_four_cpu_always_seven_including_original_baseline(self):
        host=self.four()
        for auto in (1,2,3,4):
            p=generate_affinity_profiles(host,auto)
            self.assertEqual(len(p),6)
            self.assertEqual(len({tuple(x['cpu_ids']) for x in p}),6)
            self.assertTrue(all(x['threads']==len(x['cpu_ids']) for x in p))
            self.assertEqual(p,generate_affinity_profiles(host,auto))

    def test_three_permitted_cpu_ids_support_six_unique_affinities(self):
        host={'allowed_cpu_ids':[1,3,7], 'core_groups':[[1],[3],[7]],
              'l3_cache_bytes':4*1024*1024}
        p=generate_affinity_profiles(host,2)
        self.assertEqual(len(p),6)
        self.assertEqual(len({tuple(x['cpu_ids']) for x in p}),6)
        self.assertTrue(all(set(x['cpu_ids'])<={1,3,7} for x in p))

    def test_two_cpu_constraint_fails_closed(self):
        with self.assertRaisesRegex(ProfilePlanError,'>=3'):
            generate_affinity_profiles({'allowed_cpu_ids':[0,1]},1)

    def test_sparse_cpu_ids_and_cgroups(self):
        host={'allowed_cpu_ids':[4,8,16,20],
              'core_groups':[[4,16],[8,20]],
              'l3_cache_bytes':8*1024*1024}
        p=generate_affinity_profiles(host,2)
        self.assertEqual(len(p),6)
        self.assertTrue(all(set(v['cpu_ids'])<={4,8,16,20} for v in p))
        for v in p:
            config={'cpu':{'rx':[-1]},'autosave':True}
            count=set_xmrig_affinity_config(config,v['cpu_ids'],allowed={4,8,16,20})
            self.assertEqual(count,v['threads'])
            self.assertEqual(config['cpu']['rx'],v['cpu_ids'])
            self.assertFalse(config['autosave'])

    def test_xmrig_affinity_rejects_invalid_ids(self):
        for cpu_ids in ([0,0],[],[-1],[0,99],['1',2]):
            with self.assertRaises(ProfilePlanError):
                set_xmrig_affinity_config({},cpu_ids,allowed={0,1,2,3})

    def test_smt_siblings_have_penalty(self):
        host=self.four()
        core_groups=[(0,2),(1,3)]
        self.assertGreater(_ranking((0,2),2,core_groups,host),
                           _ranking((0,1),2,core_groups,host))

    def test_cpuset_parsing(self):
        self.assertEqual(parse_cpu_list('0-2,7,9-10'),[0,1,2,7,9,10])
        with self.assertRaises(ProfilePlanError):
            parse_cpu_list('0-foo')

    def test_large_host_is_bounded(self):
        h={'allowed_cpu_ids':list(range(64)),
           'core_groups':[[i,i+32] for i in range(32)],
           'l3_cache_bytes':64*1024*1024}
        p=generate_affinity_profiles(h,24)
        self.assertEqual(len(p),6)
        self.assertEqual(len(set(tuple(x['cpu_ids']) for x in p)),6)


if __name__=='__main__':
    unittest.main()
