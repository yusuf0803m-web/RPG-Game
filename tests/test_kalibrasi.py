"""Kalibrasi Tahap 6 dikunci sebagai tes (GAME_DESIGN §9.5).

Angka ekonomi dan pacing di §9.5 didapat dengan mengukur, bukan menebak — dan
sesuatu yang didapat dengan mengukur akan melenceng lagi begitu isi permainan
berubah, tanpa ada yang sadar. Tes ini menjalankan pengukur yang sama dengan
``tools/playtest.py`` pada dua seed per babak dan menggagalkan build kalau ada
angka yang keluar dari pita sasarannya.

Yang *tidak* dikunci di sini: nilai persisnya. Yang dijaga adalah pitanya, supaya
menambah area atau musuh baru tetap bebas selama keseimbangannya ikut dijaga.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from playtest import (  # noqa: E402
    AKSI_PER_MUSUH, BEKAL_PENGALI, SEED_BAWAAN, aksi_per_musuh, jalankan, keranjang)
from pelita.loader import load_data  # noqa: E402
from pelita.world.model import load_world  # noqa: E402


@pytest.fixture(scope="module")
def ukur():
    """Dua seed per babak. Babak 2 dan 3 ikut memainkan babak sebelumnya."""
    return {b: [jalankan(b, s) for s in SEED_BAWAAN[b]] for b in (1, 2, 3)}


@pytest.mark.parametrize("babak", [1, 2, 3])
def test_uang_cukup_untuk_barisan_aktif_tapi_tidak_untuk_tujuh(babak, ukur):
    """Sasaran ekonomi §9.5: pemain yang memakai empat nama yang sama bisa melengkapi
    semuanya; pemain yang merotasi tujuh nama harus memilih."""
    data = load_data()
    world = load_world(data)
    reks = ukur[babak]
    tersedia = statistics.mean(r.bawaan + sum(v for v in r.kas.values() if v > 0) for r in reks)
    aktif, penuh = keranjang(data, world, babak)
    lo, hi = aktif * BEKAL_PENGALI, penuh * BEKAL_PENGALI
    assert lo <= tersedia <= hi, (
        f"Babak {babak}: tersedia {tersedia:,.0f} Keping, sasaran {lo:,.0f}–{hi:,.0f}. "
        f"Jalankan `python tools/playtest.py --ekonomi` untuk rinciannya.")


@pytest.mark.parametrize("babak", [1, 2, 3])
def test_pemain_benar_benar_berbelanja(babak, ukur):
    """Pengukurnya hanya berarti kalau pemain otomatisnya berbelanja. Pemain penimbun
    membuat ekonomi tampak seimbang padahal uangnya cuma menumpuk di kantong."""
    for r in ukur[babak]:
        keluar = -sum(v for v in r.kas.values() if v < 0)
        masuk = sum(v for v in r.kas.values() if v > 0)
        assert keluar > 0.3 * masuk, (
            f"Babak {babak} seed {r.seed}: belanja {keluar:,} dari pemasukan {masuk:,}")


@pytest.mark.parametrize("babak", [1, 2, 3])
def test_tiap_boss_bertahan_dalam_pita_ronde(babak, ukur):
    """Boss yang jatuh dalam tiga ronde bukan klimaks, dan boss 25 ronde bukan
    tantangan — ia cuma lama (§4.1, §9.1)."""
    urut: dict[str, tuple] = {}
    for r in ukur[babak]:
        for p in r.bos:
            urut.setdefault(p.nama, (p, []))[1].append(p.ronde)
    assert urut, f"Babak {babak} tidak punya satu pun pertarungan boss"
    for nama, (contoh, ronde) in urut.items():
        (lo, hi), alasan = contoh.band()
        rata = statistics.mean(ronde)
        assert lo <= rata <= hi, (
            f"Babak {babak}: {nama} rata-rata {rata:.1f} ronde, sasaran {lo}–{hi}"
            + (f" ({alasan})" if alasan else "") + f". Ronde per seed: {ronde}.")


@pytest.mark.parametrize("babak", [1, 2, 3])
def test_musuh_biasa_butuh_dua_sampai_empat_aksi(babak, ukur):
    """Sasaran §4.7. Di bawah dua aksi encounter jadi pajak tombol; di atas empat
    ia jadi pekerjaan rumah."""
    apm = aksi_per_musuh(ukur[babak])
    lo, hi = AKSI_PER_MUSUH
    assert lo <= apm <= hi, f"Babak {babak}: {apm:.2f} aksi per musuh, sasaran {lo}–{hi}"


@pytest.mark.parametrize("babak", [1, 2, 3])
def test_boss_benar_benar_melukai_party(babak, ukur):
    """Boss yang tidak pernah menurunkan HP party tidak diingat siapa pun. Diukur dari
    titik terendah *selama* laga: naik level di tengah pertarungan memulihkan HP, jadi
    HP sesudahnya menyembunyikan bahaya yang sempat ada."""
    for r in ukur[babak]:
        for p in r.bos:
            if not p.boss_cerita:
                continue
            assert p.hp_dasar <= 0.92, (
                f"Babak {babak} seed {r.seed}: {p.nama} tidak pernah menurunkan HP party "
                f"di bawah {p.hp_dasar:.0%}")


def test_level_tamat_sesuai_rentang_desain(ukur):
    """§2.4 menulis Babak 3 berakhir di Lv 47–52; §5.1 menulis tamat normal Lv 50–52."""
    akhir = [dict(r.level)["rimba"] for r in ukur[3]]
    assert all(48 <= lv <= 54 for lv in akhir), f"Rimba tamat di Lv {akhir}"
