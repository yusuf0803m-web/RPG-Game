"""Laporan playtest seluruh permainan: ekonomi Keping dan pacing pertarungan.

Alat kalibrasi Tahap 6 (GAME_DESIGN §9.5). Ia menjalankan walkthrough otomatis tiap
babak pada beberapa seed, lalu melaporkan dua hal yang selama ini hanya ditebak:

- **Ekonomi** — dari mana Keping datang dan ke mana perginya (buku kas
  ``GameState.kas``), saldo di akhir tiap babak, dan berapa saldo itu dibanding
  harga satu kali belanja penuh di toko babak tersebut.
- **Pacing** — lama tiap boss dalam ronde, dan berapa aksi party yang dihabiskan
  per musuh biasa yang tumbang (sasaran §4.7: 2–3 aksi).

Tiap angka yang keluar dari pita sasaran dicetak ulang di bagian PERINGATAN, jadi
kalibrasi berikutnya punya daftar kerja, bukan firasat.

    python tools/playtest.py                      seluruh permainan, seed bawaan
    python tools/playtest.py --babak 2            satu babak saja
    python tools/playtest.py --seeds 3 11 23      seed lain
    python tools/playtest.py --ekonomi            hanya tabel ekonomi
"""
from __future__ import annotations

import argparse
import random
import re
import statistics
import sys
import tempfile
from dataclasses import dataclass, field
from typing import ClassVar
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pelita.loader import load_data  # noqa: E402
from pelita.world.explore import Game  # noqa: E402
from pelita.world.model import load_world  # noqa: E402
from pelita.world.state import new_game  # noqa: E402
from tests.test_babak1 import SEMUA, BerhentiUji, make_equipper  # noqa: E402
from tests.test_babak2 import SEMUA_BABAK2, mulai_babak2  # noqa: E402
from tests.test_babak3 import ENDING_NYALA, SEMUA_BABAK3, make_pemain, mulai_babak3  # noqa: E402
from tests.walker import Walker  # noqa: E402

#: Pita sasaran, dipisah per jenis pertarungan. Tidak semua yang ditandai ``boss``
#: di skrip adalah boss cerita: gelombang Tujuh Penjaga Suar dan sergapan Gema
#: memakai tanda yang sama supaya tidak bisa dikabur i, padahal masing-masing memang
#: pendek. §9.1 mencatat "boss akhir 4–10 ronde" sebagai hasil yang dianggap benar;
#: §4.7 menyasar "2–3 aksi per musuh biasa kalau kelemahannya dipakai".
BOSS_RONDE = (4, 12)
GELOMBANG_RONDE = (2, 6)
AKSI_PER_MUSUH = (2.0, 4.0)
#: Bagian giliran boss cerita yang memakai aksi bernama (skill polanya), bukan Serang
#: biasa. Di bawah ini polanya praktis tidak pernah jalan — biasanya karena Goyah
#: permanen (§9.8). Pola terlemah yang sah (Hampa Penjaga Hutan: dua Serang dari empat)
#: memberi ±0,4 kalau tidak diganggu apa pun.
RASIO_POLA_MIN = 0.3
#: Pertarungan yang memang di luar pita umum, beserta alasannya.
BAND_KHUSUS = {
    "boss_pelita_pertama": ((12, 22), "final empat fase (§9.4)"),
}
#: Sasaran ekonomi Tahap 6. Uang yang tersedia sepanjang satu babak (saldo bawaan +
#: seluruh pemasukan babak itu) harus cukup untuk melengkapi **barisan aktif** —
#: empat orang, semua tingkat senjata babak itu, zirah terbaik, dua aksesori terbaik —
#: tapi tidak cukup untuk melengkapi **ketujuhnya**. Pemain yang memakai empat nama
#: yang sama bisa membeli semuanya; pemain yang merotasi tujuh nama harus memilih.
#: Pengalinya menyediakan ruang untuk bekal (ramuan, Abu Fajar, Bekal Kemah, Suku
#: Cadang), yang tidak ikut dihitung di keranjang.
BEKAL_PENGALI = 1.3

#: Toko yang sudah terbuka di tiap babak, dan berapa anggota party yang ada.
TOKO_BABAK = {
    1: ("warung_ratna", "pasar_apung", "pasar_bawah", "kafilah_tambang",
        "pedagang_keliling", "kios_sarwa"),
    2: ("pasar_sanggar", "penjaja_padasuara", "kios_darma"),
    3: ("pasar_kapal", "kios_laut"),
}
AKTIF = ("rimba", "sela", "lintang", "bagas")
PARTY_BABAK = {1: AKTIF, 2: AKTIF + ("rangga", "ratih", "kelana"), 3: AKTIF + ("rangga", "ratih", "kelana")}
SEED_BAWAAN = {1: (11, 23), 2: (5, 17), 3: (3, 19)}
AUTO_RE = re.compile(r"^ \S+ \(auto\): ")


@dataclass
class Pertarungan:
    musuh: list[str]
    boss: bool
    ronde: int = 0
    aksi: int = 0
    hasil: str = ""
    hp_dasar: float = 1.0       # HP party terendah selama pertarungan (titik paling genting)
    nama_boss: frozenset[str] = frozenset()   # nama tampilan boss cerita di laga ini
    aksi_bernama: int = 0       # giliran boss yang memakai skill (pola)
    aksi_serang: int = 0        # giliran boss yang jatuh ke Serang biasa

    @property
    def rasio_pola(self) -> float:
        total = self.aksi_bernama + self.aksi_serang
        return self.aksi_bernama / total if total else float("nan")

    @property
    def nama(self) -> str:
        return " + ".join(sorted(set(self.musuh)))

    #: Musuh yang juga muncul di tabel encounter acak. Diisi sekali dari data dunia.
    biasa_ids: ClassVar[frozenset[str]] = frozenset()

    @property
    def boss_cerita(self) -> bool:
        """Boss cerita = musuh ber-id ``boss_``; sisanya gelombang/elit terskrip."""
        return self.boss and any(m.startswith("boss_") for m in self.musuh)

    @property
    def sergapan(self) -> bool:
        """Pertarungan terskrip yang isinya musuh biasa belaka.

        Ditandai ``boss`` di skrip supaya tidak bisa dikabur i, tapi ia bukan boss:
        menilainya dengan pita ronde akan menyuruh kita menggemukkan musuh biasa
        sampai keluar dari sasaran §4.7. Ia dihitung bersama pertarungan biasa.
        """
        return self.boss and not self.boss_cerita and all(m in self.biasa_ids for m in self.musuh)

    def band(self) -> tuple[tuple[int, int], str]:
        for m in self.musuh:
            if m in BAND_KHUSUS:
                return BAND_KHUSUS[m]
        return (BOSS_RONDE if self.boss_cerita else GELOMBANG_RONDE), ""


@dataclass
class Rekaman:
    """Satu jalannya walkthrough: daftar pertarungan, buku kas, dan level akhir."""
    babak: int
    seed: int
    pertarungan: list[Pertarungan] = field(default_factory=list)
    kas: dict[str, int] = field(default_factory=dict)   # selisih selama babak ini saja
    bawaan: int = 0                                     # saldo saat babak ini dimulai
    saldo: int = 0
    level: list[tuple[str, int]] = field(default_factory=list)
    hasil: str = ""

    @property
    def biasa(self) -> list[Pertarungan]:
        return [p for p in self.pertarungan if not p.boss or p.sergapan]

    @property
    def bos(self) -> list[Pertarungan]:
        return [p for p in self.pertarungan if p.boss and not p.sergapan]


class GameTerekam(Game):
    """``Game`` yang mencatat tiap pertarungan; tidak mengubah jalannya permainan."""

    def __init__(self, *args, rekaman: Rekaman, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rekaman = rekaman
        self.sekarang: Pertarungan | None = None

    def do_battle(self, enemy_ids, boss, can_flee, *args, **kwargs):
        self.sekarang = Pertarungan(list(enemy_ids), boss)
        self.sekarang.nama_boss = frozenset(
            self.data.enemies[m].name for m in enemy_ids if m.startswith("boss_"))
        self.rekaman.pertarungan.append(self.sekarang)
        try:
            hasil = super().do_battle(enemy_ids, boss, can_flee, *args, **kwargs)
        finally:
            self.sekarang = None
        self.rekaman.pertarungan[-1].hasil = hasil
        return hasil


def pasang_perekam(game: GameTerekam, wk: Walker) -> None:
    """Rekam ronde (lewat event ``battle_end``), aksi party (lewat baris "(auto):"), dan
    apakah boss cerita memainkan polanya atau jatuh ke Serang biasa."""
    tulis_asli = wk.io.write

    def tulis(s: str) -> None:
        p = game.sekarang
        if p is not None:
            if AUTO_RE.match(s):
                p.aksi += 1
            for baris in s.splitlines():
                baris = baris.strip()
                for nama in p.nama_boss:
                    if baris.startswith(f"{nama} memakai "):
                        p.aksi_bernama += 1
                    elif baris.startswith(f"{nama} menyerang "):
                        p.aksi_serang += 1
        tulis_asli(s)

    def emit(kind: str, payload: dict) -> None:
        if game.sekarang is None:
            return
        if kind == "battle_end":
            game.sekarang.ronde = int(payload.get("rounds", 0))
        elif kind == "battle":
            # Diemit tiap kali musuh selesai bertindak — persis saat damage mendarat.
            # HP *sesudah* pertarungan menyesatkan: naik level di tengah laga memulihkan
            # HP dan menaikkan HP maks, jadi party sering tampak pulang tanpa lecet.
            pasukan = [h for h in payload.get("heroes", []) if h.get("max_hp")]
            if pasukan:
                rata = statistics.mean(h["hp"] / h["max_hp"] for h in pasukan)
                game.sekarang.hp_dasar = min(game.sekarang.hp_dasar, rata)

    wk.io.write = tulis
    wk.io.emit = emit


def musuh_biasa(world) -> frozenset[str]:
    """Id musuh yang muncul di tabel encounter acak mana pun."""
    keluar: set[str] = set()
    for a in world.areas.values():
        for enc in a.encounters:
            keluar.update(enc.enemies)
        for r in a.rooms.values():
            for enc in (r.encounters or []):
                keluar.update(enc.enemies)
    return frozenset(keluar)


def jalankan(babak: int, seed: int) -> Rekaman:
    data = load_data()
    world = load_world(data)
    Pertarungan.biasa_ids = musuh_biasa(world)
    rek = Rekaman(babak=babak, seed=seed)
    if babak == 1:
        st = new_game(data)
        st.rng = random.Random(seed)
        steps, perintah = SEMUA, make_equipper(st)
        kotak: list = []
    elif babak == 2:
        st = mulai_babak2(data, seed)
        steps, perintah = SEMUA_BABAK2, make_equipper(st)
        kotak = []
    else:
        st = mulai_babak3(data, seed, lengkap=True)
        kotak = []
        steps, perintah = SEMUA_BABAK3 + ENDING_NYALA, make_pemain(st, kotak)
    # Serah-terima antarbabak dijalankan sungguhan (lihat ``mulai_babak2``), jadi buku
    # kasnya sudah memuat babak-babak sebelumnya. Yang dilaporkan selisihnya.
    kas_awal = dict(st.kas)
    rek.bawaan = st.keping
    wk = Walker(steps, on_command=perintah)
    g = GameTerekam(data, world, st, wk.io, auto_battle=True, auto_script=True,
                    auto_choice=False, save_dir=Path(tempfile.mkdtemp()), rekaman=rek)
    kotak.append(g)
    pasang_perekam(g, wk)
    try:
        rek.hasil = g.run()
    except BerhentiUji:
        rek.hasil = "berhenti"
    rek.kas = {k: v - kas_awal.get(k, 0) for k, v in st.kas.items() if v != kas_awal.get(k, 0)}
    rek.saldo = st.keping
    rek.level = [(h.id, h.level) for h in st.party]
    return rek


# -- perhitungan ------------------------------------------------------------
def keranjang(data, world, babak: int) -> tuple[int, int]:
    """(harga melengkapi 4 aktif, harga melengkapi seluruh party) di toko babak ini.

    Satu keranjang per orang = semua tingkat senjata yang dijual untuk karakter itu
    (pemain memang naik tingkat satu per satu), zirah termahal, dan dua aksesori
    termahal. Batas atas ikut menghitung seluruh Kaca yang dijual babak itu, karena
    Kaca adalah tempat uang lebih mengalir begitu perlengkapan sudah lengkap.
    """
    senjata: dict[str, int] = {}
    zirah: list[int] = []
    aksesori: list[int] = []
    kaca: dict[str, int] = {}
    for sid in TOKO_BABAK[babak]:
        for iid in world.shops[sid]["items"]:
            it = data.items[iid]
            if it.kind == "senjata" and it.weapon_for:
                senjata[it.weapon_for] = senjata.get(it.weapon_for, 0) + it.price
            elif it.kind == "zirah":
                zirah.append(it.price)
            elif it.kind == "aksesori":
                aksesori.append(it.price)
        for kid in world.shops[sid].get("kaca", []):
            kaca[kid] = data.kaca[kid].price
    per_orang = (max(zirah, default=0)) + sum(sorted(aksesori)[-2:])

    def total(anggota) -> int:
        return sum(senjata.get(cid, 0) for cid in anggota) + per_orang * len(anggota)

    return total(AKTIF), total(PARTY_BABAK[babak]) + sum(kaca.values())


def aksi_per_musuh(reks: list[Rekaman]) -> float:
    aksi = sum(p.aksi for r in reks for p in r.biasa)
    musuh = sum(len(p.musuh) for r in reks for p in r.biasa)
    return aksi / musuh if musuh else float("nan")


def rasio_pola(laga: list[Pertarungan]) -> float:
    """Rasio aksi bernama boss, dijumlah dulu dari beberapa laga (bukan rata-rata rasio)."""
    bernama = sum(p.aksi_bernama for p in laga)
    total = bernama + sum(p.aksi_serang for p in laga)
    return bernama / total if total else float("nan")


def rupiah(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# -- laporan ----------------------------------------------------------------
def lapor_ekonomi(data, world, per_babak: dict[int, list[Rekaman]], peringatan: list[str]) -> None:
    print()
    print("═══ EKONOMI KEPING ═══")
    print(f"{'babak':<6}{'bawaan':>10}{'masuk':>10}{'keluar':>10}{'tersedia':>10}"
          f"{'4 aktif':>10}{'party':>10}   sasaran")
    for babak, reks in sorted(per_babak.items()):
        keluar = statistics.mean(sum(v for v in r.kas.values() if v < 0) for r in reks)
        bawaan = statistics.mean(r.bawaan for r in reks)
        total_masuk = statistics.mean(sum(v for v in r.kas.values() if v > 0) for r in reks)
        tersedia = bawaan + total_masuk
        aktif, penuh = keranjang(data, world, babak)
        lo, hi = aktif * BEKAL_PENGALI, penuh * BEKAL_PENGALI
        luar = not (lo <= tersedia <= hi)
        print(f"{babak:<6}{rupiah(int(bawaan)):>10}{rupiah(int(total_masuk)):>10}"
              f"{rupiah(int(keluar)):>10}{rupiah(int(tersedia)):>10}"
              f"{rupiah(aktif):>10}{rupiah(penuh):>10}   "
              f"{rupiah(int(lo))}–{rupiah(int(hi))}" + ("  <-" if luar else ""))
        if luar:
            arah = "menumpuk" if tersedia > hi else "terlalu sedikit"
            peringatan.append(
                f"Babak {babak}: uang {arah} — tersedia {rupiah(int(tersedia))} Keping, "
                f"sasaran {rupiah(int(lo))}–{rupiah(int(hi))} "
                f"(cukup untuk 4 aktif, tidak cukup untuk tujuh)")
    print("  tersedia = saldo bawaan + seluruh pemasukan babak ini.")
    print("  4 aktif / party = harga melengkapi senjata, zirah, dan dua aksesori di toko babak itu.")
    print(f"  sasaran = keranjang itu dikali {BEKAL_PENGALI} (ruang untuk bekal).")


def lapor_pacing(per_babak: dict[int, list[Rekaman]], peringatan: list[str]) -> None:
    print()
    print("═══ PACING BOSS ═══")
    for babak, reks in sorted(per_babak.items()):
        urut: dict[str, tuple[Pertarungan, list[int], list[float], list[Pertarungan]]] = {}
        for r in reks:
            for p in r.bos:
                baris = urut.setdefault(p.nama, (p, [], [], []))
                baris[1].append(p.ronde)
                baris[2].append(p.hp_dasar)
                baris[3].append(p)
        for nama, (contoh, ronde, hp, laga) in urut.items():
            (lo, hi), alasan = contoh.band()
            rata = statistics.mean(ronde)
            luar = not (lo <= rata <= hi)
            jenis = "boss " if contoh.boss_cerita else "gelombang"
            print(f"  B{babak} {jenis} {nama[:38]:<38} {str(ronde):<11} rata {rata:>4.1f}"
                  f"  [{lo}-{hi}]  HP terendah {statistics.mean(hp):>4.0%}"
                  + (f"  pola {rasio_pola(laga):.2f}" if contoh.boss_cerita else "")
                  + ("  <-" if luar else ""))
            if contoh.boss_cerita and rasio_pola(laga) < RASIO_POLA_MIN:
                peringatan.append(
                    f"Babak {babak}: {nama} hampir tidak memainkan polanya (rasio aksi "
                    f"bernama {rasio_pola(laga):.2f}; sasaran >= {RASIO_POLA_MIN}). "
                    f"Cek Goyah permanen, §9.8.")
            if luar:
                arah = "terlalu cepat" if rata < lo else "terlalu lama"
                peringatan.append(
                    f"Babak {babak}: {nama} {arah} ({rata:.1f} ronde; sasaran {lo}–{hi}"
                    + (f", {alasan}" if alasan else "") + ")")

    print()
    print("═══ PERTARUNGAN BIASA ═══")
    print(f"{'babak':<6}{'jumlah':>8}{'ronde':>8}{'aksi':>8}{'aksi/musuh':>12}{'HP terendah':>12}")
    for babak, reks in sorted(per_babak.items()):
        biasa = [p for r in reks for p in r.biasa]
        if not biasa:
            continue
        apm = aksi_per_musuh(reks)
        luar = not (AKSI_PER_MUSUH[0] <= apm <= AKSI_PER_MUSUH[1])
        print(f"{babak:<6}{len(biasa) // len(reks):>8}{statistics.mean(p.ronde for p in biasa):>8.1f}"
              f"{statistics.mean(p.aksi for p in biasa):>8.1f}{apm:>12.2f}"
              f"{statistics.mean(p.hp_dasar for p in biasa):>12.0%}" + ("  <-" if luar else ""))
        if luar:
            arah = "jatuh terlalu cepat" if apm < AKSI_PER_MUSUH[0] else "terlalu tahan banting"
            peringatan.append(
                f"Babak {babak}: musuh biasa {arah} ({apm:.2f} aksi per musuh; "
                f"sasaran {AKSI_PER_MUSUH[0]}–{AKSI_PER_MUSUH[1]})")


def lapor_level(per_babak: dict[int, list[Rekaman]]) -> None:
    print()
    print("═══ KURVA LEVEL ═══")
    for babak, reks in sorted(per_babak.items()):
        akhir = [dict(r.level).get("rimba", 0) for r in reks]
        print(f"  Babak {babak}: Rimba tamat di Lv {min(akhir)}–{max(akhir)}"
              f"   ({len(reks[0].pertarungan)} pertarungan)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--babak", type=int, action="append", choices=(1, 2, 3),
                    help="babak yang diukur (boleh diulang; bawaan: semua)")
    ap.add_argument("--seeds", type=int, nargs="+", help="seed yang dipakai untuk tiap babak")
    ap.add_argument("--ekonomi", action="store_true", help="hanya tabel ekonomi")
    ap.add_argument("--pacing", action="store_true", help="hanya tabel pacing")
    args = ap.parse_args(argv)

    data = load_data()
    world = load_world(data)
    babak_list = sorted(set(args.babak or (1, 2, 3)))
    per_babak: dict[int, list[Rekaman]] = {}
    for babak in babak_list:
        seeds = args.seeds or SEED_BAWAAN[babak]
        per_babak[babak] = []
        for seed in seeds:
            print(f"… babak {babak} seed {seed}", file=sys.stderr)
            per_babak[babak].append(jalankan(babak, seed))

    gagal = [r for reks in per_babak.values() for r in reks if r.hasil not in ("berhenti", "chapter_end")]
    peringatan: list[str] = [f"Babak {r.babak} seed {r.seed} tidak tamat: {r.hasil}" for r in gagal]

    semua = not (args.ekonomi or args.pacing)
    if semua or args.ekonomi:
        lapor_ekonomi(data, world, per_babak, peringatan)
    if semua or args.pacing:
        lapor_pacing(per_babak, peringatan)
    if semua:
        lapor_level(per_babak)

    print()
    if peringatan:
        print("═══ PERINGATAN ═══")
        for p in peringatan:
            print(f"  ! {p}")
    else:
        print("Semua angka di dalam pita sasaran.")
    return 1 if peringatan else 0


if __name__ == "__main__":
    sys.exit(main())
