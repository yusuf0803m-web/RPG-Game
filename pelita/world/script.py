"""Interpreter skrip cerita (perintah JSON di ``area.scripts``).

Perintah yang didukung (satu objek per perintah):

    {"text": "narasi"}                          tampilkan narasi
    {"say": "Nama", "text": "..."}              baris dialog
        tambahan opsional (hanya tampilan web, GAME_DESIGN §7.3):
                  "ekspresi": "happy"   ekspresi potret; tanpa ini = ekspresi bawaan tokoh
                  "tokoh": "rimba"      id tokoh kalau teks "say" bukan nama/aliasnya (mis. "???")
    {"pause": true}                             tunggu Enter
    {"if": <kondisi>, "then": [...], "else": [...]}
    {"once": "flag", "do": [...]}               jalankan sekali, lalu set flag
    {"set": "flag" | ["f1","f2"]}   {"unset": "flag"}
    {"battle": ["id", ...], "boss": true, "can_flee": false, "win": [...], "lose": "gameover"|"continue"}
        tambahan: "bertahan": N  (menang setelah N ronde, bukan setelah musuh habis)
                  "bertahan_teks": "..."  (baris penutup pertarungan bertahan)
    {"join": "sela", "level": 4, "guest": false}   {"leave": "guntur"}
    {"give": {"item": n}}   {"take": {"item": n}}   {"keping": ±n}   {"xp": n}
    {"heal": "all"}                             pulihkan HP/MP semua
    {"choice": [{"text": "...", "if": <kondisi>, "then": [...]}, ...]}
    {"goto": "ruang"}   {"travel": {"area": "...", "room": "..."}}
    {"save": true}   {"shop": "id"}   {"inn": harga}
    {"tukang_kaca": "toko_kaca"}   {"kemah": true}   {"papan_buruan": true}   {"arena": true}
    {"adegan": {"latar": "...", "efek": "zoom"|"flash"|"shake"|"gelap", "teks": "..."}}
    {"ilustrasi": "events/...", "teks": "keterangan"}      ilustrasi layar penuh (peristiwa besar)
    {"kaca": {"kaca_api": 1}}                   beri Kaca Ingatan
    {"quest": "id", "state": "..."}
    {"barisan": ["ratih"]}                      tarik nama-nama itu ke barisan aktif
    {"bara": true}                              aktifkan sumber daya Bara
    {"bara": 8}                                 naikkan Bara maks ke angka itu (syarat Jurus Empat)
    {"lucuti": true}                            lepaskan Bara, Kaca, dan Jalur seluruh party
                                                (ending "Mengembalikan": dunia tanpa sihir)
    {"run": "skrip_lain"}   {"end": true}   {"end_chapter": "teks penutup"}

Kondisi: lihat ``GameState.check``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from ..ui.menu import Menu
from ..ui.terminal import IO
from .model import Area
from .state import BARA_HOLDER_ID, PARTY_AKTIF_MAKS, XP_CADANGAN, GameState


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
    battle: Callable[..., str]      # (enemy_ids, boss, can_flee, **opsi) -> "menang"|"kalah"|"kabur"
    save_menu: Callable[[], None]
    shop: Callable[[str], None]
    inn: Callable[[int], None]
    move: Callable[[str, Optional[str]], None]               # (room, area) — pindah tanpa skrip on_enter ganda
    tukang_kaca: Callable[[str], None] = lambda shop_id: None   # bengkel Kaca & penukaran Serpihan
    kemah: Callable[[], None] = lambda: None                    # berkemah + adegan Kenangan
    papan_buruan: Callable[[], None] = lambda: None             # papan kontrak Buruan
    arena: Callable[[], None] = lambda: None                    # Arena Kafilah


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
    def __init__(self, state: GameState, io: IO, hooks: Hooks, auto: bool = False, auto_choice: Optional[bool] = None) -> None:
        self.state = state
        self.io = io
        self.hooks = hooks
        self.auto = auto          # tanpa jeda Enter (untuk tes)
        self.auto_choice = auto if auto_choice is None else auto_choice   # pilihan pertama otomatis

    # -- utilitas tampilan --------------------------------------------------
    def narrate(self, text: str) -> None:
        self.io.emit("text", {"text": text})
        if self.io.structured:
            return
        for line in wrap(text):
            self.io.line(line)
        self.io.line("")

    def say(self, who: str, text: str, ekspresi: Optional[str] = None, tokoh: Optional[str] = None) -> None:
        payload = {"who": who, "text": text}
        if ekspresi:
            payload["ekspresi"] = ekspresi
        if tokoh:
            payload["tokoh"] = tokoh
        self.io.emit("say", payload)
        if self.io.structured:
            return
        lines = wrap(text, width=56, indent="")
        head = f" {who:<8}: "
        for i, l in enumerate(lines):
            self.io.line((head if i == 0 else " " * len(head)) + l)

    def pause(self) -> None:
        if not self.auto:
            self.io.pause()

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
                self.say(c["say"], c["text"], c.get("ekspresi"), c.get("tokoh"))
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
                outcome = self.hooks.battle(list(c["battle"]), bool(c.get("boss", False)),
                                            bool(c.get("can_flee", False)),
                                            bertahan=int(c.get("bertahan", 0)),
                                            bertahan_teks=c.get("bertahan_teks", ""))
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
                delta = st.ubah_keping(int(c["keping"]), "cerita")
                self.io.line(f" ** Keping {'+' if delta >= 0 else ''}{delta} (sekarang {st.keping}). **")
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
                # Pilihan cerita memang tidak punya "kembali": jawabannya menggerakkan adegan.
                m = Menu().no_back("pilihan cerita")
                for o in opts:
                    m.add(o["text"])
                idx = m.pick(self.io, "> ", auto="1" if self.auto_choice else None)
                self.run_commands(area, opts[idx or 0].get("then", []))
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
            elif "tukang_kaca" in c:
                self.hooks.tukang_kaca(c["tukang_kaca"] if isinstance(c["tukang_kaca"], str) else "")
            elif "kemah" in c:
                self.hooks.kemah()
            elif "papan_buruan" in c:
                self.hooks.papan_buruan()
            elif "arena" in c:
                self.hooks.arena()
            elif "adegan" in c:
                a = c["adegan"]
                self.io.emit("adegan", {"latar": a.get("latar", ""), "efek": a.get("efek", "fade")})
                if a.get("teks"):
                    self.narrate(a["teks"])
            elif "ilustrasi" in c:
                self.io.emit("ilustrasi", {"latar": c["ilustrasi"], "teks": c.get("teks", "")})
                if not self.io.structured:
                    judul = c.get("teks") or c["ilustrasi"]
                    self.io.line("")
                    self.io.line(" " + "─" * 60)
                    for l in wrap(judul, width=58, indent="  "):
                        self.io.line(l)
                    self.io.line(" " + "─" * 60)
                    self.io.line("")
                self.pause()
            elif "kaca" in c:
                for kid, n in c["kaca"].items():
                    st.add_kaca(kid, int(n))
                    self.io.line(f" ** Dapat {st.data.kaca[kid].name}. **")
                self.io.line("")
            elif "quest" in c:
                st.quests[c["quest"]] = c.get("state", "aktif")
                self.io.line(f" ** Quest: {c['quest'].replace('_', ' ').title()} — {c.get('state', 'aktif')} **")
                self.io.line("")
            elif "barisan" in c:
                # Beberapa adegan menuntut orang tertentu berdiri di depan (Ratih memimpin
                # lagu di ending "Mendendangkan"). Rimba tetap tidak bisa digeser keluar.
                minta = list(c["barisan"])
                for cid in minta:
                    h = st.hero(cid)
                    if h is None or st.is_active(cid):
                        continue
                    i = st.party.index(h)
                    for j in range(PARTY_AKTIF_MAKS - 1, -1, -1):
                        if st.party[j].id != BARA_HOLDER_ID and st.party[j].id not in minta:
                            st.tukar_posisi(i, j)
                            break
                nama = ", ".join(h.name for h in st.active_party)
                self.io.line(f" ** Barisan aktif: {nama}. **")
                self.io.line("")
            elif "bara" in c:
                from ..combat.engine import BARA_MAX_DASAR
                nilai = c["bara"]
                st.bara_max = BARA_MAX_DASAR if nilai is True else max(st.bara_max, int(nilai))
                st.flags.add("bara")
                if nilai is not True:
                    self.io.line(f" ** Meteran Bara melebar: maksimum {st.bara_max}. **")
                    self.io.line("")
            elif "lucuti" in c:
                # Ending "Mengembalikan" (§2.4): tidak ada lagi Nyala, tidak ada lagi sihir.
                # Ini bukan teks penutup — state-nya betul-betul kehilangan semuanya.
                st.bara_max = 0
                st.flags.discard("bara")
                st.kaca.clear()
                st.kaca_uses.clear()
                for h in st.party:
                    h.kaca = [None] * len(h.kaca)
                    h.jalur = None
                    h.hp = min(h.hp, h.max_hp)
                    h.mp = min(h.mp, h.max_mp)
                self.io.line(" ** Bara padam. Kaca Ingatan menjadi kaca biasa. Jalur yang kalian pilih tinggal cara berjalan. **")
                self.io.line("")
            elif "run" in c:
                self.run_commands(area, area.scripts[c["run"]])
            elif "end" in c:
                raise ScriptEnd()
            elif "end_chapter" in c:
                raise ChapterEnd(c["end_chapter"])
            else:
                raise ValueError(f"perintah skrip tidak dikenal: {c}")

    def grant_xp(self, amount: int) -> None:
        """XP penuh untuk barisan aktif, 70% untuk cadangan (GAME_DESIGN §5.1)."""
        st = self.state
        aktif = {id(h) for h in st.active_party}
        for h in st.party:
            if h.guest:
                continue
            bagian = amount if id(h) in aktif else int(amount * XP_CADANGAN)
            bagian = int(bagian * (1 + h.passive().xp_pct))
            levels = h.gain_xp(bagian)
            if levels:
                self.io.line(f" ** {h.name} naik ke Lv {h.level}! **")
                for lv in levels:
                    for s in h.new_skills_at(lv):
                        self.io.line(f"    {h.name} mempelajari {s.name}!")
                if h.butuh_pilih_jalur:
                    self.io.line(f" ** {h.name} bisa memilih Jalur! Buka menu Party. **")
