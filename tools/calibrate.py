"""Kalibrasi Tahap 1 (GAME_DESIGN §4.7): "musuh biasa mati dalam 2–3 aksi kalau
kelemahannya dipakai, 4–6 kalau tidak".

Menjalankan ratusan pertarungan tersimulasi per skenario dengan dua kebijakan
party ("pintar" = pakai kelemahan, "serang" = hanya Serang biasa) dan melaporkan:
- rata-rata aksi party per musuh yang tumbang
- rata-rata ronde per pertarungan
- persentase menang
- rata-rata sisa HP party (%)

Pakai: ``python tools/calibrate.py [--n 300] [--seed 7]``
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pelita.combat import ai  # noqa: E402
from pelita.combat.engine import Battle, Bestiary  # noqa: E402
from pelita.loader import load_data  # noqa: E402
from pelita.party import Hero  # noqa: E402
from pelita.scenarios import SCENARIOS  # noqa: E402


#: Aturan penurunan stat musuh dari formula §4.7. ``peran`` mengikuti tabel di sana:
#: swarm 0.3 · rapuh 0.5-0.7 · normal 0.9-1.0 · tank 1.3-1.4 · boss 30x off (lalu ×1.5, §9.1).
PERAN = {"swarm": 0.3, "rapuh": 0.6, "normal": 0.95, "tank": 1.35}


def off(level: int) -> float:
    return 9.3 + 1.83 * (level - 1)


def stat_musuh(level: int, peran: str = "normal", boss: bool = False, zirah: float = 1.0) -> dict:
    """Stat satu musuh yang diturunkan dari §4.7 — bukan ditebak.

    ``zirah`` menaikkan DEF/RES untuk musuh berzirah/konstruk (tabel §4.7 menyebut
    "tank/zirah lebih tinggi"). Boss memakai HP 30×off lalu ×1.5 sesuai kalibrasi
    ulang §9.1.
    """
    o = off(level)
    if boss:
        hp = round(30 * o * 1.5)
    else:
        hp = round((PERAN[peran] if peran in PERAN else float(peran)) * 7 * o)
    return {
        "hp": hp, "mp": 0,
        "atk": round(7.3 + 1.26 * (level - 1)),
        "def": round(0.55 * o * zirah),
        "mag": round(o * (0.75 if not boss else 0.78)),
        "res": round(0.55 * o * zirah),
        "agi": round(o * 0.25),
        "lck": round(o * 0.12),
        "xp": (30 if boss else 6) * level * level,
        "keping": (5 if boss else 1) * level * level,
    }


def simulate(data, scenario, policy: str, seed: int, bestiary: Bestiary):
    heroes = [Hero.create(data, cid, lv) for cid, lv in scenario.party]
    b = Battle(data, heroes, scenario.enemies, rng=random.Random(seed), bestiary=bestiary, inventory=dict(scenario.inventory))
    b.start()
    hero_actions = 0
    guard = 0
    while not b.over and guard < 400:
        guard += 1
        t = b.next_turn()
        if t.skipped or t.actor is None:
            continue
        if t.actor.is_player:
            a = ai.choose_hero_action(b, t.actor, policy)
            if a.kind in ("serang", "skill") and (a.skill is None or a.skill.is_attack):
                hero_actions += 1
        else:
            a = ai.choose_enemy_action(b, t.actor)
        b.act(t.actor, a)
    r = b.result
    kills = sum(1 for e in b.enemies if not e.alive)
    hp_left = statistics.mean(h.hp / h.max_hp for h in b.heroes) if b.heroes else 0
    return {
        "menang": r is not None and r.outcome == "menang",
        "ronde": r.rounds if r else guard,
        "aksi_per_kill": hero_actions / kills if kills else float("nan"),
        "hp_sisa": hp_left,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", help="id skenario")
    ap.add_argument("--musuh", nargs="+", metavar="LEVEL:PERAN[:zirah]",
                    help="cetak stat musuh dari rumus §4.7, mis. --musuh 47:boss 45:tank")
    args = ap.parse_args(argv)
    if args.musuh:
        for spec in args.musuh:
            bagian = spec.split(":")
            lv, peran = int(bagian[0]), bagian[1]
            zirah = float(bagian[2]) if len(bagian) > 2 else 1.0
            st = stat_musuh(lv, peran, boss=(peran == "boss"), zirah=zirah)
            print(spec, json.dumps(st, ensure_ascii=False))
        return 0
    data = load_data()
    print(f"{'skenario':<12} {'kebijakan':<8} {'menang%':>8} {'ronde':>6} {'aksi/kill':>10} {'HP sisa%':>9}")
    for sc in SCENARIOS:
        if args.only and sc.id != args.only:
            continue
        for policy in ("pintar", "tunggal", "serang"):
            # bestiary dibagi antar-run supaya kebijakan "pintar" belajar kelemahan seperti pemain
            bestiary = Bestiary()
            rows = [simulate(data, sc, policy, args.seed * 1000 + i, bestiary) for i in range(args.n)]
            menang = 100 * sum(r["menang"] for r in rows) / len(rows)
            ronde = statistics.mean(r["ronde"] for r in rows)
            apk = statistics.mean(r["aksi_per_kill"] for r in rows if r["aksi_per_kill"] == r["aksi_per_kill"])
            hp = 100 * statistics.mean(r["hp_sisa"] for r in rows)
            print(f"{sc.id:<12} {policy:<8} {menang:>7.0f}% {ronde:>6.1f} {apk:>10.2f} {hp:>8.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
