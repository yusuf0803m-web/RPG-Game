"""Memuat data JSON dari ``pelita/data`` menjadi objek ``models``.

Semua fungsi memvalidasi rujukan silang (skill yang dirujuk karakter/musuh harus
ada) agar kesalahan ketik di data ketahuan saat start, bukan di tengah pertarungan.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .models import (
    AIAction,
    AIPhase,
    Affinity,
    CharacterDef,
    CostType,
    Drop,
    Element,
    EnemyDef,
    Growth,
    ItemDef,
    Skill,
    SkillKind,
    StatMod,
    Stats,
    StatusInflict,
    Target,
)

DATA_DIR = Path(__file__).parent / "data"


class DataError(ValueError):
    """Data JSON tidak konsisten."""


def _read(name: str, data_dir: Path) -> dict:
    with open(data_dir / name, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def _inflicts(rows: list[dict]) -> list[StatusInflict]:
    return [StatusInflict(r["status"], float(r["chance"]), r.get("turns")) for r in rows]


def parse_skill(sid: str, d: dict) -> Skill:
    try:
        return Skill(
            id=sid,
            name=d["name"],
            kind=SkillKind(d["kind"]),
            element=Element(d.get("element", "netral")),
            target=Target(d["target"]),
            power=float(d.get("power", 1.0 if d["kind"] in ("fisik", "sihir") else 0.0)),
            cost=int(d.get("cost", 0)),
            cost_type=CostType(d.get("cost_type", "mp")),
            level=int(d.get("level", 1)),
            inflict=_inflicts(d.get("inflict", [])),
            self_inflict=_inflicts(d.get("self_inflict", [])),
            mods=[StatMod(m["stat"], float(m["mult"]), int(m["turns"])) for m in d.get("mods", [])],
            heal_base=int(d.get("heal_base", 0)),
            heal_pct=float(d.get("heal_pct", 0.0)),
            cure=list(d.get("cure", [])),
            hit_mod=float(d.get("hit_mod", 0.0)),
            cannot_miss=bool(d.get("cannot_miss", False)),
            ignore_def=bool(d.get("ignore_def", False)),
            ignore_resist=bool(d.get("ignore_resist", False)),
            ignore_absorb=bool(d.get("ignore_absorb", False)),
            ketahanan=int(d.get("ketahanan", 0)),
            hits=int(d.get("hits", 1)),
            users=list(d.get("users", [])),
            bara_gain=int(d.get("bara_gain", 0)),
            once_per_battle=bool(d.get("once_per_battle", False)),
            tags=list(d.get("tags", [])),
            description=d.get("description", ""),
        )
    except (KeyError, ValueError) as e:
        raise DataError(f"skill '{sid}': {e}") from e


def parse_character(cid: str, d: dict) -> CharacterDef:
    try:
        return CharacterDef(
            id=cid,
            name=d["name"],
            title=d.get("title", ""),
            base=Stats.from_dict(d["base"]),
            growth=Growth.from_dict(d["growth"]),
            skills=list(d.get("skills", [])),
            weapon_type=d.get("weapon_type", ""),
            element_note=d.get("element_note", ""),
            cost_type=CostType(d.get("cost_type", "mp")),
            join_level_offset=int(d.get("join_level_offset", -1)),
            description=d.get("description", ""),
        )
    except (KeyError, ValueError) as e:
        raise DataError(f"karakter '{cid}': {e}") from e


def parse_enemy(eid: str, d: dict) -> EnemyDef:
    try:
        aff = {Element(k): Affinity(v) for k, v in d.get("affinities", {}).items()}
        ai = [
            AIAction(
                action=a["action"],
                weight=int(a.get("weight", 1)),
                hp_below=a.get("hp_below"),
                hp_above=a.get("hp_above"),
                every_n_turns=a.get("every_n_turns"),
                target_rule=a.get("target_rule", "acak"),
            )
            for a in d.get("ai", [])
        ]
        phases = [AIPhase(float(p["hp_above"]), list(p["pattern"]), p.get("name", "")) for p in d.get("phases", [])]
        return EnemyDef(
            id=eid,
            name=d["name"],
            level=int(d.get("level", 1)),
            stats=Stats.from_dict(d["stats"]),
            affinities=aff,
            ai=ai,
            xp=int(d.get("xp", 0)),
            keping=int(d.get("keping", 0)),
            skills=list(d.get("skills", [])),
            drops=[Drop(x["item"], float(x["chance"])) for x in d.get("drops", [])],
            steal=d.get("steal"),
            is_boss=bool(d.get("is_boss", False)),
            ketahanan=int(d.get("ketahanan", 0)),
            phases=phases,
            immune=list(d.get("immune", [])),
            lesson=d.get("lesson", ""),
            description=d.get("description", ""),
        )
    except (KeyError, ValueError) as e:
        raise DataError(f"musuh '{eid}': {e}") from e


def parse_item(iid: str, d: dict) -> ItemDef:
    try:
        return ItemDef(
            id=iid,
            name=d["name"],
            kind=d["kind"],
            price=int(d.get("price", 0)),
            heal_hp=int(d.get("heal_hp", 0)),
            heal_mp=int(d.get("heal_mp", 0)),
            heal_pct=float(d.get("heal_pct", 0.0)),
            revive_pct=float(d.get("revive_pct", 0.0)),
            cure=list(d.get("cure", [])),
            element=Element(d.get("element", "netral")),
            power=float(d.get("power", 0.0)),
            target=Target(d.get("target", "satu_kawan")),
            stats=Stats.from_dict(d["stats"]) if "stats" in d else None,
            slots=int(d.get("slots", 0)),
            weapon_for=d.get("weapon_for"),
            description=d.get("description", ""),
        )
    except (KeyError, ValueError) as e:
        raise DataError(f"item '{iid}': {e}") from e


@dataclass
class GameData:
    skills: dict[str, Skill] = field(default_factory=dict)
    characters: dict[str, CharacterDef] = field(default_factory=dict)
    enemies: dict[str, EnemyDef] = field(default_factory=dict)
    items: dict[str, ItemDef] = field(default_factory=dict)

    def skill(self, sid: str) -> Skill:
        try:
            return self.skills[sid]
        except KeyError:
            raise DataError(f"skill '{sid}' tidak ada") from None

    def enemy(self, eid: str) -> EnemyDef:
        try:
            return self.enemies[eid]
        except KeyError:
            raise DataError(f"musuh '{eid}' tidak ada") from None

    def character(self, cid: str) -> CharacterDef:
        try:
            return self.characters[cid]
        except KeyError:
            raise DataError(f"karakter '{cid}' tidak ada") from None

    def validate(self) -> None:
        for c in self.characters.values():
            for sid in c.skills:
                if sid not in self.skills:
                    raise DataError(f"karakter '{c.id}' merujuk skill '{sid}' yang tidak ada")
        for e in self.enemies.values():
            refs = [a.action for a in e.ai] + [x for p in e.phases for x in p.pattern] + list(e.skills)
            for sid in refs:
                if sid != "serang" and sid not in self.skills:
                    raise DataError(f"musuh '{e.id}' merujuk skill '{sid}' yang tidak ada")
            for d in e.drops:
                if d.item not in self.items:
                    raise DataError(f"musuh '{e.id}' menjatuhkan item '{d.item}' yang tidak ada")
            if e.phases and e.ai:
                raise DataError(f"musuh '{e.id}' punya 'ai' dan 'phases' sekaligus; pilih salah satu")
        for s in self.skills.values():
            for uid in s.users:
                if uid not in self.characters:
                    raise DataError(f"skill '{s.id}' merujuk karakter '{uid}' yang tidak ada")
            if s.cost_type == CostType.BARA and not s.users:
                raise DataError(f"skill Bara '{s.id}' harus punya 'users'")


_CACHE: dict[Path, GameData] = {}


def load_data(data_dir: Optional[Path] = None, use_cache: bool = True) -> GameData:
    data_dir = data_dir or DATA_DIR
    if use_cache and data_dir in _CACHE:
        return _CACHE[data_dir]
    gd = GameData(
        skills={k: parse_skill(k, v) for k, v in _read("skills.json", data_dir).items()},
        characters={k: parse_character(k, v) for k, v in _read("characters.json", data_dir).items()},
        enemies={k: parse_enemy(k, v) for k, v in _read("enemies.json", data_dir).items()},
        items={k: parse_item(k, v) for k, v in _read("items.json", data_dir).items()},
    )
    gd.validate()
    if use_cache:
        _CACHE[data_dir] = gd
    return gd
