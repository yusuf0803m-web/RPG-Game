"""Sesi permainan untuk web: menjalankan ``Game.run()`` di thread dengan IO antrian.

``WebIO`` menggantikan terminal:

- ``line(teks)``   → event ``log``
- ``emit(k, v)``   → event terstruktur (``room``, ``battle``, ``say``, ``text``, ``end``)
- ``menu(opsi)``   → event ``prompt`` berisi daftar opsi **sebagai data** (lihat
  ``pelita/ui/menu.py``), lalu **memblokir** sampai klien mengirim jawaban
- ``confirm``/``pause`` → prompt ya-tidak dan prompt "Lanjut", juga bertombol

Tiap prompt punya ``kind``: ``menu`` | ``confirm`` | ``enter`` | ``free``.
Mesin permainan tidak pernah lagi mengarang opsi dari teks yang sudah dicetak —
dulu itu sumber bug "menu tanpa tombol keluar": satu baris yang memuat beberapa
opsi hanya jadi satu tombol. ``free`` karena itu seharusnya tidak pernah muncul;
tes ``tests/test_menu_web.py`` menjaga hal itu.

Judul menu ikut di dalam ``prompt`` (``title``/``subtitle``/``note``), bukan
dikirim sebagai ``log``. Karena tiap prompt *mengganti* panel pilihan, judul toko
yang digambar ulang tiap putaran menu tidak lagi menumpuk di log — sama seperti
deskripsi ruang yang hanya ditulis saat pemain benar-benar pindah.

Klien mengambil event lewat ``GET .../state?since=N`` dan menjawab lewat
``POST .../input``. Semua state permainan tetap milik mesin yang sama dengan
versi terminal; modul ini tidak menyalin aturan apa pun.
"""
from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..loader import GameData, load_data
from ..ui.menu import Header, Option
from ..ui.terminal import IO
from ..world.explore import Game
from ..world.model import World, load_world
from ..world.state import SAVE_SLOTS, GameState, new_game

YA_TIDAK = (("y", "Ya"), ("n", "Tidak"))
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


def as_payload(o: Option) -> dict:
    """Bentuk satu opsi untuk klien."""
    return {"key": o.key, "label": o.label, "meta": o.meta, "back": o.back}


class WebIO(IO):
    """IO terminal, tapi keluaran & prompt-nya masuk antrian event.

    Mewarisi ``IO`` supaya ``pick()``/``Menu`` yang dipakai mesin permainan
    bekerja sama persis; hanya cara menampilkan dan membaca yang berbeda.
    """

    structured = True          # klien menggambar ruang & pertarungan dari emit()

    def __init__(self, session: "WebSession") -> None:
        super().__init__(read=lambda prompt="> ": self.ask(prompt), write=self.line)
        self.session = session

    # -- keluaran -----------------------------------------------------------
    def line(self, s: str = "") -> None:
        self.session.push("log", {"text": s})

    def emit(self, kind: str, payload: dict) -> None:
        self.session.push(kind, payload)

    def render_options(self, options, header: Optional[Header] = None) -> None:
        """Keterangan tambahan tetap masuk log; labelnya sendiri jadi tombol.

        Judul sengaja **tidak** ditulis ke log: ia ikut payload prompt supaya
        panelnya diganti, bukan ditumpuk (lihat docstring modul).
        """
        for o in options:
            for d in o.detail:
                self.line(d)

    # -- masukan ------------------------------------------------------------
    def _prompt(self, prompt: str, kind: str, options: list[dict], required: Optional[str] = None,
                header: Optional[Header] = None) -> str:
        """Kirim satu prompt dan tunggu jawaban yang sah."""
        keys = {o["key"].lower() for o in options}
        payload = {"prompt": prompt.strip(), "kind": kind, "options": options,
                   "free": kind == "free", "required": required,
                   "title": header.title if header else None,
                   "subtitle": header.subtitle if header else None,
                   "note": list(header.note) if header else []}
        while True:
            self.session.push("prompt", payload)
            s = self.session.wait_for_input().strip().lower()
            if kind == "free" or kind == "enter" or s in keys:
                return s
            if s == "":
                back = next((o["key"] for o in options if o.get("back") and not o.get("meta")), None)
                if back is not None:
                    return back
            # klien mengirim jawaban yang tidak ada di daftar: tanya ulang, jangan
            # membiarkan sesi menggantung.

    def menu(self, options, prompt: str = "> ", auto: Optional[str] = None,
             required: Optional[str] = None, header: Optional[Header] = None) -> str:
        self.render_options(options, header)
        if auto is not None:
            return auto.lower()
        return self._prompt(prompt, "menu", [as_payload(o) for o in options], required, header)

    def confirm(self, question: str, auto: Optional[bool] = None) -> bool:
        if auto is not None:
            return auto
        opsi = [{"key": k, "label": l, "meta": False, "back": k == "n"} for k, l in YA_TIDAK]
        return self._prompt(question, "confirm", opsi) == "y"

    def pause(self) -> None:
        self._prompt("(Enter)", "enter", [])

    def ask(self, prompt: str = "> ") -> str:
        """Jawaban bebas. Tidak dipakai lagi oleh mesin permainan; lihat docstring modul."""
        return self._prompt(prompt, "free", [])


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
