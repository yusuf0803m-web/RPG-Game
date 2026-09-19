"""Mekanik baru Babak 3 (GAME_DESIGN §4.5, §6.1-§6.3, §2.4).

Satu tes per aturan, supaya kalau salah satunya rusak ketahuan aturan mana yang
rusak — bukan cuma "walkthrough-nya gagal".
"""
import random

import pytest

from pelita.combat.engine import Action, Battle
from pelita.loader import load_data
from pelita.models import Affinity, Element
from pelita.party import Hero


@pytest.fixture(scope="module")
def data():
    return load_data()


def battle(data, ids, enemies=("gema_pesta",), level=50, seed=4, **kw):
    heroes = [Hero.create(data, cid, level) for cid in ids]
    return Battle(data, heroes, list(enemies), rng=random.Random(seed), **kw)


def pakai(b, aktor, sid, target=None):
    sk = next(s for s in aktor.skills if s.id == sid)
    ts = target if target is not None else b.valid_targets(aktor, sk.target)
    return b.act(aktor, Action("skill", skill=sk, targets=ts))


def pakai_bara(b, aktor, sid, target=None):
    """Jurus Bara tidak ada di ``aktor.skills``; ia milik party (lihat Battle.bara_skills)."""
    sk = next(s for s in b.bara_skills if s.id == sid)
    ts = target if target is not None else b.valid_targets(aktor, sk.target)
    return b.act(aktor, Action("skill", skill=sk, targets=ts))


def musuh_pakai(b, aktor, sid, target=None):
    sk = b.data.skill(sid)
    ts = target if target is not None else b.valid_targets(aktor, sk.target)
    return b.act(aktor, Action("skill", skill=sk, targets=ts))


# -- Jurus Empat ------------------------------------------------------------
EMPAT = ["rimba", "sela", "lintang", "bagas"]


def test_jurus_empat_butuh_bara_maks_delapan(data):
    b = battle(data, EMPAT, bara_max=5, bara_start=5)
    assert not [s for s in b.usable_bara_skills(b.heroes[0]) if "jurus_empat" in s.tags]
    b = battle(data, EMPAT, bara_max=8, bara_start=8)
    assert [s for s in b.usable_bara_skills(b.heroes[0]) if "jurus_empat" in s.tags]


def test_jurus_empat_butuh_empat_orang_hidup(data):
    b = battle(data, EMPAT, bara_max=8, bara_start=8)
    b.heroes[2].hp = 0
    assert not [s for s in b.usable_bara_skills(b.heroes[0]) if "jurus_empat" in s.tags]


def test_jurus_empat_boleh_dipakai_siapa_saja_di_barisan(data):
    """Tidak seperti Jurus Ganda, Jurus Empat tidak punya daftar ``users``."""
    b = battle(data, EMPAT, bara_max=8, bara_start=8)
    for h in b.heroes:
        assert [s for s in b.usable_bara_skills(h) if "jurus_empat" in s.tags], h.key


def test_jurus_empat_memukul_tiap_musuh_dengan_kelemahannya_sendiri(data):
    # Gema Prajurit lemah Kelam; Pelita Padam Kuno juga lemah Kelam tapi menyerap Cahaya.
    b = battle(data, EMPAT, enemies=("gema_prajurit", "pelita_padam_kuno"),
               bara_max=8, bara_start=8)
    prajurit, padam = b.enemies
    ev = pakai_bara(b, b.heroes[0], "jurus_pelita_terakhir")
    assert "JURUS EMPAT!" in "\n".join(ev)
    assert b.bestiary.get(prajurit.key).get(Element.KELAM) == Affinity.LEMAH
    assert b.bestiary.get(padam.key).get(Element.KELAM) == Affinity.LEMAH
    # Elemennya mengikuti kelemahan, jadi tidak ada yang menyerap apa pun.
    assert "MENYERAP" not in "\n".join(ev)


def test_jurus_empat_sekali_per_pertarungan_untuk_seluruh_party(data):
    b = battle(data, EMPAT, bara_max=8, bara_start=8)
    pakai_bara(b, b.heroes[0], "jurus_pelita_terakhir")
    b.bara = 8
    for h in b.heroes:
        assert not [s for s in b.usable_bara_skills(h) if "jurus_empat" in s.tags], h.key


# -- Gema Prajurit: formasi -------------------------------------------------
def test_formasi_menggandakan_def_selama_dua_masih_berdiri(data):
    b = battle(data, ["sela"], enemies=("gema_prajurit", "gema_prajurit"))
    a, c = b.enemies
    ev = b.act(b.heroes[0], Action("serang", targets=[a]))
    dua = int([e for e in ev if "damage" in e][0].split("terkena ")[1].split(" ")[0])
    c.hp = 0                                    # tinggal satu: formasinya bubar
    a.hp = a.max_hp
    ev = b.act(b.heroes[0], Action("serang", targets=[a]))
    satu = int([e for e in ev if "damage" in e][0].split("terkena ")[1].split(" ")[0])
    assert satu > dua, (satu, dua)


# -- Gema Guntur: Nyala Penjaga --------------------------------------------
def test_nyala_penjaga_memulihkan_kalau_bara_ditabung(data):
    b = battle(data, ["rimba"], enemies=("boss_gema_guntur",), bara_max=8, bara_start=5)
    guntur = b.enemies[0]
    guntur.hp = guntur.max_hp // 2
    ev = musuh_pakai(b, guntur, "m_guntur_penjaga")
    assert guntur.hp == guntur.max_hp
    assert any("meminum Bara" in e for e in ev)


def test_nyala_penjaga_gagal_kalau_bara_sudah_dibelanjakan(data):
    b = battle(data, ["rimba"], enemies=("boss_gema_guntur",), bara_max=8, bara_start=2)
    guntur = b.enemies[0]
    guntur.hp = guntur.max_hp // 2
    musuh_pakai(b, guntur, "m_guntur_penjaga")
    assert guntur.hp == guntur.max_hp // 2


# -- Sang Pelita Pertama fase 3 --------------------------------------------
def test_fase_hanya_jurus_membuat_serangan_biasa_tidak_melukai(data):
    b = battle(data, EMPAT, enemies=("boss_pelita_pertama",), bara_max=8, bara_start=8)
    boss = b.enemies[0]
    boss.traits.add("hanya_jurus")
    ev = b.act(b.heroes[1], Action("serang", targets=[boss]))
    assert "terkena 1 damage" in "\n".join(ev), ev
    sebelum = boss.hp
    pakai_bara(b, b.heroes[0], "jurus_pelita_terakhir")
    assert boss.max_hp - boss.hp > 100 and boss.hp < sebelum


def test_serangan_biasa_tetap_mengisi_bara_di_fase_hanya_jurus(data):
    """Pukulan biasa cuma menggores, tapi kelemahan tetap memberi +1 Bara —
    itulah cara party membiayai Jurus-nya."""
    b = battle(data, EMPAT, enemies=("boss_pelita_pertama",), bara_max=8, bara_start=0)
    boss = b.enemies[0]
    boss.traits.add("hanya_jurus")
    boss.affinities = {Element.CAHAYA: Affinity.LEMAH}
    pakai(b, b.heroes[0], "sinar_lentera", target=[boss])
    assert b.bara >= 1


def test_hapus_skill_lalu_lagu_mengembalikannya(data):
    b = battle(data, ["rimba", "ratih"], enemies=("boss_pelita_pertama",))
    boss = b.enemies[0]
    jumlah = {h.key: len(h.skills) for h in b.heroes}
    musuh_pakai(b, boss, "m_hapus_ingatan")
    assert sum(len(h.skills) for h in b.heroes) == sum(jumlah.values()) - 1
    assert b.skill_terhapus
    ratih = b.hero_by_key("ratih")
    pakai(b, ratih, "t_lagu_rawat")
    assert not b.skill_terhapus
    assert sum(len(h.skills) for h in b.heroes) == sum(jumlah.values())


def test_padamkan_dunia_mengembalikan_bara_per_kenangan_puncak(data):
    b = battle(data, EMPAT, enemies=("boss_pelita_pertama",), bara_max=8, bara_start=6,
               bara_kenangan=3)
    boss = b.enemies[0]
    ev = musuh_pakai(b, boss, "m_padamkan_dunia")
    assert all(h.hp == 1 for h in b.heroes), [h.hp for h in b.heroes]
    assert b.bara == 3, "\n".join(ev)


def test_padamkan_dunia_tanpa_kenangan_puncak_mengosongkan_bara(data):
    b = battle(data, EMPAT, enemies=("boss_pelita_pertama",), bara_max=8, bara_start=6)
    musuh_pakai(b, b.enemies[0], "m_padamkan_dunia")
    assert b.bara == 0


# -- Sang Penenun -----------------------------------------------------------
def test_tenun_ulang_memberi_kelemahan_baru_ke_party(data):
    b = battle(data, EMPAT, enemies=("superboss_penenun",), seed=9)
    assert all(not h.affinities for h in b.heroes)
    musuh_pakai(b, b.enemies[0], "m_tenun_ulang")
    for h in b.heroes:
        assert list(h.affinities.values()) == [Affinity.LEMAH], h.key


def test_kaca_penenun_membuat_serang_dasar_adaptif(data):
    h = Hero.create(data, "sela", 50)
    h.equipment["senjata"] = "pedang_laut"
    h.rapikan_soket()
    h.kaca[0] = "kaca_penenun"
    b = Battle(data, [h], ["gema_prajurit"], rng=random.Random(4))
    assert b.heroes[0].serang_adaptif
    ev = b.act(b.heroes[0], Action("serang", targets=b.enemies))
    assert "LEMAH!" in "\n".join(ev), ev


# -- Cacing Abu Ibu ---------------------------------------------------------
def test_segmen_pulih_kalau_kepala_dibiarkan(data):
    b = battle(data, ["sela"], enemies=("buruan_cacing_ibu", "buruan_cacing_ibu_segmen"))
    kepala, segmen = b.enemies
    segmen.hp = segmen.max_hp // 2
    b.round = 1
    b.kepala_dipukul = False
    ev = []
    b._new_round(ev)                            # ronde 2 tanpa kepala dipukul
    assert segmen.hp > segmen.max_hp // 2, ev


def test_segmen_tidak_pulih_kalau_kepala_dipukul(data):
    b = battle(data, ["sela"], enemies=("buruan_cacing_ibu", "buruan_cacing_ibu_segmen"))
    kepala, segmen = b.enemies
    segmen.hp = segmen.max_hp // 2
    b.act(b.heroes[0], Action("serang", targets=[kepala]))
    assert b.kepala_dipukul
    b.round = 1
    ev = []
    b._new_round(ev)
    assert segmen.hp == segmen.max_hp // 2


# -- Kabut Terakhir (ending "Mendendangkan") --------------------------------
def test_kabut_terakhir_kebal_semua_serangan(data):
    b = battle(data, ["sela", "lintang"], enemies=("kabut_terakhir",))
    kabut = b.enemies[0]
    b.act(b.heroes[0], Action("serang", targets=[kabut]))
    pakai(b, b.heroes[1], "tirai_kelam")
    assert kabut.hp == kabut.max_hp


def test_hanya_lagu_yang_mengurai_kabut_terakhir(data):
    b = battle(data, ["rimba", "ratih"], enemies=("kabut_terakhir",))
    kabut = b.enemies[0]
    ratih = b.hero_by_key("ratih")
    ev = pakai(b, ratih, "t_lagu_rawat")
    assert kabut.hp < kabut.max_hp, ev
    assert any("terurai" in e for e in ev)


def test_delapan_lagu_menyelesaikan_kabut_terakhir(data):
    b = battle(data, ["rimba", "ratih"], enemies=("kabut_terakhir",))
    ratih = b.hero_by_key("ratih")
    for _ in range(8):
        ratih.mp = ratih.max_mp
        pakai(b, ratih, "t_lagu_rawat")
    assert b.over and b.result.outcome == "menang"


# -- Pertarungan bertahan (ending "Menyalakan Kembali") ---------------------
def test_bertahan_menang_setelah_rondenya_lewat(data):
    b = battle(data, EMPAT, enemies=("kabut_gelombang",), survive_rounds=3,
               survive_text="Menara ketujuh menyala.")
    for _ in range(400):
        if b.over:
            break
        t = b.next_turn()
        if t.skipped or t.actor is None:
            continue
        b.act(t.actor, Action("jaga") if t.actor.is_player else Action("serang", targets=b.heroes))
    assert b.over and b.result.outcome == "menang"
    assert "Menara ketujuh menyala." in b.log


def test_bertahan_tidak_selesai_walau_musuhnya_dihabisi(data):
    b = battle(data, EMPAT, enemies=("kabut_gelombang",), survive_rounds=5)
    b.round = 1
    b.enemies[0].hp = 0
    ev = []
    b._check_end(ev)
    assert not b.over
    assert b.enemies[0].alive and "Gelombang berikutnya" in "\n".join(ev)
