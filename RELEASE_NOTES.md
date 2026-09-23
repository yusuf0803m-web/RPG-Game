# Pelita Terakhir — perubahan sesudah v1.0.0 (belum dirilis)

- **Boss cerita kebal Goyah.** Di v1.0.0, dua belas dari tujuh belas boss cerita
  hampir tidak pernah memainkan polanya: party yang memukul kelemahannya tiap ronde
  membuat mereka Goyah permanen, dan musuh yang Goyah selalu jatuh ke Serang biasa.
  Empat di antaranya (Penambang Raksasa, Penjaga Mercusuar, Cacing Abu Purba, Sunan
  Wirya) tidak memainkan satu aksi polanya pun. Sekarang kedua belasnya kebal Goyah,
  seperti elit Tahap 7. Kelemahan tetap berguna lewat Ketahanan/PECAH, Bara, dan
  pengali damage. Boss pengisi (Penjaga Mercusuar, Penjaga Suar Wirasaba) sekarang hanya
  bisa dibatalkan dengan PECAH.
- **Rekalibrasi** Ular Cermin, Penambang Raksasa, Penjaga Mercusuar, Nirmala, Sang
  Pelita Pertama, Nyi Pandansari, dan Gema Pesta. Semua boss tetap di pita §9.5.
- **Gema Penghitung** (Buruan 10) memanggil klonnya dengan pola tetap, bukan undian.
- `tools/playtest.py` melaporkan rasio aksi bernama tiap boss, dan
  `tests/test_kalibrasi.py` menggagalkan build kalau ada boss yang polanya hilang.
- 148 dari 161 entri latar sekarang bergambar.

Rinciannya di `GAME_DESIGN.md` §9.8.

---

# Pelita Terakhir — v1.0.0

Rilis pertama. Seluruh tujuh tahap rencana pembangunan di `GAME_DESIGN.md` §9 selesai:
permainan bisa ditamatkan dari prolog sampai salah satu dari tiga ending, keseimbangannya
diukur lewat playtest otomatis (bukan ditebak), dan konten sampingannya lengkap.

## Isi

- **18 area / 140 ruang**, tiga babak (~20 jam total)
- **78 musuh** — 16 boss cerita, tiga boss dungeon opsional, satu mid-boss tujuh
  gelombang, satu superboss, dan target Buruan
- **236 skill**, **88 item**, **24 Kaca Ingatan**, **14 Jalur** spesialisasi
- **23 adegan Kenangan**, **11 kontrak Buruan**, **18 side quest**, **3 dungeon
  opsional**, **5 tingkat Arena**
- **161 entri latar bergambar** (29 gambar .webp terpasang; ruang tanpa gambar
  memakai panorama SVG prosedural, jadi permainan tetap utuh tanpanya)
- Party 7 orang (4 aktif + 3 cadangan), tamat di Lv 52–53 dengan ±65.000 Keping
- **Tiga ending**, masing-masing dengan segmen mainnya sendiri, plus jalur
  "Kelana dibunuh" di Babak 3

## Tiga antarmuka, satu mesin

- **Terminal** — `python -m pelita`
- **Web (Flask)** — `python -m pelita --web`, dipakai juga di HP lewat `--lan` atau Termux
- **APK Android** (Chaquopy) — dibangun otomatis lewat `.github/workflows/android.yml`,
  seluruh Python + Flask ikut terkemas, tidak perlu koneksi internet saat bermain

## Keseimbangan diukur, bukan ditebak

`tools/playtest.py` memainkan seluruh permainan dengan pemain otomatis yang benar-benar
berbelanja, memasang Kaca, dan menukar Serpihan, lalu melaporkan ekonomi dan pacing
tiap babak. `tests/test_kalibrasi.py` mengunci pita sasarannya (§9.5) sebagai tes, dan
`tests/test_opsional.py` (40 tes) membuktikan tiap dungeon/Buruan/quest opsional bisa
dimainkan sungguhan **dan** boleh dilewati.

```
python -m pytest -q          247 tes lulus
python tools/playtest.py     ekonomi & pacing ketiga babak di dalam pita §9.5
tools/walkthrough.py         enam walkthrough hijau (3 babak + 3 ending + jalur Kelana dibunuh)
```

## Diketahui, bukan cacat tersembunyi

- **APK ini masih ditandatangani dengan kunci debug bawaan Android** (`assembleDebug`).
  Bukan kelalaian: menandatangani rilis butuh keystore, dan itu rahasia milik pemilik
  proyek, bukan sesuatu yang bisa dibuat begitu saja oleh proses build otomatis. Android
  akan menampilkan peringatan "aplikasi tidak dikenal"/Play Protect saat pemasangan —
  ini normal untuk APK sideload, bukan indikasi APK-nya rusak. Kalau kelak dibutuhkan
  keystore rilis (misalnya untuk publikasi di Play Store), pemilik proyek yang perlu
  membuatnya dan menaruhnya sebagai *secret* di pengaturan repo — lihat catatan di
  `GAME_DESIGN.md` §9.7.
- **132 dari 161 entri latar belum bergambar.** Ruang tanpa gambar tampil dengan
  panorama SVG prosedural; tidak ada yang rusak, hanya belum digambar.
- *(Diperbaiki sesudah v1.0.0 untuk boss cerita, lihat bagian atas.)*
  **`ai.py` punya keterbatasan yang diketahui dan sengaja tidak diubah** di rilis ini:
  musuh yang kena status Goyah selalu jatuh ke serangan biasa. Untuk lima elit baru
  Tahap 7 yang identitasnya adalah urutan terskrip, ini diatasi dengan membuat elit
  tersebut kebal Goyah (kelemahan tetap dibayar lewat Ketahanan/PECAH dan pengali
  damage). Musuh lama sengaja tidak disentuh, karena mengubah `ai.py` akan menggeser
  seluruh kalibrasi Tahap 6. Rinciannya di §9.6.

## Menjalankan dari sumber

```bash
git clone https://github.com/yusuf0803m-web/RPG-Game
cd RPG-Game
pip install flask pytest
python -m pytest -q
python -m pelita
```

Rincian lengkap arsitektur, desain, dan catatan implementasi tiap tahap ada di
[`GAME_DESIGN.md`](GAME_DESIGN.md).
