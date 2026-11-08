from fss_feasibility import *
import numpy as np, pandas as pd, os, sys
from scipy.ndimage import median_filter

os.makedirs("hasil", exist_ok=True)
SEEDS = range(3)
DENSITIES = (0.01, 0.05, 0.10, 0.20, 0.30)

pairs = [("data/4.2.03.tiff", "data/4.2.01.tiff"),   
         ("data/4.2.07.tiff", "data/4.2.05.tiff"),  
         ("data/4.2.01.tiff", "data/4.2.07.tiff")]   

def recover_C(F1s, F2s, C, size=3):
    A = recover_A(F1s, F2s, C)
    return np.stack([median_filter(A[:, :, c], size=size, mode="reflect")
                     for c in range(3)], axis=2)

def get_pairs():
    return pairs

def run(pairs, seeds=SEEDS, densities=DENSITIES):
    rows = []
    for sp, cp in pairs:
        I, C = load(sp), load(cp)
        F1, F2 = share(I, C)
        assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
        for d in densities:
            for seed in seeds:
                rng = np.random.default_rng(seed)
                F1s, t1 = salt_pepper(F1, d, rng)
                F2s, t2 = salt_pepper(F2, d, rng)
                res = {"A": recover_A(F1s, F2s, C),
                       "C_med3": recover_C(F1s, F2s, C, 3)}
                Dm, m1, m2 = recover_D(F1s, F2s, C, ir_mode="median")
                Dc, _, _ = recover_D(F1s, F2s, C, ir_mode="const")
                res["D_irmedian"], res["D_irconst"] = Dm, Dc
                det1, det2 = detection(m1, t1), detection(m2, t2)
                for name, R in res.items():
                    r = dict(secret=sp, cover=cp, d=d, seed=seed, skenario=name)
                    r.update(metrics(I, R))
                    if name.startswith("D"):
                        r.update(F1_det=det1["det_rate"], F1_fp=det1["false_pos"],
                                 F2_det=det2["det_rate"], F2_fp=det2["false_pos"])
                    rows.append(r)
                print("selesai", sp, d, seed, flush=True)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = run(pairs)
    df.to_csv("hasil/uji_kelayakan2.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", None)
    ringkas = (df.groupby(["d", "skenario"])
                 .agg(PSNR=("PSNR", "mean"), SSIM=("SSIM", "mean"),
                      persis=("pct_exact", "mean"),
                      F1_det=("F1_det", "mean"), F2_det=("F2_det", "mean"))
                 .round(2))
    print(ringkas)
    ringkas.to_csv("hasil/ringkasan2.csv")
