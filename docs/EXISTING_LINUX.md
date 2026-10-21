# Existing Ubuntu users — ZTM-SRP1V1

You do not need to reinstall Ubuntu to install ZTM-SRP1V1.

## Install

Close any active ZTM/XMRig session.

Then run the verified stable installer as your normal Ubuntu desktop user:

```bash
python3 -c 'import hashlib,subprocess,urllib.request;u="https://github.com/I2PS-Engineering/ZTM_Benchmark/releases/download/ZTM-SRP1V1/install-ztm-srp1v1.sh";b=urllib.request.urlopen(u,timeout=60).read();assert hashlib.sha256(b).hexdigest()=="ec069736a9e683b3e6294a4af066963a0c21ae2d5e835157a483c4c2b31b85ff","SECURITY STOP: installer checksum mismatch";subprocess.run(["bash","-s"],input=b,check=True)'
```

ZTM verifies the stable package before installation.

The current stable release targets Ubuntu Desktop x86-64.

Installation does not automatically begin the benchmark. CPU work starts only after preparation, both acknowledgements and explicit Start.
