"""Tokoh bergambar: registri + pencari aset potret (GAME_DESIGN §7.3).

Sama seperti latar (§7.2), server yang memutuskan berkas mana yang benar-benar ada
supaya klien tidak menembak URL yang berakhir 404. Tokoh yang tidak terdaftar, atau
yang belum punya gambar, tetap tampil sebagai dialog biasa.

Urutan pencarian untuk satu baris ``say``:

1. tokoh = ``tokoh`` eksplisit dari skrip kalau terdaftar, kalau tidak dari alias
   teks ``say`` ("Rimba" → ``rimba``). Tidak ketemu → tanpa visual.
2. ekspresi = ``ekspresi`` dari skrip kalau ada di kosakata, kalau tidak ekspresi
   bawaan tokoh.
3. berkas ``characters/<id>/<ekspresi>.webp`` lalu ``.png``; tidak ada → berkas
   ekspresi bawaan; tidak ada juga → tanpa visual.

Panggung (bust-up di atas latar) hanya memakai berkas yang punya kanal alpha. Gambar
yang latarnya masih buram tetap dipakai untuk face graphic di log, tapi panggungnya
jatuh ke ekspresi bawaan supaya tidak muncul kotak berlatar di atas pemandangan.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ASET_TOKOH = Path(__file__).parent / "static" / "assets" / "characters"
URL_TOKOH = "/static/assets/characters"
REGISTRI = Path(__file__).parent.parent / "data" / "tokoh.json"
EKSTENSI = (".webp", ".png")
KANVAS = (720, 960)             # kanvas acuan koordinat crop wajah


def punya_alpha(berkas: Path) -> bool:
    """Baca header PNG/WebP saja; tidak butuh pustaka gambar."""
    try:
        with berkas.open("rb") as f:
            kepala = f.read(64)
    except OSError:
        return False
    if kepala[:8] == b"\x89PNG\r\n\x1a\n":
        if len(kepala) > 25 and kepala[25] in (4, 6):      # grey+alpha, RGBA
            return True
        try:
            return b"tRNS" in berkas.read_bytes()[:65536]
        except OSError:
            return False
    if kepala[:4] == b"RIFF" and kepala[8:12] == b"WEBP":
        jenis = kepala[12:16]
        if jenis == b"VP8X":
            return bool(kepala[20] & 0x10)
        if jenis == b"VP8L" and len(kepala) >= 25:
            bits = int.from_bytes(kepala[21:25], "little")
            return bool((bits >> 28) & 1)
    return False


@dataclass
class Tokoh:
    id: str
    nama: str
    sisi: str
    ekspresi_bawaan: str
    wajah: list
    wajah_ekspresi: dict = field(default_factory=dict)


class DaftarTokoh:
    """Registri tokoh dan pencari berkasnya. Hasil pencarian berkas di-cache."""

    def __init__(self, registri: dict, aset: Path = ASET_TOKOH, url: str = URL_TOKOH) -> None:
        self.aset = aset
        self.url = url
        self.kosakata = list(registri.get("ekspresi", ["neutral"]))
        bawaan = list(registri.get("wajah_bawaan", [216, 120, 288]))
        self.tokoh: dict[str, Tokoh] = {}
        self.alias: dict[str, str] = {}
        for tid, t in registri.get("tokoh", {}).items():
            eks = t.get("ekspresi", {}) or {}
            self.tokoh[tid] = Tokoh(
                id=tid, nama=t.get("nama", tid), sisi=t.get("sisi", "kanan"),
                ekspresi_bawaan=t.get("ekspresi_bawaan", self.kosakata[0]),
                wajah=list(t.get("wajah", bawaan)),
                wajah_ekspresi={k: list(v["wajah"]) for k, v in eks.items() if isinstance(v, dict) and "wajah" in v},
            )
            for nama in [t.get("nama", tid)] + list(t.get("alias", [])):
                self.alias.setdefault(nama.casefold(), tid)
        self._berkas: dict[tuple[str, str], Optional[tuple[str, bool]]] = {}

    @classmethod
    def muat(cls, path: Path = REGISTRI, **kw) -> "DaftarTokoh":
        try:
            return cls(json.loads(path.read_text(encoding="utf-8")), **kw)
        except (OSError, ValueError):
            return cls({}, **kw)          # registri rusak/hilang: semua dialog tampil biasa

    def cari_id(self, who: str, tokoh: Optional[str] = None) -> Optional[str]:
        if tokoh and tokoh in self.tokoh:
            return tokoh
        return self.alias.get((who or "").casefold())

    def _cari_berkas(self, tid: str, eks: str) -> Optional[tuple[str, bool]]:
        """(url, punya_alpha) untuk berkas yang ada, atau None."""
        kunci = (tid, eks)
        if kunci not in self._berkas:
            hasil = None
            akar = self.aset.resolve()
            for ext in EKSTENSI:
                b = self.aset / tid / f"{eks}{ext}"
                try:
                    if b.is_file() and akar in b.resolve().parents:
                        hasil = (f"{self.url}/{tid}/{eks}{ext}", punya_alpha(b))
                        break
                except OSError:
                    continue
            self._berkas[kunci] = hasil
        return self._berkas[kunci]

    def visual(self, who: str, tokoh: Optional[str] = None, ekspresi: Optional[str] = None) -> Optional[dict]:
        """Data visual untuk satu baris dialog, atau None kalau tokohnya tidak dikenal."""
        tid = self.cari_id(who, tokoh)
        if tid is None:
            return None
        t = self.tokoh[tid]
        diminta = ekspresi if ekspresi in self.kosakata else t.ekspresi_bawaan
        eks, berkas = diminta, self._cari_berkas(tid, diminta)
        if berkas is None and diminta != t.ekspresi_bawaan:
            eks, berkas = t.ekspresi_bawaan, self._cari_berkas(tid, t.ekspresi_bawaan)
        out = {"tokoh": tid, "nama": t.nama, "ekspresi": eks, "sisi": t.sisi,
               "potret_url": "", "panggung_url": "", "wajah": None}
        if berkas is None:
            return out
        out["potret_url"] = berkas[0]
        out["wajah"] = self.css_wajah(t.wajah_ekspresi.get(eks, t.wajah))
        if berkas[1]:
            out["panggung_url"] = berkas[0]
        else:
            cadangan = self._cari_berkas(tid, t.ekspresi_bawaan)
            if cadangan and cadangan[1]:
                out["panggung_url"] = cadangan[0]
        return out

    @staticmethod
    def css_wajah(kotak: list) -> dict:
        """Kotak crop [x, y, sisi] di kanvas 720x960 → nilai background-size/-position (%).

        Persen, bukan piksel: gambar 1086x1448 dan 720x960 memakai angka yang sama,
        dan face graphic boleh tampil di ukuran berapa pun.
        """
        w, h = KANVAS
        x, y, s = (float(v) for v in kotak)
        s = max(1.0, min(s, w, h))
        return {"ukuran": round(w / s * 100, 3),
                "x": round(x / (w - s) * 100, 3) if w > s else 50.0,
                "y": round(y / (h - s) * 100, 3) if h > s else 50.0}


_bawaan: Optional[DaftarTokoh] = None


def daftar_tokoh() -> DaftarTokoh:
    global _bawaan
    if _bawaan is None:
        _bawaan = DaftarTokoh.muat()
    return _bawaan
