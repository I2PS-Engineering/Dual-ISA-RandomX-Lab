import os,sys,unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0,sys.argv[1] if len(sys.argv)>1 else '/mnt/data/ztm_v2_timing_work/base/usr/lib/ztm')
import ztm_engine as e
from ztm_surgical_runtime import cpu_inventory,candidate_profiles,choose_init_threads

class RC3Acceptance(unittest.TestCase):
    def setUp(self):
        self.old4={'logical_cpus':4,'physical_cores':4,'l3_cache_bytes':6291456,'l2_cache_bytes':262144,'memory_available_kb':8192000,'memory_type':'DDR3'}
    def test_limits(self):
        self.assertEqual(e._profile_limits(86400),(7,900))
        self.assertEqual(e.PROFILE_SECONDS,900)
        self.assertEqual(e.TRANSITION_SECONDS,5)
    def test_4core(self):
        x=candidate_profiles(self.old4,3,7)
        self.assertEqual(len(x),3)
        self.assertEqual(len(set(x)),3)
        self.assertNotIn(3,x)
        self.assertEqual(x,candidate_profiles(self.old4,3,11))
    def test_large_host_cap(self):
        host={'logical_cpus':32,'physical_cores':16,'l3_cache_bytes':64*1024*1024,'l2_cache_bytes':8*1024*1024,'memory_available_kb':64*1024*1024,'memory_type':'unknown'}
        x=candidate_profiles(host,16,7)
        self.assertEqual(len(x),6)
        self.assertEqual(len(set(x)),10)
        self.assertNotIn(16,x)
        self.assertEqual(x,candidate_profiles(host,16,11))
    def test_initializer_deterministic(self):
        self.assertEqual(choose_init_threads(self.old4,None),4)
        self.assertEqual(choose_init_threads(self.old4,None),choose_init_threads(self.old4,None))
    def test_inventory_recorded(self):
        inv=cpu_inventory()
        for k in ('cpu_model','physical_cores','logical_cpus','l2_cache_bytes','l3_cache_bytes','memory_type','memory_total_kb','memory_available_kb'):
            self.assertIn(k,inv)
    def test_transition_sequence(self):
        call=[]
        def stop(): call.append('stop');return True
        results=iter([True,True])
        def absent():call.append('absent');return next(results)
        def snooze(n):call.append(('sleep',n))
        e.verify_transition(stop,absent,sleep=snooze)
        self.assertEqual(call,['stop','absent',('sleep',5), 'absent'])
    def test_transition_never_continues_if_miner_alive(self):
        for after in (0,1):
            called=[]
            it=iter(([False] if after==0 else [True,False]))
            def absent():called.append('absent');return next(it)
            with self.assertRaises(e.BenchError):e.verify_transition(lambda:True,absent,sleep=lambda n:called.append('gap'))
            self.assertEqual('gap' in called,after==1)
    def test_failure_when_stop_not_confirmed(self):
        with self.assertRaises(e.BenchError):e.verify_transition(lambda:False,lambda: self.fail('should not scan'))
    def test_unboundlocal_error_gone(self):
        self.assertNotIn('candidate_profiles',e.run_benchmark.__code__.co_varnames)
        self.assertTrue(callable(e.candidate_profiles))
    def test_24h_gate_preserved(self):
        self.assertEqual(e.main(['--plan','--minutes','1440']),0)
        with self.assertRaises(e.BenchError):e.main(['--plan','--minutes','60'])
    def test_gui_controls_and_progress(self):
        import tkinter as tk
        from ztm_gui import ZTMApp
        root=tk.Tk(); app=ZTMApp(root);root.update_idletasks()
        try:
            self.assertTrue(app.benchmark_btn.winfo_ismapped())
            self.assertFalse(app.confirm_power.get())
            self.assertFalse(app.confirm_reward.get())
            sample='[ZTM_PROFILE] {"phase":"threads-3","index":2,"total":4,"active":3,"init":4,"elapsed":65,"target":900}'
            app.append(sample)
            self.assertIn('Profile 2/4',app.profile_live.get())
            self.assertIn('Active 3',app.profile_live.get())
            self.assertIn('01:05 / 15:00',app.profile_live.get())
            self.assertLessEqual(root.winfo_height(),root.winfo_screenheight())
            self.assertLessEqual(root.winfo_width(),root.winfo_screenwidth())
        finally:root.destroy()

if __name__=='__main__':unittest.main(argv=[sys.argv[0]],verbosity=2)
