"""Satu tempat untuk semua daftar pilihan.

Kenapa ada modul ini: klien web/APK membuat tombol dari daftar opsi yang dikirim
mesin permainan. Dulu tiap menu mencetak sendiri barisnya dan lapisan web menebak
opsi dengan mencocokkan pola teks ``  N) label``. Menu yang memadatkan beberapa
opsi dalam satu baris (``1) Beli   2) Jual   0) Pergi``) karena itu cuma jadi
*satu* tombol, dan menu yang lupa mencetak ``0) Kembali`` tidak punya tombol
keluar sama sekali — di terminal tidak terasa (pemain mengetik angkanya sendiri),
di layar sentuh pemain jadi terkurung.

Karena itu opsi sekarang dibawa sebagai data, bukan sebagai teks yang ditebak
ulang: ``Menu`` menyusun daftar ``Option`` dan ``IO.menu()`` yang memutuskan cara
menampilkannya (terminal mencetak satu opsi per baris; web mengirim daftarnya apa
adanya). Jalan keluar ikut secara bawaan — menu tanpa jalan keluar harus
dinyatakan dengan ``no_back()``, jadi tidak bisa terlupa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence


@dataclass(frozen=True)
class Option:
    """Satu pilihan yang bisa dijawab pemain.

    ``key``    jawaban yang diterima (angka atau huruf, selalu dibandingkan lowercase)
    ``label``  teks tombol / baris menu
    ``meta``   pintasan huruf: di terminal dirangkum jadi satu baris ``[P]arty  [I]tem``
    ``back``   opsi ini adalah jalan keluar dari menu
    ``detail`` baris keterangan tambahan yang ikut tercetak di bawah opsi
    """
    key: str
    label: str
    meta: bool = False
    back: bool = False
    detail: tuple[str, ...] = ()

    @property
    def text(self) -> str:
        """Baris menu untuk terminal."""
        if not self.meta:
            return f"  {self.key}) {self.label}"
        if self.label[:1].lower() == self.key.lower():
            return f"[{self.label[0].upper()}]{self.label[1:]}"
        return f"[{self.key.upper()}] {self.label}"


@dataclass
class Menu:
    """Penyusun daftar opsi. Nomor urut diisi otomatis; jalan keluar ditambah di akhir."""

    back: Optional[str] = "Kembali"
    back_key: str = "0"
    #: alasan menu ini boleh tanpa jalan keluar (dipakai tes regresi antarmuka)
    required: Optional[str] = None
    _options: list[Option] = field(default_factory=list)
    _n: int = 0

    def add(self, label: str, key: Optional[str] = None, detail: Iterable[str] = ()) -> str:
        """Tambah satu opsi bernomor (atau dengan ``key`` sendiri). Kembalikan key-nya."""
        if key is None:
            self._n += 1
            key = str(self._n)
        self._options.append(Option(str(key), label, detail=tuple(detail)))
        return str(key)

    def letter(self, key: str, label: str, back: bool = False) -> str:
        """Tambah pintasan huruf, mis. ``letter("p", "Party")`` → ``[P]arty``."""
        self._options.append(Option(key.lower(), label, meta=True, back=back))
        return key.lower()

    def no_back(self, reason: Optional[str] = None) -> "Menu":
        """Menu tanpa "0) Kembali".

        ``reason`` wajib diisi kalau menu ini benar-benar tidak punya jalan keluar
        (aksi pertarungan, pilihan cerita); tes regresi memakainya untuk memisahkan
        pengecualian yang disengaja dari menu yang lupa diberi tombol keluar.
        """
        self.back = None
        self.required = reason
        return self

    def __len__(self) -> int:
        return len(self._options)

    def __bool__(self) -> bool:
        return bool(self._options)

    def build(self) -> list[Option]:
        opts = list(self._options)
        if self.back is not None:
            opts.append(Option(self.back_key, self.back, back=True))
        keys = [o.key.lower() for o in opts]
        assert len(keys) == len(set(keys)), f"key opsi bentrok: {keys}"
        return opts

    def ask(self, io, prompt: str = "> ", auto: Optional[str] = None) -> str:
        """Tampilkan menu dan kembalikan key yang dipilih."""
        return io.menu(self.build(), prompt, auto=auto, required=self.required)

    def pick(self, io, prompt: str = "> ", auto: Optional[str] = None) -> Optional[int]:
        """Seperti ``ask``, tapi untuk menu bernomor: kembalikan indeks (0-based) atau None."""
        s = self.ask(io, prompt, auto=auto)
        return int(s) - 1 if s.isdigit() and 1 <= int(s) <= self._n else None


def numbered(labels: Sequence[str], back: Optional[str] = "Kembali", back_key: str = "0",
             required: Optional[str] = None) -> Menu:
    """Menu sederhana dari daftar label."""
    m = Menu(back=back, back_key=back_key, required=required)
    for l in labels:
        m.add(l)
    return m


def exit_option(options: Sequence[Option]) -> Optional[Option]:
    """Opsi keluar dari sebuah menu, kalau ada. Dipakai tes regresi antarmuka."""
    return next((o for o in options if o.back), None)
