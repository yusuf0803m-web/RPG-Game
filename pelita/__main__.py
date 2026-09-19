"""Titik masuk.

    python -m pelita                      layar judul (Mulai Baru / Muat / Prototipe Combat)
    python -m pelita --web                antarmuka web di http://127.0.0.1:5000
    python -m pelita --web --lan          antarmuka web yang bisa dibuka dari HP (satu Wi-Fi)
    python -m pelita --new                langsung mulai permainan baru
    python -m pelita --load N             muat slot N
    python -m pelita --scenario ID        prototipe pertarungan tunggal (Tahap 1)
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from .combat.engine import Battle
from .loader import load_data
from .party import Hero
from .scenarios import SCENARIOS, get_scenario
from .ui.terminal import IO, LEBAR, run_battle
from .world.explore import Game
from .world.model import load_world
from .world.state import SAVE_DIR, SAVE_SLOTS, GameState, new_game

JUDUL = r"""
  ____       _ _ _          _____              _    _     _
 |  _ \ ___| (_) |_ __ _  |_   _|__ _ __ __ _| | _(_)___| |__  (_)_ __
 | |_) / _ \ | | __/ _` |   | |/ _ \ '__/ _` | |/ / / __| '_ \ | | '__|
 |  __/  __/ | | || (_| |   | |  __/ | | (_| |   <| \__ \ | | || | |
 |_|   \___|_|_|\__\__,_|   |_|\___|_|  \__,_|_|\_\_|___/_| |_||_|_|
"""


def build_battle(data, scenario, seed=None) -> Battle:
    heroes = [Hero.create(data, cid, lv) for cid, lv in scenario.party]
    return Battle(data, heroes, scenario.enemies, rng=random.Random(seed), inventory=dict(scenario.inventory))


def play(data, world, state: GameState, io: IO, save_dir: Path) -> str:
    game = Game(data, world, state, io, save_dir=save_dir)
    return game.run()


def load_menu(data, io: IO, save_dir: Path):
    sums = GameState.slot_summaries(data, save_dir)
    if not any(sums):
        io.line(" Belum ada save.")
        return None
    for i, s in enumerate(sums, 1):
        io.line(f"  {i}) {s or '(kosong)'}")
    io.line("  0) Kembali")
    s = io.ask("slot> ")
    if s.isdigit() and 1 <= int(s) <= SAVE_SLOTS and sums[int(s) - 1]:
        return GameState.load(data, int(s), save_dir)
    return None


def title_loop(data, world, io: IO, save_dir: Path) -> int:
    while True:
        io.line(JUDUL)
        io.line("  1) Mulai Baru   2) Muat   3) Prototipe Combat   0) Keluar")
        s = io.ask("> ")
        if s == "1":
            play(data, world, new_game(data), io, save_dir)
        elif s == "2":
            st = load_menu(data, io, save_dir)
            if st:
                play(data, world, st, io, save_dir)
        elif s == "3":
            prototype_menu(data, io)
        elif s in ("0", "q", "keluar"):
            return 0


def prototype_menu(data, io: IO) -> None:
    io.line("Pilih skenario:")
    for i, s in enumerate(SCENARIOS, 1):
        io.line(f"  {i}) {s.name}")
    io.line("  0) Kembali")
    s = io.ask("> ")
    if s.isdigit() and 1 <= int(s) <= len(SCENARIOS):
        sc = SCENARIOS[int(s) - 1]
        io.line(f"\n{sc.name}\n{sc.note}\n")
        run_battle(build_battle(data, sc), sc.name, io)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pelita", description="Pelita Terakhir — RPG teks turn-based")
    ap.add_argument("--web", action="store_true", help="jalankan antarmuka web (butuh Flask)")
    ap.add_argument("--lan", action="store_true", help="--web: izinkan HP/tablet di Wi-Fi yang sama ikut main")
    ap.add_argument("--host", default="127.0.0.1", help="--web: alamat server")
    ap.add_argument("--port", type=int, default=5000, help="--web: porta server")
    ap.add_argument("--new", action="store_true", help="langsung mulai permainan baru")
    ap.add_argument("--load", type=int, metavar="SLOT", help="muat save dari slot")
    ap.add_argument("--save-dir", default=str(SAVE_DIR), help="folder save (default: saves/)")
    ap.add_argument("--scenario", "-s", help="prototipe pertarungan: id skenario (lihat --list)")
    ap.add_argument("--list", "-l", action="store_true", help="daftar skenario prototipe")
    ap.add_argument("--auto", "-a", action="store_true", help="prototipe: party dikendalikan otomatis")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--no-pause", action="store_true")
    args = ap.parse_args(argv)

    data = load_data()
    io = IO()
    save_dir = Path(args.save_dir)
    try:
        if args.web:
            try:
                from .web.app import main as web_main
            except ImportError:
                io.line("Antarmuka web butuh Flask:  pip install flask")
                return 1
            web_argv = ["--host", args.host, "--port", str(args.port), "--save-dir", args.save_dir]
            if args.lan:
                web_argv.append("--lan")
            return web_main(web_argv)
        if args.list:
            for s in SCENARIOS:
                io.line(f"  {s.id:<12} {s.name}")
                io.line(f"  {'':<12} {s.note}")
            return 0
        if args.scenario:
            sc = get_scenario(args.scenario)
            io.line(f"\n{sc.name}\n{sc.note}\n")
            run_battle(build_battle(data, sc, args.seed), sc.name, io, auto=args.auto, pause=not args.no_pause)
            return 0
        world = load_world(data)
        if args.new:
            play(data, world, new_game(data), io, save_dir)
            return 0
        if args.load:
            play(data, world, GameState.load(data, args.load, save_dir), io, save_dir)
            return 0
        return title_loop(data, world, io, save_dir)
    except KeyboardInterrupt:
        io.line("\nKeluar.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
