"""Daftar belanja gambar latar: apa yang dibutuhkan, di mana ditaruh, dan mana yang sudah ada.

    python tools/daftar_latar.py                 # ringkasan di terminal
    python tools/daftar_latar.py --prioritas 1   # hanya gambar paling penting
    python tools/daftar_latar.py --tulis         # perbarui README di folder aset

Permainan tidak butuh satu pun gambar ini untuk jalan: selama berkasnya belum ada,
panorama SVG prosedural yang dipakai (GAME_DESIGN §7.2).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pelita.loader import load_data  # noqa: E402
from pelita.world.model import load_world  # noqa: E402

AKAR = Path(__file__).resolve().parents[1]
ASET = AKAR / "pelita" / "web" / "static" / "assets" / "backgrounds"
UKURAN = "1600×900 px (16:9), .webp, usahakan di bawah 250 KB per berkas"

PANDUAN = f"""# Gambar latar Pelita Terakhir

Taruh berkas di folder ini mengikuti path pada daftar di bawah, mis.
`pelita_rendah/warung.webp` untuk latar Warung Bu Ratna.

- **Format & ukuran:** {UKURAN}.
- **Kalau berkasnya belum ada**, permainan memakai panorama SVG prosedural.
  Tidak ada yang rusak; gambar bisa diisi bertahap.
- **Gaya:** dark fantasy Nusantara, sumber cahaya utama selalu lentera/nyala,
  komposisi lebar dengan ruang kosong di bagian bawah supaya teks tetap terbaca.
  Hindari detail ramai di tengah bawah — di situ kotak dialog menumpuk.
- **Kontras:** permainan menambahkan gradien gelap di bagian bawah secara otomatis,
  jadi gambar tidak perlu digelapkan sendiri.
- Sumber daftar ini: `pelita/data/world/latar.json`. Perbarui dengan
  `python tools/daftar_latar.py --tulis`.

Prioritas 1 = ruang yang paling sering dilihat pemain (kerjakan lebih dulu).
Prioritas 3 = varian kondisi dunia; gambarnya boleh menyusul.
"""


def baris(path: str, info: dict, ada: bool) -> str:
    tanda = "x" if ada else " "
    return (f"- [{tanda}] `{path}.webp` — **{info['nama']}** "
            f"(prioritas {info.get('prioritas', 2)})\n      {info.get('deskripsi', '').strip()}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prioritas", type=int, help="saring berdasarkan prioritas (1-3)")
    ap.add_argument("--tulis", action="store_true", help="tulis README.md di folder aset")
    a = ap.parse_args()

    world = load_world(load_data())
    gambar = world.latar
    if not gambar:
        print("latar.json kosong atau tidak ada.")
        return 1

    bagian: dict[str, list[str]] = {"lokasi": [], "varian": [], "peristiwa": []}
    ada_total = 0
    for path, info in sorted(gambar.items(), key=lambda x: (x[1].get("prioritas", 2), x[0])):
        if a.prioritas and info.get("prioritas", 2) != a.prioritas:
            continue
        ada = (ASET / f"{path}.webp").exists()
        ada_total += ada
        bagian.setdefault(info.get("kategori", "lokasi"), []).append(baris(path, info, ada))

    judul = {"lokasi": "Latar lokasi", "varian": "Varian kondisi dunia", "peristiwa": "Ilustrasi peristiwa besar"}
    teks = [PANDUAN]
    for kat, rows in bagian.items():
        if rows:
            teks.append(f"\n## {judul[kat]} ({len(rows)})\n\n" + "\n".join(rows) + "\n")
    isi = "\n".join(teks)

    if a.tulis:
        ASET.mkdir(parents=True, exist_ok=True)
        (ASET / "README.md").write_text(isi, encoding="utf-8")
        print(f"Ditulis: {ASET / 'README.md'}")
    else:
        print(isi)
    print(f"\n{ada_total} dari {len(gambar)} gambar sudah ada di {ASET.relative_to(AKAR)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
