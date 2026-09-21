"""Walkthrough otomatis Babak 2: dari Celah Angin sampai Nirmala jatuh.

Melanjutkan ``tests/test_babak1.py``. Party dimulai dari keadaan akhir Babak 1
(Lv 24, empat anggota + Rangga) supaya tesnya fokus ke Babak 2 dan tidak
mengulang enam jam pertama tiap kali dijalankan.
"""
from __future__ import annotations

import random
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.party import xp_to_reach
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.test_babak1 import BerhentiUji, make_equipper
from tests.walker import Walker

CELAH = [
    "Masuk ke celah",
    "Terus ke jembatan",
    "Batu penahan selatan", "Batu penahan tengah", "Batu penahan utara",
    "Seberangi jembatan",
    "Buntalan di bawah batu",
    "Lentera penjaga",
    "Naik ke tangga angin", "Naik terus",
    "Ke punggung celah",
    "Lentera penjaga",
]
DATARAN = [
    "Turun ke Dataran Abu",
    "Masuk ke dataran",
    "Menyimpang ke reruntuhan", "Tungku yang masih utuh", "Kembali ke jalan abu",
    "Ikuti bekas roda",
    "Ke gerobak Nyai Rukmini", "Nyai Rukmini", "Kembali ke pos",
    "Lentera raksasa",
    "Ke jalan utara",
    "Periksa bekas roda yang terputus",
    "Kembali ke jalan utara",
]
HUTAN = [
    "Menuju garis hijau di utara",
    "Masuk ke hutan", "Ikuti suara nyanyian",
    "Lubang di pangkal pohon",
    "Lanjut ke desa",
    "Ke Balai Nyanyi", "Tetua Lelana", "Kembali ke desa",
    "Ke tepi desa",
    "Ikuti jejak sepatu",
    "Lanjut ke jalan Wirasaba",
    "Lentera penjaga",
]
WIRASABA = [
    "Menuju Kota Kaca Wirasaba",
    "Masuk ke distrik pasar",
    "Ke jalan rumah-rumah", "Rumah ketiga dari ujung", "Kotak alat di bawah meja",
    "Keluar ke jalan rumah", "Kembali ke pasar",
    "Ke jalan kaca",
    "Lentera penjaga",
    "Ke alun-alun Suar",
    "Kembali ke jalan kaca",
    "Ke gudang di sisi utara",
    # Setelah Hampa Berzirah jatuh, pemain memilih secara eksplisit (GAME_DESIGN §6.2 no. 12).
    # Jalur "Habisi dia" diuji terpisah di tests/test_babak3.py.
    "Turunkan pedangmu",
    "Keluar lewat gerbang barat",
    "Lentera penjaga",
]
GARAM = [
    "Turun ke Danau Garam",
    "Menyeberang ke ladang garam",
    "Ke bangkai kapal", "Palka yang masih tertutup", "Kembali ke ladang",
    "Ke dermaga rakit",
    "Alur garam di depan rakit",
    "Lentera penjaga",
    "Dorong rakit ke menara",
    "Naik ke ruang buku besar",
    "Buku besar di meja tengah",
    "Naik ke puncak menara",
]
BENTENG = [
    "Turun ke rakit, menuju Benteng Ordo",
    "Lentera penjaga",
    "Naik tangga benteng",
    "Papan jadwal panen",
    "Naik ke tingkat tengah",
    "Ke ruang doa", "Kembali ke asrama",
    "Lentera penjaga",
    "Naik ke tingkat atas",
    "Lentera penjaga",
    "Masuk ke Suar Benteng",
    # Seperti batas Babak 1 (§9.3), ceritanya mengalir langsung: setelah Nirmala jatuh
    # party sudah berdiri di dek Kapal Lentera, awal Babak 3.
    "#stop:babak_2_selesai",
]
SEMUA_BABAK2 = CELAH + DATARAN + HUTAN + WIRASABA + GARAM + BENTENG


def mulai_babak2(data, seed):
    """State seperti tepat setelah Babak 1: party Lv 24 berdiri di Kaki Celah."""
    st = new_game(data)
    st.rng = random.Random(seed)
    st.bara_max = 5
    st.flags.update({"bara", "boss_hutan_kalah", "boss_katak_kalah", "boss_ular_kalah",
                     "boss_rangga_kalah", "boss_penambang_kalah", "boss_penjaga_kalah",
                     "babak_1_selesai", "guntur_hilang", "desa_epilog"})
    st.party[0].level = 24
    st.party[0].xp = xp_to_reach(24)          # tanpa ini Rimba tertinggal dari yang lain
    st.party[0].equipment.update({"senjata": "tongkat_guntur", "zirah": "jubah_penyala"})
    for cid, senjata, zirah in (("sela", "pedang_sumpah", "zirah_kaca_lapis"),
                                ("lintang", "lentera_kaca", "zirah_rantai"),
                                ("bagas", "peluncur_kaca", "zirah_rantai")):
        h = st.join(cid, 24)
        h.equipment.update({"senjata": senjata, "zirah": zirah})
        h.restore()
    st.party[0].restore()
    st.keping = 18000
    for iid, n in (("ramuan_sari", 10), ("cawan_nyala", 8), ("abu_fajar", 5),
                   ("penawar", 5), ("bekal_kemah", 3), ("suku_cadang", 20),
                   ("ramuan_daun", 5), ("minyak_lentera", 10)):
        st.add_item(iid, n)
    st.area_id, st.room_id = "celah_angin", "kaki_celah"
    st.wire()
    return st


def jalankan(steps, seed, tmp_path):
    data = load_data()
    world = load_world(data)
    st = mulai_babak2(data, seed)
    wk = Walker(steps, on_command=make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=tmp_path)
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    return res, st, wk


@pytest.mark.parametrize("seed", [5, 17])
def test_babak2_tamat(seed, tmp_path):
    res, st, wk = jalankan(SEMUA_BABAK2, seed, tmp_path)
    txt = wk.text
    assert res == "berhenti", txt[-3000:]
    assert "AKHIR BABAK 2" in txt
    assert "babak_2_selesai" in st.flags
    # Cerita mengalir langsung ke Babak 3, bukan kembali ke layar judul.
    assert st.area_id == "laut_lupa", f"{st.area_id}/{st.room_id}"
    for flag in ("boss_garuda_kalah", "boss_cacing_kalah", "boss_wirya_kalah",
                 "boss_penjaga_suar_kalah", "kelana_berhenti", "boss_pandansari_kalah",
                 "boss_nirmala_kalah"):
        assert flag in st.flags, f"{flag} belum menyala\n{txt[-2000:]}"
    assert [h.id for h in st.party] == ["rimba", "sela", "lintang", "bagas",
                                        "rangga", "ratih", "kelana"]
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"


def test_party_penuh_tujuh_dengan_cadangan(tmp_path):
    """Babak 2 menutup party: empat aktif, tiga cadangan (GAME_DESIGN §3.1)."""
    res, st, wk = jalankan(SEMUA_BABAK2, 5, tmp_path)
    assert len(st.party) == 7
    assert len(st.active_party) == 4 and len(st.reserve_party) == 3
    assert st.is_active("rimba"), "Rimba pemegang Bara, harus selalu aktif"


def test_semua_boss_babak2_dilalui_dengan_level_wajar(tmp_path):
    """Level party saat tiap boss harus dekat dengan level boss-nya (GAME_DESIGN §2.3)."""
    res, st, wk = jalankan(SEMUA_BABAK2, 5, tmp_path)
    assert 39 <= st.party[0].level <= 48, f"Rimba tamat Babak 2 di Lv {st.party[0].level}"
