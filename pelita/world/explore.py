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
from ..party import Hero
from ..ui.terminal import IO, LEBAR, run_battle
from .model import Area, Room, World
from .script import ChapterEnd, GameOver, Hooks, ScriptRunner, wrap
from .state import ENCOUNTER_JEDA, SAVE_DIR, SAVE_SLOTS, GameState

SLOT_LABEL = {"senjata": "Senjata", "zirah": "Zirah", "aksesori": "Aksesori"}
HARGA_JUAL = 0.5


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
        self.runner = ScriptRunner(state, io, Hooks(self.do_battle, self.save_menu, self.shop, self.inn, self.move_to),
                                   auto=auto_script, auto_choice=auto_choice)
        self._pending_move: Optional[tuple[str, Optional[str]]] = None

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
            return "quit"
        except GameOver:
            self.io.line("")
            self.io.line(" Seluruh party tumbang...")
            self.io.line(" Lentera terakhir yang kau nyalakan masih menunggu. (muat save terakhir)")
            return "gameover"
        except ChapterEnd as e:
            self.io.line("")
            self.io.line("═" * LEBAR)
            for l in wrap(e.text):
                self.io.line(l)
            self.io.line("═" * LEBAR)
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
    def render_room(self) -> None:
        st, room = self.state, self.room
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

    def do_battle(self, enemy_ids: list[str], boss: bool, can_flee: bool) -> str:
        st = self.state
        heroes = st.active_party
        bara_start = min(2, sum(1 for h in heroes if h.equipment.get("aksesori") == "kalung_bara")) if st.bara_max else 0
        b = Battle(self.data, heroes, enemy_ids, rng=st.rng, bestiary=st.bestiary,
                   can_flee=can_flee and not boss, bara_max=st.bara_max, inventory=st.inventory, bara_start=bara_start)
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
        return r.outcome

    # -- menu party ---------------------------------------------------------
    def party_menu(self) -> None:
        st = self.state
        while True:
            self.io.line("")
            self.io.line("═" * LEBAR)
            for i, h in enumerate(st.party, 1):
                s = h.stats
                tag = " (tamu)" if h.guest else ""
                self.io.line(f" {i}) {h.name:<8} Lv {h.level:<3} HP {h.hp:>4}/{s.hp:<4} MP {h.mp:>3}/{s.mp:<3}{tag}")
                self.io.line(f"    ATK {s.atk:<3} DEF {s.def_:<3} MAG {s.mag:<3} RES {s.res:<3} AGI {s.agi:<3} LCK {s.lck:<3} "
                             f"XP {h.xp} (berikut: {self._xp_next(h)})")
                eq = ", ".join(f"{SLOT_LABEL[k]}: {self.data.items[v].name if v else '-'}" for k, v in h.equipment.items())
                self.io.line(f"    {eq}")
            self.io.line("═" * LEBAR)
            self.io.line("  Nomor) Equipment & skill   0) Kembali")
            s = self.io.ask("> ")
            if s in ("", "0"):
                return
            if s.isdigit() and 1 <= int(s) <= len(st.party):
                self.hero_menu(st.party[int(s) - 1])

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
        slots = list(SLOT_LABEL)
        for i, slot in enumerate(slots, 1):
            cur = h.equipment.get(slot)
            self.io.line(f"  {i}) {SLOT_LABEL[slot]}: {self.data.items[cur].name if cur else '-'}")
        self.io.line("  0) Kembali")
        s = self.io.ask("slot> ")
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
            self.io.line("  1) Beli   2) Jual   0) Pergi")
            s = "0" if self.auto_menus else self.io.ask("> ")
            if s == "1":
                self._buy(sh)
            elif s == "2":
                self._sell()
            else:
                return

    def _buy(self, sh: dict) -> None:
        st = self.state
        while True:
            items = [self.data.items[i] for i in sh["items"]]
            self.io.line("")
            for i, it in enumerate(items, 1):
                self.io.line(f"  {i}) {it.name:<22} {it.price:>5} K  {self._stat_str(it) if it.kind != 'konsumsi' else it.description}  (punya {st.count(it.id)})")
            self.io.line("  0) Kembali")
            s = self.io.ask("beli> ")
            if not (s.isdigit() and 1 <= int(s) <= len(items)):
                return
            it = items[int(s) - 1]
            if st.keping < it.price:
                self.io.line("  Keping tidak cukup.")
                continue
            st.keping -= it.price
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
        if price > 0 and st.keping < price:
            self.io.line(f"  Menginap {price} Keping. Kepingmu tidak cukup.")
            return
        if not self.auto_menus and price > 0:
            if self.io.ask(f"  Menginap {price} Keping? (y/N) ").lower() != "y":
                return
        st.keping -= price
        st.heal_all()
        self.io.line("  Kalian beristirahat. HP dan MP pulih.")
