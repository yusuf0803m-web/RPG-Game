"""Anggota party di luar pertarungan: level, XP, stat, skill, Jalur, dan soket Kaca.

GAME_DESIGN §4.2 (pertumbuhan deterministik), §4.9 (Jalur), §5.1 (kurva XP = 20·n²),
§5.3 (Kaca Ingatan).
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Optional

from .loader import GameData
from .models import STAT_NAMES, CharacterDef, CostType, Element, JalurDef, KacaDef, Passive, Skill, Stats

LEVEL_MAX = 60

# Kaca naik tingkat setelah sekian pertarungan sambil terpasang (GAME_DESIGN §5.3).
KACA_AMBANG = (12, 36)
# Kaca Skill meminjam skill karakter lain: biaya MP ×1.5 di tingkat I, makin murah di atasnya.
KACA_BIAYA_SKILL = {1: 1.5, 2: 1.25, 3: 1.0}
# Satu langkah Serpihan Ingatan menaikkan HP maks 10% (maks 3 langkah per karakter, §5.5).
HP_BONUS_PER_LANGKAH = 0.10
HP_BONUS_MAKS = 3


def kaca_tingkat(pemakaian: int) -> int:
    """Tingkat Kaca (1–3) dari jumlah pertarungan yang pernah dilaluinya."""
    return 3 if pemakaian >= KACA_AMBANG[1] else 2 if pemakaian >= KACA_AMBANG[0] else 1


def angka_romawi(n: int) -> str:
    return {1: "I", 2: "II", 3: "III"}.get(n, str(n))


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
    guest: bool = False                 # companion sementara (Pak Guntur): tidak bisa ganti equipment
    jalur: Optional[str] = None         # id JalurDef yang dipilih (§4.9)
    kaca: list[Optional[str]] = field(default_factory=list)   # isi soket senjata, urut (§5.3)
    hp_bonus: int = 0                   # langkah Serpihan Ingatan yang dipakai untuk HP maks
    # Dua tabel berikut dimiliki GameState dan dibagi ke semua Hero (lihat GameState.wire).
    kaca_uses: dict[str, int] = field(default_factory=dict)
    slot_bonus: dict[str, int] = field(default_factory=dict)
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

    # -- Kaca Ingatan -------------------------------------------------------
    @property
    def soket(self) -> int:
        """Jumlah soket Kaca: dari senjata terpasang + bonus Serpihan untuk senjata itu."""
        w = self.equipment.get("senjata")
        if not w or not self._data or w not in self._data.items:
            return 0
        return self._data.items[w].slots + self.slot_bonus.get(w, 0)

    def rapikan_soket(self) -> list[str]:
        """Sesuaikan panjang daftar Kaca dengan jumlah soket. Kembalikan Kaca yang terlepas."""
        n = self.soket
        lepas = [k for k in self.kaca[n:] if k]
        self.kaca = (self.kaca + [None] * n)[:n]
        return lepas

    def kaca_terpasang(self) -> list[tuple[KacaDef, int]]:
        """(definisi Kaca, tingkat) untuk tiap soket yang terisi."""
        if not self._data:
            return []
        out = []
        for kid in self.kaca:
            if kid and kid in self._data.kaca:
                out.append((self._data.kaca[kid], kaca_tingkat(self.kaca_uses.get(kid, 0))))
        return out

    def jalur_def(self) -> Optional[JalurDef]:
        return self._data.jalur.get(self.jalur) if (self._data and self.jalur) else None

    def jalur_tersedia(self) -> list[JalurDef]:
        """Jalur yang bisa dipilih sekarang (level sudah cukup dan belum memilih)."""
        if not self._data or self.guest:
            return []
        return [j for j in self._data.jalur_for(self.id) if self.level >= j.level]

    @property
    def butuh_pilih_jalur(self) -> bool:
        return self.jalur is None and bool(self.jalur_tersedia())

    def passive(self) -> Passive:
        """Gabungan semua pasif: Jalur + tiap Kaca terpasang (diskalakan tingkatnya)."""
        p = Passive()
        j = self.jalur_def()
        if j:
            p = p.gabung(j.passive)
        for kdef, tingkat in self.kaca_terpasang():
            p = p.gabung(kdef.passive.skala(tingkat))
        if self.hp_bonus:
            p = p.gabung(Passive(stat_mult={"hp": HP_BONUS_PER_LANGKAH * min(self.hp_bonus, HP_BONUS_MAKS)}))
        return p

    @property
    def kaca_element(self) -> Optional[Element]:
        """Elemen serangan dasar dari Kaca Elemen (soket paling kiri yang berisi)."""
        for kdef, _ in self.kaca_terpasang():
            if kdef.kind == "elemen" and kdef.element != Element.NETRAL:
                return kdef.element
        return None

    @property
    def stats(self) -> Stats:
        """Stat dasar + equipment + pasif Jalur/Kaca (tambahan tetap lalu pengali)."""
        s = self.base_stats
        if self._data:
            for iid in self.equipment.values():
                if iid and iid in self._data.items and self._data.items[iid].stats:
                    for name in STAT_NAMES:
                        s.set(name, s.get(name) + self._data.items[iid].stats.get(name))
        p = self.passive()
        for name in STAT_NAMES:
            v = s.get(name) + p.stat_flat.get(name, 0)
            mult = p.stat_mult.get(name, 0.0)
            s.set(name, max(0, int(v * (1 + mult))))
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
        """Skill yang dikuasai: bawaan + Jalur + pinjaman Kaca Skill (urut level unlock)."""
        assert self._data is not None
        out = [self._data.skill(sid) for sid in self.cdef.skills]
        j = self.jalur_def()
        if j:
            out += [self._data.skill(sid) for sid in j.skills]
        dikuasai = {s.id for s in out}
        pinjaman: list[Skill] = []
        for kdef, tingkat in self.kaca_terpasang():
            if kdef.kind == "skill" and kdef.skill and kdef.skill not in dikuasai:
                dasar = self._data.skill(kdef.skill)
                dikuasai.add(dasar.id)
                biaya = dasar.cost
                if dasar.cost_type == CostType.MP and biaya:
                    biaya = max(1, round(biaya * KACA_BIAYA_SKILL.get(tingkat, 1.5)))
                pinjaman.append(dataclasses.replace(dasar, cost=biaya, level=1,
                                                    name=f"{dasar.name} (Kaca)"))
        siap = [s for s in out if s.level <= self.level] + pinjaman
        potong = self.passive().biaya_mp_pct
        if potong:
            siap = [dataclasses.replace(s, cost=max(1, round(s.cost * (1 - potong))))
                    if s.cost_type == CostType.MP and s.cost else s for s in siap]
        return sorted(siap, key=lambda s: (s.level, s.name))

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

    def to_dict(self) -> dict:
        return {"id": self.id, "level": self.level, "xp": self.xp, "hp": self.hp, "mp": self.mp,
                "equipment": dict(self.equipment), "guest": self.guest,
                "jalur": self.jalur, "kaca": list(self.kaca), "hp_bonus": self.hp_bonus}

    @classmethod
    def from_dict(cls, data: GameData, d: dict) -> "Hero":
        h = cls.create(data, d["id"], int(d["level"]), full=False)
        h.xp = int(d.get("xp", h.xp))
        h.equipment.update(d.get("equipment", {}))
        h.guest = bool(d.get("guest", False))
        h.jalur = d.get("jalur")
        h.kaca = list(d.get("kaca", []))
        h.hp_bonus = int(d.get("hp_bonus", 0))
        h.hp = min(int(d.get("hp", h.max_hp)), h.max_hp)
        h.mp = min(int(d.get("mp", h.max_mp)), h.max_mp)
        return h

    def new_skills_at(self, level: int) -> list[Skill]:
        assert self._data is not None
        ids = list(self.cdef.skills)
        j = self.jalur_def()
        if j:
            ids += j.skills
        return [self._data.skill(sid) for sid in ids if self._data.skill(sid).level == level]
