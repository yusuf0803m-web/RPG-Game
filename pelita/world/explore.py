"""Loop eksplorasi: ruang, perpindahan, encounter acak, menu, toko, penginapan, save/muat."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Callable, Optional

from ..combat import ai
from ..combat.engine import Battle
from ..combat.status import make_status
from ..loader import GameData
from ..models import Affinity, Element, ItemDef
from ..party import HP_BONUS_MAKS, Hero, angka_romawi, kaca_tingkat
from ..ui.terminal import IO, LEBAR, run_battle
from .model import Area, Room, World
from .script import ChapterEnd, GameOver, Hooks, ScriptRunner, wrap
from .state import BARA_HOLDER_ID, ENCOUNTER_JEDA, PARTY_AKTIF_MAKS, SAVE_DIR, SAVE_SLOTS, GameState

SLOT_LABEL = {"senjata": "Senjata", "zirah": "Zirah", "aksesori": "Aksesori"}
HARGA_JUAL = 0.5
BEKAL_KEMAH = "bekal_kemah"
SERPIHAN = "serpihan_ingatan"
SERPIHAN_PER_TUKAR = 3
BARA_MAKS_TERTINGGI = 8


class QuitGame(Exception):
    """Pemain memilih keluar ke layar judul."""


class Game:
    def __init__(self, data: GameData, world: World, state: GameState, io: IO,
                 auto_battle: bool = False, auto_script: bool = False, save_dir: Path = SAVE_DIR,
                 battle_policy: str = "pintar", auto_choice: Optional[bool] = None) -> None:
        self.data = data
        self.world = world
        self.state = state
        self.io = io
        self.auto_battle = auto_battle
        self.auto_menus = auto_battle       # toko/penginapan/save memilih default (untuk tes)
        self.save_dir = save_dir
        self.battle_policy = battle_policy
        self.runner = ScriptRunner(state, io, Hooks(self.do_battle, self.save_menu, self.shop, self.inn, self.move_to,
                                                    self.tukang_kaca, self.kemah, self.papan_buruan, self.arena),
                                   auto=auto_script, auto_choice=auto_choice)
        self._pending_move: Optional[tuple[str, Optional[str]]] = None
        # Kaca hanya boleh dibongkar-pasang di Tukang Kaca atau saat berkemah (GAME_DESIGN §5.3).
        self.kaca_bebas = False

    # -- properti -----------------------------------------------------------
    @property
    def area(self) -> Area:
        return self.world.area(self.state.area_id)

    @property
    def room(self) -> Room:
        return self.area.room(self.state.room_id)

    # -- alur utama ---------------------------------------------------------
    def start(self) -> None:
        st = self.state
        if not st.area_id:
            first = next(iter(self.world.areas.values()))
            st.area_id, st.room_id = first.id, first.start
        self.enter_room(st.room_id, st.area_id, run_enter=True)

    def run(self) -> str:
        """Jalankan sampai keluar. Mengembalikan 'quit' | 'gameover' | 'chapter_end'."""
        try:
            self.start()
            while True:
                self.render_room()
                self.menu()
        except QuitGame:
            self.io.emit("end", {"result": "quit"})
            return "quit"
        except GameOver:
            self.io.line("")
            self.io.line(" Seluruh party tumbang...")
            self.io.line(" Lentera terakhir yang kau nyalakan masih menunggu. (muat save terakhir)")
            self.io.emit("end", {"result": "gameover"})
            return "gameover"
        except ChapterEnd as e:
            self.io.line("")
            self.io.line("═" * LEBAR)
            for l in wrap(e.text):
                self.io.line(l)
            self.io.line("═" * LEBAR)
            self.io.emit("end", {"result": "chapter_end", "text": e.text})
            return "chapter_end"

    def move_to(self, room_id: str, area_id: Optional[str]) -> None:
        """Dipanggil skrip (goto/travel): ditunda sampai skrip selesai agar on_enter tidak bertumpuk."""
        self._pending_move = (room_id, area_id)

    def enter_room(self, room_id: str, area_id: Optional[str] = None, run_enter: bool = True) -> None:
        st = self.state
        if area_id and area_id != st.area_id:
            st.area_id = area_id
            self.io.line("")
            self.io.line(f" ═══ {self.area.name} ═══")
        st.room_id = room_id
        room = self.room
        if self.io.structured:
            self.io.emit("room", self.room_snapshot())
        if run_enter and room.on_enter:
            self.run_script(room.on_enter)

    def run_script(self, script_id: str) -> None:
        self.runner.run(self.area, script_id)
        self._flush_move()

    def _flush_move(self) -> None:
        while self._pending_move:
            room_id, area_id = self._pending_move
            self._pending_move = None
            self.enter_room(room_id, area_id, run_enter=True)

    # -- tampilan -----------------------------------------------------------
    def room_snapshot(self) -> dict:
        st, room = self.state, self.room
        return {
            "area_id": self.area.id, "area": self.area.name, "room_id": room.id, "room": room.name,
            "text": room.text, "safe": room.safe, "fog": self.area.fog, "lentera": st.lentera_steps,
            "keping": st.keping, "bara_max": st.bara_max,
            "party": [{"key": h.id, "name": h.name, "level": h.level, "hp": h.hp, "max_hp": h.max_hp,
                       "mp": h.mp, "max_mp": h.max_mp, "guest": h.guest,
                       "aktif": i < PARTY_AKTIF_MAKS,
                       "jalur": (j.name if (j := h.jalur_def()) else ("pilih!" if h.butuh_pilih_jalur else "")),
                       "kaca": [self.data.kaca[k].name for k in h.kaca if k]}
                      for i, h in enumerate(st.party)],
            "quests": {q: s for q, s in st.quests.items()},
        }

    def render_room(self) -> None:
        st, room = self.state, self.room
        self.io.emit("room", self.room_snapshot())
        if self.io.structured:
            return
        self.io.line("")
        self.io.line("─" * LEBAR)
        self.io.line(f" {self.area.name} — {room.name}")
        self.io.line("─" * LEBAR)
        for l in wrap(room.text):
            self.io.line(l)
        party = "  ".join(f"{h.name} {h.hp}/{h.max_hp}" for h in st.active_party)
        self.io.line("")
        self.io.line(f" [{party}]  Keping {st.keping}" + (f"  Lentera {st.lentera_steps}" if self.area.fog else ""))

    def _options(self) -> list[tuple[str, Callable[[], None]]]:
        st, room = self.state, self.room
        opts: list[tuple[str, Callable[[], None]]] = []
        for e in room.exits:
            if e.hidden_if and st.check(e.hidden_if):
                continue
            if not st.check(e.cond):
                if e.locked:
                    opts.append((f"{e.label} (terhalang)", (lambda e=e: self.narrate(e.locked))))
                continue
            opts.append((e.label, (lambda e=e: self.go(e.to, e.area))))
        for n in room.npcs:
            if st.check(n.cond):
                opts.append((f"{n.verb}: {n.name}", (lambda n=n: self.run_script(n.script))))
        for o in room.objects:
            if st.check(o.cond):
                opts.append((f"{o.verb}: {o.name}", (lambda o=o: self.run_script(o.script))))
        for bid, b in self.world.buruan.items():
            if st.buruan.get(bid) == "aktif" and b["area"] == self.area.id and b["room"] == room.id:
                opts.append((f"Buruan: {b['nama']}", (lambda bid=bid: self.lawan_buruan(bid))))
        return opts

    def narrate(self, text: str) -> None:
        for l in wrap(text):
            self.io.line(l)

    def menu(self) -> None:
        opts = self._options()
        for i, (label, _) in enumerate(opts, 1):
            self.io.line(f"  {i}) {label}")
        self.io.line("  [P]arty  [I]tem  [C]atatan Penyala  [Q]uest  [K]eluar")
        s = self.io.ask("> ").lower()
        if s.isdigit() and 1 <= int(s) <= len(opts):
            opts[int(s) - 1][1]()
        elif s == "p":
            self.party_menu()
        elif s == "i":
            self.item_menu()
        elif s == "c":
            self.bestiary_menu()
        elif s == "q":
            self.quest_menu()
        elif s in ("k", "quit", "keluar"):
            if self.auto_menus or self.io.ask("Keluar ke layar judul? Progres yang belum disimpan hilang. (y/N) ").lower() == "y":
                raise QuitGame()
        elif s == "":
            return
        else:
            self.io.line("  Pilihan tidak dikenal.")

    # -- perpindahan & encounter -------------------------------------------
    def go(self, room_id: str, area_id: Optional[str]) -> None:
        st = self.state
        target_area = self.world.area(area_id) if area_id else self.area
        for m in st.step(target_area.fog):
            self.io.line(" " + m)
        self.enter_room(room_id, area_id, run_enter=True)
        if not self.room.safe:
            self.try_encounter()

    def try_encounter(self) -> None:
        st, room, area = self.state, self.room, self.area
        pool = room.encounters if room.encounters is not None else area.encounters
        if not pool or st.steps_since_encounter < ENCOUNTER_JEDA or st.dupa_steps > 0:
            return
        rate = room.encounter_rate if room.encounter_rate is not None else area.encounter_rate
        if st.rng.random() >= rate:
            return
        enc = st.rng.choices(pool, weights=[e.weight for e in pool], k=1)[0]
        st.steps_since_encounter = 0
        outcome = self.do_battle(list(enc.enemies), boss=False, can_flee=True)
        if outcome == "kalah":
            raise GameOver()

    def jurus_terbuka(self) -> set[str]:
        """Jurus Ganda yang sudah dibuka lewat adegan Kenangan (GAME_DESIGN §4.5)."""
        return {k["jurus"] for kid, k in self.world.kenangan.items()
                if k.get("jurus") and kid in self.state.kenangan}

    def do_battle(self, enemy_ids: list[str], boss: bool, can_flee: bool, allow_items: bool = True) -> str:
        st = self.state
        heroes = st.active_party
        bara_start = min(2, sum(1 for h in heroes if h.equipment.get("aksesori") == "kalung_bara")) if st.bara_max else 0
        b = Battle(self.data, heroes, enemy_ids, rng=st.rng, bestiary=st.bestiary,
                   can_flee=can_flee and not boss, bara_max=st.bara_max, inventory=st.inventory, bara_start=bara_start,
                   reserves=[h for h in st.reserve_party if not h.guest], allow_items=allow_items,
                   jurus_terbuka=self.jurus_terbuka())
        if self.area.fog and st.in_dark_fog:
            for h in b.heroes:
                h.statuses["lupa"] = make_status("lupa")
        title = f"{self.area.name} — {self.room.name}"
        run_battle(b, title, self.io, auto=self.auto_battle, pause=not self.auto_battle)
        b.sync_heroes()
        r = b.result
        assert r is not None
        if r.outcome == "menang":
            self.runner.grant_xp(r.xp)
            st.keping += r.keping
            for d in r.drops:
                st.add_item(d, 1)
            for kid in st.kaca_dipakai_selesai_bertarung():
                k = self.data.kaca[kid]
                self.io.line(f" ** {k.name} naik ke tingkat {angka_romawi(kaca_tingkat(st.kaca_uses[kid]))}! **")
        return r.outcome

    # -- menu party ---------------------------------------------------------
    def party_menu(self) -> None:
        st = self.state
        while True:
            self.io.line("")
            self.io.line("═" * LEBAR)
            for i, h in enumerate(st.party, 1):
                stat = h.stats
                posisi = "AKTIF " if i <= PARTY_AKTIF_MAKS else "cadang"
                tag = " (tamu)" if h.guest else ""
                self.io.line(f" {i}) [{posisi}] {h.name:<8} Lv {h.level:<3} HP {h.hp:>4}/{stat.hp:<4} MP {h.mp:>3}/{stat.mp:<3}{tag}")
                self.io.line(f"    ATK {stat.atk:<3} DEF {stat.def_:<3} MAG {stat.mag:<3} RES {stat.res:<3} AGI {stat.agi:<3} LCK {stat.lck:<3} "
                             f"XP {h.xp} (berikut: {self._xp_next(h)})")
                eq = ", ".join(f"{SLOT_LABEL[k]}: {self.data.items[v].name if v else '-'}" for k, v in h.equipment.items())
                self.io.line(f"    {eq}")
                self.io.line(f"    Jalur: {self._jalur_label(h)}   Kaca: {self._kaca_label(h)}")
            self.io.line("═" * LEBAR)
            butuh = [h.name for h in st.party if h.butuh_pilih_jalur]
            if butuh:
                self.io.line(f"  ! Menunggu pilihan Jalur: {', '.join(butuh)}")
            self.io.line("  Nomor) Equipment & skill   [S]usun barisan   [J]alur   0) Kembali")
            s = self.io.ask("> ").lower()
            if s in ("", "0"):
                return
            if s == "s":
                self.susun_party()
            elif s == "j":
                self.jalur_menu()
            elif s.isdigit() and 1 <= int(s) <= len(st.party):
                self.hero_menu(st.party[int(s) - 1])

    def _jalur_label(self, h: Hero) -> str:
        j = h.jalur_def()
        if j:
            return f"{j.name} ({j.passive_note})" if j.passive_note else j.name
        opsi = h.jalur_tersedia()
        if opsi:
            return "BELUM DIPILIH"
        semua = self.data.jalur_for(h.id)
        return f"terbuka Lv {semua[0].level}" if semua else "-"

    def _kaca_label(self, h: Hero) -> str:
        if h.soket <= 0:
            return "senjata tanpa soket"
        isi = []
        for i in range(h.soket):
            kid = h.kaca[i] if i < len(h.kaca) else None
            if kid:
                k = self.data.kaca[kid]
                isi.append(f"{k.name} {angka_romawi(kaca_tingkat(self.state.kaca_uses.get(kid, 0)))}")
            else:
                isi.append("(kosong)")
        return " | ".join(isi)

    def susun_party(self) -> None:
        """Tukar posisi dua anggota; empat teratas adalah barisan aktif (GAME_DESIGN §3.1)."""
        st = self.state
        if len(st.party) < 2:
            self.io.line("  Belum ada yang bisa disusun.")
            return
        self.io.line("")
        self.io.line(" Empat nama teratas ikut bertarung. Rimba harus selalu aktif (ia pemegang Bara).")
        for i, h in enumerate(st.party, 1):
            posisi = "AKTIF " if i <= PARTY_AKTIF_MAKS else "cadang"
            self.io.line(f"  {i}) [{posisi}] {h.name} Lv {h.level}")
        self.io.line("  0) Kembali")
        a = self.io.ask("tukar siapa> ")
        if not (a.isdigit() and 1 <= int(a) <= len(st.party)):
            return
        b = self.io.ask("dengan siapa> ")
        if not (b.isdigit() and 1 <= int(b) <= len(st.party)):
            return
        if st.tukar_posisi(int(a) - 1, int(b) - 1):
            self.io.line("  Barisan disusun ulang: " + ", ".join(h.name for h in st.active_party))
        else:
            self.io.line("  Tidak bisa: Rimba harus tetap di barisan aktif.")

    def jalur_menu(self) -> None:
        st = self.state
        kandidat = [h for h in st.party if h.jalur_tersedia() or h.jalur]
        if not kandidat:
            self.io.line("  Belum ada yang cukup level untuk memilih Jalur.")
            return
        for i, h in enumerate(kandidat, 1):
            self.io.line(f"  {i}) {h.name} — {self._jalur_label(h)}")
        self.io.line("  0) Kembali")
        s = self.io.ask("siapa> ")
        if not (s.isdigit() and 1 <= int(s) <= len(kandidat)):
            return
        h = kandidat[int(s) - 1]
        if h.jalur:
            j = h.jalur_def()
            assert j is not None
            self.io.line(f"  {h.name} sudah menempuh Jalur {j.name}. {j.description}")
            self.io.line("  Reset Jalur bisa dilakukan di Tukang Kaca (3 Serpihan Ingatan).")
            return
        self.pilih_jalur(h)

    def pilih_jalur(self, h: Hero) -> None:
        opsi = h.jalur_tersedia()
        if not opsi:
            return
        self.io.line("")
        self.io.line(f" ═══ Jalur {h.name} ═══")
        for i, j in enumerate(opsi, 1):
            self.io.line(f"  {i}) {j.name} — {j.description}")
            skill_nama = ", ".join(f"{self.data.skill(sid).name} (Lv {self.data.skill(sid).level})" for sid in j.skills)
            self.io.line(f"     Pasif: {j.passive_note or '-'}   Skill: {skill_nama}")
        self.io.line("  0) Nanti saja")
        s = "1" if self.auto_menus else self.io.ask("jalur> ")
        if not (s.isdigit() and 1 <= int(s) <= len(opsi)):
            return
        j = opsi[int(s) - 1]
        h.jalur = j.id
        h.hp = min(h.hp, h.max_hp)
        h.mp = min(h.mp, h.max_mp)
        self.io.line(f"  ** {h.name} menempuh Jalur {j.name}. **")
        for sid in j.skills:
            sk = self.data.skill(sid)
            status = "terbuka" if sk.level <= h.level else f"terbuka di Lv {sk.level}"
            self.io.line(f"     {sk.name} — {status}")

    def harga(self, dasar: int) -> int:
        """Harga beli setelah potongan Kaca Kikir (GAME_DESIGN §5.3)."""
        return max(1, int(dasar * (1 - self.state.potongan_harga))) if dasar > 0 else dasar

    def _xp_next(self, h: Hero) -> int:
        from ..party import LEVEL_MAX, xp_to_reach
        return 0 if h.level >= LEVEL_MAX else xp_to_reach(h.level + 1) - h.xp

    def hero_menu(self, h: Hero) -> None:
        self.io.line("")
        self.io.line(f" {h.name} — {h.cdef.title}. {h.cdef.description}")
        self.io.line(" Skill: " + (", ".join(f"{s.name} ({s.cost} {s.cost_type.value.upper()})" for s in h.skills()) or "-"))
        if h.guest:
            self.io.line(" (Tamu: equipment tidak bisa diganti.)")
            return
        self.io.line(f" Jalur: {self._jalur_label(h)}")
        self.io.line(f" Kaca: {self._kaca_label(h)}" + ("" if self.kaca_bebas else "  (bongkar-pasang di Tukang Kaca atau saat berkemah)"))
        slots = list(SLOT_LABEL)
        for i, slot in enumerate(slots, 1):
            cur = h.equipment.get(slot)
            self.io.line(f"  {i}) {SLOT_LABEL[slot]}: {self.data.items[cur].name if cur else '-'}")
        if h.butuh_pilih_jalur:
            self.io.line("  4) Pilih Jalur")
        if self.kaca_bebas and h.soket > 0:
            self.io.line("  5) Soket Kaca")
        self.io.line("  0) Kembali")
        s = self.io.ask("slot> ")
        if s == "4" and h.butuh_pilih_jalur:
            self.pilih_jalur(h)
            return
        if s == "5" and self.kaca_bebas and h.soket > 0:
            self.kaca_menu(h)
            return
        if not (s.isdigit() and 1 <= int(s) <= 3):
            return
        slot = slots[int(s) - 1]
        cands = [iid for iid, n in self.state.inventory.items() if n > 0 and self._fits(self.data.items[iid], slot, h)]
        if not cands:
            self.io.line("  Tidak ada yang bisa dipasang.")
            return
        for i, iid in enumerate(cands, 1):
            it = self.data.items[iid]
            self.io.line(f"  {i}) {it.name}  {self._stat_str(it)}")
        self.io.line("  0) Kembali")
        s = self.io.ask("pasang> ")
        if not (s.isdigit() and 1 <= int(s) <= len(cands)):
            return
        new = cands[int(s) - 1]
        old = h.equipment.get(slot)
        h.equipment[slot] = new
        self.state.add_item(new, -1)
        if old:
            self.state.add_item(old, 1)
        for kid in h.rapikan_soket():
            self.state.add_kaca(kid, 1)
            self.io.line(f"  {self.data.kaca[kid].name} terlepas dan disimpan.")
        h.hp = min(h.hp, h.max_hp)
        h.mp = min(h.mp, h.max_mp)
        self.io.line(f"  {h.name} memakai {self.data.items[new].name}.")

    @staticmethod
    def _fits(it: ItemDef, slot: str, h: Hero) -> bool:
        if it.kind != slot:
            return False
        return it.weapon_for in (None, h.id) if slot == "senjata" else True

    @staticmethod
    def _stat_str(it: ItemDef) -> str:
        if not it.stats:
            return it.description
        parts = [f"{n.upper()}+{it.stats.get(n)}" for n in ("atk", "def", "mag", "res", "agi", "lck", "hp", "mp") if it.stats.get(n)]
        el = f" [{it.element.label}]" if it.element != Element.NETRAL else ""
        return " ".join(parts) + el + (f"  {it.description}" if it.description else "")

    # -- Kaca Ingatan -------------------------------------------------------
    def kaca_menu(self, h: Hero) -> None:
        """Pasang atau lepas Kaca di soket senjata ``h``. Hanya di Tukang Kaca atau kemah."""
        st = self.state
        while True:
            if h.soket <= 0:
                self.io.line(f"  Senjata {h.name} tidak punya soket Kaca.")
                return
            h.rapikan_soket()
            self.io.line("")
            self.io.line(f" ═══ Soket {h.name} ═══")
            for i in range(h.soket):
                kid = h.kaca[i]
                if kid:
                    k = self.data.kaca[kid]
                    t = kaca_tingkat(st.kaca_uses.get(kid, 0))
                    self.io.line(f"  {i + 1}) {k.name} {angka_romawi(t)} — {k.description}")
                else:
                    self.io.line(f"  {i + 1}) (kosong)")
            self.io.line("  0) Kembali")
            sel = self.io.ask("soket> ")
            if not (sel.isdigit() and 1 <= int(sel) <= h.soket):
                return
            idx = int(sel) - 1
            if h.kaca[idx]:
                lepas = h.kaca[idx]
                h.kaca[idx] = None
                st.add_kaca(lepas, 1)
                self.io.line(f"  {self.data.kaca[lepas].name} dilepas dan disimpan.")
                continue
            stok = [kid for kid, n in sorted(st.kaca.items()) if n > 0]
            if not stok:
                self.io.line("  Tidak punya Kaca yang bisa dipasang.")
                continue
            for i, kid in enumerate(stok, 1):
                k = self.data.kaca[kid]
                t = kaca_tingkat(st.kaca_uses.get(kid, 0))
                self.io.line(f"  {i}) {k.name} {angka_romawi(t)} ×{st.kaca[kid]} — {k.description}")
            self.io.line("  0) Kembali")
            pilih = self.io.ask("pasang> ")
            if not (pilih.isdigit() and 1 <= int(pilih) <= len(stok)):
                continue
            kid = stok[int(pilih) - 1]
            h.kaca[idx] = kid
            st.add_kaca(kid, -1)
            h.hp, h.mp = min(h.hp, h.max_hp), min(h.mp, h.max_mp)
            self.io.line(f"  {h.name} memasang {self.data.kaca[kid].name}.")

    def pilih_anggota(self, prompt: str = "siapa> ", dengan_tamu: bool = False) -> Optional[Hero]:
        st = self.state
        kandidat = [h for h in st.party if dengan_tamu or not h.guest]
        if not kandidat:
            return None
        for i, h in enumerate(kandidat, 1):
            self.io.line(f"  {i}) {h.name} Lv {h.level}")
        self.io.line("  0) Kembali")
        sel = self.io.ask(prompt)
        if not (sel.isdigit() and 1 <= int(sel) <= len(kandidat)):
            return None
        return kandidat[int(sel) - 1]

    def tukang_kaca(self, shop_id: str = "") -> None:
        """Bengkel Kaca: pasang/lepas, beli Kaca, tukar Serpihan Ingatan (GAME_DESIGN §5.3, §5.5)."""
        st = self.state
        self.kaca_bebas = True
        try:
            while True:
                self.io.line("")
                self.io.line(f" ═══ Tukang Kaca ═══  Keping: {st.keping}  Serpihan: {st.count(SERPIHAN)}")
                self.io.line("  1) Pasang / lepas Kaca")
                if shop_id and self.world.shops.get(shop_id, {}).get("kaca"):
                    self.io.line("  2) Beli Kaca")
                self.io.line(f"  3) Tukar Serpihan Ingatan ({SERPIHAN_PER_TUKAR} per penukaran)")
                self.io.line("  0) Pergi")
                sel = "0" if self.auto_menus else self.io.ask("> ")
                if sel == "1":
                    h = self.pilih_anggota("pasang pada> ")
                    if h:
                        self.kaca_menu(h)
                elif sel == "2" and shop_id:
                    self.beli_kaca(shop_id)
                elif sel == "3":
                    self.tukar_serpihan()
                else:
                    return
        finally:
            self.kaca_bebas = False

    def beli_kaca(self, shop_id: str) -> None:
        st = self.state
        daftar = [kid for kid in self.world.shops[shop_id].get("kaca", []) if self.data.kaca[kid].price > 0]
        while True:
            if not daftar:
                self.io.line("  Tidak ada Kaca yang dijual di sini.")
                return
            self.io.line("")
            for i, kid in enumerate(daftar, 1):
                k = self.data.kaca[kid]
                harga = self.harga(k.price)
                self.io.line(f"  {i}) {k.name:<16} {harga:>5} K  {k.description}  (punya {st.kaca.get(kid, 0)})")
            self.io.line("  0) Kembali")
            sel = self.io.ask("beli kaca> ")
            if not (sel.isdigit() and 1 <= int(sel) <= len(daftar)):
                return
            kid = daftar[int(sel) - 1]
            harga = self.harga(self.data.kaca[kid].price)
            if st.keping < harga:
                self.io.line("  Keping tidak cukup.")
                continue
            st.keping -= harga
            st.add_kaca(kid, 1)
            self.io.line(f"  Membeli {self.data.kaca[kid].name}. Keping: {st.keping}")

    def tukar_serpihan(self) -> None:
        """Tiga Serpihan Ingatan = satu peningkatan permanen (GAME_DESIGN §5.5)."""
        st = self.state
        if st.count(SERPIHAN) < SERPIHAN_PER_TUKAR:
            self.io.line(f"  Butuh {SERPIHAN_PER_TUKAR} Serpihan Ingatan; baru punya {st.count(SERPIHAN)}.")
            return
        pilihan = [
            ("HP maks +10% untuk satu anggota", self._tukar_hp),
            ("Bara maks +1", self._tukar_bara),
            ("Soket Kaca +1 pada satu senjata", self._tukar_soket),
            ("Reset Jalur satu anggota", self._tukar_reset_jalur),
            ("Kaca Skill langka", self._tukar_kaca_langka),
        ]
        for i, (label, _) in enumerate(pilihan, 1):
            self.io.line(f"  {i}) {label}")
        self.io.line("  0) Kembali")
        sel = self.io.ask("tukar> ")
        if not (sel.isdigit() and 1 <= int(sel) <= len(pilihan)):
            return
        if pilihan[int(sel) - 1][1]():
            st.add_item(SERPIHAN, -SERPIHAN_PER_TUKAR)
            self.io.line(f"  Tiga Serpihan larut jadi cahaya. Sisa: {st.count(SERPIHAN)}")

    def _tukar_hp(self) -> bool:
        h = self.pilih_anggota("HP siapa> ")
        if not h:
            return False
        if h.hp_bonus >= HP_BONUS_MAKS:
            self.io.line(f"  {h.name} sudah mencapai batas ({HP_BONUS_MAKS}×).")
            return False
        h.hp_bonus += 1
        h.hp = min(h.hp + h.max_hp // 10, h.max_hp)
        self.io.line(f"  HP maks {h.name} kini {h.max_hp}.")
        return True

    def _tukar_bara(self) -> bool:
        st = self.state
        if st.bara_max <= 0:
            self.io.line("  Bara belum menyala.")
            return False
        if st.bara_max >= BARA_MAKS_TERTINGGI:
            self.io.line(f"  Bara sudah penuh di {BARA_MAKS_TERTINGGI}.")
            return False
        st.bara_max += 1
        self.io.line(f"  Bara maks kini {st.bara_max}.")
        return True

    def _tukar_soket(self) -> bool:
        st = self.state
        h = self.pilih_anggota("senjata siapa> ")
        if not h:
            return False
        w = h.equipment.get("senjata")
        if not w:
            self.io.line(f"  {h.name} tidak memegang senjata.")
            return False
        if st.slot_bonus.get(w, 0) >= 1:
            self.io.line(f"  {self.data.items[w].name} sudah pernah diperlebar.")
            return False
        st.slot_bonus[w] = st.slot_bonus.get(w, 0) + 1
        h.rapikan_soket()
        self.io.line(f"  {self.data.items[w].name} kini punya {h.soket} soket.")
        return True

    def _tukar_reset_jalur(self) -> bool:
        h = self.pilih_anggota("reset siapa> ")
        if not h or not h.jalur:
            self.io.line("  Tidak ada Jalur untuk direset.")
            return False
        h.jalur = None
        h.hp, h.mp = min(h.hp, h.max_hp), min(h.mp, h.max_mp)
        self.io.line(f"  Jalur {h.name} dilupakan. Pilih lagi lewat menu Party.")
        return True

    def _tukar_kaca_langka(self) -> bool:
        st = self.state
        langka = [kid for kid, k in sorted(self.data.kaca.items())
                  if k.langka and st.kaca.get(kid, 0) == 0 and not any(kid in h.kaca for h in st.party)]
        if not langka:
            self.io.line("  Tukang Kaca kehabisan barang langka.")
            return False
        for i, kid in enumerate(langka, 1):
            self.io.line(f"  {i}) {self.data.kaca[kid].name} — {self.data.kaca[kid].description}")
        self.io.line("  0) Kembali")
        sel = self.io.ask("kaca> ")
        if not (sel.isdigit() and 1 <= int(sel) <= len(langka)):
            return False
        st.add_kaca(langka[int(sel) - 1], 1)
        self.io.line(f"  Dapat {self.data.kaca[langka[int(sel) - 1]].name}.")
        return True

    # -- berkemah & Kenangan ------------------------------------------------
    def kemah(self) -> None:
        """Berkemah: pulih penuh, bongkar-pasang Kaca, dan satu adegan Kenangan (GAME_DESIGN §5.6)."""
        st = self.state
        if not st.has_item(BEKAL_KEMAH):
            self.io.line("  Butuh Bekal Kemah untuk mendirikan kemah di sini.")
            return
        if not self.auto_menus and self.io.ask("  Pakai satu Bekal Kemah dan berkemah? (y/N) ").lower() != "y":
            return
        st.add_item(BEKAL_KEMAH, -1)
        st.heal_all()
        self.io.line("")
        self.io.line(" Api kecil, teh pahit, dan malam yang untuk sekali ini tidak bergerak.")
        self.io.line(" HP dan MP seluruh party pulih.")
        self.kaca_bebas = True
        try:
            while True:
                self.io.line("")
                self.io.line("  1) Mengobrol (Kenangan)")
                self.io.line("  2) Bongkar-pasang Kaca")
                self.io.line("  0) Bongkar kemah")
                sel = "0" if self.auto_menus else self.io.ask("kemah> ")
                if sel == "1":
                    self.kenangan_menu()
                elif sel == "2":
                    h = self.pilih_anggota("kaca siapa> ")
                    if h:
                        self.kaca_menu(h)
                else:
                    return
        finally:
            self.kaca_bebas = False

    def kenangan_tersedia(self) -> list[tuple[str, dict]]:
        """Adegan Kenangan yang syaratnya terpenuhi dan belum pernah dilihat."""
        st = self.state
        out = []
        for kid, k in sorted(self.world.kenangan.items(), key=lambda x: (x[1].get("tingkat", 1), x[0])):
            if kid in st.kenangan:
                continue
            if not all(st.in_party(cid) and st.hero(cid) for cid in k["pasangan"]):
                continue
            if not st.check(k.get("syarat", [])):
                continue
            sebelum = k.get("setelah")
            if sebelum and sebelum not in st.kenangan:
                continue
            out.append((kid, k))
        return out

    def kenangan_menu(self) -> None:
        st = self.state
        tersedia = self.kenangan_tersedia()
        if not tersedia:
            self.io.line("  Malam ini semua orang diam. (Belum ada obrolan baru.)")
            return
        for i, (_, k) in enumerate(tersedia, 1):
            nama = " & ".join(self.data.character(c).name for c in k["pasangan"])
            self.io.line(f"  {i}) {nama} — {k['judul']}")
        self.io.line("  0) Kembali")
        sel = "1" if self.auto_menus else self.io.ask("obrol> ")
        if not (sel.isdigit() and 1 <= int(sel) <= len(tersedia)):
            return
        kid, k = tersedia[int(sel) - 1]
        self.mainkan_kenangan(kid, k)

    def mainkan_kenangan(self, kid: str, k: dict) -> None:
        st = self.state
        self.io.line("")
        self.io.line(f" ═══ {k['judul']} ═══")
        self.runner.run_commands(self.area, k.get("adegan", []))
        st.kenangan.add(kid)
        jurus = k.get("jurus")
        if jurus:
            sk = self.data.skill(jurus)
            self.io.line(f" ** Jurus Ganda terbuka: {sk.name} ({sk.cost} Bara) **")
        self.runner.pause()

    # -- papan Buruan -------------------------------------------------------
    def papan_buruan(self) -> None:
        """Papan kontrak: ambil buruan, lihat yang sedang berjalan (GAME_DESIGN §5.7)."""
        st = self.state
        while True:
            self.io.line("")
            self.io.line(" ═══ Papan Buruan ═══")
            tersedia = [(bid, b) for bid, b in sorted(self.world.buruan.items())
                        if st.buruan.get(bid) != "selesai" and st.check(b.get("syarat", []))]
            if not tersedia:
                self.io.line(" Papan kosong. Kafilah belum menempel kertas baru.")
                return
            for i, (bid, b) in enumerate(tersedia, 1):
                tanda = " [DIAMBIL]" if st.buruan.get(bid) == "aktif" else ""
                self.io.line(f"  {i}) {b['nama']} — Lv {b['level']}{tanda}")
                self.io.line(f"     {b['deskripsi']}")
                self.io.line(f"     Tempat: {self.world.area(b['area']).name} — {self.world.area(b['area']).room(b['room']).name}")
                self.io.line(f"     Upah: {self._hadiah_label(b.get('hadiah', {}))}")
            self.io.line("  0) Pergi")
            sel = "0" if self.auto_menus else self.io.ask("ambil> ")
            if not (sel.isdigit() and 1 <= int(sel) <= len(tersedia)):
                return
            bid, b = tersedia[int(sel) - 1]
            if st.buruan.get(bid) == "aktif":
                self.io.line("  Kontrak itu sudah di tanganmu.")
                continue
            st.buruan[bid] = "aktif"
            self.io.line(f"  Kontrak diambil: {b['nama']}. Cari targetnya di {self.world.area(b['area']).name}.")

    def _hadiah_label(self, hadiah: dict) -> str:
        bagian = []
        if hadiah.get("keping"):
            bagian.append(f"{hadiah['keping']} Keping")
        for iid, n in hadiah.get("item", {}).items():
            bagian.append(f"{self.data.items[iid].name} ×{n}")
        for kid in hadiah.get("kaca", []):
            bagian.append(self.data.kaca[kid].name)
        return ", ".join(bagian) or "-"

    def beri_hadiah(self, hadiah: dict) -> None:
        st = self.state
        if hadiah.get("keping"):
            st.keping += int(hadiah["keping"])
            self.io.line(f" ** +{hadiah['keping']} Keping (total {st.keping}). **")
        for iid, n in hadiah.get("item", {}).items():
            st.add_item(iid, int(n))
            self.io.line(f" ** Dapat {self.data.items[iid].name} ×{n}. **")
        for kid in hadiah.get("kaca", []):
            st.add_kaca(kid, 1)
            self.io.line(f" ** Dapat {self.data.kaca[kid].name}. **")

    def lawan_buruan(self, bid: str) -> None:
        st = self.state
        b = self.world.buruan[bid]
        self.io.line("")
        for l in wrap(b.get("petunjuk", b["deskripsi"])):
            self.io.line(l)
        if not self.auto_menus and self.io.ask(f"  Hadapi {b['nama']}? (y/N) ").lower() != "y":
            return
        hasil = self.do_battle(list(b["musuh"]), boss=True, can_flee=False)
        if hasil == "kalah":
            raise GameOver()
        if hasil != "menang":
            return
        st.buruan[bid] = "selesai"
        self.io.line(f" ** Buruan selesai: {b['nama']}. **")
        self.beri_hadiah(b.get("hadiah", {}))

    # -- Arena Kafilah ------------------------------------------------------
    def arena(self) -> None:
        """Tiga pertarungan beruntun tanpa item (GAME_DESIGN §5.7)."""
        st = self.state
        if not self.world.arena:
            self.io.line("  Arena belum dibuka.")
            return
        while True:
            self.io.line("")
            self.io.line(f" ═══ Arena Kafilah ═══  Tingkat tertamat: {st.arena}/{len(self.world.arena)}")
            self.io.line(" Aturan: tiga gelombang beruntun, tanpa item, tanpa istirahat.")
            boleh = []
            for i, t in enumerate(self.world.arena, 1):
                kunci = "" if i <= st.arena + 1 else "  (terkunci)"
                tamat = "  [tamat]" if i <= st.arena else ""
                self.io.line(f"  {i}) {t['nama']} — Lv {t['level']}, upah {self._hadiah_label(t.get('hadiah', {}))}{tamat}{kunci}")
                if i <= st.arena + 1:
                    boleh.append(i)
            self.io.line("  0) Pergi")
            sel = "0" if self.auto_menus else self.io.ask("tingkat> ")
            if not (sel.isdigit() and int(sel) in boleh):
                return
            self.mulai_arena(int(sel))

    def mulai_arena(self, tingkat: int) -> None:
        st = self.state
        t = self.world.arena[tingkat - 1]
        self.io.line("")
        self.io.line(f" {t['nama']} dimulai. Semoga kau sudah makan.")
        for i, gelombang in enumerate(t["gelombang"], 1):
            self.io.line(f" — Gelombang {i} dari {len(t['gelombang'])} —")
            hasil = self.do_battle(list(gelombang), boss=False, can_flee=False, allow_items=False)
            if hasil != "menang":
                self.io.line(" Kau diangkat keluar arena. Tidak ada upah, tapi juga tidak ada yang mati.")
                st.revive_downed_minimal()
                return
        self.io.line(f" ** {t['nama']} ditamatkan! **")
        if tingkat > st.arena:
            st.arena = tingkat
            self.beri_hadiah(t.get("hadiah", {}))
        else:
            self.io.line(" (Tingkat ini sudah pernah kau tamatkan; upahnya tidak diulang.)")

    # -- item di luar pertarungan ------------------------------------------
    def item_menu(self) -> None:
        st = self.state
        while True:
            items = [self.data.items[i] for i, n in sorted(st.inventory.items()) if n > 0]
            self.io.line("")
            if not items:
                self.io.line(" Inventori kosong.")
                return
            for i, it in enumerate(items, 1):
                self.io.line(f"  {i}) {it.name} ×{st.inventory[it.id]}  {self._stat_str(it) if it.kind != 'konsumsi' else it.description}")
            self.io.line("  0) Kembali")
            s = self.io.ask("item> ")
            if not (s.isdigit() and 1 <= int(s) <= len(items)):
                return
            it = items[int(s) - 1]
            if it.id == "dupa_sunyi":
                st.dupa_steps = 30
                st.add_item(it.id, -1)
                self.io.line("  Asap dupa menyelimuti kalian. Musuh tidak akan mengganggu selama 30 langkah.")
                continue
            if it.kind != "konsumsi" or not (it.heal_hp or it.heal_mp or it.cure or it.revive_pct):
                self.io.line("  Tidak bisa dipakai di sini.")
                continue
            targets = [h for h in st.party if (h.hp <= 0) == bool(it.revive_pct)]
            if not targets:
                self.io.line("  Tidak ada sasaran yang cocok.")
                continue
            for i, h in enumerate(targets, 1):
                self.io.line(f"  {i}) {h.name} HP {h.hp}/{h.max_hp} MP {h.mp}/{h.max_mp}")
            s = self.io.ask("pada> ")
            if not (s.isdigit() and 1 <= int(s) <= len(targets)):
                continue
            h = targets[int(s) - 1]
            if it.revive_pct:
                h.hp = max(1, int(h.max_hp * it.revive_pct))
            if it.heal_hp:
                h.hp = min(h.max_hp, h.hp + it.heal_hp)
            if it.heal_mp:
                h.mp = min(h.max_mp, h.mp + it.heal_mp)
            st.add_item(it.id, -1)
            self.io.line(f"  {h.name}: HP {h.hp}/{h.max_hp} MP {h.mp}/{h.max_mp}")

    # -- catatan & quest ----------------------------------------------------
    def bestiary_menu(self) -> None:
        st = self.state
        self.io.line("")
        self.io.line(" ═══ Catatan Penyala ═══")
        if not st.bestiary.known:
            self.io.line(" Belum ada catatan. Pukul musuh dengan berbagai elemen untuk mengisi.")
            return
        for eid, aff in st.bestiary.known.items():
            e = self.data.enemy(eid)
            lemah = [el.label for el, a in aff.items() if a == Affinity.LEMAH]
            buruk = [f"{el.label}({a.value})" for el, a in aff.items() if a in (Affinity.TAHAN, Affinity.IMUN, Affinity.SERAP)]
            self.io.line(f" {e.name:<22} lemah: {', '.join(lemah) or '?'}   {('buruk: ' + ', '.join(buruk)) if buruk else ''}")
            self.io.line(f"   {e.description}")

    def quest_menu(self) -> None:
        st = self.state
        self.io.line("")
        self.io.line(" ═══ Quest ═══")
        if not st.quests:
            self.io.line(" Belum ada quest.")
            return
        for qid, state in st.quests.items():
            q = self.world.quests.get(qid, {"name": qid, "states": {}})
            self.io.line(f" {q['name']} — {state}")
            desc = q.get("states", {}).get(state, "")
            if desc:
                for l in wrap(desc, indent="   "):
                    self.io.line(l)

    # -- save / muat --------------------------------------------------------
    def save_menu(self) -> None:
        st = self.state
        self.io.line("")
        self.io.line(" Simpan di slot mana?")
        for i, s in enumerate(st.slot_summaries(self.data, self.save_dir), 1):
            self.io.line(f"  {i}) {s or '(kosong)'}")
        self.io.line("  0) Batal")
        s = "1" if self.auto_menus else self.io.ask("slot> ")
        if s.isdigit() and 1 <= int(s) <= SAVE_SLOTS:
            p = st.save(int(s), self.save_dir)
            self.io.line(f" Tersimpan ({p.name}).")

    # -- toko & penginapan --------------------------------------------------
    def shop(self, shop_id: str) -> None:
        st = self.state
        sh = self.world.shops[shop_id]
        while True:
            self.io.line("")
            self.io.line(f" ═══ {sh['name']} ═══  Keping: {st.keping}")
            punya_kaca = bool(sh.get("kaca"))
            self.io.line("  1) Beli   2) Jual" + ("   3) Kaca Ingatan" if punya_kaca else "") + "   0) Pergi")
            s = "0" if self.auto_menus else self.io.ask("> ")
            if s == "1":
                self._buy(sh)
            elif s == "2":
                self._sell()
            elif s == "3" and punya_kaca:
                self.beli_kaca(shop_id)
            else:
                return

    def _buy(self, sh: dict) -> None:
        st = self.state
        while True:
            items = [self.data.items[i] for i in sh["items"]]
            self.io.line("")
            for i, it in enumerate(items, 1):
                self.io.line(f"  {i}) {it.name:<22} {self.harga(it.price):>5} K  {self._stat_str(it) if it.kind != 'konsumsi' else it.description}  (punya {st.count(it.id)})")
            self.io.line("  0) Kembali")
            s = self.io.ask("beli> ")
            if not (s.isdigit() and 1 <= int(s) <= len(items)):
                return
            it = items[int(s) - 1]
            harga = self.harga(it.price)
            if st.keping < harga:
                self.io.line("  Keping tidak cukup.")
                continue
            st.keping -= harga
            st.add_item(it.id, 1)
            self.io.line(f"  Membeli {it.name}. Keping: {st.keping}")

    def _sell(self) -> None:
        st = self.state
        while True:
            items = [self.data.items[i] for i, n in sorted(st.inventory.items()) if n > 0 and self.data.items[i].price > 0]
            if not items:
                self.io.line("  Tidak ada yang bisa dijual.")
                return
            self.io.line("")
            for i, it in enumerate(items, 1):
                self.io.line(f"  {i}) {it.name:<22} ×{st.inventory[it.id]:<3} {int(it.price * HARGA_JUAL):>5} K")
            self.io.line("  0) Kembali")
            s = self.io.ask("jual> ")
            if not (s.isdigit() and 1 <= int(s) <= len(items)):
                return
            it = items[int(s) - 1]
            st.add_item(it.id, -1)
            st.keping += int(it.price * HARGA_JUAL)
            self.io.line(f"  Menjual {it.name}. Keping: {st.keping}")

    def inn(self, price: int) -> None:
        st = self.state
        price = self.harga(price)
        if price > 0 and st.keping < price:
            self.io.line(f"  Menginap {price} Keping. Kepingmu tidak cukup.")
            return
        if not self.auto_menus and price > 0:
            if self.io.ask(f"  Menginap {price} Keping? (y/N) ").lower() != "y":
                return
        st.keping -= price
        st.heal_all()
        self.io.line("  Kalian beristirahat. HP dan MP pulih.")
