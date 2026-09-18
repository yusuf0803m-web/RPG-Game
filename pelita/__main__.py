"""Titik masuk prototipe: ``python -m pelita [--scenario ID] [--auto] [--seed N]``."""
from __future__ import annotations

import argparse
import random
import sys

from .combat.engine import Battle
from .loader import load_data
from .party import Hero
from .scenarios import SCENARIOS, get_scenario
from .ui.terminal import IO, run_battle


def build_battle(data, scenario, seed=None) -> Battle:
    heroes = [Hero.create(data, cid, lv) for cid, lv in scenario.party]
    return Battle(data, heroes, scenario.enemies, rng=random.Random(seed), inventory=dict(scenario.inventory))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pelita", description="Pelita Terakhir — prototipe pertarungan (Tahap 1)")
    ap.add_argument("--scenario", "-s", help="id skenario (lihat --list)")
    ap.add_argument("--list", "-l", action="store_true", help="daftar skenario")
    ap.add_argument("--auto", "-a", action="store_true", help="party dikendalikan kebijakan otomatis (demo)")
    ap.add_argument("--seed", type=int, default=None, help="seed RNG agar pertarungan bisa diulang")
    ap.add_argument("--no-pause", action="store_true", help="jangan berhenti menunggu Enter setelah giliran musuh")
    args = ap.parse_args(argv)

    data = load_data()
    io = IO()
    if args.list:
        for s in SCENARIOS:
            io.line(f"  {s.id:<12} {s.name}")
            io.line(f"  {'':<12} {s.note}")
        return 0
    if args.scenario:
        scenario = get_scenario(args.scenario)
    else:
        io.line("Pelita Terakhir — prototipe pertarungan")
        io.line("Pilih skenario:")
        for i, s in enumerate(SCENARIOS, 1):
            io.line(f"  {i}) {s.name}")
        while True:
            s = io.ask("> ")
            if s.isdigit() and 1 <= int(s) <= len(SCENARIOS):
                scenario = SCENARIOS[int(s) - 1]
                break
            if s.lower() in ("q", "keluar"):
                return 0
    io.line(f"\n{scenario.name}\n{scenario.note}\n")
    battle = build_battle(data, scenario, args.seed)
    try:
        run_battle(battle, scenario.name, io, auto=args.auto, pause=not args.no_pause)
    except KeyboardInterrupt:
        io.line("\nKeluar.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
