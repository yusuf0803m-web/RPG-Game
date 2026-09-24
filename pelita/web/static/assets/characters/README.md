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

Rilis kedua (semua 720×960 WebP dengan alpha, ≤ 160 KB), dipasang apa adanya:

| Berkas | Ukuran | Panggung | Catatan |
|---|---|---|---|
| `rimba/neutral.webp` | 123 KB | ya | Master. |
| `rimba/happy.webp` | 159 KB | **tidak** (`"panggung": false`) | Latar papan catur masih tercetak di gambar (piksel opak), dan ada lubang transparan di rompi. Hanya dipakai untuk face graphic; panggung memakai neutral. |
| `rimba/worried.webp` | 134 KB | ya | Ada lubang transparan di rompi bagian bawah; di panggung nyaris tak terlihat karena tertutup gradien bawah panorama. |
| `rimba/serious.webp` | 133 KB | ya | Ujung bawah memudar transparan. |

Framing ketiga ekspresi masih lebih besar dan lebih tinggi daripada `neutral`, jadi crop wajah
diatur per ekspresi di `tokoh.json`, dan bust-up terlihat "melompat" saat berganti dari/ke neutral.
Perbaikannya di sisi aset: buat ekspresi dari master `neutral` dengan kanvas dan posisi kepala yang
sama (inpainting di Zona Ekspresi). Setelah itu kotak crop per ekspresi bisa dihapus, dan setelah
`happy` punya latar yang benar-benar transparan, hapus `"panggung": false`-nya.
