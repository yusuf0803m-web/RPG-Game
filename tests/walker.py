"""Pemain otomatis untuk tes alur cerita: memilih opsi menu berdasarkan potongan label."""
from __future__ import annotations

import re
from collections import deque
from typing import Iterable

from pelita.ui.terminal import IO

OPT_RE = re.compile(r"^\s*(\d+)\)\s+(.*)$")


class Walker:
    """``steps`` = daftar potongan label (case-insensitive) atau perintah huruf ('p', 'i', 'k', ...).

    Saat permainan bertanya, Walker mencari opsi bernomor di output terakhir yang labelnya
    memuat potongan itu, lalu menjawab nomornya. Kalau tidak ketemu, ia menjawab '' (lanjut).
    """

    def __init__(self, steps: Iterable[str], on_command=None) -> None:
        self.steps: deque[str] = deque(steps)
        self.on_command = on_command          # dipanggil untuk langkah '#...'; False = jangan dikonsumsi
        self.out: list[str] = []
        self.answers: list[str] = []
        self._since_prompt: list[str] = []
        self.io = IO(read=self._read, write=self._write)
        self.stuck = 0

    def _write(self, s: str) -> None:
        self.out.append(s)
        self._since_prompt.append(s)

    def _options(self) -> dict[str, str]:
        opts: dict[str, str] = {}
        for line in self._since_prompt:
            m = OPT_RE.match(line)
            if m:
                opts[m.group(1)] = m.group(2)
        return opts

    def _read(self, prompt: str) -> str:
        opts = self._options()
        self._since_prompt = []
        if not self.steps:
            self.stuck += 1
            if self.stuck > 50:
                raise RuntimeError("Walker kehabisan langkah:\n" + "\n".join(self.out[-40:]))
            return "k"          # keluar
        while self.steps and self.steps[0].startswith("#"):
            cmd = self.steps.popleft()
            if self.on_command and self.on_command(cmd[1:]) is False:
                self.steps.appendleft(cmd)      # syaratnya belum terpenuhi; coba lagi nanti
                break
        if not self.steps:
            return "k"
        step = self.steps[0]
        if step.startswith("@"):            # perintah huruf langsung
            self.steps.popleft()
            self.answers.append(step[1:])
            return step[1:]
        for num, label in opts.items():
            if step.lower() in label.lower():
                self.steps.popleft()
                self.answers.append(num)
                return num
        # opsi belum muncul (mis. prompt Enter/slot): jawab kosong dan coba lagi nanti
        self.stuck += 1
        if self.stuck > 200:
            raise RuntimeError(f"Walker macet mencari '{step}'. Opsi terakhir: {opts}\n" + "\n".join(self.out[-60:]))
        return ""

    @property
    def text(self) -> str:
        return "\n".join(self.out)
