# Pelita Terakhir

RPG teks turn-based bergaya JRPG klasik, dibangun dengan Python (stdlib saja).

- **Dokumen desain**: [`GAME_DESIGN.md`](GAME_DESIGN.md) (edisi 20 jam, tiga babak).
- **Status**: Tahap 2 dari rencana di §9 dokumen desain selesai — **Babak 1 (Lembah Larung) bisa dimainkan
  sampai tamat**: 8 area, 8 boss, 4 anggota party, 5 side quest, save/muat.

## Bermain

Butuh Python 3.10+.

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
python -m pytest -q                     # 61 tes, termasuk walkthrough otomatis Babak 1
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
  ui/terminal.py   layar pertarungan & menu teks
  data/            characters, skills, enemies, items; world/area_*.json, shops, quests
tools/             calibrate.py, walkthrough.py
tests/             pytest (walker.py = pemain otomatis untuk tes alur)
```

## Menambah konten

Semua isi hidup di JSON. Area baru = satu file `pelita/data/world/area_NN_<id>.json` dengan ruang,
exit, NPC, objek, encounter, dan skrip; loader memvalidasi semua rujukan saat start. Perintah skrip
didokumentasikan di `pelita/world/script.py`, bentuk area di `pelita/world/model.py`.
