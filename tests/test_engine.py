import random

import pytest

from pelita.combat import ai
from pelita.combat.engine import Action, Battle
from pelita.combat.status import make_status
from pelita.loader import load_data
from pelita.models import Affinity, Element
from pelita.party import Hero


@pytest.fixture(scope="module")
def data():
    return load_data()


def make_battle(data, party, enemies, seed=1, **kw):
    heroes = [Hero.create(data, cid, lv) for cid, lv in party]
    b = Battle(data, heroes, enemies, rng=random.Random(seed), **kw)
    b.start()
    return b


def hero(b, key):
    h = b.hero_by_key(key)
    assert h is not None
    return h


def play_out(b, policy="pintar", max_turns=500):
    n = 0
    while not b.over and n < max_turns:
        n += 1
        t = b.next_turn()
        if t.skipped or t.actor is None:
            continue
        a = ai.choose_hero_action(b, t.actor, policy) if t.actor.is_player else ai.choose_enemy_action(b, t.actor)
        b.act(t.actor, a)
    return b.result


# --- urutan giliran ---------------------------------------------------------
def test_urutan_giliran_agi_tertinggi_duluan(data):
    b = make_battle(data, [("rimba", 5), ("lintang", 5)], ["lumut_berjalan"])
    t = b.next_turn()
    assert t.actor is not None and t.actor.key == "lintang"      # AGI 15 > Rimba 11 > Lumut 3


def test_pertarungan_selesai_dan_memberi_xp(data):
    b = make_battle(data, [("rimba", 5), ("sela", 5), ("lintang", 5)], ["kunang_kelam", "kunang_kelam"])
    r = play_out(b)
    assert r is not None and r.outcome == "menang"
    assert r.xp == 48 and r.keping == 8


# --- kelemahan, Goyah, Bara, Catatan Penyala --------------------------------
def test_kelemahan_memberi_goyah_bara_dan_catatan(data):
    b = make_battle(data, [("rimba", 5)], ["lumut_berjalan"])
    rimba, lumut = hero(b, "rimba"), b.enemies[0]
    ev = b.act(rimba, Action("skill", skill=data.skill("sulut"), targets=[lumut]))
    assert any("LEMAH" in e for e in ev)
    assert lumut.has("goyah") or not lumut.alive
    assert b.bara == 1
    assert b.bestiary.get("lumut_berjalan")[Element.API] == Affinity.LEMAH


def test_serap_menyembuhkan_musuh(data):
    b = make_battle(data, [("lintang", 8)], ["hampa_pengembara"])
    lintang, hampa = hero(b, "lintang"), b.enemies[0]
    hampa.hp = 50
    ev = b.act(lintang, Action("skill", skill=data.skill("bisikan_lupa"), targets=[hampa]))
    assert hampa.hp > 50
    assert any("MENYERAP" in e for e in ev)
    assert b.bara == 0


def test_imun_tidak_berpengaruh(data):
    b = make_battle(data, [("rimba", 5)], ["kunang_kelam"])
    b.enemies[0].affinities[Element.API] = Affinity.IMUN
    hp = b.enemies[0].hp
    ev = b.act(hero(b, "rimba"), Action("skill", skill=data.skill("sulut"), targets=[b.enemies[0]]))
    assert b.enemies[0].hp == hp
    assert any("Tidak berpengaruh" in e for e in ev)


def test_jaga_menambah_bara_hanya_untuk_rimba_dan_habis_di_giliran_berikutnya(data):
    b = make_battle(data, [("rimba", 3), ("sela", 3)], ["lumut_berjalan"])
    rimba, sela = hero(b, "rimba"), hero(b, "sela")
    b.act(sela, Action("jaga"))
    assert b.bara == 0 and sela.has("jaga")
    assert sela.effective("def") == int(sela.base.def_ * 1.5)
    b.act(rimba, Action("jaga"))
    assert b.bara == 1
    # jaga berakhir di awal giliran pemilik berikutnya
    b.queue = [rimba]
    b.next_turn()
    assert not rimba.has("jaga")


def test_bara_membeku_saat_rimba_pingsan(data):
    b = make_battle(data, [("rimba", 5), ("sela", 5)], ["lumut_berjalan"])
    rimba = hero(b, "rimba")
    rimba.hp = 0
    assert b.bara_frozen
    b.act(hero(b, "sela"), Action("jaga"))
    assert b.bara == 0
    assert b.usable_bara_skills(hero(b, "sela")) == []


def test_kawan_pingsan_memberi_dua_bara(data):
    b = make_battle(data, [("rimba", 5), ("lintang", 1)], ["penambang_terlupa"])
    lintang = hero(b, "lintang")
    lintang.hp = 1
    b.act(b.enemies[0], Action("serang", targets=[lintang]))
    assert not lintang.alive
    assert b.bara == 2


def test_jurus_ganda_butuh_kedua_pengguna_dan_memakai_stat_terbaik(data):
    b = make_battle(data, [("rimba", 10), ("sela", 10)], ["lumut_berjalan"], bara_start=4)
    rimba, sela = hero(b, "rimba"), hero(b, "sela")
    jg = data.skill("jg_tebas_berapi")
    assert jg in b.usable_bara_skills(rimba)
    assert jg in b.usable_bara_skills(sela)
    assert b._skill_source(rimba, jg) is sela                     # ATK Sela lebih tinggi
    ev = b.act(rimba, Action("skill", skill=jg, targets=[b.enemies[0]]))
    assert any("JURUS GANDA" in e for e in ev)
    assert b.bara in (0, 1)          # 4 Bara habis; +1 kalau pukulan Api (kelemahan) mengenai
    b2 = make_battle(data, [("rimba", 10), ("sela", 10)], ["lumut_berjalan"], bara_start=4)
    hero(b2, "sela").hp = 0
    assert jg not in b2.usable_bara_skills(hero(b2, "rimba"))


def test_nyala_pulih_menyembuhkan_dan_membersihkan_status(data):
    b = make_battle(data, [("rimba", 5), ("sela", 5)], ["lumut_berjalan"], bara_start=2)
    rimba, sela = hero(b, "rimba"), hero(b, "sela")
    sela.hp = 10
    sela.statuses["racun"] = make_status("racun")
    b.act(rimba, Action("skill", skill=data.skill("nyala_pulih"), targets=[]))
    assert sela.hp == 10 + int(sela.max_hp * 0.3)
    assert not sela.has("racun")
    assert b.bara == 0


# --- status -----------------------------------------------------------------
def test_racun_mengurangi_hp_di_akhir_giliran_dan_habis(data):
    b = make_battle(data, [("sela", 5)], ["kunang_kelam"])
    sela = hero(b, "sela")
    sela.statuses["racun"] = make_status("racun")
    hp = sela.hp
    b.act(sela, Action("jaga"))
    assert sela.hp == hp - max(1, int(sela.max_hp * 0.08))
    assert sela.statuses["racun"].turns_left == 3
    for _ in range(3):
        b.act(sela, Action("jaga"))
    assert not sela.has("racun")


def test_lupa_memblokir_skill(data):
    b = make_battle(data, [("rimba", 5)], ["kunang_kelam"])
    rimba = hero(b, "rimba")
    rimba.statuses["lupa"] = make_status("lupa")
    assert b.usable_skills(rimba) == []
    assert b.usable_bara_skills(rimba) == []


def test_tidur_melewati_giliran_dan_bangun_kalau_dipukul(data):
    b = make_battle(data, [("rimba", 5)], ["kunang_kelam"])
    rimba = hero(b, "rimba")
    rimba.statuses["tidur"] = make_status("tidur")
    b.queue = [rimba]
    t = b.next_turn()
    assert t.skipped and t.actor is rimba
    b.act(b.enemies[0], Action("serang", targets=[rimba]))
    assert not rimba.has("tidur")


def test_imunitas_status_musuh(data):
    b = make_battle(data, [("lintang", 8)], ["hampa_pengembara"])
    ev: list[str] = []
    ok = b._add_status(b.enemies[0], "lupa", None, ev)
    assert ok is False and any("kebal" in e for e in ev)


def test_provokasi_mengalihkan_serangan_musuh(data):
    b = make_battle(data, [("rimba", 5), ("sela", 5)], ["serigala_kabut"])
    sela = hero(b, "sela")
    b.act(sela, Action("skill", skill=data.skill("pasang_badan"), targets=[]))
    assert sela.taunting
    rimba_hp = hero(b, "rimba").hp
    for _ in range(5):
        a = ai.choose_enemy_action(b, b.enemies[0])
        b.enemies[0].turn_count += 1
        b.act(b.enemies[0], a)
        # provokasi hanya 1 giliran; pasang lagi
        sela.statuses["provokasi"] = make_status("provokasi")
    assert hero(b, "rimba").hp == rimba_hp


# --- Pecah (break) ----------------------------------------------------------
def test_pecah_saat_ketahanan_habis_lalu_pulih(data):
    b = make_battle(data, [("rimba", 6)], ["boss_hampa_penjaga_hutan"])
    rimba, boss = hero(b, "rimba"), b.enemies[0]
    boss.ketahanan = 25
    ev = b.act(rimba, Action("skill", skill=data.skill("sulut"), targets=[boss]))
    assert boss.has("pecah") and any("PECAH" in e for e in ev)
    assert not boss.has("goyah")
    # giliran boss dilewati, meter pulih
    b.queue = [boss]
    t = b.next_turn()
    assert t.skipped
    assert not boss.has("pecah") and boss.ketahanan == boss.ketahanan_max


def test_tertelan_lepas_saat_penelan_pecah(data):
    b = make_battle(data, [("rimba", 9), ("sela", 9)], ["boss_raja_katak_lumpur"])
    boss, sela = b.enemies[0], hero(b, "sela")
    sela.statuses["tertelan"] = make_status("tertelan", source=boss)
    boss.ketahanan = 5
    b.act(hero(b, "rimba"), Action("serang", targets=[boss]))
    assert boss.has("pecah")
    assert not sela.has("tertelan")


# --- AI ---------------------------------------------------------------------
def test_boss_mengikuti_pola_fase(data):
    b = make_battle(data, [("rimba", 9), ("sela", 9)], ["boss_raja_katak_lumpur"])
    boss = b.enemies[0]
    labels = [ai.choose_enemy_action(b, boss).label for _ in range(4)]
    assert labels == ["Hantam Lidah", "Serang", "Serang", "Muntah Racun"]
    boss.hp = int(boss.max_hp * 0.4)
    assert ai.choose_enemy_action(b, boss).label == "Telan"       # fase 2 mulai dari awal pola


def test_musuh_goyah_hanya_serang_biasa(data):
    b = make_battle(data, [("rimba", 5)], ["lumut_berjalan"])
    b.enemies[0].statuses["goyah"] = make_status("goyah")
    assert ai.choose_enemy_action(b, b.enemies[0]).kind == "serang"


def test_kebijakan_pintar_menghindari_serap_yang_diketahui(data):
    b = make_battle(data, [("lintang", 8)], ["hampa_pengembara"])
    b.bestiary.learn("hampa_pengembara", Element.KELAM, Affinity.SERAP)
    lintang = hero(b, "lintang")
    for _ in range(10):
        a = ai.choose_hero_action(b, lintang)
        assert not (a.skill and a.skill.element == Element.KELAM)


# --- item & kabur -----------------------------------------------------------
def test_item_heal_dan_bubuk_elemen(data):
    b = make_battle(data, [("rimba", 5)], ["katak_rawa_bengkak"], inventory={"ramuan_daun": 1, "bubuk_petir": 1})
    rimba, katak = hero(b, "rimba"), b.enemies[0]
    rimba.hp = 5
    b.act(rimba, Action("item", item=data.items["ramuan_daun"], targets=[rimba]))
    assert rimba.hp == 45 and b.inventory["ramuan_daun"] == 0
    hp = katak.hp
    ev = b.act(rimba, Action("item", item=data.items["bubuk_petir"], targets=[katak]))
    assert katak.hp < hp and any("LEMAH" in e for e in ev)
    assert b.usable_items() == []


def test_tidak_bisa_kabur_dari_boss(data):
    b = make_battle(data, [("rimba", 5)], ["boss_hampa_penjaga_hutan"])
    assert not b.can_flee
    ev = b.act(hero(b, "rimba"), Action("kabur"))
    assert any("Tidak bisa kabur" in e for e in ev)
    assert not b.over


def test_deterministik_dengan_seed(data):
    r1 = play_out(make_battle(data, [("rimba", 7), ("sela", 7), ("lintang", 6)], ["lumut_berjalan", "katak_rawa_bengkak"], seed=42))
    r2 = play_out(make_battle(data, [("rimba", 7), ("sela", 7), ("lintang", 6)], ["lumut_berjalan", "katak_rawa_bengkak"], seed=42))
    assert (r1.outcome, r1.rounds, r1.xp) == (r2.outcome, r2.rounds, r2.xp)
