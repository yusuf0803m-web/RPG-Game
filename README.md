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
internet. Pilihan bisa diklik atau ditekan dengan angka 1–9.

## Bermain di HP Android

Antarmuka web dibuat untuk layar sentuh: tombol besar, tata letak menyesuaikan lebar
layar dan orientasi, dan panorama menyusut otomatis saat bertarung agar arena serta
log tetap muat. Ada dua cara memainkannya di HP.

**Cara 1 — server di komputer, main dari HP (paling mudah).** Komputer dan HP harus
tersambung ke Wi-Fi yang sama.

```bash
python -m pelita --web --lan
```

Perintah itu mencetak alamat yang tinggal diketik di browser HP, misalnya
`http://192.168.1.10:5000`. Simpanan permainan tersimpan di komputer, jadi kamu bisa
lanjut main di layar besar kapan saja.

> Mode `--lan` membuka permainan untuk siapa pun di jaringan itu dan tidak memakai
> kata sandi. Pakai di jaringan rumah sendiri; jangan di Wi-Fi publik.

**Cara 2 — langsung di HP, tanpa komputer.** Pasang [Termux](https://termux.dev) dari
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

**Pasang ke layar utama.** Di Chrome Android, buka menu titik tiga lalu
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
python -m pytest -q                     # 73 tes: unit, walkthrough Babak 1, dan API web
python tools/calibrate.py --n 200       # simulasi rasio "2–3 pukulan" per skenario
python tools/walkthrough.py --seed 11   # pemain otomatis dari prolog sampai Akhir Babak 1;
                                        # mencetak level party & lama tiap boss
```

## Struktur

```
pelita/
  models.py        tipe data (Stats, Skill, EnemyDef, CharacterDef, ItemDef)
  loader.py        memuat & memvalidasi pelita/data/*.json
  party.py         Hero: level, XP (20·n²), pertumbuhan stat deterministik, serialisasi
  scenarios.py     skenario prototipe combat
  combat/
    formulas.py    formula damage/heal/peluang (murni)
    status.py      status efek & buff
    engine.py      Battle: giliran, afinitas, Goyah, Bara, Jurus Ganda, Ketahanan/Pecah,
                   pemanggilan, rotasi afinitas, isian meriam, Tandai, aksi ganda, Curi, ...
    ai.py          AI musuh (tabel bobot, skrip fase) & kebijakan otomatis party
  world/
    model.py       Area/Room/Exit/NPC dari data/world/*.json (+ validasi rujukan)
    state.py       GameState: party, inventori, flag, quest, kabut, save/load
    script.py      interpreter skrip cerita (narasi, dialog, if/once/choice, battle, join, ...)
    explore.py     loop eksplorasi, encounter, menu, toko, penginapan
  ui/terminal.py   layar pertarungan & menu teks; IO.emit() = kanal terstruktur untuk web
  web/
    session.py     satu sesi = satu thread Game.run() dengan IO antrian (event ⇄ input)
    app.py         server Flask: /api/session, /state (long-poll), /input
    static/        index.html, style.css, app.js (klien), art.js (SVG prosedural)
  data/            characters, skills, enemies, items; world/area_*.json, shops, quests
tools/             calibrate.py, walkthrough.py
tests/             pytest (walker.py = pemain otomatis untuk tes alur)
```

## Cara antarmuka web bekerja

Mesin permainan tidak tahu-menahu soal web. Ia hanya menulis ke sebuah objek `IO`.
Versi terminal mencetak ke layar; versi web menaruh tiap keluaran ke antrian event,
dan `IO.ask()` memblokir sampai browser mengirim jawaban.

```
Game.run()  ──IO.line/emit──▶  antrian event  ──GET /state (long-poll)──▶  browser
     ▲                                                                        │
     └──────────────  IO.ask() menunggu  ◀── POST /input ──────────────────────┘
```

Selain baris teks, mesin mengirim **event terstruktur** lewat `IO.emit()`: `room`
(area, ruang, party, keping), `battle` (musuh, HP, afinitas yang sudah diketahui,
status, Bara), `say` dan `text` (dialog dan narasi), serta `end`. Itulah yang
digambar klien. Menambah area atau musuh baru tidak perlu menyentuh kode web sama
sekali; panorama memakai seni bawaan bila id area belum punya gambar sendiri.

## Menambah konten

Semua isi hidup di JSON. Area baru = satu file `pelita/data/world/area_NN_<id>.json` dengan ruang,
exit, NPC, objek, encounter, dan skrip; loader memvalidasi semua rujukan saat start. Perintah skrip
didokumentasikan di `pelita/world/script.py`, bentuk area di `pelita/world/model.py`.
