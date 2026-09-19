"""Tes sistem Tahap 3: Kaca Ingatan, Jalur, cadangan & Ganti, Kenangan, Buruan, Arena."""
import random

import pytest

from pelita.combat.engine import Battle
from pelita.loader import load_data
from pelita.models import Element
from pelita.party import HP_BONUS_MAKS, Hero, kaca_tingkat
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import PARTY_AKTIF_MAKS, GameState, new_game
from tests.walker import Walker


@pytest.fixture(scope="module")
def data():
    return load_data()


@pytest.fixture(scope="module")
def world(data):
    return load_world(data)


def siap(data, world, steps, party=("rimba", "sela", "lintang"), level=20, tmp_path=None):
    """State siap-pakai dengan party terisi, lalu jalankan Walker di atasnya."""
    st = new_game(data)
    st.rng = random.Random(7)
    st.bara_max = 5
    st.flags.add("bara")
    for cid in party[1:]:
        st.join(cid, level)
    st.party[0].level = level
    st.party[0].xp = 0
    st.area_id, st.room_id = "pelita_rendah", "jalan_desa"
    st.wire()
    wk = Walker(steps)
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             save_dir=tmp_path or "/tmp/pelita-test-saves")
    return g, st, wk


# -- Kaca Ingatan -----------------------------------------------------------
def test_kaca_tingkat_naik_dari_pemakaian():
    assert kaca_tingkat(0) == 1 and kaca_tingkat(11) == 1
    assert kaca_tingkat(12) == 2 and kaca_tingkat(35) == 2
    assert kaca_tingkat(36) == 3 and kaca_tingkat(999) == 3


def test_soket_mengikuti_senjata(data):
    h = Hero.create(data, "rimba", 20)
    h.equipment["senjata"] = "tongkat_kayu_jati"     # 0 soket
    assert h.soket == 0 and h.rapikan_soket() == []
    h.equipment["senjata"] = "tongkat_kaca"          # 1 soket
    h.rapikan_soket()
    h.kaca[0] = "kaca_api"
    assert h.kaca_element == Element.API
    # turun ke senjata tanpa soket: Kaca terlepas, bukan hilang diam-diam
    h.equipment["senjata"] = "tongkat_kayu_jati"
    assert h.rapikan_soket() == ["kaca_api"] and h.kaca == []


def test_kaca_pasif_mengubah_stat_dan_skill(data):
    h = Hero.create(data, "rimba", 20)
    h.equipment["senjata"] = "tongkat_guntur"        # 2 soket
    h.rapikan_soket()
    dasar = h.stats.agi
    h.kaca[0] = "kaca_gesit"
    assert h.stats.agi > dasar
    # Kaca Skill meminjam skill karakter lain dengan MP lebih mahal
    h.kaca[1] = "kaca_kilat"
    pinjam = [s for s in h.skills() if s.id == "kilat_kecil"]
    assert pinjam and pinjam[0].cost == round(data.skill("kilat_kecil").cost * 1.5)


def test_kaca_tingkat_menguatkan_pasif(data):
    h = Hero.create(data, "rimba", 20)
    h.equipment["senjata"] = "tongkat_kaca"
    h.rapikan_soket()
    h.kaca[0] = "kaca_tajam"
    assert h.passive().kritikal == pytest.approx(0.10)
    h.kaca_uses["kaca_tajam"] = 40                   # tingkat III
    assert h.passive().kritikal == pytest.approx(0.20)


def test_kaca_dihitung_setelah_pertarungan(data):
    st = new_game(data)
    h = st.party[0]
    h.equipment["senjata"] = "tongkat_kaca"
    h.rapikan_soket()
    h.kaca[0] = "kaca_api"
    for _ in range(12):
        st.kaca_dipakai_selesai_bertarung()
    assert st.kaca_uses["kaca_api"] == 12 and kaca_tingkat(st.kaca_uses["kaca_api"]) == 2


def test_kaca_elemen_mengubah_serangan_dasar(data):
    h = Hero.create(data, "sela", 12)
    h.equipment["senjata"] = "pedang_sumpah"
    h.rapikan_soket()
    h.kaca[0] = "kaca_petir"
    b = Battle(data, [h], ["kunang_kelam"], rng=random.Random(3))
    assert b.heroes[0].weapon_element == Element.PETIR


# -- Jalur ------------------------------------------------------------------
def test_jalur_membuka_skill_dan_pasif(data):
    h = Hero.create(data, "sela", 20)
    assert h.butuh_pilih_jalur and len(h.jalur_tersedia()) == 2
    sebelum = h.stats.def_
    h.jalur = "sela_benteng"
    assert not h.butuh_pilih_jalur
    assert h.stats.def_ > sebelum
    assert any(s.id == "j_dinding_hidup" for s in h.skills())
    # skill jalur di level lebih tinggi belum muncul
    assert not any(s.id == "j_perisai_terakhir" for s in h.skills())


def test_jalur_belum_terbuka_di_level_rendah(data):
    h = Hero.create(data, "lintang", 19)
    assert not h.butuh_pilih_jalur and h.jalur_tersedia() == []


def test_semua_jalur_punya_dua_opsi_dan_skill_valid(data):
    for cid in {j.character for j in data.jalur.values()}:
        opsi = data.jalur_for(cid)
        assert len(opsi) == 2
        for j in opsi:
            assert j.skills and all(sid in data.skills for sid in j.skills)
            assert j.passive_note


# -- Cadangan & Ganti -------------------------------------------------------
def test_xp_cadangan_tujuh_puluh_persen(data, world, tmp_path):
    g, st, wk = siap(data, world, [], party=("rimba", "sela", "lintang"), level=5, tmp_path=tmp_path)
    st.join("bagas", 5)
    st.join("rangga", 5)                       # anggota kelima = cadangan
    for h in st.party:
        h.xp = 0
    g.runner.grant_xp(1000)
    assert st.party[0].xp == 1000 and st.party[-1].xp == 700


def test_rimba_tidak_bisa_keluar_barisan(data):
    st = new_game(data)
    for cid in ("sela", "lintang", "bagas", "rangga"):
        st.join(cid, 5)
    assert not st.tukar_posisi(0, 4)           # Rimba keluar: ditolak
    assert st.is_active("rimba")
    assert st.tukar_posisi(1, 4)               # Sela <-> Rangga: boleh
    assert [h.id for h in st.active_party] == ["rimba", "rangga", "lintang", "bagas"]


def test_ganti_menukar_dengan_cadangan(data):
    aktif = [Hero.create(data, cid, 10) for cid in ("rimba", "sela")]
    cadangan = [Hero.create(data, "lintang", 10)]
    b = Battle(data, aktif, ["kunang_kelam"], rng=random.Random(5), reserves=cadangan)
    sela = b.hero_by_key("sela")
    assert b.bisa_ganti(sela) and not b.bisa_ganti(b.hero_by_key("rimba"))  # Rimba terkunci
    masuk = b.bisa_ganti(sela)[0]
    from pelita.combat.engine import Action
    b.act(sela, Action("ganti", targets=[masuk]))
    assert [c.key for c in b.heroes] == ["rimba", "lintang"]
    assert [c.key for c in b.bench] == ["sela"]
    b.sync_heroes()                            # HP cadangan tetap ikut tersimpan


def test_arena_melarang_item(data):
    h = Hero.create(data, "rimba", 10)
    b = Battle(data, [h], ["kunang_kelam"], rng=random.Random(1),
               inventory={"ramuan_daun": 5}, allow_items=False)
    assert b.usable_items() == []


# -- Jurus Ganda & Kenangan -------------------------------------------------
def test_jurus_ganda_terkunci_sampai_kenangan(data):
    heroes = [Hero.create(data, cid, 20) for cid in ("rimba", "sela")]
    terkunci = Battle(data, heroes, ["kunang_kelam"], rng=random.Random(2), bara_max=5, bara_start=5,
                      jurus_terbuka=set())
    assert not [s for s in terkunci.usable_bara_skills(terkunci.heroes[0]) if s.id == "jg_tebas_berapi"]
    terbuka = Battle(data, heroes, ["kunang_kelam"], rng=random.Random(2), bara_max=5, bara_start=5,
                     jurus_terbuka={"jg_tebas_berapi"})
    assert [s for s in terbuka.usable_bara_skills(terbuka.heroes[0]) if s.id == "jg_tebas_berapi"]


def test_kenangan_tersedia_mengikuti_syarat(data, world, tmp_path):
    g, st, wk = siap(data, world, [], tmp_path=tmp_path)
    ids = [kid for kid, _ in g.kenangan_tersedia()]
    assert "rimba_sela_1" in ids
    assert "rimba_bagas_1" not in ids                  # Bagas belum di party
    assert "rimba_sela_2" not in ids                   # syarat cerita belum terpenuhi
    st.kenangan.add("rimba_sela_1")
    assert "rimba_sela_1" not in [kid for kid, _ in g.kenangan_tersedia()]


def test_kenangan_membuka_jurus_ganda(data, world, tmp_path):
    g, st, wk = siap(data, world, [], tmp_path=tmp_path)
    assert g.jurus_terbuka() == set()
    kid, k = next((kid, k) for kid, k in g.kenangan_tersedia() if k.get("jurus"))
    g.mainkan_kenangan(kid, k)
    assert k["jurus"] in g.jurus_terbuka()
    assert any("Jurus Ganda terbuka" in l for l in wk.out)


def test_setiap_kenangan_punya_adegan(world):
    for kid, k in world.kenangan.items():
        assert k["judul"] and k["adegan"], kid
        # Kenangan biasa berpasangan; Kenangan puncak Babak 3 adalah renungan satu orang.
        assert len(k["pasangan"]) == (1 if k.get("puncak") else 2), kid


# -- Tukang Kaca & Serpihan -------------------------------------------------
def test_tukar_serpihan_hp_dan_soket(data, world, tmp_path):
    g, st, wk = siap(data, world, ["@1", "@1", "@1"], tmp_path=tmp_path)
    st.add_item("serpihan_ingatan", 3)
    h = st.party[0]
    hp_lama = h.max_hp
    g.tukar_serpihan()
    assert h.hp_bonus == 1 and h.max_hp > hp_lama
    assert st.count("serpihan_ingatan") == 0
    # batas 3 langkah per karakter
    h.hp_bonus = HP_BONUS_MAKS
    st.add_item("serpihan_ingatan", 3)
    wk.steps.extend(["@1", "@1"])
    g.tukar_serpihan()
    assert st.count("serpihan_ingatan") == 3          # gagal: Serpihan tidak terpakai


def test_tukar_serpihan_soket_tambahan(data, world, tmp_path):
    g, st, wk = siap(data, world, ["@3", "@1"], tmp_path=tmp_path)
    h = st.party[0]
    h.equipment["senjata"] = "tongkat_kaca"
    h.rapikan_soket()
    st.add_item("serpihan_ingatan", 3)
    g.tukar_serpihan()
    assert st.slot_bonus.get("tongkat_kaca") == 1 and h.soket == 2


def test_beli_kaca_dengan_potongan_harga(data, world, tmp_path):
    g, st, wk = siap(data, world, ["@1", "@0"], tmp_path=tmp_path)
    g.auto_menus = False
    st.keping = 1000
    harga_penuh = data.kaca["kaca_api"].price
    g.beli_kaca("kios_sarwa")
    assert st.kaca.get("kaca_api") == 1 and st.keping == 1000 - harga_penuh
    # Kaca Kikir memotong harga berikutnya
    h = st.party[0]
    h.equipment["senjata"] = "tongkat_guntur"
    h.rapikan_soket()
    h.kaca[0] = "kaca_kikir"
    assert g.harga(harga_penuh) < harga_penuh


# -- Buruan & Arena ---------------------------------------------------------
def test_papan_buruan_dan_target_muncul_di_ruangnya(data, world, tmp_path):
    g, st, wk = siap(data, world, ["@1", "@0"], tmp_path=tmp_path)
    st.flags.add("boss_hutan_kalah")
    g.auto_menus = False                               # auto_menus selalu memilih "pergi"
    g.papan_buruan()
    assert st.buruan.get("buruan_1_kunang") == "aktif"
    b = world.buruan["buruan_1_kunang"]
    st.area_id, st.room_id = b["area"], b["room"]
    assert any("Buruan:" in label for label, _ in g._options())
    # di ruang lain, target tidak muncul
    st.room_id = "tepi_hutan"
    assert not any("Buruan:" in label for label, _ in g._options())


def test_buruan_selesai_memberi_hadiah(data, world, tmp_path):
    g, st, wk = siap(data, world, [], level=24, tmp_path=tmp_path)
    st.buruan["buruan_1_kunang"] = "aktif"
    st.area_id, st.room_id = "hutan_kelabu", "lembah_kabut"
    g.auto_menus = True
    g.lawan_buruan("buruan_1_kunang")
    assert st.buruan["buruan_1_kunang"] == "selesai"
    assert st.kaca.get("kaca_tabah") == 1 and st.count("bekal_kemah") >= 2


def test_arena_tiga_gelombang(data, world, tmp_path):
    g, st, wk = siap(data, world, [], party=("rimba", "sela", "lintang"), level=30, tmp_path=tmp_path)
    g.auto_menus = True
    st.arena = 0
    g.mulai_arena(1)
    assert st.arena == 1 and st.kaca.get("kaca_gesit") == 1
    g.mulai_arena(1)                                   # diulang: upah tingkat tidak diberikan dua kali
    assert st.kaca.get("kaca_gesit") == 1
    assert any("sudah pernah kau tamatkan" in l for l in wk.out)


def test_semua_hadiah_buruan_arena_valid(data, world):
    for b in world.buruan.values():
        for kid in b["hadiah"].get("kaca", []):
            assert kid in data.kaca
    for t in world.arena:
        assert len(t["gelombang"]) == 3


# -- save / muat ------------------------------------------------------------
def test_save_membawa_kaca_jalur_dan_kemajuan(data, world, tmp_path):
    st = new_game(data)
    st.join("sela", 20)
    h = st.hero("sela")
    h.equipment["senjata"] = "pedang_sumpah"
    h.rapikan_soket()
    h.kaca[0] = "kaca_tajam"
    h.jalur = "sela_algojo"
    h.hp_bonus = 2
    st.kaca_uses["kaca_tajam"] = 20
    st.slot_bonus["pedang_sumpah"] = 1
    st.kenangan.add("rimba_sela_1")
    st.buruan["buruan_1_kunang"] = "selesai"
    st.arena = 2
    st.add_kaca("kaca_napas", 1)
    st.save(1, tmp_path)

    ulang = GameState.load(data, 1, tmp_path)
    h2 = ulang.hero("sela")
    assert h2.jalur == "sela_algojo" and h2.kaca[0] == "kaca_tajam" and h2.hp_bonus == 2
    assert h2.soket == 3 and kaca_tingkat(ulang.kaca_uses["kaca_tajam"]) == 2
    assert ulang.kenangan == {"rimba_sela_1"} and ulang.arena == 2
    assert ulang.buruan["buruan_1_kunang"] == "selesai" and ulang.kaca["kaca_napas"] == 1
    # tabel Kaca tetap terhubung ke Hero setelah dimuat
    assert h2.kaca_uses is ulang.kaca_uses


def test_snapshot_ruang_membawa_jalur_dan_kaca(data, world, tmp_path):
    g, st, wk = siap(data, world, [], party=("rimba", "sela", "lintang"), level=20, tmp_path=tmp_path)
    st.join("bagas", 20)
    st.join("rangga", 20)
    h = st.party[0]
    h.equipment["senjata"] = "tongkat_kaca"
    h.rapikan_soket()
    h.kaca[0] = "kaca_api"
    h.jalur = "rimba_penuntun"
    snap = g.room_snapshot()
    assert snap["party"][0]["jalur"] == "Penuntun" and snap["party"][0]["kaca"] == ["Kaca Api"]
    assert snap["party"][0]["aktif"] and not snap["party"][PARTY_AKTIF_MAKS]["aktif"]
    assert snap["party"][1]["jalur"] == "pilih!"        # Sela Lv 20 belum memilih
