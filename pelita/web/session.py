"""Sesi permainan untuk web: menjalankan ``Game.run()`` di thread dengan IO antrian.

``WebIO`` menggantikan terminal:

- ``line(teks)``   → event ``log`` (dan, kalau berpola ``  N) label``, dikumpulkan
  sebagai pilihan untuk prompt berikutnya — sama seperti pemain otomatis di tes)
- ``emit(k, v)``   → event terstruktur (``room``, ``battle``, ``say``, ``text``, ``end``)
- ``ask(prompt)``  → event ``prompt`` berisi daftar pilihan, lalu **memblokir**
  sampai klien mengirim jawaban

Klien mengambil event lewat ``GET .../state?since=N`` dan menjawab lewat
``POST .../input``. Semua state permainan tetap milik mesin yang sama dengan
versi terminal; modul ini tidak menyalin aturan apa pun.
"""
from __future__ import annotations

import queue
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..loader import GameData, load_data
from ..world.explore import Game
from ..world.model import World, load_world
from ..world.state import SAVE_SLOTS, GameState, new_game

OPT_RE = re.compile(r"^\s*(\d+)\)\s+(.*)$")
HURUF_RE = re.compile(r"\[([A-Za-z])\]([A-Za-z ]*)")
TIMEOUT_INPUT = 3600.0          # sesi menganggur >1 jam dianggap ditinggalkan
POLL_TIMEOUT = 25.0             # long-poll: tunggu event baru maksimal sekian detik
SESSION_TTL = 6 * 3600.0


@dataclass
class Event:
    seq: int
    kind: str
    payload: dict


class SessionClosed(Exception):
    """Sesi dihentikan dari luar (pemain menutup permainan)."""


class WebIO:
    structured = True          # klien menggambar ruang & pertarungan dari emit()

    def __init__(self, session: "WebSession") -> None:
        self.session = session
        self._pending_options: list[dict] = []
        self._pending_lines: list[str] = []

    # -- keluaran -----------------------------------------------------------
    def line(self, s: str = "") -> None:
        m = OPT_RE.match(s)
        if m:
            self._pending_options.append({"key": m.group(1), "label": m.group(2).strip()})
            return
        if "[P]arty" in s or "[K]eluar" in s:
            for key, label in HURUF_RE.findall(s):
                self._pending_options.append({"key": key.lower(), "label": (key + label).strip(), "meta": True})
            return
        self._pending_lines.append(s)
        self.session.push("log", {"text": s})

    def emit(self, kind: str, payload: dict) -> None:
        self.session.push(kind, payload)

    # -- masukan ------------------------------------------------------------
    def ask(self, prompt: str = "> ") -> str:
        options = self._pending_options
        self._pending_options = []
        self._pending_lines = []
        self.session.push("prompt", {"prompt": prompt.strip(), "options": options,
                                     "free": not options or prompt.strip().lower().endswith(("(y/n)", "(y/n) "))})
        return self.session.wait_for_input()


class WebSession:
    def __init__(self, data: GameData, world: World, state: GameState, save_dir: Path, sid: Optional[str] = None) -> None:
        self.id = sid or uuid.uuid4().hex[:12]
        self.data = data
        self.world = world
        self.state = state
        self.io = WebIO(self)
        self.game = Game(data, world, state, self.io, save_dir=save_dir)
        self.events: list[Event] = []
        self.seq = 0
        self.lock = threading.Lock()
        self.new_event = threading.Condition(self.lock)
        self.inbox: queue.Queue[str] = queue.Queue()
        self.finished = False
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self.closed = False
        self.last_touch = time.time()
        self.thread = threading.Thread(target=self._run, name=f"pelita-{self.id}", daemon=True)

    # -- siklus hidup -------------------------------------------------------
    def start(self) -> "WebSession":
        self.thread.start()
        return self

    def _run(self) -> None:
        try:
            self.result = self.game.run()
        except SessionClosed:
            self.result = "closed"
        except Exception as e:                       # noqa: BLE001 — tampilkan ke pemain, jangan diam
            self.error = f"{type(e).__name__}: {e}"
            self.push("error", {"message": self.error})
        finally:
            self.finished = True
            self.push("finished", {"result": self.result, "error": self.error})

    def close(self) -> None:
        self.closed = True
        self.inbox.put("k")                          # bangunkan thread yang menunggu input
        self.inbox.put("y")

    # -- event --------------------------------------------------------------
    def push(self, kind: str, payload: dict) -> None:
        with self.new_event:
            self.seq += 1
            self.events.append(Event(self.seq, kind, payload))
            if len(self.events) > 4000:
                del self.events[:1000]
            self.new_event.notify_all()

    def poll(self, since: int, timeout: float = POLL_TIMEOUT) -> dict:
        self.last_touch = time.time()
        deadline = time.time() + timeout
        with self.new_event:
            while True:
                fresh = [e for e in self.events if e.seq > since]
                if fresh or self.finished:
                    return {
                        "seq": self.seq,
                        "events": [{"seq": e.seq, "kind": e.kind, "payload": e.payload} for e in fresh],
                        "finished": self.finished,
                        "result": self.result,
                        "error": self.error,
                    }
                remaining = deadline - time.time()
                if remaining <= 0:
                    return {"seq": self.seq, "events": [], "finished": self.finished,
                            "result": self.result, "error": self.error}
                self.new_event.wait(remaining)

    # -- input --------------------------------------------------------------
    def send(self, text: str) -> None:
        self.last_touch = time.time()
        self.inbox.put(text)

    def wait_for_input(self) -> str:
        if self.closed:
            raise SessionClosed()
        try:
            s = self.inbox.get(timeout=TIMEOUT_INPUT)
        except queue.Empty:
            raise SessionClosed() from None
        if self.closed and s in ("k", "y"):
            raise SessionClosed()
        return s

    @property
    def stale(self) -> bool:
        return time.time() - self.last_touch > SESSION_TTL


class SessionStore:
    """Kumpulan sesi aktif, satu per permainan yang sedang berjalan."""

    def __init__(self, save_dir: Path) -> None:
        self.save_dir = save_dir
        self.data = load_data()
        self.world = load_world(self.data)
        self.sessions: dict[str, WebSession] = {}
        self.lock = threading.Lock()

    def _sweep(self) -> None:
        for sid, s in list(self.sessions.items()):
            if s.stale or (s.finished and time.time() - s.last_touch > 600):
                s.close()
                del self.sessions[sid]

    def create(self, state: Optional[GameState] = None) -> WebSession:
        with self.lock:
            self._sweep()
            st = state or new_game(self.data)
            s = WebSession(self.data, self.world, st, self.save_dir).start()
            self.sessions[s.id] = s
            return s

    def load_slot(self, slot: int) -> WebSession:
        st = GameState.load(self.data, slot, self.save_dir)
        return self.create(st)

    def get(self, sid: str) -> Optional[WebSession]:
        return self.sessions.get(sid)

    def drop(self, sid: str) -> None:
        with self.lock:
            s = self.sessions.pop(sid, None)
        if s:
            s.close()

    def slots(self) -> list[Optional[str]]:
        return GameState.slot_summaries(self.data, self.save_dir)

    @property
    def slot_count(self) -> int:
        return SAVE_SLOTS
