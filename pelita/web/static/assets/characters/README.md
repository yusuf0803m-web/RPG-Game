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

## Catatan aset pilot Rimba

Dipasang apa adanya dari set pilot, tanpa diubah:

| Berkas | Ukuran | Alpha | Catatan |
|---|---|---|---|
| `rimba/neutral.webp` | 720×960, 113 KB | ya | Sesuai spesifikasi. |
| `rimba/happy.png` | 1086×1448, 2,2 MB | **tidak** | Pola papan catur tercetak di gambar. Panggung memakai neutral. |
| `rimba/worried.png` | 1086×1448, 1,6 MB | **tidak** | Latar hitam pekat. Panggung memakai neutral. |
| `rimba/serious.png` | 1086×1448, 1,7 MB | ya | Terlalu besar untuk rilis; ujung bawah memudar transparan. |

Framing keempatnya tidak sama (kepala `neutral` lebih kecil dan lebih rendah), jadi crop wajah
diatur per ekspresi di `tokoh.json`, dan bust-up terlihat "melompat" saat ganti ekspresi.
Perbaikannya ada di sisi aset: ekspor ulang ketiga ekspresi dari master `neutral` dengan kanvas,
posisi kepala, dan alpha yang sama, lalu simpan sebagai WebP 720×960. Setelah itu kotak crop
per ekspresi di `tokoh.json` bisa dihapus.
