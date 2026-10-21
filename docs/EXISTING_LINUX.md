# Existing Ubuntu users — ZTM-SRP1V2

You do not need to reinstall Ubuntu to install ZTM-SRP1V2.

## Install

Close any active ZTM/XMRig session.

Then run the verified stable installer as your normal Ubuntu desktop user:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V2/install-ztm-srp1v2.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="428cd6c872f81325c3b18de8c04a88d3f085daec5795f7cf4723a881734020dd","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

ZTM verifies the stable package before installation.

The current stable release targets Ubuntu Desktop x86-64.

Installation does not automatically begin the benchmark. CPU work starts only after preparation, both acknowledgements and explicit Start.
