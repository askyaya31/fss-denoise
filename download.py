import urllib.request, os, time
os.makedirs("data", exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Referer": "https://r0k.us/graphics/kodak/"}

for i in range(1, 7):
    n = f"kodim{i:02d}.png"
    tujuan = f"data/{n}"
    if os.path.exists(tujuan) and os.path.getsize(tujuan) > 100000:
        print("sudah ada", n); continue
    for percobaan in range(3):
        try:
            req = urllib.request.Request(f"https://r0k.us/graphics/kodak/kodak/{n}", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r, open(tujuan, "wb") as f:
                f.write(r.read())
            print("ok", n); break
        except Exception as e:
            print("gagal", n, e, "-> tunggu 20 detik")
            time.sleep(20)
    time.sleep(10)  