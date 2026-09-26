"""Mesin pertarungan turn-based (GAME_DESIGN §4).

Alur pemakaian (UI atau simulasi):

    battle = Battle(data, heroes, enemy_ids, rng=random.Random(seed))
    events = battle.start()
    while not battle.over:
        turn = battle.next_turn()          # Turn(actor, events, skipped)
        if turn.skipped or turn.actor is None:
            continue                       # giliran dilewati (Beku/Tidur/Pecah/...)
        if turn.actor.is_player:
            action = ...                   # pilih lewat UI / kebijakan
        else:
            action = ai.choose_enemy_action(battle, turn.actor)
        events = battle.act(turn.actor, action)
    result = battle.result

Engine tidak mencetak apa pun; ia mengembalikan daftar string peristiwa
(``events``) yang ditampilkan UI. Semua keacakan lewat ``self.rng`` agar
pertarungan bisa diulang dengan seed yang sama.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable, Optional

from ..loader import GameData
from ..models import Affinity, CostType, Element, EnemyDef, ItemDef, Skill, SkillKind, Stats, Target
from ..party import Hero
from . import formulas as F
from .status import BAD_STATUSES, LAGU, STATUS_DEFS, StatusInstance, make_stat_mod, make_status

BARA_MAX_DASAR = 5
BARA_HOLDER = "rimba"
KETAHANAN_LEMAH = 25
KETAHANAN_NORMAL = 5
KETAHANAN_GOYAH_SKILL = 15
JAGA_MP_PCT = 0.05
ITEM_BUBUK_DASAR = 10
ITEM_BUBUK_PER_LEVEL = 4
SUKU_CADANG = "suku_cadang"
MAX_MUSUH = 5
#: Berapa banyak Lagu yang dibutuhkan untuk mengurai Kabut Terakhir (ending "Mendendangkan").
KABUT_PER_LAGU = 8


# ---------------------------------------------------------------------------
# Peserta pertarungan
# ---------------------------------------------------------------------------
@dataclass(eq=False)
class Combatant:
    key: str                      # id karakter / id musuh
    name: str
    is_player: bool
    level: int
    base: Stats                   # stat maks (HP/MP) dan stat dasar sebelum status
    hp: int
    mp: int
    skills: list[Skill] = field(default_factory=list)
    affinities: dict[Element, Affinity] = field(default_factory=dict)
    immune: set[str] = field(default_factory=set)
    statuses: dict[str, StatusInstance] = field(default_factory=dict)
    label: str = ""               # huruf pembeda musuh kembar (A, B, C)
    hero: Optional[Hero] = None
    edef: Optional[EnemyDef] = None
    ketahanan_max: int = 0
    ketahanan: int = 0
    turn_count: int = 0           # jumlah giliran yang sudah dijalani
    phase_index: int = -1
    pattern_pos: int = 0
    weapon_element: Element = Element.FISIK
    used_once: set[str] = field(default_factory=set)
    ignore_taunt: bool = False
    actions_per_turn: int = 1
    actions_done: int = 0
    stolen: bool = False
    rotation_index: int = -1
    traits: set[str] = field(default_factory=set)   # sifat musuh: "terbang", "hampa", ...
    kritikal_bonus: float = 0.0   # dari Kaca Tajam / pasif Jalur
    mp_regen: int = 0             # dari Kaca Napas / Jalur Penuntun
    curi_bonus: float = 0.0       # dari Kaca Licin / Jalur Peretas
    serang_adaptif: bool = False  # Serang dasar mengikuti kelemahan sasaran (Kaca Penenun, §6.3)

    # -- properti dasar -----------------------------------------------------
    @property
    def alive(self) -> bool:
        return self.hp > 0

    @property
    def max_hp(self) -> int:
        return self.base.hp

    @property
    def max_mp(self) -> int:
        return self.base.mp

    @property
    def hp_ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp else 0.0

    @property
    def display_name(self) -> str:
        return f"{self.name} {self.label}".strip()

    def has(self, status_id: str) -> bool:
        return status_id in self.statuses

    def effective(self, stat: str) -> int:
        """Stat setelah semua pengali status (Jaga, Lelah, buff, ...)."""
        v = float(self.base.get(stat))
        for st in self.statuses.values():
            m = st.stat_mults.get(stat)
            if m is not None:
                v *= m
        return max(0, int(v))

    def affinity(self, element: Element) -> Affinity:
        return self.affinities.get(element, Affinity.NORMAL)

    @property
    def is_boss(self) -> bool:
        return bool(self.edef and self.edef.is_boss)

    @property
    def skip_turn(self) -> bool:
        return any((st.sdef and st.sdef.skip_turn) for st in self.statuses.values())

    @property
    def can_use_skills(self) -> bool:
        return not any((st.sdef and st.sdef.no_skills) for st in self.statuses.values())

    @property
    def can_use_magic(self) -> bool:
        return self.can_use_skills and not any((st.sdef and st.sdef.no_magic) for st in self.statuses.values())

    @property
    def taunting(self) -> bool:
        return self.has("provokasi")

    def status_line(self) -> str:
        return " ".join(f"[{s.name}{'' if s.turns_left is None else f' {s.turns_left}'}]" for s in self.statuses.values())


# ---------------------------------------------------------------------------
# Aksi & hasil
# ---------------------------------------------------------------------------
@dataclass
class Action:
    kind: str                         # "serang" | "skill" | "item" | "jaga" | "kabur"
    skill: Optional[Skill] = None
    item: Optional[ItemDef] = None
    targets: list[Combatant] = field(default_factory=list)

    @property
    def label(self) -> str:
        if self.kind == "skill" and self.skill:
            return self.skill.name
        if self.kind == "item" and self.item:
            return self.item.name
        return {"serang": "Serang", "jaga": "Jaga", "kabur": "Kabur"}.get(self.kind, self.kind)


@dataclass
class Turn:
    actor: Optional[Combatant]
    events: list[str]
    skipped: bool = False


@dataclass
class BattleResult:
    outcome: str                      # "menang" | "kalah" | "kabur"
    xp: int = 0
    keping: int = 0
    drops: list[str] = field(default_factory=list)
    rounds: int = 0


def is_jurus(skill: Optional[Skill]) -> bool:
    """Jurus Bara: apa pun yang dibayar dengan Bara.

    Di fase terakhir Sang Pelita Pertama hanya ini yang melukai (§6.2 no. 16). Jurus Ganda
    dan Jurus Empat yang paling besar, tapi Nyala Pamungkas ikut dihitung — kalau tidak,
    pemain yang melewatkan semua adegan Kenangan (yang menurut §9.2 memang bonus, bukan
    syarat) tidak punya satu pun cara melukainya. Lihat §9.4."""
    return bool(skill and skill.cost_type == CostType.BARA)


class Bestiary:
    """Catatan Penyala: afinitas musuh yang sudah diketahui (GAME_DESIGN §4.4)."""

    def __init__(self) -> None:
        self.known: dict[str, dict[Element, Affinity]] = {}

    def learn(self, enemy_id: str, element: Element, aff: Affinity) -> bool:
        d = self.known.setdefault(enemy_id, {})
        if element in d:
            return False
        d[element] = aff
        return True

    def get(self, enemy_id: str) -> dict[Element, Affinity]:
        return self.known.get(enemy_id, {})

    def forget(self, enemy_id: str) -> None:
        """Musuh yang mengganti afinitasnya (fase boss, rotasi) membatalkan catatannya:
        catatan lama justru menyesatkan, dan perubahannya selalu diumumkan (§4.4, §4.6)."""
        self.known.pop(enemy_id, None)


# ---------------------------------------------------------------------------
# Pertarungan
# ---------------------------------------------------------------------------
class Battle:
    def __init__(
        self,
        data: GameData,
        heroes: list[Hero],
        enemy_ids: Iterable[str],
        rng: Optional[random.Random] = None,
        bestiary: Optional[Bestiary] = None,
        can_flee: bool = True,
        bara_max: int = BARA_MAX_DASAR,
        bara_start: int = 0,
        inventory: Optional[dict[str, int]] = None,
        reserves: Optional[list[Hero]] = None,
        allow_items: bool = True,
        jurus_terbuka: Optional[set[str]] = None,
        survive_rounds: int = 0,
        survive_text: str = "",
        bara_kenangan: int = 0,
    ) -> None:
        self.data = data
        self.rng = rng or random.Random()
        self.bestiary = bestiary or Bestiary()
        self.inventory: dict[str, int] = inventory if inventory is not None else {}
        self.heroes: list[Combatant] = [self._make_hero(h) for h in heroes]
        # Cadangan: tidak ikut bertarung sampai ditukar lewat aksi Ganti (GAME_DESIGN §4.3).
        self.bench: list[Combatant] = [self._make_hero(h) for h in (reserves or [])]
        self.enemies: list[Combatant] = self._make_enemies(list(enemy_ids))
        self.can_flee = can_flee and not any(e.is_boss for e in self.enemies)
        self.allow_items = allow_items
        self.bara_max = bara_max
        bara_pasif = sum(h.passive().bara_awal for h in heroes)
        self.bara = min(bara_start + bara_pasif, bara_max)
        self.round = 0
        self.queue: list[Combatant] = []
        self.log: list[str] = []
        self.pending_events: list[str] = []
        # Event efek untuk klien grafis (web/Android). Terminal mengabaikannya.
        # ``pos`` = jumlah baris log di ``ev`` saat efek terjadi, supaya UI bisa
        # memutar animasi tepat sebelum baris log yang bersangkutan.
        self.fx: list[dict] = []
        self.result: Optional[BattleResult] = None
        self.bara_skills: list[Skill] = [s for s in data.skills.values() if s.cost_type == CostType.BARA]
        # Jurus Ganda dibuka lewat adegan Kenangan (§4.5). None = semua terbuka (prototipe & tes).
        self.jurus_terbuka = jurus_terbuka
        # Pertarungan bertahan: menang begitu ronde ke-N lewat, bukan begitu musuh habis
        # (segmen ending "Menyalakan Kembali", GAME_DESIGN §2.4).
        self.survive_rounds = survive_rounds
        self.survive_text = survive_text
        # Bara yang kembali setelah Padamkan Dunia: satu per Kenangan puncak (§6.2 no. 16).
        self.bara_kenangan = bara_kenangan
        #: Jurus sekali-per-pertarungan yang dipegang party, bukan satu orang (Jurus Empat).
        self.used_once_party: set[str] = set()
        #: Skill yang dihapus Sang Pelita Pertama; Lagu Ratih mengembalikannya satu per satu.
        self.skill_terhapus: list[tuple[Combatant, Skill]] = []
        #: Apakah kepala (Cacing Abu Ibu) dipukul ronde ini — kalau tidak, segmennya pulih.
        self.kepala_dipukul = False

    # -- pembuatan peserta --------------------------------------------------
    def _make_hero(self, h: Hero) -> Combatant:
        st = h.stats
        p = h.passive()
        c = Combatant(
            key=h.id, name=h.name, is_player=True, level=h.level, base=st,
            hp=min(h.hp, st.hp), mp=min(h.mp, st.mp), skills=h.skills(), hero=h,
            immune=set(p.imun), kritikal_bonus=p.kritikal, mp_regen=p.mp_regen, curi_bonus=p.curi_pct,
            serang_adaptif=p.serang_adaptif,
        )
        w = h.equipment.get("senjata")
        if w and w in self.data.items and self.data.items[w].element != Element.NETRAL:
            c.weapon_element = self.data.items[w].element
        # Kaca Elemen menimpa elemen bawaan senjata (GAME_DESIGN §5.3).
        kel = h.kaca_element
        if kel is not None:
            c.weapon_element = kel
        return c

    def _make_enemies(self, ids: list[str]) -> list[Combatant]:
        out: list[Combatant] = []
        counts: dict[str, int] = {}
        for eid in ids:
            counts[eid] = counts.get(eid, 0) + 1
        seen: dict[str, int] = {}
        for eid in ids:
            edef = self.data.enemy(eid)
            label = ""
            if counts[eid] > 1:
                seen[eid] = seen.get(eid, 0) + 1
                label = chr(ord("A") + seen[eid] - 1)
            skills = [self.data.skill(a.action) for a in edef.ai if a.action != "serang"]
            skills += [self.data.skill(x.partition("@")[0]) for p in edef.phases for x in p.pattern if x.partition("@")[0] != "serang"]
            skills += [self.data.skill(x) for x in edef.skills]
            out.append(Combatant(
                key=eid, name=edef.name, is_player=False, level=edef.level, base=edef.stats.copy(),
                hp=edef.stats.hp, mp=edef.stats.mp, skills=skills, affinities=dict(edef.affinities),
                immune=set(edef.immune), traits=set(edef.traits), label=label, edef=edef,
                ketahanan_max=edef.ketahanan, ketahanan=edef.ketahanan,
            ))
        return out

    # -- properti -----------------------------------------------------------
    @property
    def over(self) -> bool:
        return self.result is not None

    @property
    def alive_heroes(self) -> list[Combatant]:
        return [h for h in self.heroes if h.alive]

    @property
    def alive_enemies(self) -> list[Combatant]:
        return [e for e in self.enemies if e.alive]

    def allies_of(self, c: Combatant) -> list[Combatant]:
        return self.heroes if c.is_player else self.enemies

    def foes_of(self, c: Combatant) -> list[Combatant]:
        return self.enemies if c.is_player else self.heroes

    def hero_by_key(self, key: str) -> Optional[Combatant]:
        for h in self.heroes:
            if h.key == key:
                return h
        return None

    @property
    def bara_frozen(self) -> bool:
        holder = self.hero_by_key(BARA_HOLDER)
        return holder is None or not holder.alive

    def _emit(self, events: list[str], msg: str) -> None:
        events.append(msg)
        self.log.append(msg)

    def _fx(self, events: list[str], t: str, **data) -> None:
        self.fx.append({"t": t, "pos": len(events), **data})
        if len(self.fx) > 500:          # alat tanpa UI (kalibrasi) tidak pernah menguras
            del self.fx[:250]

    def drain_fx(self) -> list[dict]:
        out, self.fx = self.fx, []
        return out

    # -- alur giliran -------------------------------------------------------
    def start(self) -> list[str]:
        ev: list[str] = []
        names = ", ".join(e.display_name for e in self.enemies)
        self._emit(ev, f"{names} muncul!")
        return ev

    def _new_round(self, ev: list[str]) -> None:
        self.round += 1
        if self.survive_rounds and self.round > self.survive_rounds:
            self._bertahan_selesai(ev)
            return
        self._regen_segmen(ev)
        everyone = self.alive_heroes + self.alive_enemies
        # AGI tertinggi duluan; seri: party duluan (GAME_DESIGN §4.1)
        self.queue = sorted(everyone, key=lambda c: (-c.effective("agi"), 0 if c.is_player else 1))

    def _bertahan_selesai(self, ev: list[str]) -> None:
        """Ronde bertahan habis: party menang tanpa harus menghabisi siapa pun."""
        xp = sum(e.edef.xp for e in self.enemies if e.edef)
        keping = sum(e.edef.keping for e in self.enemies if e.edef)
        self.result = BattleResult("menang", xp=xp, keping=keping, rounds=self.round - 1)
        self._emit(ev, self.survive_text or "Kalian bertahan cukup lama. Itu saja yang diminta.")

    def _regen_segmen(self, ev: list[str]) -> None:
        """Segmen yang bisa menutup lukanya (Cacing Abu Ibu, §6.3) pulih kalau kepalanya
        tidak dipukul satu ronde penuh."""
        parts = [e for e in self.alive_enemies if e.edef and e.edef.regen_pct]
        if parts and self.round > 1 and not self.kepala_dipukul:
            for e in parts:
                n = min(int(e.max_hp * e.edef.regen_pct), e.max_hp - e.hp)
                if n > 0:
                    e.hp += n
                    self._emit(ev, f"{e.display_name} menutup lukanya ({n} HP) — kepalanya tidak diganggu.")
        self.kepala_dipukul = False

    def next_turn(self) -> Turn:
        """Ambil peserta berikutnya. Menangani ronde baru dan giliran yang dilewati."""
        if self.over:
            return Turn(None, [], skipped=True)
        ev: list[str] = []
        while not self.queue:
            self._new_round(ev)
            if self.over:
                return Turn(None, ev, skipped=True)
        actor = self.queue.pop(0)
        if not actor.alive:
            return Turn(None, ev, skipped=True)
        if actor.actions_done > 0:
            # lanjutan aksi ganda di giliran yang sama (fase boss actions_per_turn > 1)
            return Turn(actor, ev, skipped=False)
        # status "sampai giliran berikutnya" (Jaga) berakhir di awal giliran pemilik
        for sid in [s for s, st in actor.statuses.items() if st.sdef and st.sdef.expires_at_own_turn_start]:
            del actor.statuses[sid]
        actor.turn_count += 1
        self._apply_rotation(actor, ev)
        if actor.skip_turn:
            alasan = next(st.name for st in actor.statuses.values() if st.sdef and st.sdef.skip_turn)
            self._emit(ev, f"{actor.display_name} tidak bisa bergerak ({alasan}).")
            self._end_turn(actor, ev)
            return Turn(actor, ev, skipped=True)
        return Turn(actor, ev, skipped=False)

    def _apply_rotation(self, actor: Combatant, ev: list[str]) -> None:
        """Afinitas berganti tiap N giliran (GAME_DESIGN §6.2: Penambang Raksasa, Kelam Berwajah)."""
        rot = actor.edef.rotation if actor.edef else None
        if not rot or not rot.sets:
            return
        idx = ((actor.turn_count - 1) // rot.every) % len(rot.sets)
        if idx != actor.rotation_index:
            actor.rotation_index = idx
            aset = rot.sets[idx]
            actor.affinities = dict(aset.affinities)
            self.bestiary.forget(actor.key)
            self._emit(ev, aset.announce or f"{actor.display_name} berubah: {aset.name}!")

    def apply_phase(self, actor: Combatant, phase, ev: list[str]) -> None:
        """Dipanggil AI saat fase boss berganti."""
        if phase.affinities is not None:
            actor.affinities = dict(phase.affinities)
            self.bestiary.forget(actor.key)
        actor.ignore_taunt = phase.ignore_taunt
        actor.actions_per_turn = max(1, phase.actions_per_turn)
        if phase.traits is not None:
            actor.traits = set(phase.traits)
        if phase.announce:
            self._emit(ev, phase.announce)
            self.log.append(phase.announce)

    def _end_turn(self, actor: Combatant, ev: list[str]) -> None:
        """Tick status pemilik giliran: DoT, kurangi durasi, hapus yang habis."""
        actor.actions_done = 0
        if actor.mp_regen and actor.alive and actor.mp < actor.max_mp:
            n = min(actor.mp_regen, actor.max_mp - actor.mp)
            actor.mp += n
            self._emit(ev, f"{actor.display_name} memulihkan {n} MP.")
        for sid in list(actor.statuses.keys()):
            st = actor.statuses.get(sid)
            if st is None:
                continue
            sdef = st.sdef
            if sdef and (sdef.regen_pct or sdef.regen_mag) and actor.alive:
                jml = int(actor.max_hp * sdef.regen_pct)
                if sdef.regen_mag and isinstance(st.source, Combatant):
                    jml += int(st.source.effective("mag") * sdef.regen_mag)
                if jml > 0 and actor.hp < actor.max_hp:
                    self._restore_hp(actor, jml, ev)
            if sdef and sdef.dot_pct and actor.alive:
                dmg = max(1, int(actor.max_hp * sdef.dot_pct))
                actor.hp = max(0, actor.hp - dmg)
                self._emit(ev, f"{actor.display_name} menderita {dmg} damage dari {st.name}.")
                if not actor.alive:
                    self._emit(ev, f"{actor.display_name} tumbang!")
                    self._on_death(actor, ev)
            if st.turns_left is not None and st.applied_turn != actor.turn_count:
                st.turns_left -= 1
                if st.turns_left <= 0:
                    actor.statuses.pop(sid, None)
                    if sid == "pecah":
                        self._fx(ev, "pecah_pulih", sasaran=actor.display_name)
                        actor.ketahanan = actor.ketahanan_max
                        self._emit(ev, f"{actor.display_name} pulih dari Pecah.")
                    elif sdef and sdef.bad and sid not in ("goyah",):
                        self._emit(ev, f"{actor.display_name} pulih dari {st.name}.")
        self._check_end(ev)

    # -- validasi aksi ------------------------------------------------------
    def cost_ok(self, actor: Combatant, skill: Skill) -> bool:
        if skill.cost_type == CostType.MP:
            return actor.mp >= skill.cost
        if skill.cost_type == CostType.SC:
            return self.inventory.get(SUKU_CADANG, 0) >= skill.cost
        if skill.cost_type == CostType.HP_PCT:
            return actor.hp > int(actor.max_hp * skill.cost / 100)
        if skill.cost_type == CostType.BARA:
            return not self.bara_frozen and self.bara >= skill.cost
        return True

    def usable_skills(self, actor: Combatant) -> list[Skill]:
        if not actor.can_use_skills:
            return []
        out = []
        for s in actor.skills:
            if s.is_magic and not actor.can_use_magic:
                continue
            if s.once_per_battle and s.id in actor.used_once:
                continue
            if self.cost_ok(actor, s):
                out.append(s)
        return out

    def usable_bara_skills(self, actor: Combatant) -> list[Skill]:
        """Jurus Bara yang bisa dipakai ``actor`` sekarang (harus salah satu ``users``, semua users hidup)."""
        if not actor.is_player or self.bara_frozen or not actor.can_use_skills:
            return []
        out = []
        for s in self.bara_skills:
            if "jurus_empat" in s.tags:
                # Jurus Empat (§4.5): seluruh barisan aktif, Bara maks 8, sekali per pertarungan.
                if (self.bara_max < s.cost or s.id in self.used_once_party
                        or len(self.heroes) < 4 or not all(h.alive for h in self.heroes)):
                    continue
                if self.bara >= s.cost:
                    out.append(s)
                continue
            if actor.key not in s.users:
                continue
            if len(s.users) >= 2 and self.jurus_terbuka is not None and s.id not in self.jurus_terbuka:
                continue
            if not all((h := self.hero_by_key(u)) is not None and h.alive for u in s.users):
                continue
            if self.bara >= s.cost:
                out.append(s)
        return out

    def usable_items(self) -> list[ItemDef]:
        if not self.allow_items:
            return []
        return [self.data.items[i] for i, n in self.inventory.items() if n > 0 and self.data.items[i].kind == "konsumsi"
                and (self.data.items[i].heal_hp or self.data.items[i].heal_mp or self.data.items[i].cure
                     or self.data.items[i].revive_pct or self.data.items[i].power)]

    def valid_targets(self, actor: Combatant, target: Target) -> list[Combatant]:
        if target == Target.SATU_MUSUH or target == Target.SEMUA_MUSUH:
            return [c for c in self.foes_of(actor) if c.alive]
        if target == Target.SATU_KAWAN or target == Target.SEMUA_KAWAN:
            return [c for c in self.allies_of(actor) if c.alive]
        if target == Target.KAWAN_PINGSAN:
            return [c for c in self.allies_of(actor) if not c.alive]
        return [actor]

    def taunt_target(self, actor: Combatant) -> Optional[Combatant]:
        """Kalau ada lawan yang Provokasi, serangan single-target diarahkan ke sana."""
        for c in self.foes_of(actor):
            if c.alive and c.taunting:
                return c
        return None

    # -- eksekusi aksi ------------------------------------------------------
    def act(self, actor: Combatant, action: Action) -> list[str]:
        ev: list[str] = []
        if self.pending_events:
            ev.extend(self.pending_events)
            self.pending_events.clear()
        if self.over or not actor.alive:
            return ev
        if action.kind in ("serang", "skill", "item", "jaga"):
            el = action.skill.element if action.kind == "skill" and action.skill else None
            self._fx(ev, "aksi", pelaku=actor.display_name, pahlawan=actor.is_player,
                     nama=action.label, jenis=action.kind,
                     elemen=el.value if el is not None else None,
                     jurus=is_jurus(action.skill) if action.kind == "skill" else False)
        if action.kind == "serang":
            self._do_attack(actor, action.targets, ev)
        elif action.kind == "skill":
            assert action.skill is not None
            self._do_skill(actor, action.skill, action.targets, ev)
        elif action.kind == "item":
            assert action.item is not None
            self._do_item(actor, action.item, action.targets, ev)
        elif action.kind == "jaga":
            self._do_guard(actor, ev)
        elif action.kind == "kabur":
            self._do_flee(actor, ev)
        elif action.kind == "ganti":
            if not self._do_ganti(actor, action.targets[0] if action.targets else None, ev):
                return ev
            self._end_turn(actor, ev)
            return ev
        else:
            raise ValueError(f"aksi tidak dikenal: {action.kind}")
        if self.over:
            return ev
        actor.actions_done += 1
        if not actor.is_player and actor.alive and actor.actions_done < actor.actions_per_turn and not actor.skip_turn:
            self.queue.insert(0, actor)          # bertindak lagi sebelum peserta lain
            self._emit(ev, f"{actor.display_name} bergerak lagi!")
            return ev
        self._end_turn(actor, ev)
        return ev

    def bisa_ganti(self, actor: Combatant) -> list[Combatant]:
        """Cadangan yang bisa masuk menggantikan ``actor`` (GAME_DESIGN §4.3 aksi Ganti)."""
        if not actor.is_player or actor.key == BARA_HOLDER or not actor.alive:
            return []
        return [c for c in self.bench if c.alive]

    def _do_ganti(self, actor: Combatant, masuk: Optional[Combatant], ev: list[str]) -> bool:
        if masuk is None or masuk not in self.bench:
            self._emit(ev, "Tidak ada cadangan yang bisa masuk.")
            return False
        i = self.heroes.index(actor)
        self.heroes[i] = masuk
        self.bench[self.bench.index(masuk)] = actor
        # Yang keluar melepas status sementaranya; yang masuk mulai bersih.
        actor.statuses.clear()
        actor.actions_done = 0
        self.queue = [c for c in self.queue if c is not actor]
        self._emit(ev, f"{actor.display_name} mundur; {masuk.display_name} maju ke barisan!")
        return True

    def _pasang_status(self, target: Combatant, sid: str, turns: Optional[int], source: Combatant) -> None:
        """Pasang status yang sumbernya penting (Lagu, Panji, Tanggung)."""
        if sid in LAGU:
            for lama in LAGU:
                target.statuses.pop(lama, None)
        st = make_status(sid, turns, source=source)
        st.applied_turn = target.turn_count
        target.statuses[sid] = st

    def _do_guard(self, actor: Combatant, ev: list[str]) -> None:
        actor.statuses["jaga"] = make_status("jaga")
        gain = max(1, int(actor.max_mp * JAGA_MP_PCT)) if actor.max_mp else 0
        actor.mp = min(actor.max_mp, actor.mp + gain)
        self._emit(ev, f"{actor.display_name} berjaga.")
        if actor.key == BARA_HOLDER and actor.is_player:
            self._gain_bara(1, ev, "berjaga")

    def _do_flee(self, actor: Combatant, ev: list[str]) -> None:
        if not self.can_flee:
            self._emit(ev, "Tidak bisa kabur dari pertarungan ini!")
            return
        agi_p = sum(h.effective("agi") for h in self.alive_heroes) / max(1, len(self.alive_heroes))
        agi_e = sum(e.effective("agi") for e in self.alive_enemies) / max(1, len(self.alive_enemies))
        p = F.peluang_kabur(agi_p, agi_e)
        if self.rng.random() < p:
            self._emit(ev, "Party berhasil kabur!")
            self.result = BattleResult("kabur", rounds=self.round)
        else:
            self._emit(ev, "Gagal kabur!")

    def _resolve_targets(self, actor: Combatant, target_type: Target, chosen: list[Combatant]) -> list[Combatant]:
        if target_type.is_multi:
            return self.valid_targets(actor, target_type)
        if target_type == Target.DIRI:
            return [actor]
        cands = self.valid_targets(actor, target_type)
        if target_type == Target.SATU_MUSUH and not actor.ignore_taunt:
            t = self.taunt_target(actor)
            if t is not None:
                return [t]
        chosen = [c for c in chosen if c in cands]
        if chosen:
            return chosen[:1]
        if not cands:
            return []
        if target_type == Target.SATU_MUSUH:
            return [self.rng.choice(cands)]
        return [min(cands, key=lambda c: c.hp_ratio)]

    def _do_attack(self, actor: Combatant, targets: list[Combatant], ev: list[str]) -> None:
        ts = self._resolve_targets(actor, Target.SATU_MUSUH, targets)
        if not ts:
            return
        t = ts[0]
        elem = actor.weapon_element if actor.is_player else Element.FISIK
        if actor.serang_adaptif:
            # Kaca Penenun (hadiah Sang Penenun, §6.3): serangan dasar menenun dirinya
            # mengikuti kelemahan sasaran.
            elem = next((el for el, a in t.affinities.items() if a == Affinity.LEMAH), elem)
        self._emit(ev, f"{actor.display_name} menyerang {t.display_name}!")
        self._hit(actor, t, elem, 1.0, SkillKind.FISIK, ev, skill=None)

    def _pay_cost(self, actor: Combatant, skill: Skill, ev: list[str]) -> None:
        if skill.cost_type == CostType.MP:
            actor.mp -= skill.cost
        elif skill.cost_type == CostType.SC:
            self.inventory[SUKU_CADANG] = self.inventory.get(SUKU_CADANG, 0) - skill.cost
        elif skill.cost_type == CostType.HP_PCT:
            actor.hp = max(1, actor.hp - int(actor.max_hp * skill.cost / 100))
        elif skill.cost_type == CostType.BARA:
            self.bara -= skill.cost
        if "hp_sacrifice_25" in skill.tags:
            korban = int(actor.max_hp * 0.25)
            actor.hp = max(1, actor.hp - korban)
            self._emit(ev, f"{actor.display_name} mengorbankan {korban} HP.")

    def _skill_source(self, actor: Combatant, skill: Skill) -> Combatant:
        """Untuk Jurus Ganda: pakai stat penyerang terbaik di antara ``users``."""
        if not is_jurus(skill):
            return actor
        if "jurus_empat" in skill.tags:
            users = [h for h in self.heroes if h.alive]
        else:
            users = [h for u in skill.users if (h := self.hero_by_key(u)) and h.alive]
        stat = "atk" if skill.kind == SkillKind.FISIK else "mag"
        return max(users, key=lambda h: h.effective(stat)) if users else actor

    def _do_skill(self, actor: Combatant, skill: Skill, targets: list[Combatant], ev: list[str]) -> None:
        if not self.cost_ok(actor, skill):
            self._emit(ev, f"{actor.display_name} tidak punya cukup {skill.cost_type.value.upper()} untuk {skill.name}.")
            return
        if not actor.can_use_skills or (skill.is_magic and not actor.can_use_magic):
            self._emit(ev, f"{actor.display_name} tidak bisa memakai skill sekarang!")
            return
        if "needs_charge" in skill.tags and not actor.has("mengisi"):
            self._emit(ev, f"{actor.display_name} mencoba {skill.name}, tapi isiannya belum siap!")
            return
        self._pay_cost(actor, skill, ev)
        if skill.once_per_battle:
            actor.used_once.add(skill.id)
        if "needs_charge" in skill.tags:
            actor.statuses.pop("mengisi", None)
        ts = self._resolve_targets(actor, skill.target, targets)
        # Cermin Berjalan memantulkan sihir satu sasaran ke penggunanya (§6.1).
        if (skill.kind == SkillKind.SIHIR and skill.target == Target.SATU_MUSUH
                and len(ts) == 1 and "pantul" in ts[0].traits and ts[0].alive):
            self._emit(ev, f"{ts[0].display_name} memantulkan {skill.name} kembali!")
            ts = [actor]
        if "jurus_empat" in skill.tags:
            self.used_once_party.add(skill.id)
            names = ", ".join(h.name for h in self.heroes if h.alive)
            self._emit(ev, f"JURUS EMPAT! {names} — {skill.name}!")
        elif skill.cost_type == CostType.BARA and len(skill.users) >= 2:
            names = " & ".join(h.name for u in skill.users if (h := self.hero_by_key(u)))
            self._emit(ev, f"JURUS GANDA! {names}: {skill.name}!")
        else:
            self._emit(ev, f"{actor.display_name} memakai {skill.name}!")
        if not ts:
            self._emit(ev, "...tapi tidak ada sasaran.")
            return
        source = self._skill_source(actor, skill)
        if self._special_skill(actor, skill, ts, ev):
            if "lagu" in skill.tags and actor.is_player:
                self._lagu_khusus(ev)
            self._check_end(ev)
            return
        for t in ts:
            if skill.kind in (SkillKind.FISIK, SkillKind.SIHIR):
                elem = skill.element
                if "elemen_kelemahan" in skill.tags:
                    # Jurus Empat: tiap musuh dipukul dengan elemen kelemahannya sendiri (§4.5).
                    elem = next((el for el, a in t.affinities.items() if a == Affinity.LEMAH), skill.element)
                for _ in range(max(1, skill.hits)):
                    if not t.alive:
                        break
                    self._hit(source, t, elem, skill.power, skill.kind, ev, skill=skill)
            elif skill.kind == SkillKind.HEAL:
                self._heal(source, t, skill, ev)
            elif skill.kind == SkillKind.BANGKIT:
                if not t.alive:
                    t.hp = max(1, int(t.max_hp * (skill.heal_pct or 0.3)))
                    self._emit(ev, f"{t.display_name} bangkit kembali!")
            elif skill.kind in (SkillKind.BUFF, SkillKind.DEBUFF):
                self._apply_mods(t, skill, ev)
                self._try_inflict(source, t, skill.inflict, ev)
        for inf in skill.self_inflict:
            self._add_status(actor, inf.status, inf.turns, ev, source=actor)
        if skill.bara_gain:
            self._gain_bara(skill.bara_gain, ev, skill.name)
        if "lagu" in skill.tags and actor.is_player:
            self._lagu_khusus(ev)
        self._check_end(ev)

    def _do_item(self, actor: Combatant, item: ItemDef, targets: list[Combatant], ev: list[str]) -> None:
        if self.inventory.get(item.id, 0) <= 0:
            self._emit(ev, f"Tidak punya {item.name}.")
            return
        ts = self._resolve_targets(actor, item.target, targets)
        if not ts:
            self._emit(ev, f"{item.name} tidak punya sasaran.")
            return
        self.inventory[item.id] -= 1
        t = ts[0]
        self._emit(ev, f"{actor.display_name} memakai {item.name} pada {t.display_name}.")
        if item.power and item.element != Element.NETRAL:
            # Bubuk elemen: kekuatan tetap, siapa pun bisa pakai (GAME_DESIGN §5.4)
            off = ITEM_BUBUK_DASAR + ITEM_BUBUK_PER_LEVEL * actor.level
            self._hit(actor, t, item.element, item.power, SkillKind.SIHIR, ev, skill=None, offense_override=off, cannot_miss=True)
            self._check_end(ev)
            return
        if item.revive_pct and not t.alive:
            t.hp = max(1, int(t.max_hp * item.revive_pct))
            self._emit(ev, f"{t.display_name} bangkit kembali dengan {t.hp} HP!")
        if item.heal_hp and t.alive:
            self._restore_hp(t, item.heal_hp, ev)
        if item.heal_pct and t.alive:
            self._restore_hp(t, int(t.max_hp * item.heal_pct), ev)
        if item.heal_mp and t.alive:
            n = min(item.heal_mp, t.max_mp - t.mp)
            t.mp += n
            self._emit(ev, f"{t.display_name} memulihkan {n} MP.")
        if item.cure:
            self._cure(t, item.cure, ev)

    # -- mekanik inti -------------------------------------------------------
    def _hit(
        self,
        actor: Combatant,
        target: Combatant,
        element: Element,
        power: float,
        kind: SkillKind,
        ev: list[str],
        skill: Optional[Skill],
        offense_override: Optional[int] = None,
        cannot_miss: bool = False,
    ) -> int:
        """Satu pukulan. Mengembalikan damage (negatif = diserap)."""
        cannot_miss = cannot_miss or (skill.cannot_miss if skill else False)
        # peluang kena (hanya fisik; sihir selalu kena kecuali Imun)
        if kind == SkillKind.FISIK and not cannot_miss:
            p = F.peluang_kena(actor.effective("agi"), target.effective("agi"),
                               skill.hit_mod if skill else 0.0, buta=actor.has("buta"))
            if self.rng.random() >= p:
                self._fx(ev, "meleset", sasaran=target.display_name, pelaku=actor.display_name)
                self._emit(ev, f"...meleset dari {target.display_name}.")
                return 0
        aff = target.affinity(element)
        if element == Element.NETRAL:
            aff = Affinity.NORMAL
        catat = False
        mult = F.pengali_afinitas(aff, skill.ignore_resist if skill else False, skill.ignore_absorb if skill else False)
        if actor.is_player and target.edef and element != Element.NETRAL:
            if self.bestiary.learn(target.key, element, aff) and aff != Affinity.NORMAL:
                catat = True
                self._emit(ev, f"(Catatan Penyala: {target.name} — {element.label}: {aff.value.upper()})")
        if mult == 0.0:
            self._fx(ev, "imun", sasaran=target.display_name, elemen=element.value,
                     kunci=target.key, catat=catat)
            self._emit(ev, f"Tidak berpengaruh pada {target.display_name}.")
            return 0
        if kind == SkillKind.FISIK:
            off = actor.effective("atk")
            deff = 0 if (skill and skill.ignore_def) else target.effective("def")
        else:
            off = actor.effective("mag")
            deff = 0 if (skill and skill.ignore_def) else target.effective("res")
        # Formasi (Gema Prajurit, §6.1 no. 29): DEF/RES ×2 selama dua atau lebih masih berdiri.
        if "formasi" in target.traits and sum(
                1 for c in self.allies_of(target) if c.alive and "formasi" in c.traits) >= 2:
            deff *= 2
        if offense_override is not None:
            off = offense_override
        if skill and "low_hp_x1_5" in skill.tags and actor.hp_ratio < 0.30:
            power *= 1.5
        if skill and "ally_down_x2" in skill.tags and any(not a.alive for a in self.allies_of(actor)):
            power *= 2.0
        for t in (skill.tags if skill else []):
            if t.startswith("vs:"):
                _, sifat, pengali = t.split(":")
                if sifat in target.traits:
                    power *= float(pengali)
        if skill and "vs_tandai_x3" in skill.tags and target.has("tandai"):
            power *= 3.0
            del target.statuses["tandai"]
            self._emit(ev, f"{actor.display_name} mengeksekusi tanda pada {target.display_name}!")
        krit = self.rng.random() < F.peluang_kritikal(actor.effective("lck")) + actor.kritikal_bonus
        dmg = F.hitung_damage(off, deff, power, mult, kritikal=krit,
                              pecah=target.has("pecah"), goyah=target.has("goyah"),
                              acak=F.acak_damage(self.rng))
        if dmg < 0:
            sembuh = min(-dmg, target.max_hp - target.hp)
            target.hp += sembuh
            self._fx(ev, "hit", sasaran=target.display_name, pelaku=actor.display_name,
                     elemen=element.value, afinitas="serap", dmg=-sembuh,
                     hp=target.hp, hp_max=target.max_hp, jurus=is_jurus(skill),
                     kunci=target.key, catat=catat)
            self._emit(ev, f"{target.display_name} MENYERAP {element.label}! Pulih {sembuh} HP.")
            return dmg
        # "Yang Ingin Dilupakan" (§6.2 no. 16): apa pun selain Jurus hanya menggores.
        if dmg > 0 and "hanya_jurus" in target.traits and not is_jurus(skill):
            dmg = 1
        # Tanggung (Kelana): sebagian damage pindah ke pelindung yang memasangnya.
        st_tanggung = target.statuses.get("tanggung")
        pelindung = st_tanggung.source if st_tanggung else None
        if (st_tanggung and st_tanggung.sdef and isinstance(pelindung, Combatant)
                and pelindung is not target and pelindung.alive):
            pindah = int(dmg * st_tanggung.sdef.redirect)
            if pindah > 0:
                dmg -= pindah
                pelindung.hp = max(0, pelindung.hp - pindah)
                self._emit(ev, f"{pelindung.display_name} menanggung {pindah} damage untuk {target.display_name}.")
                if not pelindung.alive:
                    self._emit(ev, f"{pelindung.display_name} tumbang!")
                    self._on_death(pelindung, ev)
        target.hp = max(0, target.hp - dmg)
        if "kepala" in target.traits:
            self.kepala_dipukul = True
        tag = ""
        if aff == Affinity.LEMAH:
            tag = " LEMAH!"
        elif aff == Affinity.TAHAN:
            tag = " (tahan)"
        if krit:
            tag += " KRITIKAL!"
        self._fx(ev, "hit", sasaran=target.display_name, pelaku=actor.display_name,
                 elemen=element.value, afinitas=aff.value, dmg=dmg, krit=krit,
                 hp=target.hp, hp_max=target.max_hp, jurus=is_jurus(skill),
                 pecah=target.has("pecah"), kunci=target.key, catat=catat)
        self._emit(ev, f"{target.display_name} terkena {dmg} damage{tag}")
        # Tidur bangun kalau dipukul
        if target.has("tidur"):
            del target.statuses["tidur"]
            self._emit(ev, f"{target.display_name} terbangun!")
        # Terjerat lepas kalau penjerat dipukul
        for ally in self.foes_of(target):
            st = ally.statuses.get("terjerat")
            if st is not None and st.source is target:
                del ally.statuses["terjerat"]
                self._emit(ev, f"{ally.display_name} lepas dari jerat!")
        # Kelemahan → Goyah, Bara, Ketahanan (GAME_DESIGN §4.4, §4.6)
        if aff == Affinity.LEMAH:
            if actor.is_player:
                self._gain_bara(1, ev, "kelemahan")
            if target.alive:
                if not target.has("pecah"):
                    self._add_status(target, "goyah", None, ev, quiet=True, source=actor)
                self._ketahanan(target, KETAHANAN_LEMAH, ev)
        elif target.alive:
            self._ketahanan(target, KETAHANAN_NORMAL, ev)
        if skill and skill.ketahanan and target.alive:
            self._ketahanan(target, skill.ketahanan, ev)
        # efek tag khusus
        if skill and "drain_25" in skill.tags and actor.alive:
            n = min(dmg // 4, actor.max_hp - actor.hp)
            if n > 0:
                actor.hp += n
                self._emit(ev, f"{actor.display_name} menyerap {n} HP.")
        if skill and "mp_drain_10" in skill.tags and target.mp > 0:
            n = min(10, target.mp)
            target.mp -= n
            self._emit(ev, f"{target.display_name} kehilangan {n} MP.")
        if not target.alive:
            self._emit(ev, f"{target.display_name} tumbang!")
            self._on_death(target, ev)
        elif skill:
            self._try_inflict(actor, target, skill.inflict, ev)
        return dmg

    def _special_skill(self, actor: Combatant, skill: Skill, ts: list[Combatant], ev: list[str]) -> bool:
        """Tag khusus yang menggantikan eksekusi biasa. Mengembalikan True kalau sudah ditangani."""
        tags = skill.tags
        handled = False
        for t in tags:
            if t.startswith("summon:"):
                parts = t.split(":")
                eid, n = parts[1], int(parts[2]) if len(parts) > 2 else 1
                for _ in range(n):
                    if len(self.alive_enemies) >= MAX_MUSUH:
                        break
                    c = self._make_enemies([eid])[0]
                    c.label = chr(ord("A") + sum(1 for e in self.enemies if e.key == eid))
                    self.enemies.append(c)
                    self._emit(ev, f"{c.display_name} muncul dipanggil {actor.display_name}!")
                handled = True
        if "charge" in tags:
            actor.statuses["mengisi"] = make_status("mengisi")
            batal = "hanya Pecah" if "goyah" in actor.immune else "Goyah atau Pecah"
            self._emit(ev, f"{actor.display_name} mengisi tenaga... ({batal} membatalkannya)")
            handled = True
        for t in tags:
            if t.startswith("nyala_penjaga:"):
                # Gema Guntur (§6.2 no. 15): Bara yang tidak dibelanjakan jadi makanannya.
                ambang = int(t.split(":")[1])
                handled = True
                if self.bara >= ambang:
                    pulih = actor.max_hp - actor.hp
                    actor.hp = actor.max_hp
                    self._emit(ev, f"{actor.display_name} meminum Bara yang kalian simpan. Ia pulih {pulih} HP.")
                else:
                    self._emit(ev, f"{actor.display_name} mencari nyala di meteran kalian dan tidak menemukan cukup.")
        if "hapus_skill" in tags:
            # "Yang Ingin Dilupakan": satu skill party hilang tiap giliran (§6.2 no. 16).
            handled = True
            kandidat = [h for h in self.alive_heroes if h.skills]
            if kandidat:
                korban = self.rng.choice(kandidat)
                hilang = self.rng.choice(korban.skills)
                korban.skills.remove(hilang)
                self.skill_terhapus.append((korban, hilang))
                self._emit(ev, f"{korban.display_name} lupa cara memakai {hilang.name}.")
            else:
                self._emit(ev, "Tidak ada lagi yang bisa dilupakan.")
        if "tenun_afinitas" in tags:
            # Sang Penenun (§6.3): kelemahan party ditenun ulang tiap beberapa giliran.
            handled = True
            els = [e for e in Element if e != Element.NETRAL]
            baru = []
            for h in self.alive_heroes:
                el = self.rng.choice(els)
                h.affinities = {el: Affinity.LEMAH}
                baru.append(f"{h.name}→{el.label}")
            self._emit(ev, "Benang-benang ditarik ulang. Kelemahan kalian sekarang: " + ", ".join(baru))
        if "padamkan_dunia" in tags:
            handled = True
            for f in self.foes_of(actor):
                if f.alive:
                    f.hp = 1
            self.bara = 0
            self._emit(ev, "PADAMKAN DUNIA. Semua HP party tersisa 1, dan meteran Bara kosong.")
            if self.bara_kenangan > 0:
                self.bara = min(self.bara_max, self.bara_kenangan)
                self._emit(ev, f"...lalu yang kalian ingat bersama menyala kembali: Bara +{self.bara}.")
        if "set_hp_1" in tags:
            for f in self.foes_of(actor):
                if f.alive:
                    f.hp = 1
            self._emit(ev, "Cahaya padam. Semua HP party tersisa 1!")
            handled = True
        if "curi" in tags and ts:
            t = ts[0]
            handled = True
            if t.stolen or not t.edef:
                self._emit(ev, f"{t.display_name} tidak punya apa-apa lagi.")
            else:
                loot = t.edef.steal or (t.edef.drops[0].item if t.edef.drops else None)
                p = 0.40 + actor.effective("lck") * 0.01 + actor.curi_bonus
                if loot and self.rng.random() < p:
                    t.stolen = True
                    self.inventory[loot] = self.inventory.get(loot, 0) + 1
                    self._emit(ev, f"{actor.display_name} mencuri {self.data.items[loot].name} dari {t.display_name}!")
                elif not loot:
                    t.stolen = True
                    self._emit(ev, f"{t.display_name} tidak membawa apa-apa.")
                else:
                    self._emit(ev, f"{actor.display_name} gagal mencuri.")
        if "baterai" in tags and ts:
            t = ts[0]
            n = min(15, actor.mp, t.max_mp - t.mp)
            actor.mp -= n
            t.mp += n
            self._emit(ev, f"{actor.display_name} menyalurkan {n} MP ke {t.display_name}.")
            handled = True
        if "rampas" in tags and ts and not actor.is_player:
            barang = [i for i, n in sorted(self.inventory.items())
                      if n > 0 and self.data.items[i].kind == "konsumsi"]
            handled = True
            if barang and not actor.stolen:
                iid = self.rng.choice(barang)
                self.inventory[iid] -= 1
                actor.stolen = True                      # bisa direbut kembali lewat Curi
                if actor.edef:
                    object.__setattr__(actor.edef, "steal", iid)
                self._emit(ev, f"{actor.display_name} merampas {self.data.items[iid].name}!")
            else:
                self._emit(ev, f"{actor.display_name} menggeledah, tapi tidak dapat apa-apa.")
        if "sedot_bara" in tags and not actor.is_player:
            handled = True
            if self.bara > 0:
                self.bara -= 1
                self._emit(ev, f"{actor.display_name} menyedot satu Bara dari party!")
            else:
                self._emit(ev, f"{actor.display_name} mencari Bara, tapi meteran kalian kosong.")
        if "giliran_lagi" in tags and ts:
            t = ts[0]
            if t is not actor and t.alive:
                self.queue.insert(0, t)
                self._emit(ev, f"{t.display_name} bergerak lagi atas perintah {actor.display_name}!")
            handled = True
        if "pindai" in tags and ts:
            t = ts[0]
            for el in Element:
                if el != Element.NETRAL:
                    self.bestiary.learn(t.key, el, t.affinity(el))
            lemah = [el.label for el, a in t.affinities.items() if a == Affinity.LEMAH]
            buruk = [f"{el.label}({a.value})" for el, a in t.affinities.items() if a != Affinity.LEMAH]
            self._emit(ev, f"Pindai {t.display_name}: HP {t.hp}/{t.max_hp}. Lemah: {', '.join(lemah) or '-'}. Lainnya: {', '.join(buruk) or '-'}.")
            handled = True
        if handled:
            for t in ts:
                self._try_inflict(actor, t, skill.inflict, ev)
                self._apply_mods(t, skill, ev)
            for inf in skill.self_inflict:
                self._add_status(actor, inf.status, inf.turns, ev, source=actor)
        return handled

    def _lagu_khusus(self, ev: list[str]) -> None:
        """Yang hanya bisa dilakukan Lagu: mengembalikan skill yang dilupakan (§6.2 no. 16)
        dan mengurai Kabut Terakhir, yang tidak bisa dilukai apa pun (ending "Mendendangkan")."""
        if self.skill_terhapus:
            korban, hilang = self.skill_terhapus.pop()
            if hilang not in korban.skills:
                korban.skills.append(hilang)
            self._emit(ev, f"Lagu itu mengembalikan {hilang.name} ke tangan {korban.display_name}.")
        for e in self.alive_enemies:
            if "kabut_terakhir" not in e.traits:
                continue
            n = max(1, e.max_hp // KABUT_PER_LAGU)
            e.hp = max(0, e.hp - n)
            self._emit(ev, f"{e.display_name} tidak terluka — ia terurai. ({n} dari meternya)")
            if not e.alive:
                self._emit(ev, f"{e.display_name} selesai dinyanyikan.")
                self._on_death(e, ev)

    def _ketahanan(self, target: Combatant, amount: int, ev: list[str]) -> None:
        if target.ketahanan_max <= 0 or target.has("pecah"):
            return
        target.ketahanan = max(0, target.ketahanan - amount)
        self._fx(ev, "ketahanan", sasaran=target.display_name,
                 nilai=target.ketahanan, maks=target.ketahanan_max)
        if target.ketahanan == 0:
            target.statuses.pop("goyah", None)
            target.statuses["pecah"] = make_status("pecah")
            self._fx(ev, "pecah", sasaran=target.display_name)
            self._emit(ev, f"*** {target.display_name} PECAH! Ia kehilangan giliran dan menerima damage ×1.5. ***")
            target.statuses.pop("mengisi", None)
            self._release_swallowed(target, ev)

    def _release_swallowed(self, swallower: Combatant, ev: list[str]) -> None:
        for h in self.foes_of(swallower):
            st = h.statuses.get("tertelan")
            if st is not None and st.source is swallower:
                del h.statuses["tertelan"]
                self._emit(ev, f"{h.display_name} terlepas dari perut {swallower.display_name}!")

    def _heal(self, actor: Combatant, target: Combatant, skill: Skill, ev: list[str]) -> None:
        if not target.alive:
            self._emit(ev, f"{target.display_name} sudah pingsan; butuh Abu Fajar.")
            return
        amount = 0
        if skill.power or skill.heal_base:
            amount += F.hitung_heal(actor.effective("mag"), skill.power, skill.heal_base)
        if skill.heal_pct:
            amount += int(target.max_hp * skill.heal_pct)
        if target.has("kutuk"):
            target.hp = max(0, target.hp - amount)
            self._emit(ev, f"{target.display_name} terkutuk: penyembuhan berbalik jadi {amount} damage!")
            if not target.alive:
                self._emit(ev, f"{target.display_name} tumbang!")
                self._on_death(target, ev)
            return
        self._restore_hp(target, amount, ev)
        if skill.cure:
            self._cure(target, skill.cure, ev)
        self._apply_mods(target, skill, ev)

    def _restore_hp(self, target: Combatant, amount: int, ev: list[str]) -> None:
        n = min(amount, target.max_hp - target.hp)
        target.hp += n
        self._emit(ev, f"{target.display_name} pulih {n} HP.")

    def _cure(self, target: Combatant, cure: list[str], ev: list[str]) -> None:
        removed = []
        for sid in list(target.statuses.keys()):
            st = target.statuses[sid]
            if ("*" in cure and st.bad) or sid in cure:
                removed.append(st.name)
                del target.statuses[sid]
        if removed:
            self._emit(ev, f"{target.display_name} sembuh dari {', '.join(removed)}.")

    def _apply_mods(self, target: Combatant, skill: Skill, ev: list[str]) -> None:
        for m in skill.mods:
            st = make_stat_mod(m.stat, m.mult, m.turns)
            st.applied_turn = target.turn_count
            target.statuses[st.id] = st
            self._emit(ev, f"{target.display_name}: {st.name} ({m.turns} giliran).")

    def _try_inflict(self, actor: Combatant, target: Combatant, inflicts, ev: list[str]) -> None:
        for inf in inflicts:
            if not target.alive:
                return
            p = F.peluang_status(inf.chance, target.effective("lck"))
            if self.rng.random() < p:
                self._add_status(target, inf.status, inf.turns, ev, source=actor)

    def _add_status(self, target: Combatant, sid: str, turns: Optional[int], ev: list[str],
                    quiet: bool = False, source: Optional[Combatant] = None) -> bool:
        if sid not in STATUS_DEFS:
            raise ValueError(f"status tidak dikenal: {sid}")
        if sid in target.immune:
            if not quiet:
                self._emit(ev, f"{target.display_name} kebal terhadap {STATUS_DEFS[sid].name}.")
            return False
        if sid in LAGU:
            for lama in LAGU:
                target.statuses.pop(lama, None)
        elif sid in target.statuses and sid != "goyah":
            return False
        if sid == "goyah":
            if target.statuses.pop("mengisi", None) is not None:
                self._emit(ev, f"Isian {target.display_name} buyar!")
            self._release_swallowed(target, ev)
        st = make_status(sid, turns, source=source)
        st.applied_turn = target.turn_count
        target.statuses[sid] = st
        if not quiet:
            self._emit(ev, f"{target.display_name} terkena {STATUS_DEFS[sid].name}!")
        else:
            self._emit(ev, f"{target.display_name} {STATUS_DEFS[sid].name}!")
        return True

    def _gain_bara(self, n: int, ev: list[str], alasan: str) -> None:
        if self.bara_frozen or n <= 0:
            return
        before = self.bara
        self.bara = min(self.bara_max, self.bara + n)
        if self.bara != before:
            self._fx(ev, "bara", nilai=self.bara, maks=self.bara_max, alasan=alasan)
            self._emit(ev, f"Bara +{self.bara - before} ({alasan}) → {self.bara}/{self.bara_max}")

    def _on_death(self, c: Combatant, ev: list[str]) -> None:
        c.statuses.clear()
        self._fx(ev, "tumbang", sasaran=c.display_name, pahlawan=c.is_player)
        if c.is_player:
            self._gain_bara(2, ev, "nyala dari amarah")
        else:
            self._release_swallowed(c, ev)
            for h in self.heroes:
                st = h.statuses.get("terjerat")
                if st is not None and st.source is c:
                    del h.statuses["terjerat"]
            # Pelita Hidup Muda meledak saat padam (GAME_DESIGN §6.1).
            if c.edef and c.edef.on_death and not c.used_once:
                c.used_once.add("on_death")
                skill = self.data.skill(c.edef.on_death)
                self._emit(ev, f"{c.display_name} padam — dan meledak!")
                for t in [h for h in self.heroes if h.alive]:
                    self._hit(c, t, skill.element, skill.power, skill.kind, ev, skill=skill)

    def _gelombang_baru(self, ev: list[str]) -> None:
        """Pertarungan bertahan tidak selesai dengan menghabisi siapa pun: gelombang
        berikutnya berdiri di tempat yang sama sampai rondenya habis."""
        for e in self.enemies:
            e.hp = e.max_hp
            e.mp = e.base.mp
            e.statuses.clear()
            e.ketahanan = e.ketahanan_max
            e.used_once.clear()
            e.turn_count = 0
            e.pattern_pos = 0
        self._emit(ev, "Gelombang berikutnya naik dari Sumur. Ia tidak habis-habis.")

    def _check_end(self, ev: list[str]) -> None:
        if self.over:
            return
        if not self.alive_enemies and self.survive_rounds and self.round <= self.survive_rounds:
            self._gelombang_baru(ev)
            return
        if not self.alive_enemies:
            xp = sum(e.edef.xp for e in self.enemies if e.edef)
            keping = sum(e.edef.keping for e in self.enemies if e.edef)
            drops = [d.item for e in self.enemies if e.edef for d in e.edef.drops if self.rng.random() < d.chance]
            self.result = BattleResult("menang", xp=xp, keping=keping, drops=drops, rounds=self.round)
            self._emit(ev, f"Menang! +{xp} XP, +{keping} Keping." + (f" Dapat: {', '.join(self.data.items[d].name for d in drops)}." if drops else ""))
        elif not self.alive_heroes:
            self.result = BattleResult("kalah", rounds=self.round)
            self._emit(ev, "Seluruh party tumbang...")

    # -- sinkronisasi ke Hero -----------------------------------------------
    def sync_heroes(self) -> None:
        """Salin HP/MP kembali ke objek Hero (dipanggil setelah pertarungan)."""
        for c in self.heroes + self.bench:
            if c.hero is not None:
                c.hero.hp = max(0, c.hp)
                c.hero.mp = max(0, c.mp)
