from fss_feasibility import *
from run_uji2 import recover_C
import numpy as np, pandas as pd, os
from scipy.ndimage import median_filter

os.makedirs("hasil", exist_ok=True)
SEEDS = range(3)
SIGMAS = (1, 2, 5, 10)

pairs = [("data/4.2.03.tiff", "data/4.2.01.tiff"),   
         ("data/4.2.07.tiff", "data/4.2.05.tiff"),   
         ("data/4.2.01.tiff", "data/4.2.07.tiff")]   

def gaussian_noise(F, sigma, rng):
    out = np.clip(np.rint(F.astype(np.float64) + rng.normal(0, sigma, F.shape)), 0, 255).astype(np.uint8)
    return out, out != F          

def recover_B(F1s, F2s, C, size=3):
    f = lambda F: np.stack([median_filter(F[:, :, c], size=size, mode="reflect") for c in range(3)], axis=2)
    return recover_A(f(F1s), f(F2s), C)

def run(pairs, seeds=SEEDS, sigmas=SIGMAS):
    rows = []
    for sp, cp in pairs:
        I, C = load(sp), load(cp)
        F1, F2 = share(I, C)
        assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
        for s in sigmas:
            for seed in seeds:
                rng = np.random.default_rng(seed)
                F1s, t1 = gaussian_noise(F1, s, rng)
                F2s, t2 = gaussian_noise(F2, s, rng)
                Dm, m1, m2 = recover_D(F1s, F2s, C, ir_mode="median")
                Dc, _, _ = recover_D(F1s, F2s, C, ir_mode="const")
                res = {"A": recover_A(F1s, F2s, C),
                       "B_med3": recover_B(F1s, F2s, C),
                       "C_med3": recover_C(F1s, F2s, C, 3),
                       "D_C15": Dm, "D_C15_const": Dc}
                a, b = detection(m1, t1), detection(m2, t2)
                for name, R in res.items():
                    r = dict(secret=sp, cover=cp, sigma=s, seed=seed, skenario=name,
                             pct_berubah_F1=100 * t1.mean())
                    r.update(metrics(I, R))
                    if name.startswith("D"):
                        r.update(F1_det=a["det_rate"], F1_fp=a["false_pos"],
                                 F2_det=b["det_rate"], F2_fp=b["false_pos"])
                    rows.append(r)
                print("selesai", sp, s, seed, flush=True)
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = run(pairs)
    df.to_csv("hasil/uji_kelayakan4.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", None)
    ringkas = (df.groupby(["sigma", "skenario"])
                 .agg(PSNR=("PSNR", "mean"), SSIM=("SSIM", "mean"), persis=("pct_exact", "mean"),
                      F1_berubah=("pct_berubah_F1", "mean"),
                      F1_det=("F1_det", "mean"), F1_fp=("F1_fp", "mean"),
                      F2_det=("F2_det", "mean")).round(2))
    print(ringkas)
    ringkas.to_csv("hasil/ringkasan4.csv")
    per = (df.groupby(["cover", "sigma", "skenario"]).agg(PSNR=("PSNR", "mean")).round(2).unstack("skenario"))
    print(per); per.to_csv("hasil/per_cover4.csv")
