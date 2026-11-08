from fss_feasibility import *
import numpy as np, pandas as pd, os

os.makedirs("hasil", exist_ok=True)

pairs = [("data/4.2.03.tiff", "data/4.2.01.tiff"),   
         ("data/4.2.07.tiff", "data/4.2.05.tiff"),   
         ("data/4.2.01.tiff", "data/4.2.07.tiff")]  

rows = []
for sp, cp in pairs:
    I, C = load(sp), load(cp)
    F1, F2 = share(I, C)
    assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
    for d in (0.05, 0.10):
        for seed in range(3):
            rng = np.random.default_rng(seed)
            F1s, t1 = salt_pepper(F1, d, rng)
            F2s, t2 = salt_pepper(F2, d, rng)
            A = recover_A(F1s, F2s, C)
            D, m1, m2 = recover_D(F1s, F2s, C)
            r = dict(secret=sp, cover=cp, d=d, seed=seed)
            r.update({f"A_{k}": v for k, v in metrics(I, A).items()})
            r.update({f"D_{k}": v for k, v in metrics(I, D).items()})
            r.update({f"F1_{k}": v for k, v in detection(m1, t1).items()})
            rows.append(r)

df = pd.DataFrame(rows)
df.to_csv("hasil/uji_kelayakan.csv", index=False)
print(df.groupby(["secret", "cover", "d"]).mean(numeric_only=True).round(2))