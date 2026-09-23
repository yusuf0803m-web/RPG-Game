"""Skenario prototipe Tahap 1: pertarungan tunggal dengan party & musuh tetap."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    party: tuple[tuple[str, int], ...]      # (id karakter, level)
    enemies: tuple[str, ...]
    inventory: dict = field(default_factory=dict)
    note: str = ""


SCENARIOS: list[Scenario] = [
    Scenario(
        "hutan", "Hutan Kelabu — Serigala & Kunang (Lv 3)",
        (("rimba", 3), ("sela", 3)),
        ("serigala_kabut", "kunang_kelam", "kunang_kelam"),
        {"ramuan_daun": 3},
        "Tutorial: Serigala lemah Api, Kunang lemah Cahaya & menyerap Kelam.",
    ),
    Scenario(
        "boss_hutan", "BOSS: Hampa Penjaga Hutan (Lv 4)",
        (("rimba", 4), ("sela", 4)),
        ("boss_hampa_penjaga_hutan",),
        {"ramuan_daun": 4, "garam_bangun": 2},
        "Raung Lupa tiap 3 giliran. Cahaya & Api lemah. Coba pecahkan Ketahanannya.",
    ),
    Scenario(
        "rawa", "Rawa Suar — Lumut & Katak (Lv 7)",
        (("rimba", 7), ("sela", 7), ("lintang", 6)),
        ("lumut_berjalan", "katak_rawa_bengkak", "hampa_pengembara"),
        {"ramuan_daun": 4, "penawar": 3},
        "Tiga kelemahan berbeda: Api, Petir, Cahaya. Racun dan Lupa mengancam.",
    ),
    Scenario(
        "boss_katak", "BOSS: Raja Katak Lumpur (Lv 9)",
        (("rimba", 9), ("sela", 9), ("lintang", 8)),
        ("boss_raja_katak_lumpur",),
        {"ramuan_daun": 5, "ramuan_akar": 2, "penawar": 4, "abu_fajar": 1},
        "Dua fase. Saat HP < 50% ia menelan kawan; Goyah/Pecah melepaskannya. Petir!",
    ),
    Scenario(
        "tambang", "Tambang — Pengawal Karat & Kelelawar (Lv 15)",
        (("rimba", 15), ("sela", 15), ("lintang", 15)),
        ("pengawal_karat", "kelelawar_kristal", "kelelawar_kristal"),
        {"ramuan_akar": 4, "tetes_nyala": 3, "garam_bangun": 2, "bubuk_petir": 2},
        "Pengawal tahan Fisik (Sela harus tank). Kelelawar cepat, Tidur, kuras MP.",
    ),
    Scenario(
        "mercusuar", "Mercusuar — Pelita Padam (Lv 20)",
        (("rimba", 20), ("sela", 20), ("lintang", 20)),
        ("pelita_padam", "pengawal_karat"),
        {"ramuan_akar": 4, "tetes_nyala": 3},
        "Pelita Padam MENYERAP Cahaya. Hanya Kelam yang efektif; hati-hati Nyala Pamungkas.",
    ),
]


def get_scenario(sid: str) -> Scenario:
    for s in SCENARIOS:
        if s.id == sid:
            return s
    raise KeyError(f"skenario '{sid}' tidak ada; pilihan: {', '.join(s.id for s in SCENARIOS)}")
