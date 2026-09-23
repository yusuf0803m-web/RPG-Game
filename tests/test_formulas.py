from pelita.combat import formulas as F
from pelita.models import Affinity


def test_dasar_minimum_satu():
    assert F.dasar(1, 100) == 1
    assert F.dasar(14, 6) == 22          # contoh kalibrasi GAME_DESIGN §4.6 (Rimba Lv5 vs Serigala)


def test_damage_contoh_desain():
    # dasar 22 × Sulut 1.4 × lemah 1.5 = 46.2 → 46
    assert F.hitung_damage(13, 4, 1.4, 1.5, acak=1.0) == 46


def test_afinitas_serap_negatif_dan_imun_nol():
    assert F.hitung_damage(20, 5, 1.0, F.pengali_afinitas(Affinity.SERAP), acak=1.0) < 0
    assert F.hitung_damage(20, 5, 1.0, F.pengali_afinitas(Affinity.IMUN), acak=1.0) == 0


def test_ignore_resist_dan_absorb():
    assert F.pengali_afinitas(Affinity.TAHAN, ignore_resist=True) == 1.0
    assert F.pengali_afinitas(Affinity.SERAP, ignore_absorb=True) == 1.0
    assert F.pengali_afinitas(Affinity.TAHAN) == 0.5


def test_kritikal_dan_pecah():
    base = F.hitung_damage(20, 5, 1.0, 1.0, acak=1.0)
    assert F.hitung_damage(20, 5, 1.0, 1.0, kritikal=True, acak=1.0) == int(base * 1.5)
    assert F.hitung_damage(20, 5, 1.0, 1.0, pecah=True, acak=1.0) == int(base * 1.5)
    assert F.hitung_damage(20, 5, 1.0, 1.0, goyah=True, acak=1.0) == int(base * 1.2)
    # Pecah menang atas Goyah, tidak menumpuk
    assert F.hitung_damage(20, 5, 1.0, 1.0, pecah=True, goyah=True, acak=1.0) == int(base * 1.5)


def test_peluang_kena_batas():
    assert F.peluang_kena(10, 10) == 0.92
    assert F.peluang_kena(50, 0) == 1.0
    assert F.peluang_kena(0, 50) == 0.60
    assert F.peluang_kena(10, 10, buta=True) == 0.60


def test_peluang_kritikal_batas():
    assert F.peluang_kritikal(0) == 0.05
    assert F.peluang_kritikal(100) == 0.35


def test_peluang_kabur_batas():
    assert F.peluang_kabur(10, 10) == 0.5
    assert F.peluang_kabur(100, 0) == 0.9
    assert F.peluang_kabur(0, 100) == 0.2


def test_peluang_status_lck():
    assert F.peluang_status(0.5, 0) == 0.5
    assert abs(F.peluang_status(0.5, 10) - 0.45) < 1e-9
