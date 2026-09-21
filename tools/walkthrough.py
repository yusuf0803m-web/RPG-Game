"""Jalankan walkthrough otomatis satu babak dan cetak ringkasannya: jumlah pertarungan,
level party, dan lama tiap boss.

    python tools/walkthrough.py --seed 11                 Babak 1 (berhenti di batas babak)
    python tools/walkthrough.py --babak 2 --seed 5        Babak 2 (berhenti di batas babak)
    python tools/walkthrough.py --babak 3 --seed 3        Babak 3 sampai tamat
    python tools/walkthrough.py --babak 3 --ending kembali    pilih ending lain
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
from tests.test_babak3 import (  # noqa: E402
    ENDING_DENDANG, ENDING_KEMBALI, ENDING_NYALA, SEMUA_BABAK3, make_pemain, mulai_babak3)
from tests.walker import Walker  # noqa: E402

BOSSES = {
    1: ("Hampa Penjaga Hutan", "Raja Katak Lumpur", "Ular Cermin", "Kapten Rangga",
        "Penambang Raksasa Terlupa", "Penjaga Mercusuar", "Adipati Baskara", "Kelam Berwajah"),
    2: ("Garuda Kelabu", "Cacing Abu Purba", "Sunan Wirya", "Penjaga Suar Wirasaba",
        "Hampa Berzirah", "Nyi Pandansari", "Juru Nyala Nirmala"),
    3: ("Gema Pengantin", "Gema Prajurit", "Gema Guntur", "Penjaga Suar Api", "Penjaga Suar Kelam",
        "Sang Pelita Pertama", "Gelombang Kabut A", "Kabut Terakhir"),
}
#: Tiga ending Babak 3 (GAME_DESIGN §2.4). "dendang" butuh syarat rahasia, yang
#: disiapkan ``mulai_babak3(lengkap=True)``.
ENDING = {"nyala": ENDING_NYALA, "kembali": ENDING_KEMBALI, "dendang": ENDING_DENDANG}
#: Babak 1 dan 2 tidak berakhir di layar judul — ceritanya mengalir langsung ke babak
#: berikutnya, jadi walkthrough-nya berhenti di batas babak lewat langkah "#stop:...".
#: Hanya Babak 3 yang benar-benar tamat (end_chapter = salah satu dari tiga ending).
AKHIR = {1: "berhenti", 2: "berhenti", 3: "chapter_end"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--tail", type=int, default=40)
    ap.add_argument("--sampai", type=int, default=None, help="jalankan hanya N langkah pertama")
    ap.add_argument("--babak", type=int, default=1, choices=(1, 2, 3), help="babak yang dijalankan")
    ap.add_argument("--ending", default="nyala", choices=sorted(ENDING),
                    help="--babak 3: ending yang dipilih di Sumur Ingatan")
    ap.add_argument("--bunuh-kelana", action="store_true",
                    help="--babak 3: jalur 'Kelana dibunuh' (hanya ending 'kembali' tersisa)")
    args = ap.parse_args(argv)
    data = load_data()
    world = load_world(data)
    kotak: list = []
    hook = None
    if args.babak == 1:
        st = new_game(data)
        st.rng = random.Random(args.seed)
        semua = SEMUA
    elif args.babak == 2:
        st = mulai_babak2(data, args.seed)
        semua = SEMUA_BABAK2
    else:
        st = mulai_babak3(data, args.seed, kelana_dibunuh=args.bunuh_kelana,
                          lengkap=(args.ending == "dendang"))
        semua = SEMUA_BABAK3 + ENDING[args.ending]
        hook = make_pemain(st, kotak)
    steps = semua[: args.sampai] + ["@k"] if args.sampai else semua
    wk = Walker(steps, on_command=hook or make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True, auto_choice=False, save_dir=Path(tempfile.mkdtemp()))
    kotak.append(g)
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
