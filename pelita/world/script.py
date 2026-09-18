"""Interpreter skrip cerita (perintah JSON di ``area.scripts``).

Perintah yang didukung (satu objek per perintah):

    {"text": "narasi"}                          tampilkan narasi
    {"say": "Nama", "text": "..."}              baris dialog
    {"pause": true}                             tunggu Enter
    {"if": <kondisi>, "then": [...], "else": [...]}
    {"once": "flag", "do": [...]}               jalankan sekali, lalu set flag
    {"set": "flag" | ["f1","f2"]}   {"unset": "flag"}
    {"battle": ["id", ...], "boss": true, "can_flee": false, "win": [...], "lose": "gameover"|"continue"}
    {"join": "sela", "level": 4, "guest": false}   {"leave": "guntur"}
    {"give": {"item": n}}   {"take": {"item": n}}   {"keping": ±n}   {"xp": n}
    {"heal": "all"}                             pulihkan HP/MP semua
    {"choice": [{"text": "...", "if": <kondisi>, "then": [...]}, ...]}
    {"goto": "ruang"}   {"travel": {"area": "...", "room": "..."}}
    {"save": true}   {"shop": "id"}   {"inn": harga}
    {"quest": "id", "state": "..."}
    {"bara": true}                              aktifkan sumber daya Bara
    {"run": "skrip_lain"}   {"end": true}   {"end_chapter": "teks penutup"}

Kondisi: lihat ``GameState.check``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from ..ui.terminal import IO
from .model import Area
from .state import GameState


class ScriptEnd(Exception):
    """Menghentikan skrip yang sedang berjalan."""


class ChapterEnd(Exception):
    """Akhir babak: kembali ke layar judul."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.text = text


class GameOver(Exception):
    """Seluruh party tumbang di pertarungan cerita."""


@dataclass
class Hooks:
    """Fungsi yang disediakan loop permainan untuk skrip."""
    battle: Callable[[list[str], bool, bool], str]          # (enemy_ids, boss, can_flee) -> "menang"|"kalah"|"kabur"
    save_menu: Callable[[], None]
    shop: Callable[[str], None]
    inn: Callable[[int], None]
    move: Callable[[str, Optional[str]], None]               # (room, area) — pindah tanpa skrip on_enter ganda


def wrap(text: str, width: int = 66, indent: str = " ") -> list[str]:
    import textwrap
    out: list[str] = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.extend(textwrap.wrap(para, width=width, initial_indent=indent, subsequent_indent=indent))
    return out


class ScriptRunner:
    def __init__(self, state: GameState, io: IO, hooks: Hooks, auto: bool = False) -> None:
        self.state = state
        self.io = io
        self.hooks = hooks
        self.auto = auto          # mode otomatis: pilihan pertama, tanpa jeda (untuk tes)

    # -- utilitas tampilan --------------------------------------------------
    def narrate(self, text: str) -> None:
        for line in wrap(text):
            self.io.line(line)
        self.io.line("")

    def say(self, who: str, text: str) -> None:
        lines = wrap(text, width=56, indent="")
        head = f" {who:<8}: "
        for i, l in enumerate(lines):
            self.io.line((head if i == 0 else " " * len(head)) + l)

    def pause(self) -> None:
        if not self.auto:
            self.io.ask("(Enter) ")

    # -- eksekusi -----------------------------------------------------------
    def run(self, area: Area, script_id: str) -> None:
        try:
            self.run_commands(area, area.scripts[script_id])
        except ScriptEnd:
            pass

    def run_commands(self, area: Area, cmds: list) -> None:
        st = self.state
        for c in cmds:
            if "text" in c and "say" not in c:
                self.narrate(c["text"])
            elif "say" in c:
                self.say(c["say"], c["text"])
            elif "pause" in c:
                self.pause()
            elif "if" in c:
                branch = c.get("then", []) if st.check(c["if"]) else c.get("else", [])
                self.run_commands(area, branch)
            elif "once" in c:
                if c["once"] not in st.flags:
                    st.flags.add(c["once"])
                    self.run_commands(area, c.get("do", []))
                elif "else" in c:
                    self.run_commands(area, c["else"])
            elif "set" in c:
                flags = c["set"] if isinstance(c["set"], list) else [c["set"]]
                st.flags.update(flags)
            elif "unset" in c:
                flags = c["unset"] if isinstance(c["unset"], list) else [c["unset"]]
                st.flags.difference_update(flags)
            elif "battle" in c:
                outcome = self.hooks.battle(list(c["battle"]), bool(c.get("boss", False)), bool(c.get("can_flee", False)))
                if outcome == "menang":
                    self.run_commands(area, c.get("win", []))
                elif outcome == "kalah":
                    if c.get("lose", "gameover") == "gameover":
                        raise GameOver()
                    self.run_commands(area, c.get("on_lose", []))
                else:
                    self.run_commands(area, c.get("on_flee", []))
            elif "join" in c:
                h = st.join(c["join"], c.get("level"), bool(c.get("guest", False)))
                for slot, iid in c.get("equip", {}).items():
                    h.equipment[slot] = iid
                h.restore()
                self.io.line(f" ** {h.name} bergabung ke party! **")
                self.io.line("")
            elif "leave" in c:
                h = st.hero(c["leave"])
                if h:
                    st.leave(c["leave"])
                    self.io.line(f" ** {h.name} meninggalkan party. **")
                    self.io.line("")
            elif "give" in c:
                for iid, n in c["give"].items():
                    st.add_item(iid, int(n))
                    self.io.line(f" ** Dapat {st.data.items[iid].name} ×{n}. **")
                self.io.line("")
            elif "take" in c:
                for iid, n in c["take"].items():
                    st.add_item(iid, -int(n))
                    self.io.line(f" ** {st.data.items[iid].name} ×{n} diserahkan. **")
                self.io.line("")
            elif "keping" in c:
                st.keping = max(0, st.keping + int(c["keping"]))
                self.io.line(f" ** Keping {'+' if c['keping'] >= 0 else ''}{c['keping']} (sekarang {st.keping}). **")
                self.io.line("")
            elif "xp" in c:
                self.grant_xp(int(c["xp"]))
            elif "heal" in c:
                st.heal_all()
                self.io.line(" ** HP dan MP seluruh party pulih. **")
                self.io.line("")
            elif "choice" in c:
                opts = [o for o in c["choice"] if st.check(o.get("if"))]
                if not opts:
                    continue
                idx = 0
                if not self.auto:
                    for i, o in enumerate(opts, 1):
                        self.io.line(f"  {i}) {o['text']}")
                    while True:
                        s = self.io.ask("> ")
                        if s.isdigit() and 1 <= int(s) <= len(opts):
                            idx = int(s) - 1
                            break
                        if s.lower() == "q":
                            raise KeyboardInterrupt
                self.run_commands(area, opts[idx].get("then", []))
            elif "goto" in c:
                self.hooks.move(c["goto"], None)
            elif "travel" in c:
                self.hooks.move(c["travel"]["room"], c["travel"]["area"])
            elif "save" in c:
                self.hooks.save_menu()
            elif "shop" in c:
                self.hooks.shop(c["shop"])
            elif "inn" in c:
                self.hooks.inn(int(c["inn"]))
            elif "quest" in c:
                st.quests[c["quest"]] = c.get("state", "aktif")
                self.io.line(f" ** Quest: {c['quest'].replace('_', ' ').title()} — {c.get('state', 'aktif')} **")
                self.io.line("")
            elif "bara" in c:
                from ..combat.engine import BARA_MAX_DASAR
                st.bara_max = BARA_MAX_DASAR
                st.flags.add("bara")
            elif "run" in c:
                self.run_commands(area, area.scripts[c["run"]])
            elif "end" in c:
                raise ScriptEnd()
            elif "end_chapter" in c:
                raise ChapterEnd(c["end_chapter"])
            else:
                raise ValueError(f"perintah skrip tidak dikenal: {c}")

    def grant_xp(self, amount: int) -> None:
        st = self.state
        for h in st.party:
            if h.guest:
                continue
            before = h.level
            levels = h.gain_xp(amount)
            if levels:
                self.io.line(f" ** {h.name} naik ke Lv {h.level}! **")
                for lv in levels:
                    for s in h.new_skills_at(lv):
                        self.io.line(f"    {h.name} mempelajari {s.name}!")
