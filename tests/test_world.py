import json
import random
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.world.explore import Game
from pelita.world.model import WORLD_DIR, load_world
from pelita.world.state import GameState, new_game
from tests.walker import Walker


@pytest.fixture(scope="module")
def data():
    return load_data()


@pytest.fixture(scope="module")
def world(data):
    return load_world(data)


AREA1_KE_BOSS = [
    "Masuk ke jalan desa", "Rumah Pak Guntur", "Peti minyak", "Tikar tidur",
    "Keluar ke jalan desa", "Gerbang barat", "Masuk ke Hutan",
    "Ikuti jalan", "Terus ke pohon", "Sesuatu di akar", "Kembali ke jalan setapak", "Terus ke pohon",
    "Lewati pohon", "Lentera penjaga di batu", "Naik ke tepi",
]
KEMBALI_KE_DESA = [
    "Kembali ke lembah", "Kembali ke pohon", "Kembali ke jalan setapak", "Kembali ke tepi hutan",
    "Kembali ke gerbang barat", "Kembali ke jalan desa", "Balai desa",
]
KE_RAWA = [
    "Keluar ke jalan desa", "Gerbang barat", "Masuk ke Hutan", "Ikuti jalan", "Terus ke pohon",
    "Lewati pohon", "Naik ke tepi", "Menyusuri tepi kabut",
]


def play(data, world, steps, seed=11, tmp_path=None, state=None):
    wk = Walker(steps)
    st = state or new_game(data)
    st.rng = random.Random(seed)
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True, save_dir=tmp_path or Path("/tmp/pelita-test-saves"))
    res = g.run()
    return res, st, wk


def test_data_dunia_valid(world):
    assert {"pelita_rendah", "hutan_kelabu"} <= set(world.areas)
    assert world.areas["hutan_kelabu"].fog and not world.areas["pelita_rendah"].fog


def test_state_awal(data):
    st = new_game(data)
    assert [h.id for h in st.party] == ["rimba"]
    assert st.bara_max == 0 and st.has_item("minyak_lentera")


def test_kondisi(data):
    st = new_game(data)
    st.flags.add("x")
    st.quests["q"] = "aktif"
    assert st.check(["x", "!y", "has:ramuan_daun", "!has:abu_fajar", "party:rimba", "!party:sela", "quest:q=aktif", "keping>=30", "level>=1", "!bara"])
    assert st.check({"any": ["y", "x"]})
    assert not st.check({"any": ["y", "z"]})
    assert st.check({"not": "y"})


def test_prolog_sampai_boss_hutan(data, world, tmp_path):
    res, st, wk = play(data, world, AREA1_KE_BOSS + ["@k"], tmp_path=tmp_path)
    assert res == "quit"
    assert "Guntur bergabung" in wk.text and "Guntur meninggalkan" in wk.text
    assert "memperoleh BARA" in wk.text and st.bara_max == 5
    assert st.in_party("sela") and not st.in_party("guntur")
    assert "boss_hutan_kalah" in st.flags
    assert st.quests["kirana_hilang"] == "ditemukan"
    # exit ke Rawa masih terhalang sebelum kembali ke desa
    assert "terhalang" in wk.out[-6] or any("terhalang" in l for l in wk.out[-12:])


def test_area1_tamat_sampai_rawa(data, world, tmp_path):
    res, st, wk = play(data, world, AREA1_KE_BOSS + KEMBALI_KE_DESA + KE_RAWA + ["@k"], tmp_path=tmp_path)
    assert res == "quit"
    assert st.area_id == "rawa_suar"
    assert st.quests == {"kirana_hilang": "selesai", "mencari_guntur": "aktif"}
    assert "kembali_ke_desa" in st.flags
    assert st.hero("rimba").level >= 2          # XP dari encounter & boss
    assert st.keping > 30


def test_kabut_menghabiskan_minyak(data, world, tmp_path):
    res, st, wk = play(data, world, AREA1_KE_BOSS[:8] + ["@k"], tmp_path=tmp_path)   # sampai jalan setapak
    assert st.lentera_steps > 0
    assert "menuang Minyak Lentera" in wk.text


def test_save_load_roundtrip(data, world, tmp_path):
    _, st, _ = play(data, world, AREA1_KE_BOSS + ["@k"], tmp_path=tmp_path)
    st.save(2, tmp_path)
    st2 = GameState.load(data, 2, tmp_path)
    assert [h.id for h in st2.party] == [h.id for h in st.party]
    assert st2.hero("sela").level == st.hero("sela").level
    assert st2.flags == st.flags and st2.quests == st.quests
    assert st2.inventory == st.inventory and st2.keping == st.keping
    assert st2.area_id == st.area_id and st2.room_id == st.room_id
    assert st2.bestiary.known == st.bestiary.known
    assert st2.bara_max == 5
    assert GameState.slot_summaries(data, tmp_path)[1] is not None


def test_lentera_menyimpan_dan_memulihkan(data, world, tmp_path):
    steps = AREA1_KE_BOSS[:8] + ["Lentera penjaga di tunggul", "@k"]
    # (lentera di tunggul ada di Jalan Setapak, langkah ke-8)
    res, st, wk = play(data, world, steps, tmp_path=tmp_path)
    assert (tmp_path / "slot1.json").exists()
    assert all(h.hp == h.max_hp for h in st.party)


def test_menu_party_item_catatan_quest_tidak_crash(data, world, tmp_path):
    steps = AREA1_KE_BOSS[:4] + ["@p", "@1", "@1", "@0", "@0", "@i", "@0", "@c", "@q", "@k"]
    res, st, wk = play(data, world, steps, tmp_path=tmp_path)
    assert res == "quit"
    assert "Catatan Penyala" in wk.text and "Quest" in wk.text


def test_toko_beli_jual(data, world, tmp_path):
    # beli Ramuan Daun (1), kembali, jual Ramuan Daun (1), kembali, pergi
    wk = Walker(["Masuk ke jalan desa", "Warung", "Bu Ratna", "@1", "@1", "@0", "@2", "@2", "@0", "@0", "@k", "@y"])
    st = new_game(data)
    st.rng = random.Random(1)
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True, save_dir=tmp_path)
    g.auto_menus = False
    keping_awal = st.keping
    res = g.run()
    assert res == "quit"
    assert "Membeli Ramuan Daun" in wk.text and "Menjual Ramuan Daun" in wk.text
    assert st.count("ramuan_daun") == 3                 # 3 awal + 1 beli − 1 jual


def test_tidak_ada_nama_flag_yang_dipakai_dua_area():
    """Regresi §9.5: Peti Lantai Pernikahan di Mercusuar (Babak 1) dan Kotak
    Seserahan di Pulau Pernikahan (Babak 3) dulu sama-sama memakai
    ``peti_pernikahan_diambil``, jadi membuka yang pertama menghilangkan yang kedua
    selamanya — dan tidak ada tes yang bisa melihatnya.

    Flag dunia hidup di satu ruang nama global, jadi dua area yang menyalakan nama
    yang sama hampir selalu bug, bukan kebetulan. Audit ini otomatis sekarang;
    kalau memang disengaja (mis. satu peristiwa ditulis di dua tempat), daftarkan
    di ``SENGAJA_BERSAMA`` beserta alasannya.
    """
    import collections
    import glob
    import json as _json
    import re

    #: flag yang memang sengaja dinyalakan dari lebih dari satu area
    SENGAJA_BERSAMA: dict[str, str] = {}

    setter: dict[str, set[str]] = collections.defaultdict(set)
    for f in sorted(glob.glob(str(WORLD_DIR / "area_*.json"))):
        d = _json.loads(Path(f).read_text(encoding="utf-8"))
        teks = _json.dumps(d, ensure_ascii=False)
        for m in re.finditer(r'"(?:set|once)": "([a-z0-9_]+)"', teks):
            setter[m.group(1)].add(d["id"])
        for m in re.finditer(r'"(?:set|unset)": \[([^\]]*)\]', teks):
            for nama in re.findall(r'"([a-z0-9_]+)"', m.group(1)):
                setter[nama].add(d["id"])

    tabrakan = {k: sorted(v) for k, v in setter.items()
                if len(v) > 1 and k not in SENGAJA_BERSAMA}
    assert not tabrakan, (
        "nama flag dipakai lebih dari satu area (beri cakupan areanya sendiri): "
        + ", ".join(f"{k} {v}" for k, v in sorted(tabrakan.items())))
    assert len(setter) > 200, f"audit cuma menemukan {len(setter)} flag; polanya berubah?"


#: Urutan area sepanjang cerita, dan babak keberapa tiap anggota party bergabung.
#: Dipakai ``test_tidak_ada_yang_bicara_sebelum_bergabung``.
URUT_AREA = {
    "pelita_rendah": 1, "hutan_kelabu": 2, "rawa_suar": 3, "danau_cermin": 4,
    "tengara": 5, "lorong_bawah": 6, "gua_danau": 6.5, "tambang": 7, "mercusuar": 8,
    "celah_angin": 9, "dataran_abu": 10, "hutan_nyanyi": 11, "wirasaba": 12,
    "danau_garam": 13, "benteng_ordo": 14, "suar_ketiga": 14.5, "laut_lupa": 15,
    "pusar_kabut": 16,
}
GABUNG_AREA = {"Rimba": 1, "Sela": 1, "Lintang": 3, "Bagas": 7,
               "Rangga": 9, "Ratih": 11, "Kelana": 13}
#: Baris di mana orangnya memang hadir sebagai lawan, bukan sebagai anggota party.
LAWAN_DULU = {("tengara", "Rangga"), ("lorong_bawah", "Rangga"), ("wirasaba", "Kelana")}


def test_tidak_ada_yang_bicara_sebelum_bergabung():
    """Poles naskah Tahap 7: anggota party yang belum bergabung tidak boleh punya
    baris dialog, dan Kelana — yang bisa dihabisi di Wirasaba — tidak boleh bicara
    di Babak 3 tanpa penjaga ``party:kelana``.

    Dua bug asli yang ditemukan audit ini: Bagas mengomentari Arena Kafilah di
    Tengara (tersedia sejak Babak 1, padahal Bagas baru bergabung di Tambang), dan
    Kelana bicara di serambi Benteng meski pemain memilih menghabisinya.
    """
    import glob
    import json as _json

    salah: list[str] = []
    for f in sorted(glob.glob(str(WORLD_DIR / "area_*.json"))):
        d = _json.loads(Path(f).read_text(encoding="utf-8"))
        aid, idx = d["id"], URUT_AREA[d["id"]]

        def telusur(o, dijaga=False):
            if isinstance(o, dict):
                syarat = _json.dumps(o.get("if", ""), ensure_ascii=False)
                jaga = dijaga or "party:kelana" in syarat or "kelana_dibunuh" in syarat
                nama = o.get("say")
                if nama in GABUNG_AREA and (aid, nama) not in LAWAN_DULU:
                    if GABUNG_AREA[nama] > idx:
                        salah.append(f"{aid}: {nama} bicara sebelum bergabung")
                    if nama == "Kelana" and idx >= 14 and not jaga:
                        salah.append(f"{aid}: Kelana bicara tanpa penjaga party:kelana")
                for v in o.values():
                    telusur(v, jaga)
            elif isinstance(o, list):
                for v in o:
                    telusur(v, dijaga)

        # ending "Menyalakan Kembali" hanya bisa dipilih kalau Kelana hidup,
        # jadi seluruh skripnya sudah dijaga di tempat pilihannya ditawarkan.
        skrip = {k: v for k, v in d["scripts"].items() if k != "ending_nyala"}
        telusur(skrip)
    assert not salah, "\n".join(sorted(set(salah)))
