"""Tipe data inti untuk Pelita Terakhir.

Semua angka desain (GAME_DESIGN.md §4–§6) hidup di file JSON di ``pelita/data``;
modul ini hanya mendefinisikan bentuknya. Objek di sini adalah *definisi* (tidak
berubah selama permainan). Keadaan runtime pertarungan ada di ``combat.engine``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Element(str, Enum):
    FISIK = "fisik"
    API = "api"
    ES = "es"
    PETIR = "petir"
    ANGIN = "angin"
    BUMI = "bumi"
    CAHAYA = "cahaya"
    KELAM = "kelam"
    NETRAL = "netral"  # heal, buff, dan efek tanpa elemen

    @property
    def label(self) -> str:
        return self.value.capitalize()


class Affinity(str, Enum):
    LEMAH = "lemah"
    NORMAL = "normal"
    TAHAN = "tahan"
    IMUN = "imun"
    SERAP = "serap"


# GAME_DESIGN §4.4
AFFINITY_MULT: dict[Affinity, float] = {
    Affinity.LEMAH: 1.5,
    Affinity.NORMAL: 1.0,
    Affinity.TAHAN: 0.5,
    Affinity.IMUN: 0.0,
    Affinity.SERAP: -1.0,
}


class SkillKind(str, Enum):
    FISIK = "fisik"      # memakai ATK vs DEF
    SIHIR = "sihir"      # memakai MAG vs RES
    HEAL = "heal"
    BUFF = "buff"        # efek positif ke kawan
    DEBUFF = "debuff"    # status/efek negatif tanpa damage
    BANGKIT = "bangkit"  # membangunkan yang pingsan


class Target(str, Enum):
    SATU_MUSUH = "satu_musuh"
    SEMUA_MUSUH = "semua_musuh"
    SATU_KAWAN = "satu_kawan"
    SEMUA_KAWAN = "semua_kawan"
    DIRI = "diri"
    KAWAN_PINGSAN = "kawan_pingsan"

    @property
    def is_enemy(self) -> bool:
        return self in (Target.SATU_MUSUH, Target.SEMUA_MUSUH)

    @property
    def is_multi(self) -> bool:
        return self in (Target.SEMUA_MUSUH, Target.SEMUA_KAWAN)


class CostType(str, Enum):
    MP = "mp"
    HP_PCT = "hp_pct"   # Kelana: persen HP maks
    SC = "sc"           # Bagas: Suku Cadang
    BARA = "bara"       # jurus Bara (sumber daya party)


STAT_NAMES = ("hp", "mp", "atk", "def", "mag", "res", "agi", "lck")

# Kaca naik tingkat I -> III dengan dipakai; efek numeriknya ikut menguat (§5.3).
TINGKAT_SKALA: dict[int, float] = {1: 1.0, 2: 1.5, 3: 2.0}


@dataclass
class Stats:
    hp: int = 0
    mp: int = 0
    atk: int = 0
    def_: int = 0
    mag: int = 0
    res: int = 0
    agi: int = 0
    lck: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "Stats":
        return cls(
            hp=int(d.get("hp", 0)),
            mp=int(d.get("mp", 0)),
            atk=int(d.get("atk", 0)),
            def_=int(d.get("def", 0)),
            mag=int(d.get("mag", 0)),
            res=int(d.get("res", 0)),
            agi=int(d.get("agi", 0)),
            lck=int(d.get("lck", 0)),
        )

    def get(self, name: str) -> int:
        return getattr(self, "def_" if name == "def" else name)

    def set(self, name: str, value: int) -> None:
        setattr(self, "def_" if name == "def" else name, value)

    def copy(self) -> "Stats":
        return Stats(self.hp, self.mp, self.atk, self.def_, self.mag, self.res, self.agi, self.lck)


@dataclass
class Growth:
    """Pertumbuhan stat per level (pecahan; diakumulasi lalu dibulatkan ke bawah)."""
    hp: float = 0
    mp: float = 0
    atk: float = 0
    def_: float = 0
    mag: float = 0
    res: float = 0
    agi: float = 0
    lck: float = 0

    @classmethod
    def from_dict(cls, d: dict) -> "Growth":
        return cls(
            hp=float(d.get("hp", 0)),
            mp=float(d.get("mp", 0)),
            atk=float(d.get("atk", 0)),
            def_=float(d.get("def", 0)),
            mag=float(d.get("mag", 0)),
            res=float(d.get("res", 0)),
            agi=float(d.get("agi", 0)),
            lck=float(d.get("lck", 0)),
        )

    def get(self, name: str) -> float:
        return getattr(self, "def_" if name == "def" else name)


@dataclass
class StatusInflict:
    status: str
    chance: float  # 0.0–1.0
    turns: Optional[int] = None  # None = durasi bawaan status


@dataclass
class StatMod:
    """Pengubah stat sementara yang diberikan buff/debuff: ``stat`` × ``mult`` selama ``turns``."""
    stat: str
    mult: float
    turns: int


@dataclass
class Skill:
    id: str
    name: str
    kind: SkillKind
    element: Element
    target: Target
    power: float = 1.0
    cost: int = 0
    cost_type: CostType = CostType.MP
    level: int = 1
    inflict: list[StatusInflict] = field(default_factory=list)
    self_inflict: list[StatusInflict] = field(default_factory=list)
    mods: list[StatMod] = field(default_factory=list)       # untuk target
    heal_base: int = 0
    heal_pct: float = 0.0                                    # heal berbasis % HP maks (Nyala Pulih)
    cure: list[str] = field(default_factory=list)            # status yang dihapus ("*" = semua buruk)
    hit_mod: float = 0.0                                     # +/- peluang kena (fisik)
    cannot_miss: bool = False
    ignore_def: bool = False                                 # DEF/RES target dihitung 0
    ignore_resist: bool = False                              # Tahan dihitung Normal
    ignore_absorb: bool = False                              # Serap dihitung Normal
    ketahanan: int = 0                                       # pengurang meter Ketahanan tambahan
    hits: int = 1
    users: list[str] = field(default_factory=list)           # jurus Bara: id karakter yang harus aktif
    bara_gain: int = 0                                       # Bara yang diberikan setelah skill (Terang Larung)
    once_per_battle: bool = False
    tags: list[str] = field(default_factory=list)          # efek khusus: lihat combat.engine.SPECIAL_TAGS
    description: str = ""

    @property
    def is_attack(self) -> bool:
        return self.kind in (SkillKind.FISIK, SkillKind.SIHIR)

    @property
    def is_magic(self) -> bool:
        return self.kind in (SkillKind.SIHIR, SkillKind.HEAL, SkillKind.BANGKIT) or (
            self.kind in (SkillKind.BUFF, SkillKind.DEBUFF) and self.element != Element.FISIK
        )


@dataclass
class Passive:
    """Efek pasif dari Kaca Ingatan (§5.3) atau Jalur (§4.9).

    Nilai numerik diskalakan tingkat Kaca (I/II/III) lewat ``skala``; ``imun``
    dan efek boolean tidak diskalakan.
    """
    stat_mult: dict[str, float] = field(default_factory=dict)   # {"atk": 0.10} = ATK +10%
    stat_flat: dict[str, int] = field(default_factory=dict)
    mp_regen: int = 0              # MP pulih tiap akhir giliran di pertarungan
    kritikal: float = 0.0          # tambahan peluang kritikal
    xp_pct: float = 0.0            # tambahan XP
    harga_pct: float = 0.0         # potongan harga toko (0.20 = -20%)
    biaya_mp_pct: float = 0.0      # potongan biaya MP skill
    bara_awal: int = 0             # Bara di awal pertarungan
    curi_pct: float = 0.0          # tambahan peluang Curi
    imun: list[str] = field(default_factory=list)

    def skala(self, tingkat: int) -> "Passive":
        f = TINGKAT_SKALA.get(tingkat, 1.0)
        return Passive(
            stat_mult={k: v * f for k, v in self.stat_mult.items()},
            stat_flat={k: int(v * f) for k, v in self.stat_flat.items()},
            mp_regen=int(self.mp_regen * f),
            kritikal=self.kritikal * f,
            xp_pct=self.xp_pct * f,
            harga_pct=self.harga_pct * f,
            biaya_mp_pct=self.biaya_mp_pct * f,
            bara_awal=self.bara_awal,
            curi_pct=self.curi_pct * f,
            imun=list(self.imun),
        )

    def gabung(self, other: "Passive") -> "Passive":
        """Jumlahkan dua pasif (efek menumpuk secara aditif)."""
        out = Passive(
            stat_mult=dict(self.stat_mult), stat_flat=dict(self.stat_flat),
            mp_regen=self.mp_regen + other.mp_regen,
            kritikal=self.kritikal + other.kritikal,
            xp_pct=self.xp_pct + other.xp_pct,
            harga_pct=self.harga_pct + other.harga_pct,
            biaya_mp_pct=self.biaya_mp_pct + other.biaya_mp_pct,
            bara_awal=self.bara_awal + other.bara_awal,
            curi_pct=self.curi_pct + other.curi_pct,
            imun=sorted(set(self.imun) | set(other.imun)),
        )
        for k, v in other.stat_mult.items():
            out.stat_mult[k] = out.stat_mult.get(k, 0.0) + v
        for k, v in other.stat_flat.items():
            out.stat_flat[k] = out.stat_flat.get(k, 0) + v
        return out


@dataclass
class KacaDef:
    """Satu jenis Kaca Ingatan (GAME_DESIGN §5.3)."""
    id: str
    name: str
    kind: str                                    # "elemen" | "pasif" | "skill"
    element: Element = Element.NETRAL            # kind == "elemen"
    skill: Optional[str] = None                  # kind == "skill"
    passive: Passive = field(default_factory=Passive)
    price: int = 0                               # 0 = tidak dijual di toko
    langka: bool = False
    description: str = ""


@dataclass
class JalurDef:
    """Satu Jalur spesialisasi (GAME_DESIGN §4.9)."""
    id: str
    name: str
    character: str
    level: int
    skills: list[str] = field(default_factory=list)
    passive: Passive = field(default_factory=Passive)
    passive_note: str = ""
    description: str = ""


@dataclass
class CharacterDef:
    """Definisi anggota party (GAME_DESIGN §3.1, §4.2)."""
    id: str
    name: str
    title: str
    base: Stats
    growth: Growth
    skills: list[str]                    # id skill yang dipelajari (urut level)
    weapon_type: str
    element_note: str = ""
    cost_type: CostType = CostType.MP
    join_level_offset: int = -1
    description: str = ""


@dataclass
class AIAction:
    """Satu baris tabel bobot AI musuh."""
    action: str                 # "serang" atau id skill
    weight: int = 1
    hp_below: Optional[float] = None    # hanya kalau HP musuh < rasio ini
    hp_above: Optional[float] = None
    every_n_turns: Optional[int] = None  # hanya pada giliran ke-n, 2n, ...
    target_rule: str = "acak"   # "acak" | "hp_terendah" | "mag_tertinggi" | "kawan_hp_terendah"


@dataclass
class AIPhase:
    """Skrip fase boss: aktif selama HP > ``hp_above`` (rasio), pola aksi siklik."""
    hp_above: float
    pattern: list[str]          # urutan id aksi, diulang
    name: str = ""
    affinities: Optional[dict] = None     # override afinitas saat fase ini mulai
    ignore_taunt: bool = False            # kebal Provokasi
    actions_per_turn: int = 1
    announce: str = ""                    # teks saat fase dimulai


@dataclass
class AffinitySet:
    name: str
    affinities: dict
    announce: str = ""


@dataclass
class Rotation:
    """Afinitas berganti tiap ``every`` giliran musuh (Penambang Raksasa, Kelam Berwajah)."""
    every: int
    sets: list[AffinitySet]


@dataclass
class Drop:
    item: str
    chance: float


@dataclass
class EnemyDef:
    id: str
    name: str
    level: int
    stats: Stats
    affinities: dict[Element, Affinity]
    ai: list[AIAction]
    xp: int
    keping: int
    skills: list[str] = field(default_factory=list)
    drops: list[Drop] = field(default_factory=list)
    steal: Optional[str] = None
    is_boss: bool = False
    ketahanan: int = 0                       # >0 = punya meter Pecah (boss/elit)
    phases: list[AIPhase] = field(default_factory=list)
    rotation: Optional[Rotation] = None
    immune: list[str] = field(default_factory=list)    # status yang tidak mempan
    traits: list[str] = field(default_factory=list)    # sifat: "terbang", "hampa", "konstruk", "pantul"
    on_death: Optional[str] = None                     # skill yang meledak saat musuh ini mati
    lesson: str = ""                          # "pelajaran" musuh ini (dokumentasi desain)
    description: str = ""

    def affinity(self, element: Element) -> Affinity:
        return self.affinities.get(element, Affinity.NORMAL)


@dataclass
class ItemDef:
    id: str
    name: str
    kind: str                     # "konsumsi" | "senjata" | "zirah" | "aksesori" | "bahan"
    price: int = 0
    heal_hp: int = 0
    heal_mp: int = 0
    heal_pct: float = 0.0
    revive_pct: float = 0.0
    cure: list[str] = field(default_factory=list)
    element: Element = Element.NETRAL
    power: float = 0.0            # bubuk elemen
    target: Target = Target.SATU_KAWAN
    stats: Optional[Stats] = None  # equipment
    slots: int = 0
    weapon_for: Optional[str] = None
    description: str = ""
