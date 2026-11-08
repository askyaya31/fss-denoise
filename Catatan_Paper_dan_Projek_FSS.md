# Catatan Friendly Secret Sharing + Denoising

## 1. Overview Projek

**Judul kerja:** Analisis Penerapan Filter Denoising pada Metode Friendly Secret Sharing Berbasis Integer terhadap Serangan Gaussian dan Salt-and-Pepper Noise

Paper acuan (Prasetyo dkk., APICS 2022) menyembunyikan citra rahasia menjadi dua citra bagian (F1, F2) yang tampak seperti citra sampul, dan citra rahasia bisa dipulihkan **persis** selama F1 dan F2 tidak berubah. Paper itu sendiri menyebut metodenya lemah terhadap noise, tetapi hanya menampilkannya secara visual pada satu pasang citra. Kita **mengukur kelemahan itu dengan angka** (PSNR, SSIM, % piksel pulih persis) pada banyak pasang citra dan tingkat noise, lalu mencoba perbaikan sederhana (filter sebelum, sesudah, dan berbasis deteksi). Semuanya program Python dengan data citra standar, tanpa deep learning.

**Dasar aturan dosen** (dari catatan sesi lain, ⚠️ cek ke slide asli): slide 16 dan 17 membolehkan mencari kelemahan penelitian yang ada tanpa rumus atau metode baru, asal tidak hanya mengganti dataset; slide 26 menyebut untuk S1 cukup mengungkap kelemahan secara empiris, solusi tidak wajib.

---

## 2. Pembaruan (Novelty) Kita

| # | Pembaruan | Pembeda dari |
|---|---|---|
| 1 | **Angka ketahanan noise**: PSNR, SSIM, % piksel persis, pada banyak pasang citra, 7 tingkat salt-and-pepper, 4 tingkat Gaussian, 10 seed | Paper acuan: satu pasang citra, noise hanya ditampilkan visual |
| 2 | **Skenario penempatan filter A–D** dibandingkan pada citra rusak yang sama | Paper acuan: tidak ada upaya perbaikan |
| 3 | **Deteksi lewat citra sampul** (aturan "F\* XOR C > 15": empat bit kiri F harus sama dengan C untuk Q = 16) dibanding deteksi biasa 0/255 | Skema tahan noise lain memakai redundansi tambahan (kode koreksi galat) |
| 4 | **Penyebab kegagalan Gaussian ditunjukkan dengan angka** | Paper acuan hanya menyebut "tidak tahan AWGN" |
| 5 | Meluruskan pernyataan paper acuan yang tampak bertentangan (Bagian IV-C: menderita S&P, tidak tahan AWGN, tetapi "cocok untuk S&P") | – |

**Klaim aman:** "sepengetahuan kami, hasil pemulihan citra rahasia secara kuantitatif di bawah noise belum dilaporkan pada paper acuan". Jangan menulis "pertama" atau "baru".

---

## 3. Per Paper: Membahas Apa, Kita Beda di Mana

### Paper 1: Prasetyo, Chamnongthai, Intyanto (2022), APICS — **paper acuan utama**
- **Membahas:** friendly secret sharing dengan representasi integer dan XOR. Citra rahasia dipecah per piksel menjadi hasil bagi `Iq = I div Q` dan sisa `Ir = I mod Q`, lalu `F1 = Iq XOR C`, `F2 = Ir XOR C`. Pemulihan: `I~ = (F1 XOR C)·Q + (F2 XOR C)`. Lossless bila F1 dan F2 tidak berubah.
- **Hasil:** Q = 16 terbaik (F1 32,01 dB / SSIM 0,947, F2 31,86 dB / 0,944), pemulihan PSNR tak hingga. Q = 64: F1 44,32 dB tetapi F2 19,77 dB.
- **Serangan:** cropping, salt-and-pepper, AWGN, **hanya gambar tanpa angka**, satu pasang citra.
- **Kelemahan yang diakui:** lemah terhadap S&P, tidak tahan AWGN.
- **Projek kita:** angka PSNR/SSIM/% persis pada banyak pasang citra dan tingkat noise, ditambah skenario perbaikan.
- **Dipakai untuk:** skema dasar, rumus, nilai Q = 16, dasar celah.

### Paper 2: Prasetyo & Prayuda (2022), IJACSA 13(12) — Fast Comprehensive Secret Sharing
- **Membahas:** secret sharing (k,n) berbasis polinomial dengan kompresi sederhana (companding) menggantikan color palette; bagian tampak seperti citra sampul; citra rahasia dan sampul bisa dipulihkan.
- **Fokus:** kecepatan. Evaluasi hanya PSNR/SSIM terhadap jumlah bit rahasia (r), **tanpa serangan noise**.
- **Future work yang disebut:** keamanan (enkripsi atau hashing), video, multi-secret.
- **Projek kita:** skema lebih sederhana (bagi, XOR, gabung), fokus ketahanan noise.
- **Dipakai untuk:** silsilah friendly secret sharing dari penulis yang sama.

### Paper 3: Saha dkk. (2023), IEEE Access vol. 11 — Survei Secret Image Sharing
- **Membahas:** peninjauan skema SIS, sifat yang dibandingkan (lossless, bagian bermakna, verifiable, dan lainnya).
- **Temuan penting:** di bagian tantangan terbuka (hlm. 98356), SIS dapat terkena noise, kompresi, dan cropping, sehingga perlu skema yang tahan distorsi. Teks survei tidak membahas median, filter, denoising, restorasi, atau inpainting.
- **Dipakai untuk:** motivasi di Pendahuluan (ketahanan noise adalah tantangan terbuka umum).
- **Jangan dipakai** sebagai bukti bahwa tidak ada yang mengerjakan setelah 2023.

### Paper 4: Chattopadhyay dkk. (2024), Computer Science Review 51 — Survei Secret Sharing
- **Membahas:** threshold secret sharing secara umum (Shamir, CRT, multi-secret, verifiable, kuantum, DNA). SIS hanya disinggung singkat.
- **Dipakai untuk:** latar belakang dasar (definisi, Shamir, CRT). Tidak untuk argumen celah.

### Paper 5: *A Strongly Robust Secret Image Sharing Algorithm Based on QR Codes* (MDPI Algorithms 2025, 18(9):535)
- **Membahas:** SIS tahan noise dengan kode Reed–Solomon, error mask, dan inpainting, memakai pembawa kode QR. Menguji salt-and-pepper, Gaussian, kompresi, dan noise campuran. ⚠️ batas angka (lossless sampai d ≤ 2%, PSNR ≥ 40 dB sampai d ≈ 8%) dari ringkasan, cek ke PDF.
- **Beda dengan kita:** skema polinomial threshold dengan redundansi 100%, citra uji 128×128 dan 256×256. Kita memakai skema integer-XOR tanpa redundansi, mengukur kerapuhan, dan mencoba perbaikan di sisi penerima.
- **Dipakai untuk:** **pembanding terdekat.** Gap "ketahanan noise pada SIS bermakna" **tidak boleh diklaim kosong.**

### Paper 6: Srinivasan & Ebenezer (2007), IEEE SPL — Decision-Based Algorithm untuk impuls kepadatan tinggi
- **Membahas:** pemulihan noise impuls dengan memeriksa piksel 0/255 lalu mengganti dengan median atau tetangga.
- **Hubungan dengan kita:** skenario **D_0255 pada dasarnya ide ini**, diterapkan di domain Iq/Ir. Kutip dengan jelas, jangan klaim baru. Materi pertemuan 9 silabus.

### Paper 7: Hwang & Haddad (1995) dan filter median lain — Adaptive Median Filter
- **Membahas:** median yang jendelanya diperbesar bertahap dan hanya mengganti piksel yang tampak sebagai impuls.
- **Dipakai untuk:** pembanding skenario C_adapt. Materi pertemuan 8 silabus.

### Paper 8: Karya friendly secret sharing dosen lain (ISESD 2021, ISPACS 2019, ICCE-Taiwan 2020)
- **Membahas:** silsilah friendly SS (CRT dan Boolean, XOR-ed progressive, multiple secret sharing).
- **Status:** tidak menguji noise menurut pembacaan kelompok. ⚠️ cek ke PDF sebelum menulis klaim.

---

## 4. Tabel Perbandingan Singkat

| Paper | Masalah | Metode | Noise diuji? | Beda dengan kita |
|---|---|---|---|---|
| 1 APICS 2022 | Friendly SS integer-XOR | Bagi, XOR | Visual, 1 pasang citra | Kita ukur dengan angka, banyak citra, ada perbaikan |
| 2 IJACSA 2022 | (k,n) SS polinomial | Polinomial + companding | Tidak | Skema berbeda, fokus kecepatan |
| 3 Saha 2023 | Survei SIS | – | Noise disebut tantangan terbuka | Motivasi |
| 4 Chattopadhyay 2024 | Survei SS umum | – | – | Latar belakang |
| 5 QR Codes 2025 | SIS tahan noise | Reed–Solomon + inpainting | Ya | Kita tanpa redundansi, skema berbeda |
| 6 DBA 2007 | Impuls kepadatan tinggi | Decision-based median | Ya | D_0255 pada domain Iq/Ir |
| 7 AMF 1995 | Impuls | Adaptive median | Ya | Pembanding C_adapt |

---

## 5. Detail Projek Kita

### Model dan alasan noise merusak
- `Iq = I div 16`, `Ir = I mod 16`, `F1 = Iq XOR C`, `F2 = Ir XOR C`, `I~ = (F1 XOR C)·16 + (F2 XOR C)`.
- Dengan Q = 16, Iq dan Ir selalu 0–15, jadi F1 dan F2 asli selalu punya **empat bit kiri sama dengan C**.
- Kesalahan di F1 dikalikan 16 saat pemulihan, dan satu perubahan kecil bisa membalik beberapa bit saat di-XOR. Karena itu noise kecil pun merusak hasil.

### Skenario

| Kode | Isi |
|---|---|
| **A** | Tanpa perbaikan (baseline replikasi) |
| **B_med3** | Median 3×3 pada F1\*, F2\* sebelum pemulihan |
| **C_med3** | Median 3×3 pada citra pulihan |
| **C_adapt** | Adaptive median (jendela sampai 7×7) pada citra pulihan |
| **D_C15** | Deteksi "(F\* XOR C) > 15", ganti piksel rusak dengan median tetangga sehat di domain Iq/Ir |
| **D_0255** | Deteksi nilai 0 atau 255 (tanpa C), penggantian sama |

### Dataset

| Bagian | Isi |
|---|---|
| Sumber | USC-SIPI Misc 4.2.xx (4.2.01, 4.2.03, 4.2.05, 4.2.07 yang tersedia) dan Kodak (hanya kodim01 dan kodim02 berhasil diunduh otomatis) |
| Format | Citra berwarna 8 bit per kanal, 512×512, disimpan PNG |
| Noise | Dibangkitkan pada **F1 dan F2** secara independen (bukan pada citra rahasia), seed dicatat |
| Salt-and-pepper | d = 1, 5, 7, 10, 15, 20, 30% |
| Gaussian | σ = 1, 2, 5, 10 (skala 0–255) |
| Parameter | Q = 16, 10 seed |
| **Yang wajib dicatat** | Jumlah pasang citra yang benar-benar terpakai di eksperimen akhir |

Catatan: Kodak sempat membalas 401, resize ke 512×512 mengubah proporsi sebagian citra. Lisensi citra: cek dan sitasi sumbernya, jangan distribusi ulang.

### Metrik
PSNR, SSIM, % piksel pulih persis, tingkat deteksi dan positif palsu (terhadap ground truth noise).

---

## 6. Hasil Sejauh Ini (PSNR rata-rata, dB)

### Salt-and-pepper
| d | A | C_med3 | D_0255 | D_C15 |
|---|---|---|---|---|
| 1% | 22,3 | 30,6 | 38,3 | **42,6** |
| 10% | 12,4 | 23,4 | **33,7** | 32,5 |
| 30% | 8,0 | 9,4 | **29,9** | 27,5 |

B_med3 datar sekitar 8–9 dB (selalu di bawah A untuk d ≤ 20%).

### Gaussian
| σ | A | C_med3 | D_0255 | D_C15 |
|---|---|---|---|---|
| 1 | 13,6 | **23,5** | 13,5 | 16,4 |
| 10 | 5,7 | 5,2 | 5,7 | **9,8** |

### Temuan inti
1. **A rapuh sekali**, bahkan pada σ = 1 (sekitar 14 dB). Ini **temuan kelemahan skema**, bukan kegagalan eksperimen.
2. **B (filter sebelum pemulihan) merusak**: median mengubah piksel sehat yang menyimpan rahasia di bit bawah.
3. **C memperbaiki tetapi membuat buram**: pada d = 1% hanya 31% piksel persis (A: 98%).
4. **D unggul di salt-and-pepper**, sekitar 7 dB atau lebih di atas filter terbaik, 67–99% piksel persis.
5. **Aturan C15 unggul di d rendah** (positif palsu 0%), **D_0255 unggul di d tinggi** (deteksi 100%). Titik silang sekitar 5–7%. ⚠️ **Verifikasi ulang** dengan tabel per pasang citra; jangan mengutip angka titik silang sebelum dicek.
6. **Nilai tambah aturan C terlihat di Gaussian**: D_0255 sama dengan A, D_C15 memberi sekitar +4 dB pada σ = 10.
7. **Gaussian titik gagal**: tidak ada skenario di atas 24 dB. Penyebab terukur: 61,6% piksel F1 berubah pada σ = 1, kesalahan dikali 16, dan sebagian besar perubahan tetap di rentang sah sehingga tidak terdeteksi (deteksi 7,6–48,1%).

---

## 7. Pertanyaan Dosen yang Mungkin Muncul

| Pertanyaan | Jawaban singkat |
|---|---|
| Bedanya dengan paper APICS? | Paper itu menampilkan noise secara visual pada satu pasang citra. Kita mengukur dengan angka, banyak citra dan tingkat noise, ditambah skenario perbaikan. |
| Kenapa Gaussian gagal? | Karena 61,6% piksel F1 sudah berubah pada σ = 1, kesalahan dikali 16, dan sebagian besar perubahan tetap di rentang sah sehingga tidak terdeteksi. |
| Apa bedanya D_0255 dengan decision-based median? | Idenya sama (dikutip), diterapkan pada domain Iq/Ir. Yang khas kita adalah aturan C15 yang memakai citra sampul. |
| Apa bedanya dengan kelompok yang meneliti salt-and-pepper dengan median dan AMF? | Mereka meneliti denoising citra biasa. Kita meneliti pemulihan citra rahasia pada skema secret sharing. |
| Kenapa tidak pakai Reed–Solomon seperti paper QR? | Itu skema lain dengan redundansi tambahan. Kita menguji skema yang sudah ada tanpa mengubah pembagiannya. |
| Kenapa Q = 16? | Karena 16 × 16 = 256, sehingga Iq dan Ir sama-sama 0–15 (alasan di paper "nilai tengah" kurang tepat). |
| Apakah D lossless? | Tidak. |
| Boleh pakai Q lain? | Aturan C15 hanya berlaku untuk Q = 16, jadi harus diturunkan ulang. |

---

## 8. Yang Masih Perlu Dicek atau Belum Pasti

- Jumlah pasang citra sebenarnya yang terpakai (Kodak hanya dua berhasil diunduh) dan simpangan antar pasang.
- Titik silang D_C15 vs D_0255 (5–7%), diverifikasi lewat tabel per pasang citra.
- Angka dan batas di paper QR (Algorithms 2025), definisi Gaussian di sana, dan klaim kompresinya.
- Apakah ISESD 2021, ISPACS 2019, dan ICCE-Taiwan 2020 benar-benar tidak menguji noise.
- Isi slide dosen (nomor slide dikutip dari sesi lain).
- Kemungkinan tumpang tindih desain eksperimen dengan klaim kelompok lain (salt-and-pepper, median, adaptive median, PSNR/SSIM). Sebutkan ke dosen.
- Pencarian novelty di Google Scholar. "Tidak ditemukan di koleksi" bukan bukti "belum pernah dilakukan".
- Mekanisme (pembesaran 16×, kenapa median gagal pada σ besar) adalah interpretasi, bukan fakta terbukti.

## 9. Keterbatasan yang Wajib Ditulis

- Jumlah pasang citra dan seed terbatas (sebutkan angka sebenarnya).
- Hanya Q = 16, dan penerima diasumsikan memegang C.
- Gaussian hanya sampai σ = 10.
- Pembanding filter terbatas (median 3×3, adaptive median).
- Cover dengan piksel ekstrem (< 16 atau ≥ 240) melemahkan deteksi aturan C (deteksi sekitar 98,4%).
- Hasil D tidak lossless.
- Resize Kodak ke 512×512 mengubah proporsi.
