# Pelita Terakhir

RPG teks turn-based bergaya JRPG klasik, dibangun dengan Python. Mesin permainan hanya memakai
pustaka standar; antarmuka web menambah satu dependensi, Flask.

- **Dokumen desain**: [`GAME_DESIGN.md`](GAME_DESIGN.md) (edisi 20 jam, tiga babak).
- **Status**: Tahap 2 dari rencana di §9 dokumen desain selesai — **Babak 1 (Lembah Larung) bisa dimainkan
  sampai tamat**: 8 area, 8 boss, 4 anggota party, 5 side quest, save/muat.
- **Dua antarmuka**: web (grafis) dan terminal. Keduanya memakai mesin permainan yang sama.

## Bermain di browser

```bash
pip install flask
python -m pelita --web                  # lalu buka http://127.0.0.1:5000
python -m pelita --web --lan            # izinkan HP/tablet di Wi-Fi yang sama ikut main
python -m pelita --web --port 8000      # porta lain
```

Antarmuka web menampilkan panorama per area, kartu musuh dengan bar HP dan meter
Ketahanan, kartu party dengan potret dan bar HP/MP, meteran Bara, dialog bergaya,
serta angka damage yang melayang saat pukulan mendarat. Semua gambar dibuat dari
SVG di `pelita/web/static/art.js`, jadi tidak ada berkas aset dan tidak butuh
internet. Pilihan bisa diklik atau ditekan lewat papan ketik (angka untuk opsi
bernomor, huruf untuk pintasan seperti `p` Party dan `i` Item). Tiap menu selalu
punya tombol keluar, yang ditampilkan selebar layar di baris paling bawah.

## Bermain di HP Android

Antarmuka web dibuat untuk layar sentuh: tombol besar, tata letak menyesuaikan lebar
layar dan orientasi, dan panorama menyusut otomatis saat bertarung agar arena serta
log tetap muat. Ada tiga cara memainkannya di HP.

**Cara 1 — pasang APK (paling praktis).** Seluruh permainan, termasuk Python dan
Flask, ikut dikemas ke dalam aplikasi; tidak perlu komputer, Termux, atau koneksi
internet saat bermain.

1. Buka tab [**Actions**](https://github.com/yusuf0803m-web/RPG-Game/actions) di repo
   ini, pilih jalannya alur kerja **Bangun APK** paling atas yang bertanda centang
   hijau.
2. Di bagian **Artifacts** paling bawah, unduh `pelita-terakhir-apk`. Berkasnya
   berupa zip (~19 MB); buka lalu ambil `app-debug.apk` di dalamnya.
3. Di HP, buka berkas APK itu. Android akan meminta izin "Instal aplikasi tidak
   dikenal" untuk aplikasi yang membukanya (biasanya Files atau Chrome) — izinkan,
   lalu pasang.

APK ini ditandatangani dengan kunci debug bawaan Android, jadi Play Protect mungkin
menampilkan peringatan; pilih "Pasang saja". Aplikasi menjalankan server permainan di
dalam dirinya sendiri dan hanya mendengarkan di `127.0.0.1`, jadi tidak ada lalu
lintas yang keluar dari HP. Simpanan tersimpan di penyimpanan privat aplikasi dan
ikut terhapus kalau aplikasi dicopot.

**Cara 2 — server di komputer, main dari HP.** Komputer dan HP harus
tersambung ke Wi-Fi yang sama.

```bash
python -m pelita --web --lan
```

Perintah itu mencetak alamat yang tinggal diketik di browser HP, misalnya
`http://192.168.1.10:5000`. Simpanan permainan tersimpan di komputer, jadi kamu bisa
lanjut main di layar besar kapan saja.

> Mode `--lan` membuka permainan untuk siapa pun di jaringan itu dan tidak memakai
> kata sandi. Pakai di jaringan rumah sendiri; jangan di Wi-Fi publik.

**Cara 3 — langsung di HP lewat Termux.** Pasang [Termux](https://termux.dev) dari
F-Droid, lalu:

```bash
pkg install python git
git clone https://github.com/yusuf0803m-web/RPG-Game
cd RPG-Game
pip install flask
python -m pelita --web
```

Buka `http://127.0.0.1:5000` di browser HP. Biarkan Termux berjalan di latar belakang
selama bermain.

**Pasang ke layar utama (untuk cara 2 dan 3).** Di Chrome Android, buka menu titik tiga lalu
"Tambahkan ke Layar utama". Permainan akan terbuka layar penuh tanpa bilah alamat,
seperti aplikasi biasa.

## Bermain di terminal

Butuh Python 3.10+ saja.

```bash
python -m pelita                        # layar judul: Mulai Baru / Muat / Prototipe Combat
python -m pelita --new                  # langsung mulai
python -m pelita --load 1               # muat slot 1 (save di folder saves/)
```

Di eksplorasi: ketik nomor pilihan; `p` party & equipment, `i` item, `c` Catatan Penyala (bestiary),
`q` quest, `k` keluar. Di pertarungan: nomor pilihan, `0` kembali. Simpan di lentera penjaga
(sekaligus memulihkan HP/MP).

Prototipe pertarungan tunggal (Tahap 1) masih ada:

```bash
python -m pelita --list
python -m pelita -s boss_katak
python -m pelita -s rawa --auto --seed 3 --no-pause
```

## Tes & kalibrasi

```bash
pip install pytest
python -m pytest -q                     # 120 tes: unit, walkthrough Babak 1, sistem Tahap 3,
                                        # API web, dan regresi menu (tiap prompt harus ada jalan keluar)
python tools/calibrate.py --n 200       # simulasi rasio "2–3 pukulan" per skenario
python tools/walkthrough.py --seed 11   # pemain otomatis dari prolog sampai Akhir Babak 1;
                                        # mencetak level party & lama tiap boss
```

## Struktur

```
pelita/
  models.py        tipe data (Stats, Skill, EnemyDef, CharacterDef, ItemDef)
  loader.py        memuat & memvalidasi pelita/data/*.json
  party.py         Hero: level, XP (20·n²), pertumbuhan stat, Jalur, soket Kaca, serialisasi
  scenarios.py     skenario prototipe combat
  combat/
    formulas.py    formula damage/heal/peluang (murni)
    status.py      status efek & buff
    engine.py      Battle: giliran, afinitas, Goyah, Bara, Jurus Ganda, Ketahanan/Pecah,
                   pemanggilan, rotasi afinitas, isian meriam, Tandai, aksi ganda, Curi, ...
    ai.py          AI musuh (tabel bobot, skrip fase) & kebijakan otomatis party
  world/
    model.py       Area/Room/Exit/NPC dari data/world/*.json (+ validasi rujukan)
    state.py       GameState: party aktif/cadangan, inventori, Kaca, flag, quest, kabut, save/load
    script.py      interpreter skrip cerita (narasi, dialog, if/once/choice, battle, join, ...)
    explore.py     loop eksplorasi, encounter, menu, toko, Tukang Kaca, kemah, Buruan, Arena
  ui/
    menu.py        Option/Menu: satu tempat menyusun daftar pilihan (satu opsi = satu tombol)
    terminal.py    layar pertarungan & menu teks; IO.menu()/emit() = kanal terstruktur untuk web
  web/
    session.py     satu sesi = satu thread Game.run() dengan IO antrian (event ⇄ input)
    app.py         server Flask: /api/session, /state (long-poll), /input
    static/        index.html, style.css, app.js (klien), art.js (SVG prosedural)
  data/            characters, skills, enemies, items, kaca, jalur;
                   world/area_*.json, shops, quests, kenangan, buruan, arena
tools/             calibrate.py, walkthrough.py
tests/             pytest (walker.py = pemain otomatis untuk tes alur;
                   test_menu_web.py = crawler yang memastikan tiap menu bisa ditinggalkan)
```

## Sistem lanjutan (Tahap 3)

Semuanya data-driven; rinciannya di `GAME_DESIGN.md` §9.2.

- **Kaca Ingatan** — 21 keping kaca yang dipasang ke soket senjata. Kaca Elemen mengubah elemen
  serangan dasar, Kaca Pasif memberi bonus (regen MP, kritikal, XP, potongan harga, ...), Kaca Skill
  meminjam skill karakter lain. Naik tingkat I→III setelah 12 dan 36 pertarungan.
- **Jalur** — di Lv 20 tiap karakter Babak 1 memilih satu dari dua spesialisasi: 3 skill eksklusif
  plus satu pasif. Bisa direset di Tukang Kaca.
- **Cadangan & Ganti** — empat nama teratas ikut bertarung, sisanya dapat 70% XP. Aksi **Ganti**
  menukar penyerang dengan cadangan di tengah pertarungan. Rimba selalu aktif (pemegang Bara).
- **Tukang Kaca** (Tengara) — pasang/lepas Kaca, beli Kaca, dan tukar tiap 3 Serpihan Ingatan jadi
  HP maks, Bara maks, soket tambahan, reset Jalur, atau Kaca Skill langka.
- **Berkemah** — satu Bekal Kemah di lentera penjaga memulihkan party dan membuka adegan **Kenangan**.
  Jurus Ganda hanya terbuka lewat Kenangan pasangannya.
- **Papan Buruan & Arena Kafilah** (Dermaga Kota) — 3 target elit dengan mekanik khas, dan 3 tingkat
  arena berisi tiga gelombang beruntun tanpa item.

## Cara antarmuka web bekerja

Mesin permainan tidak tahu-menahu soal web. Ia hanya menulis ke sebuah objek `IO`.
Versi terminal mencetak ke layar; versi web menaruh tiap keluaran ke antrian event,
dan `IO.ask()` memblokir sampai browser mengirim jawaban.

```
Game.run()  ──IO.line/emit──▶  antrian event  ──GET /state (long-poll)──▶  browser
     ▲                                                                        │
     └──────────────  IO.ask() menunggu  ◀── POST /input ──────────────────────┘
```

Pilihan **tidak** ditebak dari teks yang sudah dicetak. Semua menu disusun lewat
`Menu` di `pelita/ui/menu.py`, lalu `IO.menu()` memutuskan cara menampilkannya:
terminal mencetak satu opsi per baris, web mengirim daftarnya sebagai data. Tiap
prompt punya `kind` — `menu`, `confirm` (ya/tidak), atau `enter` (Lanjut) — dan
tiap menu dapat jalan keluar secara bawaan, sehingga tidak ada menu yang bisa
"menyangkutkan" pemain di layar sentuh. `tests/test_menu_web.py` menjelajah semua
menu dan menggagalkan build kalau ada prompt yang kehilangan tombol keluarnya.

Selain baris teks, mesin mengirim **event terstruktur** lewat `IO.emit()`: `room`
(area, ruang, party, keping), `battle` (musuh, HP, afinitas yang sudah diketahui,
status, Bara), `say` dan `text` (dialog dan narasi), serta `end`. Itulah yang
digambar klien. Menambah area atau musuh baru tidak perlu menyentuh kode web sama
sekali; panorama memakai seni bawaan bila id area belum punya gambar sendiri.

## Menambah konten

Semua isi hidup di JSON. Area baru = satu file `pelita/data/world/area_NN_<id>.json` dengan ruang,
exit, NPC, objek, encounter, dan skrip; loader memvalidasi semua rujukan saat start. Perintah skrip
didokumentasikan di `pelita/world/script.py`, bentuk area di `pelita/world/model.py`.
