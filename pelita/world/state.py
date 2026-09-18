"""State permainan yang persisten: party, inventori, flag, posisi, quest; save/load JSON."""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..combat.engine import BARA_MAX_DASAR, Bestiary
from ..loader import GameData
from ..models import Affinity, Element
from ..party import Hero

SAVE_DIR = Path("saves")
SAVE_SLOTS = 5
PARTY_AKTIF_MAKS = 4
MINYAK_LANGKAH = 20          # satu Minyak Lentera menahan Lupa selama 20 langkah di kabut (§5.4)
ENCOUNTER_JEDA = 2           # tidak ada dua encounter dalam 2 langkah (§4.1)


@dataclass
class GameState:
    data: GameData
    party: list[Hero] = field(default_factory=list)
    inventory: dict[str, int] = field(default_factory=dict)
    keping: int = 0
    flags: set[str] = field(default_factory=set)
    quests: dict[str, str] = field(default_factory=dict)
    area_id: str = ""
    room_id: str = ""
    bestiary: Bestiary = field(default_factory=Bestiary)
    bara_max: int = 0                 # 0 sampai Bara diperoleh (Area 1)
    steps: int = 0
    steps_since_encounter: int = 99
    lentera_steps: int = 0
    seed: int = field(default_factory=lambda: random.randrange(1 << 30))
    rng: random.Random = field(default=None, repr=False)  # type: ignore[assignment]
    started_at: float = field(default_factory=time.time)
    playtime: float = 0.0
    log: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.rng is None:
            self.rng = random.Random(self.seed)

    # -- party --------------------------------------------------------------
    @property
    def active_party(self) -> list[Hero]:
        return self.party[:PARTY_AKTIF_MAKS]

    def hero(self, cid: str) -> Optional[Hero]:
        for h in self.party:
            if h.id == cid:
                return h
        return None

    def in_party(self, cid: str) -> bool:
        return self.hero(cid) is not None

    def join(self, cid: str, level: Optional[int] = None, guest: bool = False) -> Hero:
        if self.in_party(cid):
            return self.hero(cid)  # type: ignore[return-value]
        cdef = self.data.character(cid)
        lead = self.hero("rimba")
        if level is None:
            level = max(1, (lead.level if lead else 1) + cdef.join_level_offset) if not guest else 10
        h = Hero.create(self.data, cid, level)
        h.guest = guest
        self.party.append(h)
        return h

    def leave(self, cid: str) -> None:
        self.party = [h for h in self.party if h.id != cid]

    def heal_all(self) -> None:
        for h in self.party:
            h.restore()

    def all_down(self) -> bool:
        return all(h.hp <= 0 for h in self.active_party)

    def revive_downed_minimal(self) -> None:
        """Setelah pertarungan, yang pingsan bangun dengan 1 HP (tidak ada penalti tambahan, §5.9)."""
        for h in self.party:
            if h.hp <= 0:
                h.hp = 1

    # -- inventori ----------------------------------------------------------
    def add_item(self, iid: str, n: int = 1) -> None:
        if iid not in self.data.items:
            raise KeyError(f"item '{iid}' tidak ada")
        self.inventory[iid] = self.inventory.get(iid, 0) + n
        if self.inventory[iid] <= 0:
            del self.inventory[iid]

    def has_item(self, iid: str, n: int = 1) -> bool:
        return self.inventory.get(iid, 0) >= n

    def count(self, iid: str) -> int:
        return self.inventory.get(iid, 0)

    # -- kondisi skrip ------------------------------------------------------
    def check(self, cond) -> bool:
        """Evaluasi kondisi: list = AND; {"any": [...]} = OR; string = satu syarat."""
        if cond is None or cond == []:
            return True
        if isinstance(cond, dict):
            if "any" in cond:
                return any(self.check(c) for c in cond["any"])
            if "not" in cond:
                return not self.check(cond["not"])
            raise ValueError(f"kondisi tidak dikenal: {cond}")
        if isinstance(cond, list):
            return all(self.check(c) for c in cond)
        s = str(cond).strip()
        neg = s.startswith("!")
        if neg:
            s = s[1:]
        if s.startswith("has:"):
            iid, _, n = s[4:].partition("*")
            val = self.has_item(iid, int(n) if n else 1)
        elif s.startswith("party:"):
            val = self.in_party(s[6:])
        elif s.startswith("quest:"):
            qid, _, st = s[6:].partition("=")
            val = self.quests.get(qid, "") == st if st else qid in self.quests
        elif s.startswith("keping>="):
            val = self.keping >= int(s[8:])
        elif s.startswith("level>="):
            lead = self.hero("rimba")
            val = (lead.level if lead else 0) >= int(s[7:])
        elif s.startswith("known:"):
            eid, _, el = s[6:].partition("=")
            val = Element(el) in self.bestiary.get(eid) if el else bool(self.bestiary.get(eid))
        elif s == "bara":
            val = self.bara_max > 0
        else:
            val = s in self.flags
        return (not val) if neg else val

    # -- kabut & langkah ----------------------------------------------------
    def step(self, fog: bool) -> list[str]:
        """Satu langkah perpindahan ruang. Mengelola Minyak Lentera di area kabut."""
        msgs: list[str] = []
        self.steps += 1
        self.steps_since_encounter += 1
        if fog:
            if self.lentera_steps > 0:
                self.lentera_steps -= 1
                if self.lentera_steps == 0:
                    msgs.append("Minyak lentera saku hampir habis...")
            if self.lentera_steps == 0 and self.has_item("minyak_lentera"):
                self.add_item("minyak_lentera", -1)
                self.lentera_steps = MINYAK_LANGKAH
                msgs.append(f"Kau menuang Minyak Lentera baru. (sisa {self.count('minyak_lentera')})")
            elif self.lentera_steps == 0:
                msgs.append("Lentera saku padam. Kabut merayap ke ingatanmu... (musuh akan memulai dengan Lupa)")
        return msgs

    @property
    def in_dark_fog(self) -> bool:
        return self.lentera_steps == 0

    # -- save / load --------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "version": 1,
            "party": [h.to_dict() for h in self.party],
            "inventory": dict(self.inventory),
            "keping": self.keping,
            "flags": sorted(self.flags),
            "quests": dict(self.quests),
            "area": self.area_id,
            "room": self.room_id,
            "bestiary": {eid: {el.value: a.value for el, a in d.items()} for eid, d in self.bestiary.known.items()},
            "bara_max": self.bara_max,
            "steps": self.steps,
            "lentera_steps": self.lentera_steps,
            "seed": self.rng.randrange(1 << 30),
            "playtime": self.playtime + (time.time() - self.started_at),
        }

    @classmethod
    def from_dict(cls, data: GameData, d: dict) -> "GameState":
        st = cls(data=data, seed=int(d.get("seed", 0)))
        st.party = [Hero.from_dict(data, h) for h in d.get("party", [])]
        st.inventory = {k: int(v) for k, v in d.get("inventory", {}).items()}
        st.keping = int(d.get("keping", 0))
        st.flags = set(d.get("flags", []))
        st.quests = dict(d.get("quests", {}))
        st.area_id = d.get("area", "")
        st.room_id = d.get("room", "")
        for eid, m in d.get("bestiary", {}).items():
            for el, a in m.items():
                st.bestiary.learn(eid, Element(el), Affinity(a))
        st.bara_max = int(d.get("bara_max", 0))
        st.steps = int(d.get("steps", 0))
        st.lentera_steps = int(d.get("lentera_steps", 0))
        st.playtime = float(d.get("playtime", 0.0))
        return st

    def save(self, slot: int, save_dir: Path = SAVE_DIR) -> Path:
        save_dir.mkdir(parents=True, exist_ok=True)
        p = save_dir / f"slot{slot}.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=1)
        return p

    @classmethod
    def load(cls, data: GameData, slot: int, save_dir: Path = SAVE_DIR) -> "GameState":
        with open(save_dir / f"slot{slot}.json", encoding="utf-8") as f:
            return cls.from_dict(data, json.load(f))

    @staticmethod
    def slot_summaries(data: GameData, save_dir: Path = SAVE_DIR) -> list[Optional[str]]:
        out: list[Optional[str]] = []
        for i in range(1, SAVE_SLOTS + 1):
            p = save_dir / f"slot{i}.json"
            if not p.exists():
                out.append(None)
                continue
            try:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                lead = d["party"][0] if d.get("party") else {"id": "?", "level": 0}
                m = int(d.get("playtime", 0) // 60)
                out.append(f"{d.get('area', '?')}/{d.get('room', '?')}  Lv {lead['level']}  {len(d.get('party', []))} anggota  {m} mnt")
            except (OSError, ValueError, KeyError):
                out.append("(rusak)")
        return out

    @property
    def bara_max_effective(self) -> int:
        return self.bara_max if self.bara_max > 0 else 0


def new_game(data: GameData) -> GameState:
    """State awal (GAME_DESIGN §2.2 Area 1): Rimba Lv 1 dengan senjata & zirah awal."""
    st = GameState(data=data)
    rimba = Hero.create(data, "rimba", 1)
    rimba.equipment["senjata"] = "tongkat_kayu_jati"
    rimba.equipment["zirah"] = "zirah_kain"
    rimba.restore()
    st.party = [rimba]
    st.inventory = {"ramuan_daun": 3, "minyak_lentera": 2}
    st.keping = 30
    st.bara_max = 0
    return st


def bara_max_for(state: GameState) -> int:
    return state.bara_max if state.bara_max > 0 else BARA_MAX_DASAR if "bara" in state.flags else 0
