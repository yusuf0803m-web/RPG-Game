"""Status efek (GAME_DESIGN §4.8) dan buff/debuff stat sementara."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class StatusDef:
    id: str
    name: str
    bad: bool = True
    turns: Optional[int] = None          # durasi bawaan (None = sampai giliran pemilik berikutnya)
    stat_mults: dict = field(default_factory=dict)
    skip_turn: bool = False
    dot_pct: float = 0.0                 # damage per giliran, % HP maks
    regen_pct: float = 0.0               # pulih per giliran, % HP maks (Lagu Rawat, Panji Larung)
    regen_mag: float = 0.0               # pulih per giliran, kelipatan MAG pemasang
    redirect: float = 0.0                # bagian damage yang dialihkan ke pemasang (Tanggung)
    no_skills: bool = False
    no_magic: bool = False
    hit_penalty: bool = False            # Buta
    wake_on_hit: bool = False            # Tidur
    heal_reversed: bool = False          # Kutuk
    taunt: bool = False                  # Provokasi
    expires_at_own_turn_start: bool = False   # Jaga
    consumed_at_own_turn_end: bool = False    # Goyah, Pecah
    icon: str = ""


STATUS_DEFS: dict[str, StatusDef] = {
    "racun":     StatusDef("racun", "Racun", turns=4, dot_pct=0.08),
    "bakar":     StatusDef("bakar", "Bakar", turns=3, dot_pct=0.05, stat_mults={"def": 0.8}),
    "beku":      StatusDef("beku", "Beku", turns=1, skip_turn=True),
    "lelah":     StatusDef("lelah", "Lelah", turns=3, stat_mults={"atk": 0.7, "mag": 0.7}),
    "goyah":     StatusDef("goyah", "Goyah", turns=1, consumed_at_own_turn_end=True),
    "lupa":      StatusDef("lupa", "Lupa", turns=2, no_skills=True),
    "tidur":     StatusDef("tidur", "Tidur", turns=3, skip_turn=True, wake_on_hit=True),
    "buta":      StatusDef("buta", "Buta", turns=3, hit_penalty=True),
    "berat":     StatusDef("berat", "Berat", turns=3, stat_mults={"agi": 0.5}),
    "bisu":      StatusDef("bisu", "Bisu", turns=2, no_magic=True),
    "kutuk":     StatusDef("kutuk", "Kutuk", turns=3, heal_reversed=True),
    "tertelan":  StatusDef("tertelan", "Tertelan", turns=2, skip_turn=True),
    "terjerat":  StatusDef("terjerat", "Terjerat", turns=99, skip_turn=True),
    "provokasi": StatusDef("provokasi", "Provokasi", bad=False, turns=1, taunt=True),
    "jaga":      StatusDef("jaga", "Jaga", bad=False, stat_mults={"def": 1.5, "res": 1.5}, expires_at_own_turn_start=True),
    "pecah":     StatusDef("pecah", "PECAH", turns=1, skip_turn=True, consumed_at_own_turn_end=True),
    "mengisi":   StatusDef("mengisi", "Mengisi", bad=False, turns=3),
    "tandai":    StatusDef("tandai", "Ditandai", turns=2),
    # Babak 2: lagu Ratih, panji Rangga, dan perisai Kelana (GAME_DESIGN §4.10)
    "lagu_rawat":  StatusDef("lagu_rawat", "Lagu Rawat", bad=False, turns=3, regen_mag=1.0),
    "lagu_gugah":  StatusDef("lagu_gugah", "Lagu Gugah", bad=False, turns=3,
                             stat_mults={"atk": 1.2, "mag": 1.2}),
    "lagu_cepat":  StatusDef("lagu_cepat", "Lagu Cepat", bad=False, turns=3, stat_mults={"agi": 1.3}),
    "panji":       StatusDef("panji", "Panji Larung", bad=False, turns=4, regen_pct=0.10),
    "tanggung":    StatusDef("tanggung", "Ditanggung", bad=False, turns=2, redirect=0.7),
    "siap_tebas":  StatusDef("siap_tebas", "Bersiap", bad=False, turns=1, stat_mults={"atk": 1.5, "mag": 1.5}),
}

#: Hanya satu Lagu yang boleh aktif (GAME_DESIGN §4.10): memasang lagu baru menghapus yang lama.
LAGU = ("lagu_rawat", "lagu_gugah", "lagu_cepat")

BAD_STATUSES = {k for k, v in STATUS_DEFS.items() if v.bad}


@dataclass
class StatusInstance:
    id: str
    name: str
    turns_left: Optional[int]
    stat_mults: dict = field(default_factory=dict)
    bad: bool = True
    source: object = None            # Combatant yang memasang (Telan/Jerat/Lagu/Tanggung)
    applied_turn: int = -1           # turn_count pemilik saat dipasang; durasi tidak berkurang di giliran yang sama

    @property
    def sdef(self) -> Optional[StatusDef]:
        return STATUS_DEFS.get(self.id)


def make_status(status_id: str, turns: Optional[int] = None, source: object = None) -> StatusInstance:
    sdef = STATUS_DEFS[status_id]
    return StatusInstance(
        id=sdef.id,
        name=sdef.name,
        turns_left=sdef.turns if turns is None else turns,
        stat_mults=dict(sdef.stat_mults),
        bad=sdef.bad,
        source=source,
    )


def make_stat_mod(stat: str, mult: float, turns: int) -> StatusInstance:
    """Buff/debuff satu stat. Kunci unik per stat & arah agar buff yang sama tidak menumpuk."""
    arah = "naik" if mult >= 1.0 else "turun"
    label = {"atk": "ATK", "def": "DEF", "mag": "MAG", "res": "RES", "agi": "AGI", "lck": "LCK"}.get(stat, stat.upper())
    return StatusInstance(
        id=f"{stat}_{arah}",
        name=f"{label}{'↑' if mult >= 1.0 else '↓'}",
        turns_left=turns,
        stat_mults={stat: mult},
        bad=mult < 1.0,
    )
