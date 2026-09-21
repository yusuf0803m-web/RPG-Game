# Alur kerja gambar latar: dari prompt sampai aset final

Folder ini adalah keluaran dari alat-alat di `tools/`. Tidak ada satu pun gambar yang
dibuat oleh alat-alat ini -- semuanya berhenti di teks prompt. Generate gambarnya sendiri,
manual, di **ChatGPT Image Generation**.

Permainan tidak butuh satu pun gambar ini untuk jalan (panorama SVG prosedural dipakai
selama berkas `.webp`-nya belum ada -- GAME_DESIGN §7.2), jadi kamu bisa mengisi gambar
bertahap, prioritas berapa saja, kapan saja.

## Ringkasan tiga alat

| Alat | Input | Output | Tugas |
|---|---|---|---|
| `tools/generate_latar_prompts.py` | `pelita/data/world/latar.json` | `prompts/latar_prompts.json` + `prompts/{backgrounds,variants,events}/*.md` | Merakit prompt per aset dari data dunia |
| `tools/export_image_generation_batch.py` | `prompts/latar_prompts.json` | `prompts/batches/*.md` + `*.json` | Mengelompokkan prompt jadi batch siap-tempel untuk ChatGPT |
| `tools/prepare_generated_images.py` | gambar hasil unduhan ChatGPT | `pelita/web/static/assets/backgrounds/**/*.webp` | Resize, convert, kompres gambar jadi aset final |

Kamu biasanya hanya perlu dua yang terakhir; yang pertama sudah dijalankan dan hasilnya ada
di repo.

## Langkah demi langkah

### 1. Generate sebuah batch

```
python tools/export_image_generation_batch.py --priority 1
```

Filter yang tersedia: `--priority {1,2,3}`, `--category {lokasi,variant,event,all}`
(`lokasi` adalah alias untuk `location`), `--id <asset_id>`. Tanpa filter, semua 139 aset
diekspor. Nama berkas keluaran mengikuti filter yang dipakai (mis. `batch_priority1.md`)
sehingga run yang sama selalu menghasilkan berkas yang sama (deterministik & idempoten) --
aman dijalankan ulang kapan saja.

### 2. Buka berkas Markdown batch yang dihasilkan

```
prompts/batches/batch_priority1.md
```

Aset dikelompokkan **Prioritas -> Kategori -> Region** supaya kamu bisa mengerjakannya
runtun (kerjakan Prioritas 1 dulu). Prioritas 1 = ruang yang paling sering dilihat pemain,
prioritas 3 = varian kondisi dunia (boleh menyusul belakangan).

### 3. Ambil bagian IMAGE PROMPT untuk satu aset

Tiap aset di Markdown punya dua blok kode yang jelas terpisah:

- **IMAGE PROMPT** -- salin persis ini ke ChatGPT.
- **NEGATIVE / AVOID** -- daftar hal yang harus dihindari; sebutkan di permintaan yang sama
  ("avoid: ...") atau di pesan susulan kalau hasil pertama masih melanggarnya.

Prompt sudah dalam bahasa Inggris polos, tanpa sintaks khusus Midjourney/Stable
Diffusion/dsb., jadi bisa langsung ditempel ke ChatGPT Image Generation apa adanya.

### 4. Kirim ke ChatGPT Image Generation

Tempel **IMAGE PROMPT**-nya. Kalau ChatGPT punya opsi rasio/ukuran, pilih **landscape**
(ukuran bawaannya sekitar `1536x1024`, bukan 16:9 persis -- itu wajar, langkah 7 yang
membereskannya).

### 5. Simpan gambar hasilnya dengan nama yang benar

Unduh gambarnya, lalu simpan (atau ganti nama) ke:

```
prompts/generated_incoming/<asset_id>.png
```

`<asset_id>` ada di baris **Asset ID** pada Markdown, mis. `pelita_rendah_warung`. Format
apa pun boleh (`.png`, `.jpg`, `.webp`, ...) -- langkah 7 yang mengonversinya.

Alternatif: kalau kamu suka menyusun ulang folder, `prompts/generated_incoming/` juga
menerima struktur yang meniru `asset_path`, mis.
`prompts/generated_incoming/pelita_rendah/warung.png`. Keduanya dikenali otomatis.

### 6. Ulangi untuk setiap aset di batch

Kerjakan satu per satu sampai batchnya habis. Tidak masalah kalau berhenti di tengah --
lanjutkan kapan saja, gambar yang belum ada tetap memakai panorama SVG prosedural.

### 7. Jalankan proses validasi/kompresi aset

```
python tools/prepare_generated_images.py
```

Ini akan, untuk tiap berkas di `prompts/generated_incoming/` yang cocok dengan sebuah
aset:

1. memvalidasi dimensinya (menolak gambar potret -- generate ulang dengan opsi landscape)
2. memotong tengah ke rasio 16:9 lalu resize pas ke **1600x900**
3. mengonversi ke **WebP**
4. mengompresnya bertahap sampai **di bawah 250 KB** (dilaporkan kalau tidak berhasil)
5. menyimpannya ke path aset yang benar di `pelita/web/static/assets/backgrounds/`
6. melaporkan berkas mana yang gagal/di-skip dan kenapa

Butuh Pillow (`pip install Pillow`, atau `pip install -e ".[images]"`) -- bukan dependensi
wajib permainan, cuma untuk alat pasca-produksi ini.

Berguna juga:

```
python tools/prepare_generated_images.py --dry-run     # lihat laporan tanpa menulis apa pun
python tools/prepare_generated_images.py --priority 1  # hanya proses cakupan batch ini
python tools/prepare_generated_images.py --force        # timpa .webp final yang sudah ada
```

Berkas di `prompts/generated_incoming/` yang sudah diproses boleh dihapus manual kapan
saja -- folder itu cuma tempat transit, bukan bagian dari aset permainan.

## Aturan arah seni (tidak berubah dari prompt generator)

Semua ini sudah tertanam di teks prompt itu sendiri; daftar ini cuma pengingat cepat kalau
kamu menulis ulang atau menyempurnakan sebuah prompt secara manual:

- **1600x900 px, 16:9, WebP, target di bawah 250 KB.**
- **Dark fantasy Nusantara** -- bukan Eropa medieval generik, bukan desa Indonesia modern.
- **Cahaya utama** mengikuti apa yang tertulis di `metadata.lighting` tiap aset (lentera,
  Suar/Nyala, atau memang sengaja tanpa lentera) -- jangan paksa lentera ke tiap adegan.
- **Sepertiga bawah bingkai** dibiarkan relatif kosong untuk latar lokasi/varian; kotak
  dialog dan gradien gelapnya ditambahkan game secara otomatis -- jangan gambar gradien
  hitam berat sendiri di prompt.
- **Jangan tambahkan karakter yang tidak perlu** ke latar lokasi biasa; ilustrasi peristiwa
  besar (`kategori: peristiwa`/`event`) boleh berisi karakter kalau memang diminta prompt.
- **Varian kondisi dunia** harus terlihat sebagai lokasi fisik yang SAMA dengan lokasi
  dasarnya (`variant_of` di metadata) -- arsitektur & sudut kamera tetap, yang berubah
  cuma pencahayaan/populasi/kerusakan/suasana.

## Struktur folder

```
prompts/
  latar_prompts.json          sumber kebenaran manifes (dari tools/generate_latar_prompts.py)
  backgrounds/*.md             prompt per aset lokasi (kategori "lokasi")
  variants/*.md                prompt per aset varian kondisi dunia
  events/*.md                  prompt per ilustrasi peristiwa besar
  batches/*.md, *.json         batch siap-tempel untuk ChatGPT (dari export_image_generation_batch.py)
  generated_incoming/          folder transit: taruh unduhan ChatGPT di sini sebelum diproses
```

`generated_incoming/` sengaja tidak disertakan isinya di repo -- itu ruang kerja lokal kamu.
