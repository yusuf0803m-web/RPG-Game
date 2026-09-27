"""Daftar belanja sprite musuh: prompt gambar per musuh, di mana ditaruh, dan mana yang sudah ada.

    python tools/daftar_sprite.py                 # ringkasan di terminal
    python tools/daftar_sprite.py --prioritas 1   # hanya boss
    python tools/daftar_sprite.py --tulis         # perbarui README di folder aset

Permainan tidak butuh satu pun gambar ini untuk jalan: selama berkasnya belum ada,
kartu musuh memakai siluet SVG dari art.js.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pelita.loader import load_data  # noqa: E402

AKAR = Path(__file__).resolve().parents[1]
ASET = AKAR / "pelita" / "web" / "static" / "assets" / "enemies"
PROMPT = Path(__file__).resolve().parent / "sprite_prompts.json"
UKURAN = "persegi 1:1, minimal 768×768 px; simpan sebagai .webp 640×640 (di bawah ±120 KB)"

GAYA = ("Dark fantasy Nusantara {jenis}, painterly digital painting, same style as a moody "
        "lantern-lit Indonesian night scene. {isi} Single {tunggal}, full body, centered, {sudut}, "
        "the whole creature inside the middle 70% of the frame with empty dark margin around it. "
        "Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. "
        "No text, no frame, no border. Square 1:1.")

PANDUAN = f"""# Sprite musuh Pelita Terakhir

Taruh berkas di folder ini dengan nama **id musuh**, mis. `kunang_kelam.webp`.
Semua musuh dengan id itu (Kunang Kelam A, B, C) memakai gambar yang sama.

- **Format & ukuran:** {UKURAN}.
- **Kalau berkasnya belum ada**, kartu memakai siluet SVG. Tidak ada yang rusak;
  gambar bisa diisi bertahap.
- **Komposisi:** satu makhluk di tengah, seluruh badan, latar gelap polos, dengan
  ruang kosong di sekelilingnya. Kartu memotong gambar seperti jendela lebar (kira-kira
  70% bagian tengah terlihat) lalu memudarkan seperlima bawahnya. Ciri penting makhluk
  (wajah, perut bercahaya, senjata) jangan diletakkan di tepi atas atau bawah gambar.
- **Gaya:** sama dengan gambar latar: lukisan digital, cahaya lentera hangat,
  kabut dingin. Pakai prompt di bawah apa adanya supaya semua sprite seragam.
- Sumber prompt: `tools/sprite_prompts.json`. Perbarui daftar ini dengan
  `python tools/daftar_sprite.py --tulis`.

Prioritas 1 = boss (paling lama dilihat pemain). Prioritas 2 = musuh biasa Babak 1
(sampai Mercusuar). Prioritas 3 = musuh Babak 2–3 dan buruan.
"""


def prioritas(e) -> int:
    if e.is_boss:
        return 1
    return 2 if e.level <= 23 and not e.id.startswith("buruan_") else 3


def prompt_lengkap(e, isi: str) -> str:
    return GAYA.format(
        jenis="boss creature" if e.is_boss else "creature",
        isi=isi,
        tunggal="figure" if e.is_boss else "creature",
        sudut="low angle to feel huge and threatening" if e.is_boss else "three-quarter view",
    )


def kumpulkan():
    data = load_data()
    teks = json.loads(PROMPT.read_text(encoding="utf-8"))
    baris = []
    for e in sorted(data.enemies.values(), key=lambda x: (prioritas(x), x.level, x.id)):
        baris.append({
            "id": e.id, "nama": e.name, "level": e.level, "boss": e.is_boss,
            "prioritas": prioritas(e), "ada": (ASET / f"{e.id}.webp").is_file(),
            "deskripsi": e.description, "prompt": prompt_lengkap(e, teks[e.id]) if e.id in teks else None,
        })
    return baris


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prioritas", type=int, choices=(1, 2, 3))
    ap.add_argument("--tulis", action="store_true", help="tulis README.md di folder aset")
    args = ap.parse_args(argv)

    baris = kumpulkan()
    kurang = [b["id"] for b in baris if b["prompt"] is None]
    if kurang:
        print("Musuh tanpa prompt di tools/sprite_prompts.json:", ", ".join(kurang))
    if args.prioritas:
        baris = [b for b in baris if b["prioritas"] == args.prioritas]

    ada = sum(b["ada"] for b in baris)
    print(f"Sprite musuh: {ada}/{len(baris)} sudah ada")
    for b in baris:
        print(f"  [{'x' if b['ada'] else ' '}] p{b['prioritas']} {b['id']}.webp — {b['nama']} (Lv {b['level']})")

    if args.tulis:
        semua = kumpulkan()
        out = [PANDUAN]
        for p, judul in ((1, "Boss"), (2, "Musuh Babak 1"), (3, "Musuh Babak 2–3 & buruan")):
            grup = [b for b in semua if b["prioritas"] == p]
            out.append(f"\n## Prioritas {p}: {judul} ({sum(b['ada'] for b in grup)}/{len(grup)})\n")
            for b in grup:
                out.append(f"- [{'x' if b['ada'] else ' '}] `{b['id']}.webp` — **{b['nama']}** (Lv {b['level']})  ")
                out.append(f"  {b['deskripsi']}")
                if b["prompt"]:
                    out.append(f"  ```\n  {b['prompt']}\n  ```")
        ASET.mkdir(parents=True, exist_ok=True)
        (ASET / "README.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"README ditulis: {ASET / 'README.md'}")
    return 1 if kurang else 0


if __name__ == "__main__":
    raise SystemExit(main())
