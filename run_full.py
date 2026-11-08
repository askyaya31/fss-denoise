import sys, os, glob, time
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import median_filter
from fss_feasibility import *
from run_uji2 import recover_C
from run_uji3 import recover_masked
from run_uji4 import gaussian_noise, recover_B

CEPAT = "--cepat" in sys.argv
SEEDS = range(2) if CEPAT else range(10)
DENSITIES = (0.05, 0.10) if CEPAT else (0.01, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30)
SIGMAS = (2, 5) if CEPAT else (1, 2, 5, 10)
OUT = "hasil/full_hasil.csv"

SIPI = [("data/4.2.03.tiff", "data/4.2.01.tiff"),
        ("data/4.2.07.tiff", "data/4.2.05.tiff"),
        ("data/4.2.01.tiff", "data/4.2.07.tiff")]
kodak = sorted(glob.glob("data/kodim*.png"))[:6]           
KODAK = [(kodak[i], kodak[(i + 1) % len(kodak)]) for i in range(len(kodak))] if len(kodak) > 1 else []
PAIRS = [p for p in SIPI + KODAK if os.path.exists(p[0]) and os.path.exists(p[1])]
if CEPAT: PAIRS = PAIRS[:1]

def adaptive_median(img, smax=7):
    out = img.copy()
    for c in range(img.shape[2]):
        z = img[:, :, c]; res = z.copy(); undec = np.ones(z.shape, bool)
        for r in range(1, smax // 2 + 1):
            W = sliding_window_view(np.pad(z, r, mode="reflect"), (2*r+1, 2*r+1)).reshape(*z.shape, -1)
            zmin, zmax, zmed = W.min(-1), W.max(-1), np.median(W, axis=-1)
            a_ok = (zmed > zmin) & (zmed < zmax)                 
            b_ok = (z > zmin) & (z < zmax)                       
            take = undec & a_ok
            res[take] = np.where(b_ok, z, zmed)[take]
            undec &= ~a_ok
        res[undec] = z[undec]                                     
        out[:, :, c] = res
    return out

def recover_Cadapt(F1s, F2s, C):
    return adaptive_median(recover_A(F1s, F2s, C))

def masks_c15_0255(F1s, F2s, C, Q=Q):
    Ci = C.astype(np.int32)
    gt = lambda F: (F.astype(np.int32) ^ Ci) > Q - 1
    ex = lambda F: (F == 0) | (F == 255)
    return (gt(F1s), gt(F2s)), (ex(F1s), ex(F2s))

def one_run(I, C, F1s, F2s, t1, t2):
    (c1, c2), (e1, e2) = masks_c15_0255(F1s, F2s, C)
    res = {"A": (recover_A(F1s, F2s, C), None),
           "B_med3": (recover_B(F1s, F2s, C), None),
           "C_med3": (recover_C(F1s, F2s, C, 3), None),
           "C_adapt": (recover_Cadapt(F1s, F2s, C), None),
           "D_C15": (recover_masked(F1s, F2s, C, c1, c2), (c1, c2)),
           "D_0255": (recover_masked(F1s, F2s, C, e1, e2), (e1, e2))}
    rows = []
    for name, (R, mk) in res.items():
        r = dict(skenario=name); r.update(metrics(I, R))
        if mk is not None:
            a, b = detection(mk[0], t1), detection(mk[1], t2)
            r.update(F1_det=a["det_rate"], F1_fp=a["false_pos"], F2_det=b["det_rate"], F2_fp=b["false_pos"])
        rows.append(r)
    return rows

def sudah_selesai():
    if not os.path.exists(OUT): return set()
    d = pd.read_csv(OUT, usecols=["secret", "cover", "noise", "level", "seed"]).drop_duplicates()
    return set(map(tuple, d.values.tolist()))

if __name__ == "__main__":
    os.makedirs("hasil", exist_ok=True)
    if not PAIRS: sys.exit("Tidak ada pasangan citra yang ditemukan di folder data/.")
    print("Pasangan:", PAIRS); done = sudah_selesai(); t0 = time.time()
    jobs = [("sp", d) for d in DENSITIES] + [("gauss", s) for s in SIGMAS]
    for sp, cp in PAIRS:
        I, C = load(sp), load(cp)
        F1, F2 = share(I, C)
        assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
        for noise, level in jobs:
            for seed in SEEDS:
                key = (sp, cp, noise, level, seed)
                if key in done: continue
                rng = np.random.default_rng(seed)
                gen = salt_pepper if noise == "sp" else gaussian_noise
                F1s, t1 = gen(F1, level, rng); F2s, t2 = gen(F2, level, rng)
                rows = one_run(I, C, F1s, F2s, t1, t2)
                for r in rows: r.update(secret=sp, cover=cp, noise=noise, level=level, seed=seed)
                pd.DataFrame(rows).to_csv(OUT, mode="a", header=not os.path.exists(OUT), index=False)
                print(f"[{time.time()-t0:6.0f}s] {sp} {cp} {noise} {level} seed {seed}", flush=True)
    print("Selesai ->", OUT)
