# Pelita Terakhir

RPG teks turn-based bergaya JRPG klasik, dibangun dengan Python (stdlib saja).

- **Dokumen desain**: [`GAME_DESIGN.md`](GAME_DESIGN.md) (edisi 20 jam, tiga babak).
- **Status**: Tahap 1 dari rencana di §9 dokumen desain — prototipe pertarungan yang bisa dimainkan.

## Menjalankan prototipe

Butuh Python 3.10+.

```bash
python -m pelita --list                 # daftar skenario
python -m pelita                        # pilih skenario, main interaktif
python -m pelita -s boss_katak          # langsung ke skenario tertentu
python -m pelita -s rawa --auto --seed 3 --no-pause   # demo otomatis (party dikendalikan AI)
```

Di dalam pertarungan: ketik nomor pilihan, `0` untuk kembali, `q` untuk keluar.

## Tes & kalibrasi

```bash
pip install pytest
python -m pytest -q
python tools/calibrate.py --n 200       # simulasi ratusan pertarungan per skenario
```

`tools/calibrate.py` memverifikasi target GAME_DESIGN §4.7: musuh biasa tumbang dalam
2–3 aksi kalau kelemahannya dipakai, 4–6 kalau tidak; boss 10–20 giliran.

## Struktur

```
pelita/
  models.py        tipe data (Stats, Skill, EnemyDef, CharacterDef, ItemDef)
  loader.py        memuat & memvalidasi pelita/data/*.json
  party.py         Hero: level, XP (20·n²), pertumbuhan stat deterministik
  scenarios.py     skenario prototipe
  combat/
    formulas.py    formula damage/heal/peluang (murni, tanpa state)
    status.py      definisi status efek & buff
    engine.py      Battle: urutan giliran, aksi, Bara, Pecah, afinitas, Catatan Penyala
    ai.py          AI musuh (tabel bobot, skrip fase boss) & kebijakan otomatis party
  ui/terminal.py   layar pertarungan & menu teks
  data/            characters, skills, enemies, items (JSON; angka desain hidup di sini)
tools/calibrate.py simulasi kalibrasi
tests/             pytest
```
