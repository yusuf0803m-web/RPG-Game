"""Anggota party di luar pertarungan: level, XP, stat, skill yang dikuasai.

GAME_DESIGN §4.2 (pertumbuhan deterministik) dan §5.1 (kurva XP = 20·n²).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .loader import GameData
from .models import STAT_NAMES, CharacterDef, Skill, Stats

LEVEL_MAX = 60


def xp_to_reach(level: int) -> int:
    """XP total yang dibutuhkan untuk *berada* di ``level`` (Lv 1 = 0)."""
    if level <= 1:
        return 0
    return sum(20 * n * n for n in range(2, level + 1))


def xp_for_next(level: int) -> int:
    """XP yang dibutuhkan dari level ini ke level berikutnya (20·n², n = level tujuan)."""
    n = level + 1
    return 20 * n * n


def stats_at_level(cdef: CharacterDef, level: int) -> Stats:
    """Stat dasar Lv 1 + pertumbuhan × (level − 1), dibulatkan ke bawah per stat."""
    s = Stats()
    for name in STAT_NAMES:
        base = cdef.base.get(name)
        growth = cdef.growth.get(name)
        s.set(name, int(base + growth * (level - 1)))
    return s


@dataclass
class Hero:
    """Anggota party yang persisten antar pertarungan."""
    cdef: CharacterDef
    level: int = 1
    xp: int = 0
    hp: int = 0
    mp: int = 0
    equipment: dict[str, Optional[str]] = field(default_factory=lambda: {"senjata": None, "zirah": None, "aksesori": None})
    _data: Optional[GameData] = field(default=None, repr=False)

    @classmethod
    def create(cls, data: GameData, cid: str, level: int = 1, full: bool = True) -> "Hero":
        h = cls(cdef=data.character(cid), level=max(1, min(LEVEL_MAX, level)), _data=data)
        h.xp = xp_to_reach(h.level)
        if full:
            h.restore()
        return h

    @property
    def id(self) -> str:
        return self.cdef.id

    @property
    def name(self) -> str:
        return self.cdef.name

    @property
    def base_stats(self) -> Stats:
        return stats_at_level(self.cdef, self.level)

    @property
    def stats(self) -> Stats:
        """Stat dengan equipment (Tahap 1: equipment belum menambah; siap untuk Tahap 3)."""
        s = self.base_stats
        if self._data:
            for iid in self.equipment.values():
                if iid and iid in self._data.items and self._data.items[iid].stats:
                    for name in STAT_NAMES:
                        s.set(name, s.get(name) + self._data.items[iid].stats.get(name))
        return s

    @property
    def max_hp(self) -> int:
        return self.stats.hp

    @property
    def max_mp(self) -> int:
        return self.stats.mp

    def restore(self) -> None:
        self.hp = self.max_hp
        self.mp = self.max_mp

    def skills(self) -> list[Skill]:
        """Skill yang sudah dikuasai pada level ini (urut level unlock)."""
        assert self._data is not None
        out = [self._data.skill(sid) for sid in self.cdef.skills]
        return sorted((s for s in out if s.level <= self.level), key=lambda s: (s.level, s.name))

    def gain_xp(self, amount: int) -> list[int]:
        """Tambah XP; kembalikan daftar level baru yang dicapai (bisa kosong)."""
        gained: list[int] = []
        self.xp += max(0, amount)
        while self.level < LEVEL_MAX and self.xp >= xp_to_reach(self.level + 1):
            old = self.stats
            self.level += 1
            new = self.stats
            # GAME_DESIGN §5.1: naik level memulihkan 25% HP/MP
            self.hp = min(new.hp, self.hp + (new.hp - old.hp) + new.hp // 4)
            self.mp = min(new.mp, self.mp + (new.mp - old.mp) + new.mp // 4)
            gained.append(self.level)
        return gained

    def new_skills_at(self, level: int) -> list[Skill]:
        assert self._data is not None
        return [self._data.skill(sid) for sid in self.cdef.skills if self._data.skill(sid).level == level]
