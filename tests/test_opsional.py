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

import json
import random
import re
import tempfile
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.party import xp_to_reach
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.test_babak1 import (AREA1, DANAU, LORONG, RAWA, SEMUA, TENGARA_1, BerhentiUji,
                                make_equipper)
from tests.test_babak2 import SEMUA_BABAK2
from tests.test_babak2 import jalankan as jalankan_babak2
from tests.test_babak3 import KAPAL, make_pemain, mulai_babak3
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


# -- Reruntuhan Suar Ketiga (Babak 2 opsional, Lv 45–48) --------------------
#: Dibuka setelah Nirmala jatuh (§2.3), jadi praktis dimainkan saat party berlayar
#: kembali ke Danau Garam di Babak 3. Pemainnya berbelanja dulu di palka Kapal
#: Lentera — pemain penimbun membuat pengukuran bohong (§9.5).
BELANJA_KAPAL = [x for x in KAPAL if x.startswith("#")]
SUAR_KETIGA = BELANJA_KAPAL + [
    "Ke haluan", "Berlayar kembali ke Danau Garam",
    "Dorong rakit ke menara",
    "Turun ke retakan di bawah kaki menara",
    "Lentera penjaga", "Turun ke tangga abad", "Ke ruang daftar",
    "Dinding timur", "Dinding barat",
    "Ke bilik di sisi ruang", "Buku yang terbuka", "Kembali ke ruang daftar",
    "Ke serambi Suar", "Cekungan bekas duduk", "Lentera penjaga di serambi",
    "Buka pintu perunggu",
]

#: Aksi bernama Pelita Ketiga. Ia memutar ketujuh elemen Suar satu per satu;
#: kalau cuma satu-dua yang muncul, rodanya tidak berputar.
RODA_SUAR = ("Lidah Suar", "Embun Suar", "Kejut Suar", "Embus Suar",
             "Getar Suar", "Bayang Suar", "Nyala Penuh", "Serap Nyala")


def jalankan_babak3(steps, seed, **kw):
    """Keadaan awal diambil dari Babak 2 yang benar-benar dimainkan (§9.5)."""
    data = load_data()
    world = load_world(data)
    st = mulai_babak3(data, seed, **kw)
    kotak: list = []
    wk = Walker(steps, on_command=make_pemain(st, kotak))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=Path(tempfile.mkdtemp()))
    kotak.append(g)
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    return res, st, wk


@pytest.fixture(scope="module")
def suar3():
    return jalankan_babak3(SUAR_KETIGA + ["#stop:suar3_boss_kalah"], 3)


@pytest.mark.parametrize("seed", [3, 19])
def test_suar_ketiga_bisa_ditamatkan(seed):
    res, st, wk = jalankan_babak3(SUAR_KETIGA + ["#stop:suar3_boss_kalah"], seed)
    assert res == "berhenti", wk.text[-3000:]
    assert "suar3_boss_kalah" in st.flags
    assert st.kaca.get("kaca_sumbu") == 1
    assert st.quests.get("daftar_suar_ketiga") == "selesai"
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"


def test_pelita_ketiga_memutar_roda_tujuh_elemennya(suar3):
    """Regresi: bossnya pernah hanya sempat memainkan DUA aksi bernama dalam tujuh
    ronde, karena party Babak 3 memukul kelemahannya tiap ronde dan musuh yang Goyah
    selalu jatuh ke serangan biasa (ai.py). Roda tujuh elemen adalah seluruh isi boss
    ini, jadi ia dibuat kebal Goyah — kelemahannya tetap berguna lewat Ketahanan,
    Pecah, dan pengali damage (§9.6)."""
    _, _, wk = suar3
    laga = laga_boss(wk, "Pelita Ketiga")
    diputar = [n for n in RODA_SUAR if f"memakai {n}" in laga]
    assert len(diputar) >= 4, f"roda Suar cuma berputar ke {diputar}"
    assert "Ia berhenti menghitung giliran" in datar(laga), "fase 2 tidak pernah tercapai"


def test_suar_ketiga_tertutup_sebelum_nirmala_jatuh():
    """Sebelum Suar Benteng padam, menaranya masih mengapung dan tidak ada retakan."""
    res, st, wk = jalankan_babak1(
        AREA1 + RAWA + DANAU + TENGARA_1 + LORONG + ["#stop:arsip_dibaca"], 11)
    assert "boss_nirmala_kalah" not in st.flags
    # Ruangnya memang belum terjangkau di Babak 1; yang dikunci di sini syaratnya.
    world = load_world(load_data())
    pintu = [e for e in world.area("danau_garam").room("menara_terapung").exits
             if e.to == "retak_kaki"]
    assert pintu and pintu[0].cond == ["boss_nirmala_kalah"]
    assert not st.check(pintu[0].cond)


def test_suar_ketiga_boleh_dilewati_jalur_utama_tidak_menyentuhnya():
    """Babak 3 tamat tanpa sekali pun turun ke reruntuhan."""
    from tests.test_babak3 import ENDING_NYALA, SEMUA_BABAK3
    res, st, wk = jalankan_babak3(SEMUA_BABAK3 + ENDING_NYALA, 3)
    assert res == "chapter_end", wk.text[-2500:]
    for flag in ("suar3_masuk_adegan", "suar3_boss_kalah"):
        assert flag not in st.flags, f"jalur utama menyentuh Suar Ketiga: {flag}"
    assert "kaca_sumbu" not in st.kaca


# -- Pulau Hilang (Babak 3 opsional) ----------------------------------------
#: §5.7 menyebut Pulau Hilang sebagai dungeon opsional Babak 3, tapi sampai Tahap 6
#: ia cuma SATU ruang berisi superboss. Sekarang lima ruang, dan Sang Penenun jadi
#: puncaknya, bukan pintu masuknya.
PULAU_HILANG = BELANJA_KAPAL + [
    "Ke haluan", "Berlayar ke laut kabut",
    # Pulau Hilang baru muncul di peta setelah tiga pulau besar disinggahi.
    "Singgah: Pulau Pernikahan", "Kembali ke kapal",
    "Singgah: Pulau Perang", "Kembali ke kapal",
    "Singgah: Pulau Pasar", "Kembali ke kapal",
    "Singgah: pulau yang tidak ada di peta",
    "Ikuti benang ke dalam pulau",
    "Alat tenun yang sedang bekerja",
    "Ke gudang di belakang rumah tenun",
    "Rak gulungan pola", "Gulungan berlabel",
    "Ke lorong benang di ujung gudang",
    "Barang-barang di bawah lentera", "Lentera penjaga di dinding lorong",
    "Naik mengikuti berkas benang",
]


@pytest.fixture(scope="module")
def pulau():
    """Masuk sampai puncak, lalu MUNDUR: Sang Penenun Lv 58 memang di atas party."""
    return jalankan_babak3(PULAU_HILANG + ["Naik kembali ke kapal", "@k"], 3)


def test_pulau_hilang_punya_lima_ruang_dengan_penenun_di_puncaknya():
    """§5.7 menjanjikan dungeon, bukan satu ruang berisi boss."""
    world = load_world(load_data())
    laut = world.area("laut_lupa")
    ruang = ["pulau_hilang", "rumah_tenun", "gudang_pola", "lorong_benang", "puncak_tenun"]
    for rid in ruang:
        assert rid in laut.rooms, rid
    assert laut.room("pulau_hilang").on_enter != "superboss_penenun", \
        "Penenun seharusnya di puncak, bukan di pantai"
    assert laut.room("puncak_tenun").on_enter == "superboss_penenun"


def test_gudang_pola_menunjukkan_lembah_larung_belum_ditenun(pulau):
    """Beat inti dungeon ini: Sang Penenun menyimpan rancangan pulau yang BELUM ada,
    dan salah satunya desa Rimba."""
    _, st, wk = pulau
    assert "pola_larung_dilihat" in st.flags
    assert st.quests.get("pola_pulau_hilang") == "aktif"
    assert "Mercusuarnya baru menyala tahun ini" in datar(wk.text)


def test_pulau_hilang_bisa_dijelajahi_tanpa_melawan_penenun(pulau):
    """Superboss Lv 58 tidak wajib: pemain boleh masuk, membaca polanya, dan pulang."""
    res, st, wk = pulau
    assert "penenun_kalah" not in st.flags
    assert st.count("serpihan_ingatan") >= 3, "isi dungeonnya tetap memberi hasil"
    assert "Hadapi Sang Penenun" in wk.text, "pilihan melawan seharusnya ditawarkan"


def test_penenun_masih_bisa_dikalahkan_dari_puncak():
    """Jalur lima ruangnya tidak merusak superbossnya sendiri.

    Dilawan di titik pemain yang wajar: sesudah seluruh pulau Laut Lupa dan meteran
    Bara melebar ke 8, sebelum turun ke Pusar Kabut. Lv 58 memang di atas party yang
    baru tiba di Babak 3 — party seperti itu kalah, dan itu maksudnya.
    """
    from tests.test_babak3 import KAPAL, PULAU_KECIL, PULAU_LENTERA, PULAU_WAJIB
    sebelum_pusar = KAPAL + PULAU_WAJIB + PULAU_KECIL + PULAU_LENTERA
    res, st, wk = jalankan_babak3(sebelum_pusar + [
        "Ke haluan", "Berlayar ke laut kabut",
        "Singgah: pulau yang tidak ada di peta",
        "Ikuti benang ke dalam pulau",
        "Ke gudang di belakang rumah tenun",
        "Rak gulungan pola", "Gulungan berlabel",
        "Ke lorong benang di ujung gudang", "Lentera penjaga di dinding lorong",
        "Naik mengikuti berkas benang",
        "Hadapi Sang Penenun", "#stop:penenun_kalah",
    ], 3)
    assert "penenun_kalah" in st.flags, wk.text[-2500:]
    assert st.kaca.get("kaca_penenun") == 1
    assert st.quests.get("pola_pulau_hilang") == "selesai"


def test_pulau_hilang_boleh_dilewati_jalur_utama_tidak_menyentuhnya():
    from tests.test_babak3 import ENDING_NYALA, SEMUA_BABAK3
    res, st, wk = jalankan_babak3(SEMUA_BABAK3 + ENDING_NYALA, 19)
    assert res == "chapter_end"
    for flag in ("pulau_pantai_adegan", "pola_larung_dilihat", "penenun_kalah"):
        assert flag not in st.flags, f"jalur utama menyentuh Pulau Hilang: {flag}"


# -- Tiga kontrak Buruan sisa (8 -> 11, §5.7) -------------------------------
#: (id, level, aksi bernama yang HARUS muncul). Daftar aksi itu bukan hiasan: dua
#: dari tiga target ini sempat tidak pernah memainkan satu pun mekaniknya — lihat
#: ``test_buruan_baru_memainkan_mekanik_khasnya``.
BURUAN_BARU = [
    ("buruan_9_gerobak", 41, ("Tegangkan Rantai", "Seret")),
    ("buruan_10_penghitung", 50, ("Panggil Gema Kalian", "Tarik Ingatan")),
    ("buruan_11_kedelapan", 53, ("Isi Rongga Kedelapan", "Nyala Kedelapan")),
]


def lawan_buruan(bid: str, level: int, seed: int = 3):
    """Party dinaikkan ke level buruannya, seperti pemain yang mengejar kontrak itu
    setelah siap (pola yang sama dengan ``test_buruan_cacing_abu_ibu_bisa_ditamatkan``)."""
    data = load_data()
    world = load_world(data)
    st = mulai_babak3(data, seed)
    for h in st.party:
        h.level = level
        h.xp = xp_to_reach(level)
        h.restore()
    st.buruan[bid] = "aktif"
    wk = Walker([])
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=True, auto_menus=True, save_dir=Path(tempfile.mkdtemp()))
    g.lawan_buruan(bid)
    return st, wk


@pytest.fixture(scope="module")
def buruan_baru():
    return {bid: lawan_buruan(bid, lv) for bid, lv, _ in BURUAN_BARU}


def test_papan_buruan_genap_sebelas_sesuai_pembagian_babak():
    """§5.7: 11 target — 3 Babak 1, 5 Babak 2, 3 Babak 3."""
    world = load_world(load_data())
    assert len(world.buruan) == 11
    lv = sorted(b["level"] for b in world.buruan.values())
    assert sum(1 for x in lv if x <= 22) == 3, f"Babak 1: {lv}"
    assert sum(1 for x in lv if 23 <= x <= 43) == 5, f"Babak 2: {lv}"
    assert sum(1 for x in lv if x >= 44) == 3, f"Babak 3: {lv}"


@pytest.mark.parametrize("bid,level,_aksi", BURUAN_BARU)
def test_buruan_baru_bisa_ditamatkan_dan_membayar(bid, level, _aksi, buruan_baru):
    st, wk = buruan_baru[bid]
    assert st.buruan[bid] == "selesai", wk.text[-2000:]
    world = load_world(load_data())
    hadiah = world.buruan[bid]["hadiah"]
    for iid, n in hadiah.get("item", {}).items():
        assert st.count(iid) >= n, f"{bid}: {iid} tidak masuk inventori"
    for kid in hadiah.get("kaca", []):
        assert st.kaca.get(kid, 0) >= 1, f"{bid}: {kid} tidak diberikan"


@pytest.mark.parametrize("bid,level,aksi", BURUAN_BARU)
def test_buruan_baru_memainkan_mekanik_khasnya(bid, level, aksi, buruan_baru):
    """§5.7 menjanjikan "mekanik unik" per Buruan, dan mekanik yang tidak pernah
    dimainkan sama saja dengan tidak ada.

    Dua hal membuat ketiganya nyaris mute waktu pertama ditulis:
    1. party Babak 2-3 bisa mem-Goyah sesuka hati, dan ``ai.py`` mengganti aksi
       musuh yang Goyah dengan serangan biasa — jadi elit yang identitasnya urutan
       terskrip dibuat kebal Goyah (kelemahan tetap dibayar lewat Ketahanan/PECAH);
    2. urutan isi->tembak tidak bisa dijamin tabel bobot acak, jadi keduanya pindah
       ke pola fase seperti Penjaga Mercusuar.
    """
    _, wk = buruan_baru[bid]
    hilang = [a for a in aksi if f"memakai {a}" not in wk.text]
    assert not hilang, f"{bid} tidak pernah memainkan: {hilang}"


def test_kaca_bara_akhirnya_punya_sumber():
    """``kaca_bara`` sudah ada di data sejak Tahap 3 tapi tidak pernah bisa didapat:
    tidak dijual, bukan hadiah apa pun, dan bukan penukaran Serpihan."""
    world = load_world(load_data())
    sumber = [bid for bid, b in world.buruan.items()
              if "kaca_bara" in b.get("hadiah", {}).get("kaca", [])]
    assert sumber, "kaca_bara masih tidak bisa didapat pemain"


# -- Rantai "Pendendang yang Hilang" (side quest 4 bagian, §5.7) ------------
def _sisip(langkah, setelah, tambahan):
    out = list(langkah)
    i = out.index(setelah) + 1
    out[i:i] = tambahan
    return out


def langkah_rantai_babak2():
    """SEMUA_BABAK2 dengan tiga bagian pertama rantai disisipkan di tempatnya.

    Bagian 1 butuh Ratih, dan Ratih baru bergabung di Tepi Desa — jadi party
    kembali sebentar ke Balai Nyanyi sesudahnya, persis seperti pemain yang baru
    dapat anggota baru lalu balik bertanya ke tetuanya.
    """
    l = list(SEMUA_BABAK2)
    l = _sisip(l, "Ke tepi desa", [
        "Kembali ke desa", "Ke Balai Nyanyi", "Papan sahutan",
        "Kembali ke desa", "Ke tepi desa",
    ])
    l = _sisip(l, "Masuk ke distrik pasar", ["Hampa yang bersenandung"])
    l = _sisip(l, "Menyeberang ke ladang garam", ["Pemungut garam"])
    return l


@pytest.fixture(scope="module")
def rantai():
    """Tiga bagian di Babak 2 dimainkan sungguhan, lalu bagian empat di Laut Lupa."""
    data = load_data()
    world = load_world(data)
    res, st, wk2 = jalankan_babak2(langkah_rantai_babak2(), 5, Path(tempfile.mkdtemp()))
    assert res == "berhenti", wk2.text[-2500:]
    assert st.quests.get("pendendang_hilang") == "garam", st.quests
    kotak: list = []
    wk = Walker([
        "Ke haluan", "Berlayar ke laut kabut",
        "Singgah: Pulau Nyanyi", "Tikar melingkar",
        "#stop:pendendang_terkumpul",
    ], on_command=make_pemain(st, kotak))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=Path(tempfile.mkdtemp()))
    kotak.append(g)
    try:
        g.run()
    except BerhentiUji:
        pass
    return st, wk2, wk


def test_rantai_pendendang_melewati_keempat_bagiannya(rantai):
    """Padasuara -> Wirasaba -> Danau Garam -> Laut Lupa, tiap bagian di babaknya."""
    st, wk2, wk = rantai
    assert st.quests.get("pendendang_hilang") == "selesai"
    assert "pendendang_terkumpul" in st.flags
    for frasa in ("Ini papan sahutan", "Itu sahutan Karangwuni",
                  "Ordo ambil suaranya, bukan orangnya"):
        assert frasa in datar(wk2.text), f"bagian rantai tidak dimainkan: {frasa}"
    assert "tiga desa yang sudah dihabisi Ordo masih menyahut" in datar(wk.text)


def test_rantai_pendendang_jadi_syarat_ending_mendendangkan():
    """§5.7 menyebut rantai ini syarat ending 3; sampai Tahap 6 syaratnya belum
    bisa dipasang karena rantainya belum ada."""
    world = load_world(load_data())
    teks = json.dumps(world.area("pusar_kabut").scripts, ensure_ascii=False)
    assert "pendendang_terkumpul" in teks

    data = load_data()
    st = mulai_babak3(data, 3)          # tanpa lengkap=True: syaratnya belum terpenuhi
    assert not st.check(["pendendang_terkumpul"])


def test_rantai_pendendang_boleh_dilewati():
    """Walkthrough Babak 2 biasa tidak menyentuh rantainya, dan tetap tamat."""
    res, st, wk = jalankan_babak2(list(SEMUA_BABAK2), 5, Path(tempfile.mkdtemp()))
    assert res == "berhenti"
    assert "pendendang_hilang" not in st.quests
    assert "pendendang_terkumpul" not in st.flags


# -- Side quest Babak 1 (3 baru, §5.7 menjanjikan 6) ------------------------
def langkah_sq_babak1():
    """SEMUA (Babak 1) dengan tiga side quest baru disisipkan di tempatnya.

    Ketiganya sengaja disisipkan ke jalur yang memang dilewati pemain, bukan
    dijalankan dari fixture terpisah: yang diuji bukan cuma skripnya jalan, tapi
    bahwa urutannya masuk akal dari kursi pemain.
    """
    l = list(SEMUA)
    # Dua Belas Lentera: sesudah Ular Cermin jatuh, di Desa Apung. Jangkarnya
    # "#equip:...kalung_bara" karena "Tetua Baruna" muncul dua kali — yang pertama
    # jauh sebelum ularnya dikalahkan.
    l = _sisip(l, "#equip:rimba:aksesori:kalung_bara", [
        "Kembali ke dermaga", "Lentera jembatan yang padam",
        "Sisi danau", "Lentera di rakit paling ujung",
        "Kembali ke dermaga", "Lentera jembatan yang padam",
        "Rumah Tetua",
    ])
    # Pesanan Mpu Sarwa: di kios Tukang Kaca Tengara, sesudah Lorong Bawah.
    l = _sisip(l, "Naik ke Balai Arsip", [
        "Kembali ke Pasar Bawah",
        "Kios Tukang Kaca", "Pesanan yang belum selesai",
        "#stok:suku_cadang:15",
        "Pesanan yang belum selesai",
        "Kembali ke Pasar Bawah", "Ke Balai Arsip",
    ])
    # Yang Menunggu di Gerbang Utara: kenalan di gerbang, kotaknya di Lorong Tengah.
    l = _sisip(l, "Ke Gerbang Utara", ["Anak perempuan yang duduk"])
    l = _sisip(l, "Turun dengan lift", [
        "Kotak kayu hijau",
        "Naik lift ke ruang lift", "Kembali ke lorong atas", "Kembali ke mulut tambang",
        "Turun kembali ke Gerbang Utara", "Anak perempuan yang duduk",
        "Mendaki ke Tambang", "Masuk ke lorong atas", "Ke ruang lift",
        "Turun dengan lift",
    ])
    return l


@pytest.fixture(scope="module")
def sq_babak1():
    return jalankan_babak1(langkah_sq_babak1(), 11)


def test_tiga_side_quest_babak1_bisa_diselesaikan(sq_babak1):
    res, st, wk = sq_babak1
    assert res == "berhenti", wk.text[-3000:]
    for qid in ("duabelas_lentera", "pesanan_sarwa", "penunggu_gerbang"):
        assert st.quests.get(qid) == "selesai", f"{qid}: {st.quests.get(qid)}"
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"


def test_side_quest_babak1_membayar_dan_tetap_tamat(sq_babak1):
    res, st, wk = sq_babak1
    assert "babak2_mulai" in st.flags, "Babak 1 tetap harus tamat"
    assert st.kaca.get("kaca_sabar") == 1        # upah Mpu Sarwa
    assert "Sembilan keping untuk sembilan tahun" in datar(wk.text)
    assert "Aku sudah tahu, kok. Aku cuma belum boleh tahu" in datar(wk.text)


def test_side_quest_babak1_boleh_dilewati():
    """Walkthrough Babak 1 biasa tidak menyentuh satu pun dari ketiganya."""
    res, st, wk = jalankan_babak1(list(SEMUA), 11)
    assert res == "berhenti"
    for qid in ("duabelas_lentera", "pesanan_sarwa", "penunggu_gerbang"):
        assert qid not in st.quests, f"jalur utama menyentuh {qid}"
