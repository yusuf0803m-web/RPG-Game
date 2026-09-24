# Gambar tokoh Pelita Terakhir

Potret bust-up untuk dialog (GAME_DESIGN §7.3). Satu berkas dipakai dua kali: utuh di panggung
di atas latar, dan di-crop jadi wajah kecil di samping baris dialog.

- **Path:** `<id>/<ekspresi>.webp` (atau `.png`), mis. `rimba/worried.webp`. `<id>` = kunci di
  `pelita/data/tokoh.json`, bukan nama tampilan.
- **Ekspresi:** neutral, happy, worried, serious, angry, sad, surprised, scared.
- **Kanvas:** 720×960 (3:4). Rasio 3:4 wajib; resolusi lain boleh selama rasionya sama.
- **Latar transparan (alpha).** Berkas tanpa alpha hanya dipakai untuk wajah di log; panggung
  jatuh ke ekspresi bawaan.
- **Ukuran berkas:** WebP ≤ 160 KB.
- **Crop wajah:** `[x, y, sisi]` di kanvas 720×960, diatur di `tokoh.json` per tokoh atau per
  ekspresi. Bawaan `[216, 120, 288]`.
- **Kalau berkasnya belum ada**, dialog tampil seperti biasa. Tidak ada yang rusak.

## Memeriksa & merapikan aset

```bash
python tools/audit_potret.py rimba      # ukuran, alpha, latar tercetak, lubang pakaian, garis mata vs neutral
python tools/rapikan_potret.py SUMBER.webp rimba/happy.webp --tokoh rimba --ekspresi happy \
    --papan-catur --batas-kepala 440 --tutup-lubang --selaraskan --landmark rimba@rilis2
```

`audit_potret.py` juga dijalankan oleh `tests/test_tokoh.py`: berkas dengan latar tercetak,
lubang di pakaian, atau garis mata/dagu di luar toleransi Bible (±4 / ±12 px terhadap
ekspresi bawaan) membuat tes gagal. Landmark wajah dicatat di `tools/landmark_potret.json`
dan harus diukur ulang setiap kali berkas diganti.

## Catatan aset pilot Rimba

Sumber: set rilis kedua. `neutral` dipasang apa adanya (master). Tiga ekspresi lain dirapikan
dengan `tools/rapikan_potret.py`, tanpa menggambar ulang: hanya matting latar, pemulihan alpha,
dan skala + geser (tanpa rotasi).

| Berkas | KB | Perbaikan | Transform ke neutral |
|---|---|---|---|
| `neutral.webp` | 123 | — (master) | — |
| `happy.webp` | 94 | Papan catur tercetak di-matte jadi transparan; lubang rompi tertutup (RGB di bawahnya masih utuh) | skala 0,9364, geser (+29,5; +87,7) |
| `worried.webp` | 88 | Lubang rompi (11.293 px) ditutup dengan memulihkan alpha | skala 0,9977, geser (+1,6; +38,8) |
| `serious.webp` | 133 | — | skala 1,0022, geser (−5,5; +29,3) |

Setelah dirapikan, garis mata keempatnya dalam ±1,4 px dan dagu dalam ±7,2 px dari neutral,
jadi satu crop wajah `[205, 237, 260]` dipakai untuk semuanya.

**Yang masih tersisa (butuh gambar baru, bukan transform):**

- Neutral dibuat terpisah dari tiga ekspresi lain: rambutnya lebih tipis dan bahunya lebih
  sempit/rendah. Wajah tidak melompat, tapi siluet rambut dan bahu berubah sedikit saat
  berganti dari/ke neutral (IoU siluet kepala 0,86–0,89; antar-ekspresi lain 0,93–0,94).
- Putaran kepala sedikit berbeda (galat landmark telinga 12–20 px); skala + geser tidak bisa
  memperbaikinya tanpa warp.
- Keempatnya tidak memenuhi grid Bible §4 (garis mata di y≈347, bukan 240; margin samping
  `happy`/`worried`/`serious` 11–30 px, bukan ≥ 48). Neutral master sendiri sudah di luar grid.
- `happy`: tepi lengan kiri terpotong lurus di x≈30 (tepi kanvas sumber ikut tergeser), di
  bawah y≈610; di panggung hanya ujungnya yang terlihat. Beberapa bintik 1–2 px sisa papan
  catur mungkin masih ada di ujung helai.
