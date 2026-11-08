from fss_feasibility import *
from run_uji2 import recover_C
import numpy as np, pandas as pd, os

os.makedirs("hasil", exist_ok=True)
SEEDS = range(3)
DENSITIES = (0.01, 0.05, 0.10, 0.20, 0.30)

pairs = [("data/4.2.03.tiff", "data/4.2.01.tiff"),   
         ("data/4.2.07.tiff", "data/4.2.05.tiff"),   
         ("data/4.2.01.tiff", "data/4.2.07.tiff")]  

def recover_masked(F1s, F2s, C, m1, m2, Q=Q):
    C = C.astype(np.int32)
    Iq_t, Ir_t = F1s.astype(np.int32) ^ C, F2s.astype(np.int32) ^ C
    Iq_f = np.round(masked_median_fill(Iq_t, m1)).astype(np.int32)
    Ir_f = np.round(masked_median_fill(Ir_t, m2)).astype(np.int32)
    return combine(Iq_f, Ir_f, Q)

def masks(F1s, F2s, C, Q=Q):
    C = C.astype(np.int32)
    gt = lambda F: (F.astype(np.int32) ^ C) > Q - 1                
    ex = lambda F: (F == 0) | (F == 255)                           
    return {"D_C15": (gt(F1s), gt(F2s)),
            "D_0255": (ex(F1s), ex(F2s)),
            "D_union": (gt(F1s) | ex(F1s), gt(F2s) | ex(F2s))}

def cover_stats(C):
    return dict(cover_pct_ge240=100 * np.mean(C >= 240),           
                cover_pct_lt16=100 * np.mean(C < 16))              

def run(pairs, seeds=SEEDS, densities=DENSITIES):
    rows, crow = [], []
    for sp, cp in pairs:
        I, C = load(sp), load(cp)
        crow.append(dict(cover=cp, **cover_stats(C)))
        F1, F2 = share(I, C)
        assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
        for d in densities:
            for seed in seeds:
                rng = np.random.default_rng(seed)
                F1s, t1 = salt_pepper(F1, d, rng)
                F2s, t2 = salt_pepper(F2, d, rng)
                res = {"A": (recover_A(F1s, F2s, C), None),
                       "C_med3": (recover_C(F1s, F2s, C, 3), None)}
                for name, (m1, m2) in masks(F1s, F2s, C).items():
                    res[name] = (recover_masked(F1s, F2s, C, m1, m2), (m1, m2))
                for name, (R, mk) in res.items():
                    r = dict(secret=sp, cover=cp, d=d, seed=seed, skenario=name)
                    r.update(metrics(I, R))
                    if mk is not None:
                        a, b = detection(mk[0], t1), detection(mk[1], t2)
                        r.update(F1_det=a["det_rate"], F1_fp=a["false_pos"],
                                 F2_det=b["det_rate"], F2_fp=b["false_pos"])
                    rows.append(r)
                print("selesai", sp, d, seed, flush=True)
    return pd.DataFrame(rows), pd.DataFrame(crow)

if __name__ == "__main__":
    df, cs = run(pairs)
    df.to_csv("hasil/uji_kelayakan3.csv", index=False)
    cs.to_csv("hasil/cover_ekstrem.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", None)
    print("\n== Statistik cover (persen piksel ekstrem) =="); print(cs.round(2))
    ringkas = (df.groupby(["d", "skenario"])
                 .agg(PSNR=("PSNR", "mean"), SSIM=("SSIM", "mean"), persis=("pct_exact", "mean"),
                      F1_det=("F1_det", "mean"), F1_fp=("F1_fp", "mean"),
                      F2_det=("F2_det", "mean"), F2_fp=("F2_fp", "mean")).round(2))
    print("\n== Ringkasan per d dan skenario =="); print(ringkas)
    ringkas.to_csv("hasil/ringkasan3.csv")
    per = (df[df.skenario.isin(["D_C15", "D_0255", "D_union"])]
             .groupby(["cover", "skenario"]).agg(PSNR=("PSNR", "mean"), F1_det=("F1_det", "mean")).round(2))
    print("\n== Per cover (semua d) =="); print(per)
    per.to_csv("hasil/per_cover3.csv")
