#!/usr/bin/env python3
# Smoke test: run core scripts quickly.
import subprocess, sys
cmds = [
    ["python3","src/compute_C_right.py","--P","500000"],
    ["python3","src/threshold_T0.py","--c","0.25","--kappa","2","--R0","0.125","--C_thin","18.6666667","--C_right","0.569961"],
    ["python3","src/measure_Cthin_star.py","--R0","0.125","--c1","0.6666667","--c","0.25","--kappa","2","--T","1e10","--samples","50","--seed","1"],
    ["python3","src/validate_horizontals.py","--T","1e10","--c","0.25","--kappa","2"],
]
ok = True
for c in cmds:
    print(">>>"," ".join(c))
    if subprocess.call(c) != 0:
        ok=False
print("[smoke] OK" if ok else "[smoke] FAIL")
sys.exit(0 if ok else 1)