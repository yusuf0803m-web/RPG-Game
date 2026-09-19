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
    args = ap.parse_args(argv)
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
