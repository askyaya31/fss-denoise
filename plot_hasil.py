import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("hasil/full_hasil.csv")
STYLE = {"A": "k--", "B_med3": "c:", "C_med3": "b-", "C_adapt": "g-", "D_C15": "r-o", "D_0255": "m-s"}
XL = {"sp": "Kepadatan salt-and-pepper (%)", "gauss": "Simpangan baku Gaussian (σ)"}

for noise in ("sp", "gauss"):
    sub = df[df.noise == noise].copy()
    if sub.empty: continue
    per_img = sub.groupby(["secret", "cover", "level", "skenario"])[["PSNR", "SSIM"]].mean().reset_index()
    for metric in ("PSNR", "SSIM"):
        g = per_img.groupby(["level", "skenario"])[metric].agg(["mean", "std"]).reset_index()
        plt.figure(figsize=(6.5, 4.2))
        for sk, st in STYLE.items():
            s = g[g.skenario == sk].sort_values("level")
            if s.empty: continue
            x = s.level * 100 if noise == "sp" else s.level
            plt.errorbar(x, s["mean"], yerr=s["std"].fillna(0), fmt=st, label=sk, capsize=2, markersize=4)
        plt.xlabel(XL[noise]); plt.ylabel(metric + (" (dB)" if metric == "PSNR" else ""))
        plt.grid(alpha=.3); plt.legend(fontsize=8); plt.tight_layout()
        plt.savefig(f"hasil/grafik_{noise}_{metric.lower()}.png", dpi=200); plt.close()

for noise in ("sp", "gauss"):
    sub = df[df.noise == noise]
    if sub.empty: continue
    t = sub.groupby(["level", "skenario"]).agg(PSNR=("PSNR", "mean"), PSNR_sd=("PSNR", "std"),
            SSIM=("SSIM", "mean"), persis=("pct_exact", "mean"),
            F1_det=("F1_det", "mean"), F1_fp=("F1_fp", "mean")).round(2)
    t.to_csv(f"hasil/tabel_{noise}.csv"); print(noise); print(t)
