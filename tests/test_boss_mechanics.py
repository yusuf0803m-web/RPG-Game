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


def make(data, party, enemies, seed=3, **kw):
    heroes = [Hero.create(data, cid, lv) for cid, lv in party]
    b = Battle(data, heroes, enemies, rng=random.Random(seed), **kw)
    b.start()
    return b


def hero(b, key):
    return b.hero_by_key(key)


def enemy_turn(b, e):
    """Jalankan satu giliran musuh lewat AI (tanpa antrean)."""
    e.turn_count += 1
    b._apply_rotation(e, [])
    return b.act(e, ai.choose_enemy_action(b, e))


def test_summon_menambah_musuh(data):
    b = make(data, [("rimba", 4), ("sela", 4)], ["boss_hampa_penjaga_hutan"])
    boss = b.enemies[0]
    ev = b.act(boss, Action("skill", skill=data.skill("m_panggil_kunang"), targets=[]))
    assert len(b.enemies) == 3 and sum(1 for e in b.enemies if e.key == "kunang_kelam") == 2
    assert any("dipanggil" in e for e in ev)
    assert b.enemies[1].display_name == "Kunang Kelam A" and b.enemies[2].display_name == "Kunang Kelam B"


def test_summon_dibatasi_lima(data):
    b = make(data, [("rimba", 4)], ["boss_hampa_penjaga_hutan", "kunang_kelam", "kunang_kelam", "kunang_kelam"])
    b.act(b.enemies[0], Action("skill", skill=data.skill("m_panggil_kunang"), targets=[]))
    assert len(b.alive_enemies) == 5


def test_rotasi_afinitas_penambang(data):
    b = make(data, [("rimba", 19), ("lintang", 18)], ["boss_penambang_raksasa"])
    boss = b.enemies[0]
    ev = []
    boss.turn_count = 1
    b._apply_rotation(boss, ev)
    assert boss.affinity(Element.API) == Affinity.SERAP and boss.affinity(Element.ES) == Affinity.LEMAH
    assert any("MERAH" in e for e in ev)
    boss.turn_count = 4
    b._apply_rotation(boss, ev)
    assert boss.affinity(Element.ES) == Affinity.SERAP and boss.affinity(Element.API) == Affinity.LEMAH
    boss.turn_count = 7
    b._apply_rotation(boss, ev)
    assert boss.affinity(Element.FISIK) == Affinity.LEMAH


def maju_ke_fase(battle, boss, indeks: int):
    """Dorong ``boss`` sampai fase ke-``indeks`` aktif.

    Fase naik satu tingkat per giliran (lihat ``ai.choose_enemy_action``): boss yang
    HP-nya anjlok dalam satu pukulan tetap melewati fase-fase di antaranya, supaya
    tidak ada fase yang hilang tanpa pernah dipakai. Tes mekanik fase karena itu
    memanggil AI-nya beberapa kali, bukan menyetel HP lalu berharap langsung sampai.

    Mengembalikan aksi yang dipilih pada giliran fase itu menyala — yaitu langkah
    pertama polanya, karena pergantian fase menyetel ulang posisi pola.
    """
    aksi = None
    for _ in range(indeks + 2):
        if boss.phase_index >= indeks:
            return aksi
        aksi = ai.choose_enemy_action(battle, boss)
    assert boss.phase_index == indeks, f"boss berhenti di fase {boss.phase_index}"
    return aksi


def test_fase_mengubah_afinitas_dan_mengumumkan(data):
    b = make(data, [("rimba", 12), ("lintang", 11)], ["boss_ular_cermin"])
    boss = b.enemies[0]
    assert boss.affinity(Element.PETIR) == Affinity.LEMAH
    boss.hp = int(boss.max_hp * 0.3)
    maju_ke_fase(b, boss, 1)
    assert boss.affinity(Element.PETIR) == Affinity.TAHAN and boss.affinity(Element.API) == Affinity.LEMAH
    ev = b.act(boss, ai.choose_enemy_action(b, boss))
    assert any("retak" in e.lower() for e in ev)


def test_meriam_butuh_isian_dan_goyah_membatalkan(data):
    b = make(data, [("rimba", 21), ("lintang", 20)], ["boss_penjaga_mercusuar"])
    boss = b.enemies[0]
    hp = [h.hp for h in b.heroes]
    ev = b.act(boss, Action("skill", skill=data.skill("m_meriam_nyala"), targets=[]))
    assert any("belum siap" in e for e in ev) and [h.hp for h in b.heroes] == hp
    b.act(boss, Action("skill", skill=data.skill("m_isi_meriam"), targets=[]))
    assert boss.has("mengisi")
    # kelemahan (Petir) → Goyah → isian buyar
    ev = b.act(hero(b, "lintang"), Action("skill", skill=data.skill("kilat_kecil"), targets=[boss]))
    assert not boss.has("mengisi") and any("buyar" in e for e in ev)
    # isi lagi, lalu tembak
    b.act(boss, Action("skill", skill=data.skill("m_isi_meriam"), targets=[]))
    b.act(boss, Action("skill", skill=data.skill("m_meriam_nyala"), targets=[]))
    assert all(h.hp < mh for h, mh in zip(b.heroes, hp))
    assert not boss.has("mengisi")


def test_tandai_eksekusi_x3_dan_provokasi(data):
    b = make(data, [("sela", 15), ("lintang", 14)], ["boss_kapten_rangga"])
    rangga, sela, lintang = b.enemies[0], hero(b, "sela"), hero(b, "lintang")
    a = ai.choose_enemy_action(b, rangga)         # pola: Tandai@mag_tertinggi
    assert a.label == "Tandai" and a.targets == [lintang]
    b.act(rangga, a)
    assert lintang.has("tandai")
    # Pasang Badan: eksekusi dialihkan ke Sela, tanda tetap di Lintang
    b.act(sela, Action("skill", skill=data.skill("pasang_badan"), targets=[]))
    a = ai.choose_enemy_action(b, rangga)         # Tebas Eksekusi@tandai
    assert a.label == "Tebas Eksekusi"
    lhp = lintang.hp
    ev = b.act(rangga, a)
    assert lintang.hp == lhp and lintang.has("tandai")
    # tanpa provokasi: ×3 dan tanda hilang
    sela.statuses.pop("provokasi", None)
    rangga.pattern_pos = 1
    a = ai.choose_enemy_action(b, rangga)
    ev = b.act(rangga, a)
    assert any("mengeksekusi" in e for e in ev) and not lintang.has("tandai")


def test_fase_dua_rangga_dua_aksi_dan_kebal_provokasi(data):
    b = make(data, [("sela", 15), ("rimba", 15)], ["boss_kapten_rangga"])
    rangga, sela = b.enemies[0], hero(b, "sela")
    rangga.hp = int(rangga.max_hp * 0.3)
    maju_ke_fase(b, rangga, 1)
    b.act(sela, Action("skill", skill=data.skill("pasang_badan"), targets=[]))
    b.queue = [rangga]
    t = b.next_turn()
    a = ai.choose_enemy_action(b, t.actor)
    assert rangga.ignore_taunt and rangga.actions_per_turn == 2
    ev = b.act(rangga, a)
    assert any("bergerak lagi" in e for e in ev)
    assert b.queue[0] is rangga
    t2 = b.next_turn()
    assert t2.actor is rangga and not t2.skipped
    b.act(rangga, ai.choose_enemy_action(b, rangga))
    assert rangga.actions_done == 0            # giliran berakhir setelah aksi kedua


def test_padamkan_sekali_per_pertarungan(data):
    b = make(data, [("rimba", 23), ("sela", 23)], ["boss_kelam_berwajah"])
    boss = b.enemies[0]
    b.act(boss, Action("skill", skill=data.skill("m_padamkan"), targets=[]))
    assert all(h.hp == 1 for h in b.heroes)
    boss.hp = int(boss.max_hp * 0.1)
    boss.phase_index = -1
    # Fase Padam membuka dengan m_padamkan; ia sudah dipakai, jadi jatuh ke Serang.
    a = maju_ke_fase(b, boss, len(boss.edef.phases) - 1)
    assert a.label == "Serang"


def test_suku_cadang_curi_baterai_pindai(data):
    b = make(data, [("bagas", 22), ("rimba", 22)], ["kelelawar_kristal"], inventory={"suku_cadang": 1})
    bagas, rimba, bat = hero(b, "bagas"), hero(b, "rimba"), b.enemies[0]
    bat.base.hp = bat.hp = 9999          # jangan sampai mati sebelum dicuri
    pk = data.skill("peluncur_kejut")
    assert b.cost_ok(bagas, pk)
    b.act(bagas, Action("skill", skill=pk, targets=[bat]))
    assert b.inventory["suku_cadang"] == 0 and not b.cost_ok(bagas, pk)
    assert pk not in b.usable_skills(bagas)
    # Curi: kelelawar membawa Tetes Nyala; LCK Bagas tinggi → coba beberapa kali
    got = False
    for _ in range(20):
        bat.stolen = False
        b.inventory.pop("tetes_nyala", None)
        b.act(bagas, Action("skill", skill=data.skill("curi"), targets=[bat]))
        if b.inventory.get("tetes_nyala"):
            got = True
            break
    assert got
    b.act(bagas, Action("skill", skill=data.skill("curi"), targets=[bat]))
    assert bat.stolen
    # Baterai
    rimba.mp = 0
    mp0 = bagas.mp
    b.act(bagas, Action("skill", skill=data.skill("baterai"), targets=[rimba]))
    assert rimba.mp == 15 and bagas.mp == mp0 - 15
    # Pindai
    ev = b.act(bagas, Action("skill", skill=data.skill("pindai"), targets=[bat]))
    assert b.bestiary.get("kelelawar_kristal")[Element.PETIR] == Affinity.LEMAH
    assert len(b.bestiary.get("kelelawar_kristal")) == 8
    assert any("Pindai" in e for e in ev)


def test_telan_lepas_saat_goyah(data):
    b = make(data, [("rimba", 9), ("sela", 9), ("lintang", 8)], ["boss_raja_katak_lumpur"])
    boss, sela = b.enemies[0], hero(b, "sela")
    sela.statuses["tertelan"] = make_status("tertelan", source=boss)
    b.act(hero(b, "lintang"), Action("skill", skill=data.skill("kilat_kecil"), targets=[boss]))   # Petir = lemah → Goyah
    assert not sela.has("tertelan")


def test_kalung_bara_memberi_bara_awal(data):
    heroes = [Hero.create(data, "rimba", 12), Hero.create(data, "sela", 12)]
    heroes[0].equipment["aksesori"] = "kalung_bara"
    b = Battle(data, heroes, ["lumut_berjalan"], rng=random.Random(1), bara_start=1)
    assert b.bara == 1
