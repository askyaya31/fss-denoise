import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from skimage.metrics import structural_similarity as ssim
from PIL import Image

Q = 16

def share(I, C, Q=Q):
    I = I.astype(np.int32); C = C.astype(np.int32)
    Iq, Ir = I // Q, I % Q
    F1 = (Iq ^ C).astype(np.uint8)
    F2 = (Ir ^ C).astype(np.uint8)
    return F1, F2

def combine(Iq_t, Ir_t, Q=Q):
    I = Iq_t.astype(np.int32) * Q + Ir_t.astype(np.int32)   
    return np.clip(I, 0, 255).astype(np.uint8)

def recover_A(F1s, F2s, C, Q=Q):                             
    C = C.astype(np.int32)
    return combine(F1s.astype(np.int32) ^ C, F2s.astype(np.int32) ^ C, Q)

def salt_pepper(F, d, rng):
    out = F.copy()
    hit = rng.random(F.shape) < d
    salt = rng.random(F.shape) < 0.5
    out[hit & salt] = 255
    out[hit & ~salt] = 0
    truth = out != F          
    return out, truth

def masked_median_fill(V, bad, rmax=3, fallback=7):
    V = V.astype(np.float64); out = V.copy(); todo = bad.copy()
    for r in range(1, rmax + 1):
        if not todo.any(): break
        X = np.where(bad, np.nan, V)
        for c in range(V.shape[2]):
            P = np.pad(X[:, :, c], r, mode="reflect")
            W = sliding_window_view(P, (2*r+1, 2*r+1))
            ys, xs = np.where(todo[:, :, c])
            if len(ys) == 0: continue
            win = W[ys, xs].reshape(len(ys), -1)
            valid = ~np.isnan(win).all(axis=1)
            med = np.full(len(ys), np.nan)
            med[valid] = np.nanmedian(win[valid], axis=1)
            ok = valid
            out[ys[ok], xs[ok], c] = med[ok]
            t = todo[:, :, c]; t[ys[ok], xs[ok]] = False
    out[todo] = fallback
    return out

def recover_D(F1s, F2s, C, Q=Q, ir_mode="median"):
    C = C.astype(np.int32)
    Iq_t = F1s.astype(np.int32) ^ C
    Ir_t = F2s.astype(np.int32) ^ C
    m1, m2 = Iq_t > Q - 1, Ir_t > Q - 1                       
    Iq_f = masked_median_fill(Iq_t, m1)
    if ir_mode == "median":
        Ir_f = masked_median_fill(Ir_t, m2)
    else:                                                      
        Ir_f = np.where(m2, 7, Ir_t).astype(np.float64)
    Iq_f = np.round(Iq_f).astype(np.int32); Ir_f = np.round(Ir_f).astype(np.int32)
    return combine(Iq_f, Ir_f, Q), m1, m2

def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return float("inf") if mse == 0 else 10 * np.log10(255**2 / mse)

def metrics(I, R):
    return dict(PSNR=psnr(I, R),
                SSIM=ssim(I, R, channel_axis=2, data_range=255),
                pct_exact=100 * np.mean(I == R))

def detection(mask, truth):
    tp = (mask & truth).sum()
    return dict(det_rate=100 * tp / max(truth.sum(), 1),
                false_pos=100 * (mask & ~truth).sum() / max((~truth).sum(), 1))

def load(path, size=(512, 512)):
    return np.array(Image.open(path).convert("RGB").resize(size))  

if __name__ == "__main__":
    import sys
    from skimage import data
    from skimage.transform import resize
    I = (resize(data.astronaut(), (512, 512)) * 255).astype(np.uint8)
    C = (resize(data.chelsea(), (512, 512)) * 255).astype(np.uint8)
    F1, F2 = share(I, C)
    assert np.array_equal(recover_A(F1, F2, C), I), "lossless gagal"
    print("Lossless OK. PSNR F1,F2 vs C:", round(psnr(C, F1),1), round(psnr(C, F2),1))
    for d in (0.05, 0.10):
        for seed in range(3):
            rng = np.random.default_rng(seed)
            F1s, t1 = salt_pepper(F1, d, rng); F2s, t2 = salt_pepper(F2, d, rng)
            A = recover_A(F1s, F2s, C)
            D, m1, m2 = recover_D(F1s, F2s, C)
            print(f"d={d} seed={seed} A:{metrics(I,A)}  D:{metrics(I,D)}  det_F1:{detection(m1,t1)}")
