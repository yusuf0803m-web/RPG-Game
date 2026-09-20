"""Walkthrough otomatis Babak 2: dari Celah Angin sampai Nirmala jatuh.

Melanjutkan ``tests/test_babak1.py``: keadaan awalnya benar-benar diambil dari
walkthrough Babak 1, yang memang berhenti di Kaki Celah (lihat ``mulai_babak2``).
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.world.explore import Game
from pelita.world.model import load_world
from tests.test_babak1 import SEMUA, BerhentiUji, make_equipper, run_walkthrough
from tests.walker import Walker

#: Daftar belanja Babak 2, diulang di tiap hub. "#beli" melewati yang belum
#: terjangkau dan tidak melakukan apa-apa untuk yang sudah dipakai, jadi mengulang
#: daftarnya aman dan justru meniru pemain: yang tidak kebeli sekarang, dibeli nanti.
BELANJA = [
    "#beli:rimba:senjata:tongkat_kafilah", "#beli:sela:senjata:pedang_kafilah",
    "#beli:lintang:senjata:lentera_kafilah", "#beli:bagas:senjata:peluncur_kafilah",
    "#beli:rangga:senjata:tombak_kafilah", "#beli:ratih:senjata:kecapi_nyanyi",
    "#beli:rimba:zirah:zirah_kafilah", "#beli:sela:zirah:zirah_kafilah",
    "#beli:bagas:zirah:zirah_kafilah", "#beli:rangga:zirah:zirah_kafilah",
    "#beli:kelana:zirah:zirah_kafilah",
    "#beli:lintang:zirah:jubah_pendendang", "#beli:ratih:zirah:jubah_pendendang",
    "#beli:rimba:aksesori:jimat_kafilah", "#beli:sela:aksesori:jimat_kafilah",
    "#beli:rangga:aksesori:jimat_kafilah", "#beli:bagas:aksesori:lensa_juru_kaca",
    "#beli:ratih:aksesori:anting_pendendang", "#beli:kelana:aksesori:sabuk_karat",
]
#: Soket senjata Babak 2, diisi setelah senjatanya benar-benar terpasang.
SOKET = [
    "#pasang:rimba:0:kaca_fajar", "#pasang:rimba:1:kaca_tajam",
    "#pasang:sela:0:kaca_petir", "#pasang:sela:1:kaca_teguh",
    "#pasang:lintang:0:kaca_es", "#pasang:lintang:1:kaca_napas",
    "#pasang:bagas:0:kaca_kilat", "#pasang:bagas:1:kaca_licin",
    "#pasang:rangga:0:kaca_bumi", "#pasang:rangga:1:kaca_teguh",
    "#pasang:ratih:0:kaca_angin", "#pasang:ratih:1:kaca_napas",
    "#pasang:kelana:0:kaca_kelam", "#pasang:kelana:1:kaca_tajam",
]

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
    # Pasar Kafilah Sanggar — hub Babak 2.
    *BELANJA, *SOKET,
    "#stok:ramuan_sari:12", "#stok:cawan_nyala:8", "#stok:abu_fajar:5",
    "#stok:penawar:5", "#stok:bekal_kemah:4", "#stok:suku_cadang:30",
    "Lentera raksasa",
    "#tukar:bara", "#tukar:hp:rimba", "#tukar:soket:rimba",
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
    # Penjaja Padasuara: Ratih baru bergabung di sini, jadi daftarnya diulang.
    *BELANJA, *SOKET,
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
    *BELANJA, *SOKET,
    "#stok:ramuan_sari:16", "#stok:kendi_nyala:5", "#stok:abu_fajar:6",
    "#tukar:bara", "#tukar:hp:sela",
    "Ke alun-alun Suar",
    "Kembali ke jalan kaca",
    "Ke gudang di sisi utara",
    # Senjata & zirah cerita dari peti Wirasaba: temuan dipakai, bukan disimpan.
    "#pakai:bagas:senjata:peluncur_wirasaba", "#pakai:sela:senjata:pedang_wirasaba",
    "#pakai:sela:zirah:zirah_kaca_wirasaba",
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
    # Kelana bergabung di Danau Garam; daftar belanja diulang untuknya.
    *BELANJA, *SOKET,
    "#pakai:lintang:senjata:lentera_garam", "#pakai:kelana:senjata:pedang_ingatan",
    "#pakai:kelana:zirah:zirah_kaca_wirasaba",
    "#stok:ramuan_sari:20", "#stok:abu_fajar:8", "#stok:bekal_kemah:6",
    "#tukar:bara", "#tukar:hp:lintang", "#tukar:soket:sela",
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
    """State persis seperti yang ditinggalkan walkthrough Babak 1 di Kaki Celah.

    Dulu keadaan ini ditulis tangan (Lv 24, perlengkapan pilihan, 18.000 Keping).
    Angka tulis-tangan itu menyimpang begitu Babak 1 dikalibrasi ulang, dan yang
    diuji Babak 2 lalu jadi party yang tidak pernah benar-benar ada. Sekarang
    serah-terimanya dijalankan: Babak 1 memang berhenti tepat di Kaki Celah, dan
    seluruhnya hanya butuh sepersepuluh detik (GAME_DESIGN §9.5).
    """
    res, st, _ = run_walkthrough(SEMUA, seed, Path(tempfile.mkdtemp()))
    assert res == "berhenti", f"Babak 1 seed {seed} tidak sampai ke batas babak: {res}"
    assert (st.area_id, st.room_id) == ("celah_angin", "kaki_celah")
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
