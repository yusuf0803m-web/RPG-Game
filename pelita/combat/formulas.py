"""Formula angka murni (GAME_DESIGN §4.7). Tanpa state, mudah dites.

Semua fungsi menerima angka yang sudah "efektif" (setelah buff/debuff/Jaga).
"""
from __future__ import annotations

import math
import random

from ..models import AFFINITY_MULT, Affinity

ACAK_MIN, ACAK_MAX = 0.90, 1.10
KRITIKAL_MULT = 1.5
KRITIKAL_DASAR = 0.05
KRITIKAL_PER_LCK = 0.005
KRITIKAL_MAKS = 0.35
KENA_DASAR = 0.92
KENA_PER_AGI = 0.015
KENA_MIN, KENA_MAKS = 0.60, 1.00
BUTA_PENALTI = 0.40
GOYAH_MULT = 1.2
PECAH_MULT = 1.5
KABUR_DASAR = 0.50
KABUR_PER_AGI = 0.03
KABUR_MIN, KABUR_MAKS = 0.20, 0.90


def dasar(offense: int, defense: int) -> int:
    """``dasar = ATK*2 − DEF`` (atau MAG/RES), minimum 1."""
    return max(1, offense * 2 - defense)


def peluang_kritikal(lck: int) -> float:
    return min(KRITIKAL_MAKS, KRITIKAL_DASAR + lck * KRITIKAL_PER_LCK)


def peluang_kena(agi_penyerang: int, agi_target: int, hit_mod: float = 0.0, buta: bool = False) -> float:
    p = KENA_DASAR + (agi_penyerang - agi_target) * KENA_PER_AGI + hit_mod
    if buta:
        p -= BUTA_PENALTI
    return max(KENA_MIN, min(KENA_MAKS, p))


def peluang_kabur(agi_party: float, agi_musuh: float) -> float:
    p = KABUR_DASAR + (agi_party - agi_musuh) * KABUR_PER_AGI
    return max(KABUR_MIN, min(KABUR_MAKS, p))


def pengali_afinitas(aff: Affinity, ignore_resist: bool = False, ignore_absorb: bool = False) -> float:
    if ignore_resist and aff == Affinity.TAHAN:
        aff = Affinity.NORMAL
    if ignore_absorb and aff == Affinity.SERAP:
        aff = Affinity.NORMAL
    return AFFINITY_MULT[aff]


def hitung_damage(
    offense: int,
    defense: int,
    power: float,
    afinitas: float,
    kritikal: bool = False,
    pecah: bool = False,
    goyah: bool = False,
    acak: float = 1.0,
) -> int:
    """Damage akhir. ``afinitas`` adalah pengali (1.5/1.0/0.5/0/−1).

    Nilai negatif berarti Serap (penyembuhan untuk target). Nol berarti Imun.
    Selain kedua kasus itu, damage minimum 1.
    """
    if afinitas == 0.0:
        return 0
    d = dasar(offense, defense) * power * abs(afinitas)
    if kritikal:
        d *= KRITIKAL_MULT
    if pecah:
        d *= PECAH_MULT
    elif goyah:
        d *= GOYAH_MULT
    d *= acak
    hasil = max(1, math.floor(d))
    return -hasil if afinitas < 0 else hasil


def hitung_heal(mag: int, power: float, heal_base: int) -> int:
    return math.floor(mag * power + heal_base)


def acak_damage(rng: random.Random) -> float:
    return rng.uniform(ACAK_MIN, ACAK_MAX)


def peluang_status(chance: float, lck_target: int) -> float:
    """Peluang status masuk = peluang skill × (1 − LCK_target × 1%)."""
    return max(0.0, chance * (1 - lck_target * 0.01))
