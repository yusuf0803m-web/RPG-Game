"""Tampilan pertarungan di terminal (GAME_DESIGN §7): satu layar = satu keputusan.

``IO`` memisahkan input/output supaya loop pertarungan bisa dites dengan input
terskrip tanpa terminal sungguhan.
"""
from __future__ import annotations

from typing import Callable, Optional

from ..combat import ai
from ..combat.engine import Action, Battle, Combatant
from ..models import Affinity, Element, Skill, Target

LEBAR = 66


class IO:
    def __init__(self, read: Callable[[str], str] = input, write: Callable[[str], None] = print) -> None:
        self.read = read
        self.write = write

    def line(self, s: str = "") -> None:
        self.write(s)

    def ask(self, prompt: str = "> ") -> str:
        try:
            return self.read(prompt).strip()
        except EOFError:
            return "q"


def bar(ratio: float, width: int = 10) -> str:
    n = max(0, min(width, round(ratio * width)))
    if ratio > 0 and n == 0:
        n = 1
    return "█" * n + "░" * (width - n)


def _aff_notes(battle: Battle, e: Combatant) -> str:
    known = battle.bestiary.get(e.key)
    lemah = [el.label for el, a in known.items() if a == Affinity.LEMAH]
    buruk = [f"{el.label}" for el, a in known.items() if a in (Affinity.TAHAN, Affinity.IMUN, Affinity.SERAP)]
    parts = []
    parts.append("lemah: " + (", ".join(lemah) if lemah else "?"))
    if buruk:
        serap = [el.label for el, a in known.items() if a == Affinity.SERAP]
        if serap:
            parts.append("SERAP: " + ", ".join(serap))
        tahan = [el.label for el, a in known.items() if a in (Affinity.TAHAN, Affinity.IMUN)]
        if tahan:
            parts.append("tahan: " + ", ".join(tahan))
    return "   ".join(parts)


def render_screen(battle: Battle, title: str, io: IO) -> None:
    io.line("═" * LEBAR)
    io.line(f" {title}")
    io.line("─" * LEBAR)
    for e in battle.enemies:
        if not e.alive:
            io.line(f" {e.display_name:<20} (tumbang)")
            continue
        ket = ""
        if e.ketahanan_max:
            ket = f"  KETAHANAN [{bar(e.ketahanan / e.ketahanan_max, 5)}]" if not e.has("pecah") else "  *PECAH*"
        io.line(f" {e.display_name:<20} [{bar(e.hp_ratio)}]{ket}")
        io.line(f"   {_aff_notes(battle, e)}  {e.status_line()}")
    io.line("─" * LEBAR)
    for h in battle.heroes:
        if not h.alive:
            io.line(f" {h.name:<9} pingsan")
            continue
        io.line(f" {h.name:<9} HP {h.hp:>4}/{h.max_hp:<4}  MP {h.mp:>3}/{h.max_mp:<3}  {h.status_line()}")
    io.line(f" Bara {'◆' * battle.bara}{'◇' * (battle.bara_max - battle.bara)}" + ("  (beku)" if battle.bara_frozen else ""))
    io.line("─" * LEBAR)


def _pick(io: IO, prompt: str, options: list[str], allow_back: bool = True) -> Optional[int]:
    """Tampilkan daftar bernomor, kembalikan indeks pilihan (None = batal)."""
    for i, o in enumerate(options, 1):
        io.line(f"  {i}) {o}")
    if allow_back:
        io.line("  0) Kembali")
    while True:
        s = io.ask(prompt)
        if s.lower() in ("q", "quit", "keluar"):
            raise KeyboardInterrupt
        if allow_back and s in ("0", ""):
            return None
        if s.isdigit() and 1 <= int(s) <= len(options):
            return int(s) - 1
        io.line("  Pilihan tidak dikenal.")


def _skill_label(battle: Battle, actor: Combatant, s: Skill) -> str:
    biaya = f"{s.cost} {s.cost_type.value.upper()}" if s.cost else "gratis"
    if s.cost_type.value == "bara":
        biaya = f"{s.cost} Bara"
    tgt = {Target.SATU_MUSUH: "satu musuh", Target.SEMUA_MUSUH: "semua musuh", Target.SATU_KAWAN: "satu kawan",
           Target.SEMUA_KAWAN: "semua kawan", Target.DIRI: "diri", Target.KAWAN_PINGSAN: "kawan pingsan"}[s.target]
    el = "" if s.element == Element.NETRAL else f" [{s.element.label}]"
    desc = f" — {s.description}" if s.description else ""
    return f"{s.name}{el} ({biaya}, {tgt}){desc}"


def _choose_target(battle: Battle, actor: Combatant, target: Target, io: IO) -> Optional[list[Combatant]]:
    cands = battle.valid_targets(actor, target)
    if not cands:
        io.line("  Tidak ada sasaran.")
        return None
    if target.is_multi or target == Target.DIRI or len(cands) == 1:
        return cands
    labels = [f"{c.display_name}  HP {c.hp}/{c.max_hp}" if c.is_player else f"{c.display_name}  [{bar(c.hp_ratio)}]" for c in cands]
    i = _pick(io, "sasaran> ", labels)
    return None if i is None else [cands[i]]


def choose_action_interactive(battle: Battle, actor: Combatant, io: IO) -> Action:
    while True:
        io.line(f" Giliran {actor.name}.")
        menu = ["Serang", "Skill", "Item", "Jaga"]
        bara = battle.usable_bara_skills(actor)
        if bara:
            menu.append("Bara")
        if battle.can_flee:
            menu.append("Kabur")
        i = _pick(io, "> ", menu, allow_back=False)
        choice = menu[i]
        if choice == "Serang":
            ts = _choose_target(battle, actor, Target.SATU_MUSUH, io)
            if ts:
                return Action("serang", targets=ts)
        elif choice == "Skill":
            skills = battle.usable_skills(actor)
            if not skills:
                io.line("  Tidak ada skill yang bisa dipakai." + (" (Lupa/Bisu)" if not actor.can_use_skills or not actor.can_use_magic else " (MP kurang)"))
                continue
            j = _pick(io, "skill> ", [_skill_label(battle, actor, s) for s in skills])
            if j is None:
                continue
            ts = _choose_target(battle, actor, skills[j].target, io)
            if ts:
                return Action("skill", skill=skills[j], targets=ts)
        elif choice == "Item":
            items = battle.usable_items()
            if not items:
                io.line("  Tidak ada item.")
                continue
            j = _pick(io, "item> ", [f"{it.name} ×{battle.inventory[it.id]}" + (f" — {it.description}" if it.description else "") for it in items])
            if j is None:
                continue
            ts = _choose_target(battle, actor, items[j].target, io)
            if ts:
                return Action("item", item=items[j], targets=ts)
        elif choice == "Jaga":
            return Action("jaga")
        elif choice == "Bara":
            j = _pick(io, "bara> ", [_skill_label(battle, actor, s) for s in bara])
            if j is None:
                continue
            ts = _choose_target(battle, actor, bara[j].target, io)
            if ts:
                return Action("skill", skill=bara[j], targets=ts)
        elif choice == "Kabur":
            return Action("kabur")


def run_battle(battle: Battle, title: str, io: IO, auto: bool = False, pause: bool = True) -> None:
    """Loop pertarungan lengkap. ``auto`` memakai kebijakan otomatis untuk party."""
    for e in battle.start():
        io.line(e)
    while not battle.over:
        turn = battle.next_turn()
        for e in turn.events:
            io.line("  " + e)
        if turn.skipped or turn.actor is None:
            continue
        actor = turn.actor
        if actor.is_player:
            render_screen(battle, title, io)
            if auto:
                action = ai.choose_hero_action(battle, actor)
                io.line(f" {actor.name} (auto): {action.label}")
            else:
                action = choose_action_interactive(battle, actor, io)
        else:
            action = ai.choose_enemy_action(battle, actor)
        for e in battle.act(actor, action):
            io.line("  " + e)
        if pause and not actor.is_player and not auto and not battle.over:
            io.ask("(Enter) ")
    io.line("═" * LEBAR)
    r = battle.result
    assert r is not None
    io.line(f" Hasil: {r.outcome.upper()} dalam {r.rounds} ronde.")
