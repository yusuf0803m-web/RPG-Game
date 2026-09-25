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
python tools/audit_potret.py rimba      # ukuran, alpha, latar tercetak, lubang, identitas di luar zona, garis mata
python tools/rapikan_potret.py SUMBER.webp rimba/happy.webp --tokoh rimba --ekspresi happy \
    --landmark rimba@selaras --transplantasi rimba/neutral.webp
```

`audit_potret.py` juga dijalankan oleh `tests/test_tokoh.py`. Tes gagal kalau ada berkas dengan:
latar tercetak, lubang di pakaian, piksel di luar zona ekspresi yang berbeda dari master
(`tools/zona_ekspresi.json`, Bible A6), atau garis mata/dagu di luar toleransi Bible
(±4 / ±12 px). Landmark wajah dicatat di `tools/landmark_potret.json` dan harus diukur ulang
setiap kali berkas diganti.

## Catatan aset pilot Rimba

`neutral.webp` adalah master dan dipasang apa adanya. `happy`, `worried`, dan `serious` dibangun
ulang dari master: **seluruh gambar = neutral**, kecuali wajah bagian dalam (alis, mata, hidung,
mulut, pipi) di poligon `tools/zona_ekspresi.json`. Wajah itu diambil dari artwork ekspresi yang
sudah disetujui (set rilis kedua, setelah dibersihkan & diselaraskan pada commit 069ebcd),
diskalakan supaya pupil & hidungnya jatuh di pupil & hidung neutral, disamakan warna kulitnya,
lalu dicampur dengan tepi yang dihaluskan. Helai poni neutral yang menyilang mata kiri tetap di
atas. Tidak ada piksel yang digambar/digenerate.

| Berkas | KB | Skala wajah | Geser | Galat pupil/hidung |
|---|---|---|---|---|
| `neutral.webp` | 123 | — (master) | — | — |
| `happy.webp` | 115 | 1,0416 | (−12,6; −12,3) | 1,9 / 0,5 / 1,6 px |
| `worried.webp` | 115 | 1,0489 | (−16,0; −15,0) | 2,0 / 3,7 / 5,5 px |
| `serious.webp` | 115 | 1,0691 | (−22,7; −20,6) | 0,7 / 4,6 / 4,8 px |

Hasil: siluet keempatnya identik (IoU 1,0000), di luar zona selisihnya setara derau encode WebP
(rata-rata 3,0, p99 11), garis mata dalam ±1,9 px, margin & framing = neutral.

**Yang masih tersisa:**

- Keempatnya di luar grid Bible §4 (garis mata di y≈348, bukan 240), karena neutral master
  sendiri begitu. Memperbaikinya butuh master baru, bukan transform.
- Fitur wajah `worried`/`serious` sedikit lebih besar daripada neutral (skala 1,05–1,07),
  mengikuti proporsi artwork sumbernya. Di ukuran panggung hampir tak terlihat.
- `happy` sumbernya jauh lebih terang (L −24 dikoreksi); rona kulitnya sudah disamakan di tepi
  zona, tapi di dalam wajah tetap sedikit lebih hangat daripada neutral.
- Ekspresi hanya berubah di dalam zona: senyum `happy` tidak mengangkat kontur pipi luar atau
  rahang, karena itu milik neutral.
