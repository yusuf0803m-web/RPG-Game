"""Konten sampingan Tahap 7: dungeon opsional, dan bukti bahwa ia BOLEH DILEWATI.

Syarat penerimaan Tahap 7 (GAME_DESIGN §9.6) ada dua, dan yang kedua sama
pentingnya dengan yang pertama:

1. tiap dungeon opsional bisa ditamatkan sungguhan — dimainkan dari keadaan yang
   benar-benar ditinggalkan jalur utama, bukan dari fixture karangan (§9.5);
2. jalur utama tidak menyentuhnya sama sekali, dan tidak ada yang rusak kalau
   pemain memilih lewat.

Keadaan awalnya karena itu selalu **dijalankan**: walkthrough Babak 1 dimainkan
sampai titik tempat dungeonnya terbuka, lalu party berbelok ke sana.
"""
from __future__ import annotations

import random
import re
import tempfile
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.test_babak1 import AREA1, DANAU, LORONG, RAWA, TENGARA_1, BerhentiUji, make_equipper
from tests.walker import Walker

# -- Gua Bawah Danau (Babak 1, Lv 14–17) ------------------------------------
#: Jalur utama sampai Balai Arsip. Di situlah buku "DAFTAR TITIPAN DASAR" dibaca,
#: dan ``arsip_dibaca`` — syarat pintu gua — menyala.
SAMPAI_ARSIP = AREA1 + RAWA + DANAU + TENGARA_1 + LORONG

#: Balik ke Danau Cermin lewat perahu, lalu turun sampai bossnya.
GUA_DANAU = [
    "Kembali ke Pasar Bawah", "Ke dermaga kota", "Perahu kembali ke Desa Apung",
    "Naik rakit", "Ke pulau batu", "Turun ke gua",
    "Turun ke celah di dasar sarang",
    "Lentera penjaga", "Turun ke tangga air",
    "Ke ceruk jala", "Jala yang paling bawah", "Kembali ke tangga air",
    "Turun ke ladang kendi", "Batu berukir",
    # Teka-teki tiga kendi: hanya yang "tidak diambil dari siapa pun" yang diterima.
    "Cekungan batu", "hujan",
    "Cekungan batu", "jalan yang belum",
    "Cekungan batu", "lagu tanpa syair",
    "Lewat pintu tanpa gagang",
    "Peti bersegel", "Lentera penjaga di antara peti", "Ke ujung palka",
]


def datar(teks: str) -> str:
    """Transkrip terminal dibungkus per 66 kolom, jadi satu kalimat bisa terpotong
    newline di tengah. Asersi teks selalu dijalankan pada versi yang diratakan."""
    return re.sub(r"\s+", " ", teks)


def jalankan_babak1(steps, seed):
    """Jalankan walkthrough Babak 1 (atau potongannya) dari permainan baru."""
    data = load_data()
    world = load_world(data)
    st = new_game(data)
    st.rng = random.Random(seed)
    wk = Walker(steps, on_command=make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=Path(tempfile.mkdtemp()))
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    return res, st, wk


@pytest.fixture(scope="module")
def gua():
    """Satu kali main sampai Pak Padmo jatuh; dipakai beberapa tes sekaligus."""
    return jalankan_babak1(SAMPAI_ARSIP + GUA_DANAU + ["#stop:gua_boss_kalah"], 11)


@pytest.mark.parametrize("seed", [11, 23])
def test_gua_bawah_danau_bisa_ditamatkan(seed, tmp_path):
    """Dua seed, dari permainan baru sampai Juru Kaca Tenggelam jatuh."""
    res, st, wk = jalankan_babak1(SAMPAI_ARSIP + GUA_DANAU + ["#stop:gua_boss_kalah"], seed)
    assert res == "berhenti", wk.text[-3000:]
    assert (st.area_id, st.room_id) == ("gua_danau", "dasar_menelan")
    assert "gua_boss_kalah" in st.flags
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"


def test_hadiah_gua_benar_benar_masuk_ke_state(gua):
    """Kaca Endap dan Serpihan bukan cuma diceritakan."""
    _, st, _ = gua
    assert st.kaca.get("kaca_endap") == 1
    assert st.count("tali_penyelam") == 1
    assert st.count("serpihan_ingatan") >= 2      # peti bersegel + Pak Padmo


#: Aksi bernama Pak Padmo. Kalau tidak satu pun muncul, pola fasenya tidak pernah
#: dimainkan — lihat ``test_boss_gua_benar_benar_memainkan_polanya``.
POLA_PADMO = ("Dorong Peti", "Tenggelamkan", "Ingat Air", "Isi Kendi", "Panggil Kendi")


def laga_boss(wk, nama: str) -> str:
    """Potongan transkrip satu pertarungan boss, dari kemunculan sampai hasilnya."""
    awal = wk.text.find(f"{nama} muncul!")
    assert awal > 0, f"'{nama}' tidak pernah muncul"
    sisa = wk.text[awal:]
    return sisa[: sisa.find("Hasil:")]


def test_boss_gua_melewati_dua_fasenya_dan_melukai_party(gua):
    """Pelajaran §9.5: fase yang tidak pernah menyala sama saja dengan tidak ditulis,
    dan boss yang tidak pernah menurunkan HP party tidak diingat siapa pun."""
    _, _, wk = gua
    laga = laga_boss(wk, "Juru Kaca Tenggelam")
    assert "Ia berhenti memilah" in datar(laga), "fase 2 tidak pernah tercapai"
    assert "tumbang!" in laga, "tidak ada satu pun anggota yang sempat terdesak"


def test_boss_gua_benar_benar_memainkan_polanya(gua):
    """Regresi dari bug Tahap 7: Pak Padmo pernah bertindak SATU kali dalam tujuh ronde.

    ``ai.py`` membuat musuh yang Goyah selalu jatuh ke serangan biasa, dan bossnya
    dulu punya dua kelemahan yang kebetulan keduanya ada di tangan party Babak 1
    (Petir Lintang dan Cahaya Rimba). Ia Goyah tiap ronde, jadi Tenggelamkan,
    Panggil Kendi, dan Ingat Air tidak pernah dimainkan sekali pun — mekanik yang
    ditulis tapi tidak pernah ada. Sekarang kelemahannya satu per fase.
    """
    _, _, wk = gua
    laga = laga_boss(wk, "Juru Kaca Tenggelam")
    dipakai = [nama for nama in POLA_PADMO if f"memakai {nama}" in laga]
    assert len(dipakai) >= 2, (
        f"Pak Padmo hanya memainkan {dipakai} dari polanya; sisanya jadi serangan biasa.")


def test_pintu_gua_tertutup_sebelum_arsip_dibaca():
    """Gua baru terbuka setelah buku titipan dibaca di Balai Arsip (§2.2)."""
    # Jalur utama memang sudah lewat Gua Sarang jauh sebelum Arsip; di titik itu
    # pintu ke bawah harus masih tertutup.
    sampai_gua = DANAU[: DANAU.index("Turun ke gua") + 1]
    res, st, wk = jalankan_babak1(
        AREA1 + RAWA + sampai_gua + ["Turun ke celah di dasar sarang", "@k"], 11)
    assert "arsip_dibaca" not in st.flags
    assert "(terhalang)" in wk.text, "pintu gua seharusnya tampil sebagai terhalang"
    assert "celah selebar pintu" in datar(wk.text), "teks pintu terkunci tidak muncul"
    assert (st.area_id, st.room_id) == ("danau_cermin", "sarang_ular"), "pemain ikut turun"
    assert "gua_masuk_adegan" not in st.flags


def test_teka_teki_kendi_menolak_kendi_yang_punya_pemilik():
    """Kendi yang isinya milik seseorang mengosongkan cekungan — dan tekanya tetap
    bisa diselesaikan sesudahnya (tidak ada jalan buntu)."""
    salah = [
        "Kembali ke Pasar Bawah", "Ke dermaga kota", "Perahu kembali ke Desa Apung",
        "Naik rakit", "Ke pulau batu", "Turun ke gua", "Turun ke celah di dasar sarang",
        "Turun ke tangga air", "Turun ke ladang kendi",
        "Cekungan batu", "hujan",
        "Cekungan batu", "sebuah nama",          # salah: mengosongkan ketiganya
        "Cekungan batu", "hujan",
        "Cekungan batu", "jalan yang belum",
        "Cekungan batu", "lagu tanpa syair",
        "#stop:gua_cekungan_terbuka",
    ]
    res, st, wk = jalankan_babak1(SAMPAI_ARSIP + salah, 11)
    assert "gua_cekungan_terbuka" in st.flags
    assert "kembali ke lantai" in datar(wk.text), "kendi yang salah seharusnya dikembalikan"


def test_gua_boleh_dilewati_jalur_utama_tidak_menyentuhnya():
    """Syarat konten opsional: walkthrough Babak 1 lengkap tidak pernah masuk gua,
    dan tetap tamat."""
    from tests.test_babak1 import SEMUA
    res, st, wk = jalankan_babak1(SEMUA, 11)
    assert res == "berhenti"
    assert "babak2_mulai" in st.flags, "Babak 1 tidak sampai tamat"
    for flag in ("gua_masuk_adegan", "gua_cekungan_terbuka", "gua_boss_kalah"):
        assert flag not in st.flags, f"jalur utama menyentuh gua opsional: {flag}"
    assert "kaca_endap" not in st.kaca
