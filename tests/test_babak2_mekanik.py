"""Mekanik baru Babak 2: Lagu Ratih, Panji Rangga, Tanggung Kelana, sifat musuh."""
import random

import pytest

from pelita.combat.engine import Action, Battle
from pelita.loader import load_data
from pelita.party import Hero


@pytest.fixture(scope="module")
def data():
    return load_data()


def battle(data, ids, enemies=("kunang_kelam",), level=35, **kw):
    heroes = [Hero.create(data, cid, level) for cid in ids]
    return Battle(data, heroes, list(enemies), rng=random.Random(4), **kw)


def pakai(b, aktor, sid, target=None):
    sk = next(s for s in aktor.skills if s.id == sid)
    ts = target if target is not None else b.valid_targets(aktor, sk.target)
    return b.act(aktor, Action("skill", skill=sk, targets=ts))


def test_lagu_rawat_memulihkan_tiap_giliran(data):
    b = battle(data, ["ratih", "sela"])
    ratih, sela = b.heroes
    sela.hp = sela.max_hp // 2
    pakai(b, ratih, "t_lagu_rawat")
    assert sela.has("lagu_rawat")
    sebelum = sela.hp
    ev = []
    sela.turn_count += 1                       # regen menetes di akhir giliran pemiliknya
    b._end_turn(sela, ev)
    assert sela.hp > sebelum
    assert any("pulih" in e for e in ev)


def test_hanya_satu_lagu_yang_aktif(data):
    b = battle(data, ["ratih", "sela"])
    ratih, sela = b.heroes
    pakai(b, ratih, "t_lagu_rawat")
    pakai(b, ratih, "t_lagu_gugah")
    assert sela.has("lagu_gugah") and not sela.has("lagu_rawat")


def test_lagu_gugah_menaikkan_atk_dan_bara(data):
    # Bara membeku kalau Rimba tidak di barisan, jadi ia harus ikut.
    b = battle(data, ["rimba", "ratih", "sela"], bara_max=5)
    _, ratih, sela = b.heroes
    atk = sela.effective("atk")
    pakai(b, ratih, "t_lagu_gugah")
    assert sela.effective("atk") > atk
    assert b.bara >= 1


def test_panji_memulihkan_dan_menarik_serangan(data):
    b = battle(data, ["rangga", "lintang"])
    rangga, lintang = b.heroes
    lintang.hp = lintang.max_hp // 2
    pakai(b, rangga, "r_panji_larung")
    assert lintang.has("panji") and rangga.taunting
    sebelum = lintang.hp
    lintang.turn_count += 1
    b._end_turn(lintang, [])
    assert lintang.hp > sebelum


def test_tanggung_mengalihkan_damage_ke_kelana(data):
    # Musuh yang pukulannya cukup besar; pembagian 70/30 tidak terlihat pada damage 1.
    b = battle(data, ["kelana", "lintang"], enemies=["boss_penambang_raksasa"], level=40)
    kelana, lintang = b.heroes
    pakai(b, kelana, "k_tanggung", target=[lintang])
    assert lintang.has("tanggung")
    hp_kelana, hp_lintang = kelana.hp, lintang.hp
    musuh = b.enemies[0]
    b.act(musuh, Action("serang", targets=[lintang]))
    assert kelana.hp < hp_kelana, "Kelana harus ikut menanggung"
    assert lintang.hp < hp_lintang


def test_badai_bulu_lebih_sakit_untuk_yang_terbang(data):
    """Bonus sifat 'terbang' dipakai skill Ratih; tanpa sifat itu damage-nya biasa."""
    from pelita.models import Element, SkillKind

    terbang = [e for e in data.enemies.values() if "terbang" in e.traits]
    assert terbang, "belum ada musuh bersifat terbang"
    b = battle(data, ["ratih"], enemies=[terbang[0].id])
    assert "terbang" in b.enemies[0].traits


def test_perintah_terakhir_memberi_giliran_tambahan(data):
    b = battle(data, ["rangga", "sela"], level=41)
    rangga, sela = b.heroes
    b._new_round()
    panjang = len(b.queue)
    pakai(b, rangga, "r_perintah_terakhir", target=[sela])
    assert len(b.queue) == panjang + 1 and b.queue[0] is sela


def test_kelana_membayar_dengan_hp(data):
    b = battle(data, ["kelana"], level=40)
    kelana = b.heroes[0]
    hp = kelana.hp
    pakai(b, kelana, "k_tebas_karat")
    assert kelana.hp < hp, "Tebas Karat berbiaya HP, bukan MP"


def test_diam_memulihkan_dan_menyiapkan_pukulan(data):
    b = battle(data, ["kelana"], level=44)
    kelana = b.heroes[0]
    kelana.hp = kelana.max_hp // 2
    atk = kelana.effective("atk")
    pakai(b, kelana, "k_diam")
    assert kelana.hp > kelana.max_hp // 2 and kelana.has("siap_tebas")
    assert kelana.effective("atk") > atk
