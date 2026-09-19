"""Jalankan walkthrough otomatis Babak 1 dan cetak ringkasan: level party di tiap boss & titik gagal.

Pakai: python tools/walkthrough.py [--seed N] [--tail 60] [--sampai LANGKAH]
"""
from __future__ import annotations

import argparse
import random
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pelita.loader import load_data  # noqa: E402
from pelita.world.explore import Game  # noqa: E402
from pelita.world.model import load_world  # noqa: E402
from pelita.world.state import new_game  # noqa: E402
from tests.test_babak1 import SEMUA, BerhentiUji, make_equipper  # noqa: E402
from tests.test_babak2 import SEMUA_BABAK2, mulai_babak2  # noqa: E402
from tests.walker import Walker  # noqa: E402

BOSSES = {
    1: ("Hampa Penjaga Hutan", "Raja Katak Lumpur", "Ular Cermin", "Kapten Rangga",
        "Penambang Raksasa Terlupa", "Penjaga Mercusuar", "Adipati Baskara", "Kelam Berwajah"),
    2: ("Garuda Kelabu", "Cacing Abu Purba", "Sunan Wirya", "Penjaga Suar Wirasaba",
        "Hampa Berzirah", "Nyi Pandansari", "Juru Nyala Nirmala"),
}
#: Babak 1 tidak lagi berakhir di layar judul — ceritanya mengalir ke Celah Angin,
#: jadi walkthrough-nya berhenti di batas babak lewat langkah "#stop:babak2_mulai".
AKHIR = {1: "berhenti", 2: "chapter_end"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--tail", type=int, default=40)
    ap.add_argument("--sampai", type=int, default=None, help="jalankan hanya N langkah pertama")
    ap.add_argument("--babak", type=int, default=1, choices=(1, 2), help="babak yang dijalankan")
    args = ap.parse_args(argv)
    data = load_data()
    world = load_world(data)
    if args.babak == 1:
        st = new_game(data)
        st.rng = random.Random(args.seed)
        semua = SEMUA
    else:
        st = mulai_babak2(data, args.seed)
        semua = SEMUA_BABAK2
    steps = semua[: args.sampai] + ["@k"] if args.sampai else semua
    wk = Walker(steps, on_command=make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True, auto_choice=False, save_dir=Path(tempfile.mkdtemp()))
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    t = wk.text
    print(f"HASIL: {res} | posisi: {st.area_id}/{st.room_id} | party: {[(h.id, h.level) for h in st.party]} | keping {st.keping}")
    print("sisa langkah:", list(wk.steps)[:5])
    n_enc = len(re.findall(r" muncul!$", t, re.M))
    print(f"pertarungan: {n_enc}")
    for m in re.finditer(r"^(" + "|".join(BOSSES[args.babak]) + r").* muncul!$", t, re.M):
        seg = t[m.end():m.end() + 700]
        lv = re.findall(r"^ (Rimba|Sela|Lintang|Bagas|Rangga|Ratih|Kelana)\s+HP\s+(\d+)/(\d+)", seg, re.M)
        hasil = re.search(r"Hasil: (\w+) dalam (\d+) ronde", t[m.end():])
        print(f"  {m.group(1):<26} party HP {lv}  → {hasil.group(1) if hasil else '?'} ({hasil.group(2) if hasil else '?'} ronde)")
    if res != AKHIR[args.babak]:
        print("---- akhir transkrip ----")
        print("\n".join(t.splitlines()[-args.tail:]))
    return 0 if res == AKHIR[args.babak] else 1


if __name__ == "__main__":
    sys.exit(main())
