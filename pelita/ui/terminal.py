"""Tampilan pertarungan di terminal (GAME_DESIGN §7): satu layar = satu keputusan.

``IO`` memisahkan input/output supaya loop pertarungan bisa dites dengan input
terskrip tanpa terminal sungguhan.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence

from ..combat import ai
from ..combat.engine import Action, Battle, Combatant
from ..models import Affinity, Element, Skill, Target
from .menu import Header, Menu, Option, numbered

LEBAR = 66


class IO:
    #: True kalau klien menampilkan ``emit()`` secara grafis; render teks (bar ASCII,
    #: header ruang) dilewati agar tidak tampil dua kali.
    structured = False

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

    def emit(self, kind: str, payload: dict) -> None:
        """Kanal terstruktur untuk UI selain terminal (web). Terminal mengabaikannya."""

    # -- prompt bertombol ---------------------------------------------------
    # Semua menu permainan lewat sini (lihat ``pelita/ui/menu.py``). Terminal
    # mencetak satu opsi per baris; antarmuka lain (web) menimpa metode ini dan
    # mengirim daftar opsinya sebagai data.
    def menu(self, options: Sequence[Option], prompt: str = "> ", auto: Optional[str] = None,
             required: Optional[str] = None, header: Optional[Header] = None) -> str:
        """Tampilkan daftar opsi, kembalikan key yang dipilih (sudah lowercase)."""
        keys = {o.key.lower(): o for o in options}
        keluar = next((o.key.lower() for o in options if o.back), None)
        # Enter = jalan keluar, tapi hanya untuk opsi "0) Kembali"; pintasan huruf
        # seperti [K]eluar (keluar ke layar judul) tidak boleh terpicu tanpa sengaja.
        enter = next((o.key.lower() for o in options if o.back and not o.meta), None)
        while True:
            self.render_options(options, header)
            if auto is not None:
                return auto.lower()
            s = self.ask(prompt).strip().lower()
            if s in keys:
                return s
            if s == "" and enter is not None:
                return enter
            if s in ("q", "quit", "keluar"):
                if keluar is None:
                    raise KeyboardInterrupt
                return keluar
            self.line("  Pilihan tidak dikenal.")

    def render_options(self, options: Sequence[Option], header: Optional[Header] = None) -> None:
        """Cetak menu: judul, lalu satu opsi per baris, pintasan huruf di baris terakhir."""
        if header:
            self.line("")
            if header.title:
                self.line(header.line)
            for n in header.note:
                self.line(n)
        for o in options:
            if o.meta:
                continue
            self.line(o.text)
            for d in o.detail:
                self.line(d)
        huruf = [o.text for o in options if o.meta]
        if huruf:
            self.line("  " + "  ".join(huruf))

    def pick(self, prompt: str, labels: Sequence[str], back: Optional[str] = "Kembali",
             auto: Optional[str] = None, required: Optional[str] = None,
             title: Optional[str] = None, subtitle: Optional[str] = None,
             note: Sequence[str] = ()) -> Optional[int]:
        """Menu bernomor sederhana: kembalikan indeks pilihan, None kalau kembali."""
        return numbered(labels, back=back, required=required, title=title,
                        subtitle=subtitle, note=note).pick(self, prompt, auto=auto)

    def confirm(self, question: str, auto: Optional[bool] = None) -> bool:
        """Pertanyaan ya/tidak. Web menampilkannya sebagai dua tombol."""
        if auto is not None:
            return auto
        return self.ask(f"  {question} (y/N) ").strip().lower() in ("y", "ya")

    def pause(self) -> None:
        """Tunggu pemain menekan Enter (web: tombol 'Lanjut')."""
        self.ask("(Enter) ")


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


def battle_snapshot(battle: Battle, title: str) -> dict:
    """Keadaan pertarungan untuk UI terstruktur."""
    enemies = []
    for e in battle.enemies:
        known = battle.bestiary.get(e.key)
        enemies.append({
            "key": e.key, "name": e.display_name, "alive": e.alive,
            "hp": e.hp, "max_hp": e.max_hp, "boss": e.is_boss,
            "ketahanan": e.ketahanan, "ketahanan_max": e.ketahanan_max, "pecah": e.has("pecah"),
            "weak": [el.label for el, a in known.items() if a == Affinity.LEMAH],
            "resist": [el.label for el, a in known.items() if a in (Affinity.TAHAN, Affinity.IMUN)],
            "absorb": [el.label for el, a in known.items() if a == Affinity.SERAP],
            "statuses": [{"name": s.name, "turns": s.turns_left, "bad": s.bad} for s in e.statuses.values()],
        })
    heroes = [{
        "key": h.key, "name": h.name, "alive": h.alive, "level": h.level,
        "hp": h.hp, "max_hp": h.max_hp, "mp": h.mp, "max_mp": h.max_mp,
        "statuses": [{"name": s.name, "turns": s.turns_left, "bad": s.bad} for s in h.statuses.values()],
    } for h in battle.heroes]
    bench = [{"key": h.key, "name": h.name, "alive": h.alive, "level": h.level,
              "hp": h.hp, "max_hp": h.max_hp, "mp": h.mp, "max_mp": h.max_mp} for h in battle.bench]
    return {"title": title, "round": battle.round, "enemies": enemies, "heroes": heroes, "bench": bench,
            "bara": battle.bara, "bara_max": battle.bara_max, "bara_frozen": battle.bara_frozen}


def render_screen(battle: Battle, title: str, io: IO) -> None:
    io.emit("battle", battle_snapshot(battle, title))
    if io.structured:
        return
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
    if battle.bara_max > 0:
        io.line(f" Bara {'◆' * battle.bara}{'◇' * (battle.bara_max - battle.bara)}" + ("  (beku)" if battle.bara_frozen else ""))
    io.line("─" * LEBAR)


def _pick(io: IO, prompt: str, options: list[str], allow_back: bool = True) -> Optional[int]:
    """Tampilkan daftar bernomor, kembalikan indeks pilihan (None = batal)."""
    return io.pick(prompt, options, back="Kembali" if allow_back else None,
                   required=None if allow_back else "aksi pertarungan")


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
        cadangan = battle.bisa_ganti(actor)
        if cadangan:
            menu.append("Ganti")
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
        elif choice == "Ganti":
            labels = [f"{c.name} Lv {c.level}  HP {c.hp}/{c.max_hp}  MP {c.mp}/{c.max_mp}" for c in cadangan]
            j = _pick(io, "masuk> ", labels)
            if j is None:
                continue
            return Action("ganti", targets=[cadangan[j]])
        elif choice == "Kabur":
            return Action("kabur")


def _keluarkan(io: IO, battle: Battle, events: list[str], prefix: str = "  ") -> None:
    """Tulis baris log dan sisipkan event ``fx`` tepat sebelum baris yang
    ditimbulkannya, supaya klien grafis memutar animasi dulu baru teksnya."""
    fx = battle.drain_fx()
    i = 0
    for n, line in enumerate(events):
        while i < len(fx) and fx[i]["pos"] <= n:
            io.emit("fx", fx[i])
            i += 1
        io.line(prefix + line)
    for f in fx[i:]:
        io.emit("fx", f)


def run_battle(battle: Battle, title: str, io: IO, auto: bool = False, pause: bool = True) -> None:
    """Loop pertarungan lengkap. ``auto`` memakai kebijakan otomatis untuk party."""
    _keluarkan(io, battle, battle.start(), prefix="")
    while not battle.over:
        turn = battle.next_turn()
        _keluarkan(io, battle, turn.events)
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
        _keluarkan(io, battle, battle.act(actor, action))
        if not actor.is_player:
            io.emit("battle", battle_snapshot(battle, title))
        if pause and not actor.is_player and not auto and not battle.over:
            io.pause()
    io.line("═" * LEBAR)
    r = battle.result
    assert r is not None
    io.emit("battle", battle_snapshot(battle, title))
    io.emit("battle_end", {"outcome": r.outcome, "rounds": r.rounds, "xp": r.xp, "keping": r.keping})
    io.line(f" Hasil: {r.outcome.upper()} dalam {r.rounds} ronde.")
