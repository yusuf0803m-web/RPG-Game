"""Definisi area & ruang, dimuat dari ``pelita/data/world/*.json``.

Bentuk satu file area::

    {
      "id": "pelita_rendah", "name": "...", "start": "rumah_guntur",
      "fog": false,                       # kabut: butuh Minyak Lentera (GAME_DESIGN §2.2)
      "encounter_rate": 0.35,
      "encounters": [{"enemies": ["kunang_kelam", "kunang_kelam"], "weight": 3}, ...],
      "rooms": { "<id>": Room, ... },
      "scripts": { "<id>": [ perintah, ... ] }
    }

Room::

    {
      "name": "...", "text": "deskripsi saat masuk", "safe": true,
      "exits": [{"label": "Ke warung", "to": "warung", "if": [...], "locked": "teks kalau terkunci",
                 "area": "rawa_suar"}],
      "npcs":  [{"id": "kirana", "name": "Kirana", "script": "bicara_kirana", "if": [...]}],
      "objects": [{"id": "lentera", "name": "Lentera penjaga", "script": "lentera_save"}],
      "on_enter": "skrip_id",
      "encounters": [...]                 # override daftar encounter area (opsional)
    }

Perintah skrip: lihat ``world.script``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..loader import DataError

WORLD_DIR = Path(__file__).parents[1] / "data" / "world"


@dataclass
class Encounter:
    enemies: list[str]
    weight: int = 1


@dataclass
class Exit:
    label: str
    to: str
    area: Optional[str] = None
    cond: list = field(default_factory=list)
    locked: str = ""                 # teks kalau kondisi tidak terpenuhi; kosong = exit disembunyikan
    hidden_if: list = field(default_factory=list)


@dataclass
class Interactable:
    id: str
    name: str
    script: str
    cond: list = field(default_factory=list)
    verb: str = "Bicara"


@dataclass
class LatarVarian:
    """Latar alternatif yang dipakai kalau kondisinya terpenuhi (GAME_DESIGN §7.2)."""
    cond: list
    latar: str


@dataclass
class Room:
    id: str
    name: str
    text: str = ""
    safe: bool = False
    latar: str = ""                              # path gambar tanpa ekstensi, mis. "larung/warung"
    latar_varian: list["LatarVarian"] = field(default_factory=list)
    latar_catatan: str = ""                      # deskripsi adegan untuk yang menggambar
    exits: list[Exit] = field(default_factory=list)
    npcs: list[Interactable] = field(default_factory=list)
    objects: list[Interactable] = field(default_factory=list)
    on_enter: Optional[str] = None
    encounters: Optional[list[Encounter]] = None
    encounter_rate: Optional[float] = None


@dataclass
class Area:
    id: str
    name: str
    start: str
    rooms: dict[str, Room]
    scripts: dict[str, list]
    latar: str = ""                              # latar cadangan untuk ruang tanpa latar sendiri
    fog: bool = False
    encounter_rate: float = 0.35
    encounters: list[Encounter] = field(default_factory=list)
    level_range: str = ""

    def room(self, rid: str) -> Room:
        try:
            return self.rooms[rid]
        except KeyError:
            raise DataError(f"area '{self.id}': ruang '{rid}' tidak ada") from None


def _encounters(rows) -> list[Encounter]:
    return [Encounter(list(r["enemies"]), int(r.get("weight", 1))) for r in rows]


def _inter(rows, verb) -> list[Interactable]:
    return [Interactable(r["id"], r["name"], r["script"], list(r.get("if", [])), r.get("verb", verb)) for r in rows]


def parse_area(d: dict) -> Area:
    rooms: dict[str, Room] = {}
    for rid, r in d["rooms"].items():
        rooms[rid] = Room(
            id=rid,
            name=r["name"],
            text=r.get("text", ""),
            safe=bool(r.get("safe", False)),
            latar=r.get("latar", ""),
            latar_varian=[LatarVarian(list(v.get("if", [])), v["latar"]) for v in r.get("latar_varian", [])],
            latar_catatan=r.get("latar_catatan", ""),
            exits=[Exit(e["label"], e["to"], e.get("area"), list(e.get("if", [])), e.get("locked", ""), list(e.get("hidden_if", [])))
                   for e in r.get("exits", [])],
            npcs=_inter(r.get("npcs", []), "Bicara"),
            objects=_inter(r.get("objects", []), "Periksa"),
            on_enter=r.get("on_enter"),
            encounters=_encounters(r["encounters"]) if "encounters" in r else None,
            encounter_rate=r.get("encounter_rate"),
        )
    return Area(
        id=d["id"],
        name=d["name"],
        start=d["start"],
        rooms=rooms,
        scripts={k: list(v) for k, v in d.get("scripts", {}).items()},
        fog=bool(d.get("fog", False)),
        latar=d.get("latar", ""),
        encounter_rate=float(d.get("encounter_rate", 0.35)),
        encounters=_encounters(d.get("encounters", [])),
        level_range=d.get("level_range", ""),
    )


@dataclass
class World:
    areas: dict[str, Area]
    shops: dict[str, dict]
    quests: dict[str, dict]
    latar: dict[str, dict] = field(default_factory=dict)      # daftar gambar latar (§7.2)
    kenangan: dict[str, dict] = field(default_factory=dict)   # adegan Berkemah (§5.6)
    buruan: dict[str, dict] = field(default_factory=dict)     # papan Buruan (§5.7)
    arena: list[dict] = field(default_factory=list)           # tingkat Arena Kafilah (§5.7)

    def area(self, aid: str) -> Area:
        try:
            return self.areas[aid]
        except KeyError:
            raise DataError(f"area '{aid}' tidak ada") from None

    def latar_ruang(self, area: Area, room: Room, check) -> str:
        """Path gambar latar untuk ``room`` sekarang: varian yang cocok, lalu latar ruang, lalu area.

        ``check`` adalah ``GameState.check`` sehingga latar bisa mengikuti kondisi dunia (§7.2).
        """
        for v in room.latar_varian:
            if check(v.cond):
                return v.latar
        if room.latar:
            return room.latar
        bawaan = f"{area.id}/{room.id}"
        if not self.latar or bawaan in self.latar:
            return bawaan
        return area.latar

    def validate(self, data) -> None:
        for a in self.areas.values():
            if a.start not in a.rooms:
                raise DataError(f"area '{a.id}': ruang awal '{a.start}' tidak ada")
            for r in a.rooms.values():
                for path in [r.latar or f"{a.id}/{r.id}"] + [v.latar for v in r.latar_varian]:
                    if self.latar and path not in self.latar:
                        raise DataError(f"{a.id}/{r.id}: latar '{path}' tidak terdaftar di latar.json")
                for e in r.exits:
                    target_area = self.areas.get(e.area) if e.area else a
                    if target_area is None:
                        raise DataError(f"{a.id}/{r.id}: exit ke area '{e.area}' yang tidak ada")
                    if e.to not in target_area.rooms:
                        raise DataError(f"{a.id}/{r.id}: exit ke ruang '{e.to}' yang tidak ada")
                for it in r.npcs + r.objects:
                    if it.script not in a.scripts:
                        raise DataError(f"{a.id}/{r.id}: skrip '{it.script}' tidak ada")
                if r.on_enter and r.on_enter not in a.scripts:
                    raise DataError(f"{a.id}/{r.id}: on_enter '{r.on_enter}' tidak ada")
                for enc in (r.encounters or []):
                    for eid in enc.enemies:
                        data.enemy(eid)
            for enc in a.encounters:
                for eid in enc.enemies:
                    data.enemy(eid)
            for sid, cmds in a.scripts.items():
                _validate_script(self, data, a, sid, cmds)
        for sh in self.shops.values():
            for iid in sh["items"]:
                if iid not in data.items:
                    raise DataError(f"toko '{sh['name']}' menjual item '{iid}' yang tidak ada")
            for kid in sh.get("kaca", []):
                if kid not in data.kaca:
                    raise DataError(f"toko '{sh['name']}' menjual kaca '{kid}' yang tidak ada")
        for kid, k in self.kenangan.items():
            for cid in k["pasangan"]:
                data.character(cid)
            if k.get("jurus") and k["jurus"] not in data.skills:
                raise DataError(f"kenangan '{kid}' membuka jurus '{k['jurus']}' yang tidak ada")
        for bid, b in self.buruan.items():
            for eid in b["musuh"]:
                data.enemy(eid)
            if b["area"] not in self.areas or b["room"] not in self.areas[b["area"]].rooms:
                raise DataError(f"buruan '{bid}' menunjuk ruang '{b['area']}/{b['room']}' yang tidak ada")
            _validate_hadiah(data, f"buruan '{bid}'", b.get("hadiah", {}))
        for i, t in enumerate(self.arena, 1):
            for gelombang in t["gelombang"]:
                for eid in gelombang:
                    data.enemy(eid)
            _validate_hadiah(data, f"arena tingkat {i}", t.get("hadiah", {}))


def _validate_hadiah(data, label: str, hadiah: dict) -> None:
    for iid in hadiah.get("item", {}):
        if iid not in data.items:
            raise DataError(f"{label}: hadiah item '{iid}' tidak ada")
    for kid in hadiah.get("kaca", []):
        if kid not in data.kaca:
            raise DataError(f"{label}: hadiah kaca '{kid}' tidak ada")


def _validate_script(world: World, data, area: Area, sid: str, cmds: list, depth: int = 0) -> None:
    if depth > 20:
        raise DataError(f"{area.id}/{sid}: skrip terlalu dalam")
    for c in cmds:
        if not isinstance(c, dict):
            raise DataError(f"{area.id}/{sid}: perintah bukan objek: {c!r}")
        for key in ("then", "else", "do", "win"):
            if key in c:
                _validate_script(world, data, area, sid, c[key], depth + 1)
        if "choice" in c:
            for opt in c["choice"]:
                _validate_script(world, data, area, sid, opt.get("then", []), depth + 1)
        if "battle" in c:
            for eid in c["battle"]:
                data.enemy(eid)
        if "join" in c:
            data.character(c["join"])
        if "give" in c:
            for iid in c["give"]:
                if iid not in data.items:
                    raise DataError(f"{area.id}/{sid}: give item '{iid}' tidak ada")
        if "run" in c and c["run"] not in area.scripts:
            raise DataError(f"{area.id}/{sid}: run '{c['run']}' tidak ada")
        if "goto" in c and c["goto"] not in area.rooms:
            raise DataError(f"{area.id}/{sid}: goto '{c['goto']}' tidak ada")
        if "travel" in c:
            t = c["travel"]
            world.area(t["area"]).room(t["room"])
        if "shop" in c and c["shop"] not in world.shops:
            raise DataError(f"{area.id}/{sid}: toko '{c['shop']}' tidak ada")
        if "quest" in c and c["quest"] not in world.quests:
            raise DataError(f"{area.id}/{sid}: quest '{c['quest']}' tidak ada")
        if "ilustrasi" in c and world.latar and c["ilustrasi"] not in world.latar:
            raise DataError(f"{area.id}/{sid}: ilustrasi '{c['ilustrasi']}' tidak terdaftar di latar.json")
        if "adegan" in c:
            lat = c["adegan"].get("latar")
            if lat and world.latar and lat not in world.latar:
                raise DataError(f"{area.id}/{sid}: latar adegan '{lat}' tidak terdaftar di latar.json")
        if "kaca" in c:
            for kid in c["kaca"]:
                if kid not in data.kaca:
                    raise DataError(f"{area.id}/{sid}: kaca '{kid}' tidak ada")
        if "tukang_kaca" in c and c["tukang_kaca"] and c["tukang_kaca"] not in world.shops:
            raise DataError(f"{area.id}/{sid}: toko kaca '{c['tukang_kaca']}' tidak ada")


def _opsional(path: Path) -> dict:
    """Muat file data dunia yang boleh tidak ada (Kenangan, Buruan, Arena)."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return {k: v for k, v in json.load(fh).items() if not k.startswith("_")}


_CACHE: dict[Path, World] = {}


def load_world(data, world_dir: Optional[Path] = None, use_cache: bool = True) -> World:
    world_dir = world_dir or WORLD_DIR
    if use_cache and world_dir in _CACHE:
        return _CACHE[world_dir]
    areas: dict[str, Area] = {}
    for f in sorted(world_dir.glob("area_*.json")):
        with open(f, encoding="utf-8") as fh:
            a = parse_area(json.load(fh))
        if a.id in areas:
            raise DataError(f"area '{a.id}' ganda ({f.name})")
        areas[a.id] = a
    shops: dict[str, dict] = {}
    quests: dict[str, dict] = {}
    sp = world_dir / "shops.json"
    if sp.exists():
        with open(sp, encoding="utf-8") as fh:
            shops = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    qp = world_dir / "quests.json"
    if qp.exists():
        with open(qp, encoding="utf-8") as fh:
            quests = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    latar_raw = _opsional(world_dir / "latar.json")
    latar = dict(latar_raw.get("gambar", {})) if latar_raw else {}
    kenangan = _opsional(world_dir / "kenangan.json")
    buruan = _opsional(world_dir / "buruan.json")
    arena_raw = _opsional(world_dir / "arena.json")
    arena = list(arena_raw.get("tingkat", [])) if arena_raw else []
    w = World(areas, shops, quests, latar, kenangan, buruan, arena)
    w.validate(data)
    if use_cache:
        _CACHE[world_dir] = w
    return w
