"""Pelita Terakhir: RPG teks turn-based bergaya JRPG klasik.

Struktur paket (lihat GAME_DESIGN.md §9):
- ``models``   : tipe data inti (Stats, Skill, Enemy, Hero, Item)
- ``loader``   : memuat data JSON dari ``pelita/data``
- ``combat``   : formula damage, status efek, mesin pertarungan, AI musuh
- ``party``    : leveling & pertumbuhan stat
- ``ui``       : tampilan terminal
"""

__version__ = "0.1.0"
