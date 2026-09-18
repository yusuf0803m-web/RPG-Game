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
from .status import BAD_STATUSES, STATUS_DEFS, StatusInstance, make_stat_mod, make_status

BARA_MAX_DASAR = 5
BARA_HOLDER = "rimba"
KETAHANAN_LEMAH = 25
KETAHANAN_NORMAL = 5
KETAHANAN_GOYAH_SKILL = 15
JAGA_MP_PCT = 0.05
ITEM_BUBUK_DASAR = 10
ITEM_BUBUK_PER_LEVEL = 4


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
    ) -> None:
        self.data = data
        self.rng = rng or random.Random()
        self.bestiary = bestiary or Bestiary()
        self.inventory: dict[str, int] = inventory if inventory is not None else {}
        self.heroes: list[Combatant] = [self._make_hero(h) for h in heroes]
        self.enemies: list[Combatant] = self._make_enemies(list(enemy_ids))
        self.can_flee = can_flee and not any(e.is_boss for e in self.enemies)
        self.bara_max = bara_max
        self.bara = min(bara_start, bara_max)
        self.round = 0
        self.queue: list[Combatant] = []
        self.log: list[str] = []
        self.result: Optional[BattleResult] = None
        self.bara_skills: list[Skill] = [s for s in data.skills.values() if s.cost_type == CostType.BARA]

    # -- pembuatan peserta --------------------------------------------------
    def _make_hero(self, h: Hero) -> Combatant:
        st = h.stats
        c = Combatant(
            key=h.id, name=h.name, is_player=True, level=h.level, base=st,
            hp=min(h.hp, st.hp), mp=min(h.mp, st.mp), skills=h.skills(), hero=h,
        )
        w = h.equipment.get("senjata")
        if w and w in self.data.items and self.data.items[w].element != Element.NETRAL:
            c.weapon_element = self.data.items[w].element
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
            skills += [self.data.skill(x) for p in edef.phases for x in p.pattern if x != "serang"]
            skills += [self.data.skill(x) for x in edef.skills]
            out.append(Combatant(
                key=eid, name=edef.name, is_player=False, level=edef.level, base=edef.stats.copy(),
                hp=edef.stats.hp, mp=edef.stats.mp, skills=skills, affinities=dict(edef.affinities),
                immune=set(edef.immune), label=label, edef=edef,
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

    # -- alur giliran -------------------------------------------------------
    def start(self) -> list[str]:
        ev: list[str] = []
        names = ", ".join(e.display_name for e in self.enemies)
        self._emit(ev, f"{names} muncul!")
        return ev

    def _new_round(self) -> None:
        self.round += 1
        everyone = self.alive_heroes + self.alive_enemies
        # AGI tertinggi duluan; seri: party duluan (GAME_DESIGN §4.1)
        self.queue = sorted(everyone, key=lambda c: (-c.effective("agi"), 0 if c.is_player else 1))

    def next_turn(self) -> Turn:
        """Ambil peserta berikutnya. Menangani ronde baru dan giliran yang dilewati."""
        if self.over:
            return Turn(None, [], skipped=True)
        while not self.queue:
            self._new_round()
        actor = self.queue.pop(0)
        if not actor.alive:
            return Turn(None, [], skipped=True)
        ev: list[str] = []
        # status "sampai giliran berikutnya" (Jaga) berakhir di awal giliran pemilik
        for sid in [s for s, st in actor.statuses.items() if st.sdef and st.sdef.expires_at_own_turn_start]:
            del actor.statuses[sid]
        actor.turn_count += 1
        if actor.skip_turn:
            alasan = next(st.name for st in actor.statuses.values() if st.sdef and st.sdef.skip_turn)
            self._emit(ev, f"{actor.display_name} tidak bisa bergerak ({alasan}).")
            self._end_turn(actor, ev)
            return Turn(actor, ev, skipped=True)
        return Turn(actor, ev, skipped=False)

    def _end_turn(self, actor: Combatant, ev: list[str]) -> None:
        """Tick status pemilik giliran: DoT, kurangi durasi, hapus yang habis."""
        for sid in list(actor.statuses.keys()):
            st = actor.statuses.get(sid)
            if st is None:
                continue
            sdef = st.sdef
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
                        actor.ketahanan = actor.ketahanan_max
                        self._emit(ev, f"{actor.display_name} pulih dari Pecah.")
                    elif sdef and sdef.bad and sid not in ("goyah",):
                        self._emit(ev, f"{actor.display_name} pulih dari {st.name}.")
        self._check_end(ev)

    # -- validasi aksi ------------------------------------------------------
    def cost_ok(self, actor: Combatant, skill: Skill) -> bool:
        if skill.cost_type == CostType.MP:
            return actor.mp >= skill.cost
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
            if actor.key not in s.users:
                continue
            if not all((h := self.hero_by_key(u)) is not None and h.alive for u in s.users):
                continue
            if self.bara >= s.cost:
                out.append(s)
        return out

    def usable_items(self) -> list[ItemDef]:
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
        if self.over or not actor.alive:
            return ev
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
        else:
            raise ValueError(f"aksi tidak dikenal: {action.kind}")
        if not self.over:
            self._end_turn(actor, ev)
        return ev

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
        if target_type == Target.SATU_MUSUH:
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
        self._emit(ev, f"{actor.display_name} menyerang {t.display_name}!")
        self._hit(actor, t, elem, 1.0, SkillKind.FISIK, ev, skill=None)

    def _pay_cost(self, actor: Combatant, skill: Skill, ev: list[str]) -> None:
        if skill.cost_type == CostType.MP:
            actor.mp -= skill.cost
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
        if skill.cost_type != CostType.BARA or len(skill.users) < 2:
            return actor
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
        self._pay_cost(actor, skill, ev)
        if skill.once_per_battle:
            actor.used_once.add(skill.id)
        ts = self._resolve_targets(actor, skill.target, targets)
        if skill.cost_type == CostType.BARA and len(skill.users) >= 2:
            names = " & ".join(h.name for u in skill.users if (h := self.hero_by_key(u)))
            self._emit(ev, f"JURUS GANDA! {names}: {skill.name}!")
        else:
            self._emit(ev, f"{actor.display_name} memakai {skill.name}!")
        if not ts:
            self._emit(ev, "...tapi tidak ada sasaran.")
            return
        source = self._skill_source(actor, skill)
        for t in ts:
            if skill.kind in (SkillKind.FISIK, SkillKind.SIHIR):
                for _ in range(max(1, skill.hits)):
                    if not t.alive:
                        break
                    self._hit(source, t, skill.element, skill.power, skill.kind, ev, skill=skill)
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
                self._emit(ev, f"...meleset dari {target.display_name}.")
                return 0
        aff = target.affinity(element)
        if element == Element.NETRAL:
            aff = Affinity.NORMAL
        mult = F.pengali_afinitas(aff, skill.ignore_resist if skill else False, skill.ignore_absorb if skill else False)
        if actor.is_player and target.edef and element != Element.NETRAL:
            if self.bestiary.learn(target.key, element, aff) and aff != Affinity.NORMAL:
                self._emit(ev, f"(Catatan Penyala: {target.name} — {element.label}: {aff.value.upper()})")
        if mult == 0.0:
            self._emit(ev, f"Tidak berpengaruh pada {target.display_name}.")
            return 0
        if kind == SkillKind.FISIK:
            off = actor.effective("atk")
            deff = 0 if (skill and skill.ignore_def) else target.effective("def")
        else:
            off = actor.effective("mag")
            deff = 0 if (skill and skill.ignore_def) else target.effective("res")
        if offense_override is not None:
            off = offense_override
        if skill and "low_hp_x1_5" in skill.tags and actor.hp_ratio < 0.30:
            power *= 1.5
        if skill and "ally_down_x2" in skill.tags and any(not a.alive for a in self.allies_of(actor)):
            power *= 2.0
        krit = self.rng.random() < F.peluang_kritikal(actor.effective("lck"))
        dmg = F.hitung_damage(off, deff, power, mult, kritikal=krit,
                              pecah=target.has("pecah"), goyah=target.has("goyah"),
                              acak=F.acak_damage(self.rng))
        if dmg < 0:
            sembuh = min(-dmg, target.max_hp - target.hp)
            target.hp += sembuh
            self._emit(ev, f"{target.display_name} MENYERAP {element.label}! Pulih {sembuh} HP.")
            return dmg
        target.hp = max(0, target.hp - dmg)
        tag = ""
        if aff == Affinity.LEMAH:
            tag = " LEMAH!"
        elif aff == Affinity.TAHAN:
            tag = " (tahan)"
        if krit:
            tag += " KRITIKAL!"
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

    def _ketahanan(self, target: Combatant, amount: int, ev: list[str]) -> None:
        if target.ketahanan_max <= 0 or target.has("pecah"):
            return
        target.ketahanan = max(0, target.ketahanan - amount)
        if target.ketahanan == 0:
            target.statuses.pop("goyah", None)
            target.statuses["pecah"] = make_status("pecah")
            self._emit(ev, f"*** {target.display_name} PECAH! Ia kehilangan giliran dan menerima damage ×1.5. ***")
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
        if sid in target.statuses and sid != "goyah":
            return False
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
            self._emit(ev, f"Bara +{self.bara - before} ({alasan}) → {self.bara}/{self.bara_max}")

    def _on_death(self, c: Combatant, ev: list[str]) -> None:
        c.statuses.clear()
        if c.is_player:
            self._gain_bara(2, ev, "nyala dari amarah")
        else:
            self._release_swallowed(c, ev)
            for h in self.heroes:
                st = h.statuses.get("terjerat")
                if st is not None and st.source is c:
                    del h.statuses["terjerat"]

    def _check_end(self, ev: list[str]) -> None:
        if self.over:
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
        for c in self.heroes:
            if c.hero is not None:
                c.hero.hp = max(0, c.hp)
                c.hero.mp = max(0, c.mp)
