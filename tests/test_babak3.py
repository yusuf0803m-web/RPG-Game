"""Walkthrough otomatis Babak 3: dari dek Kapal Lentera sampai salah satu dari tiga ending.

Melanjutkan pola ``tests/test_babak2.py``. Party dimulai dari keadaan akhir Babak 2
(tujuh anggota Lv 43, berdiri di dek Kapal Lentera) supaya tesnya fokus ke Babak 3.

Yang dibuktikan di sini (syarat penerimaan Tahap 5, GAME_DESIGN §9):

- Babak 3 bisa ditamatkan pada minimal dua seed;
- ketiga ending bisa dicapai, masing-masing lewat segmen mainnya sendiri;
- ending "Mendendangkan" benar-benar TERSEMBUNYI kalau syaratnya belum terpenuhi;
- jalur "Kelana dibunuh" tetap bisa ditamatkan, dengan hanya satu ending tersisa.
"""
from __future__ import annotations

import random

import pytest

from pelita.loader import load_data
from pelita.party import xp_to_reach
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.test_babak1 import BerhentiUji, make_equipper
from tests.walker import Walker


def make_pemain(state, kotak):
    """Perintah Walker tambahan untuk Babak 3.

    ``#kenangan:<id>`` memainkan satu adegan Kenangan di kemah. Ia sengaja lewat
    ``Game.kenangan_tersedia()``, jadi tesnya ikut membuktikan syarat adegan itu
    benar-benar terpenuhi di titik cerita ini — bukan sekadar menyuntikkannya.
    """
    dasar = make_equipper(state)

    def on_command(cmd: str):
        kind, _, arg = cmd.partition(":")
        if kind != "kenangan":
            return dasar(cmd)
        g = kotak[0]
        tersedia = dict(g.kenangan_tersedia())
        assert arg in tersedia, f"Kenangan '{arg}' belum tersedia; yang ada: {sorted(tersedia)}"
        g.mainkan_kenangan(arg, tersedia[arg])
    return on_command

# -- jalur utama ------------------------------------------------------------
KAPAL = [
    "Ke haluan",
    "Berlayar ke laut kabut",
]
PULAU_WAJIB = [
    "Singgah: Pulau Pernikahan",
    "Ke ujung lorong bunga", "Kotak seserahan",
    "Kembali ke lorong bunga", "Kembali ke kapal",
    "Singgah: Pulau Perang",
    "Turun ke parit", "Ransel yang tersandar",
    "Naik dari parit", "Kembali ke kapal",
    "Singgah: Pulau Pasar",
    "Masuk ke lorong lapak", "Lapak alat di ujung lorong",
    "Kembali ke pintu pasar", "Kembali ke kapal",
]
PULAU_KECIL = [
    "Singgah: Pulau Nyanyi", "Kendi di tengah tikar",
    "#kenangan:puncak_ratih",
    "Kembali ke kapal",
    "Singgah: Pulau Sunyi", "Tali jemuran",
    "#kenangan:puncak_lintang",
    "Kembali ke kapal",
]
PULAU_LENTERA = [
    "Singgah: Pulau Lentera",
    "Naik ke puncak",
    "Turun ke jalan lentera",
    "Kembali ke kapal",            # pulau lentera -> laut kabut
    "#kenangan:puncak_rimba",
    "Kembali ke kapal",            # laut kabut -> haluan
    "Kembali ke dek",
    "Nyai Rukmini",                # Bara maks 8
]
PUSAR = [
    "Ke haluan",
    "Berlayar ke laut kabut",
    "Berlayar ke barat, ke Pusar Kabut",
    "Lentera penjaga",
    "Turun ke Kota Adiluhung",
    "Turun ke Lapis Satu",
    "Turun ke Lapis Dua",
    "Turun ke Lapis Tiga",
    "Turun ke Lapis Empat",
    "Turun ke Lapis Lima",
    "Lentera penjaga",
    "Masuk ke Aula Tujuh Suar",
    "Turun ke mulut Sumur",
    "Lentera penjaga terakhir",
    "Turun ke dasar Sumur",
]

#: Jalur utama tanpa pilihan akhir. Tambahkan label ending di belakangnya.
SEMUA_BABAK3 = KAPAL + PULAU_WAJIB + PULAU_KECIL + PULAU_LENTERA + PUSAR

ENDING_NYALA = ["Menyalakan Kembali"]
ENDING_KEMBALI = ["Mengembalikan"]
ENDING_DENDANG = ["Mendendangkan"]


def mulai_babak3(data, seed, kelana_dibunuh: bool = False, lengkap: bool = False):
    """State seperti tepat setelah Babak 2: tujuh anggota Lv 43 di dek Kapal Lentera.

    ``lengkap`` menyiapkan syarat ending rahasia (Kenangan Ratih + 7 Buruan +
    Padasuara selamat) supaya jalur "Mendendangkan" bisa diuji tanpa memainkan
    ulang seluruh konten sampingan Babak 1-2.
    """
    st = new_game(data)
    st.rng = random.Random(seed)
    st.bara_max = 5
    st.flags.update({
        "bara", "babak_1_selesai", "babak_2_selesai", "guntur_hilang", "desa_epilog",
        "boss_hutan_kalah", "boss_katak_kalah", "boss_ular_kalah", "boss_rangga_kalah",
        "boss_penambang_kalah", "boss_penjaga_kalah", "boss_garuda_kalah",
        "boss_cacing_kalah", "boss_wirya_kalah", "boss_penjaga_suar_kalah",
        "boss_pandansari_kalah", "boss_nirmala_kalah", "kelana_berhenti",
        "padasuara_selamat", "ratih_gabung", "sanggar_masuk",
    })
    if kelana_dibunuh:
        st.flags.update({"kelana_dibunuh", "lintang_dingin"})
    st.party[0].level = 43
    st.party[0].xp = xp_to_reach(43)          # tanpa ini Rimba tertinggal jauh dari yang lain
    st.party[0].equipment.update({"senjata": "tongkat_nyanyi", "zirah": "jubah_penyala",
                                  "aksesori": "kalung_bara"})
    anggota = [("sela", "pedang_wirasaba", "zirah_kaca_wirasaba"),
               ("lintang", "lentera_garam", "jubah_pendendang"),
               ("bagas", "peluncur_wirasaba", "zirah_kafilah"),
               ("rangga", "tombak_panji", "zirah_kafilah"),
               ("ratih", "kecapi_tujuh", "jubah_pendendang")]
    if not kelana_dibunuh:
        anggota.append(("kelana", "pedang_ingatan", "zirah_kaca_wirasaba"))
    for cid, senjata, zirah in anggota:
        h = st.join(cid, 43)
        h.equipment.update({"senjata": senjata, "zirah": zirah})
        h.restore()
    st.party[0].restore()
    st.keping = 110000
    for iid, n in (("ramuan_sari", 20), ("ramuan_laut", 10), ("cawan_nyala", 10),
                   ("kendi_nyala", 6), ("abu_fajar", 8), ("penawar", 8),
                   ("bekal_kemah", 12), ("suku_cadang", 40), ("minyak_lentera", 10)):
        st.add_item(iid, n)
    if lengkap:
        st.kenangan.update({"ratih_rimba_1", "ratih_lintang_1", "ratih_kelana_1"})
        for bid in ("buruan_1_kunang", "buruan_2_nelayan", "buruan_3_zirah", "buruan_4_kambing",
                    "buruan_5_hantu", "buruan_6_pohon", "buruan_7_konstruk"):
            st.buruan[bid] = "selesai"
    st.area_id, st.room_id = "laut_lupa", "kapal_dek"
    st.wire()
    return st


def jalankan(steps, seed, tmp_path, **kw):
    data = load_data()
    world = load_world(data)
    st = mulai_babak3(data, seed, **kw)
    kotak: list = []
    wk = Walker(steps, on_command=make_pemain(st, kotak))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=tmp_path)
    kotak.append(g)
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    return res, st, wk


# -- jalur utama ------------------------------------------------------------
@pytest.mark.parametrize("seed", [3, 19])
def test_babak3_tamat(seed, tmp_path):
    """Babak 3 bisa ditamatkan pada dua seed berbeda (uji penerimaan Tahap 5)."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_NYALA, seed, tmp_path)
    txt = wk.text
    assert res == "chapter_end", txt[-4000:]
    assert "babak_3_selesai" in st.flags
    for flag in ("boss_gema_guntur_kalah", "tujuh_penjaga_kalah", "boss_pelita_pertama_kalah"):
        assert flag in st.flags, f"{flag} belum menyala\n{txt[-2500:]}"
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"


def test_level_akhir_sesuai_rentang(tmp_path):
    """Party tamat di rentang §2.4 (Lv 47-52 di Pusar Kabut)."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_NYALA, 3, tmp_path)
    assert 48 <= st.party[0].level <= 56, f"Rimba tamat di Lv {st.party[0].level}"


def test_bara_maks_delapan_membuka_jurus_empat(tmp_path):
    """Jurus Empat butuh Bara maks 8; Nyai Rukmini memberikannya setelah empat pulau."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_NYALA, 3, tmp_path)
    assert st.bara_max == 8
    assert "Meteran Bara melebar" in wk.text


# -- tiga ending ------------------------------------------------------------
def test_ending_menyalakan_punya_segmen_bertahan(tmp_path):
    """Ending 1 bukan sekadar teks: party menahan satu gelombang Kabut sementara
    tujuh Suar menyala (GAME_DESIGN §2.4)."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_NYALA, 3, tmp_path)
    txt = wk.text
    assert res == "chapter_end"
    assert "ending_menyalakan" in st.flags
    assert "Gelombang Kabut A" in txt, txt[-2500:]
    assert "Menara ketujuh menyala" in txt, txt[-2500:]
    assert "MENYALAKAN KEMBALI" in txt


def test_ending_mengembalikan_benar_benar_melucuti(tmp_path):
    """Ending 2 betul-betul mengambil Bara, Kaca, dan Jalur dari state, bukan
    cuma menceritakannya."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_KEMBALI, 3, tmp_path)
    assert res == "chapter_end", wk.text[-3000:]
    assert "ending_mengembalikan" in st.flags
    assert st.bara_max == 0 and "bara" not in st.flags
    assert not st.kaca and not st.kaca_uses
    assert all(h.jalur is None for h in st.party), [(h.id, h.jalur) for h in st.party]
    assert all(not any(k for k in h.kaca) for h in st.party)
    assert "MENGEMBALIKAN" in wk.text


def test_ending_mendendangkan_hanya_lagu_yang_melukai(tmp_path):
    """Ending 3 adalah pertarungan khas: serangan biasa tidak berpengaruh sama sekali,
    hanya Lagu dan Kidung Ratih yang menurunkan meternya."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_DENDANG, 3, tmp_path, lengkap=True)
    txt = wk.text
    assert res == "chapter_end", txt[-4000:]
    assert "ending_mendendangkan" in st.flags
    assert "Tidak berpengaruh pada Kabut Terakhir." in txt, txt[-3000:]
    assert "ia terurai" in txt, txt[-3000:]
    assert "Namaku Sanggabuana" in txt
    assert "MENDENDANGKAN" in txt


def test_ending_ketiga_disembunyikan_total_kalau_syarat_kurang(tmp_path):
    """Kalau syaratnya belum terpenuhi, pilihannya tidak muncul sama sekali —
    bukan "terkunci dengan alasan" (keputusan desain, GAME_DESIGN §9.4)."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_KEMBALI, 3, tmp_path)
    assert "Mendendangkan" not in wk.text, "pilihan rahasia bocor padahal syarat kurang"
    assert "Menyalakan Kembali" in wk.text


# -- jalur "Kelana dibunuh" -------------------------------------------------
def test_jalur_kelana_dibunuh_tetap_bisa_ditamatkan(tmp_path):
    """Membunuh Kelana di Wirasaba menutup ending 1 dan 3, tapi permainan tetap
    bisa ditamatkan lewat "Mengembalikan"."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_KEMBALI, 3, tmp_path, kelana_dibunuh=True)
    txt = wk.text
    assert res == "chapter_end", txt[-4000:]
    assert "ending_mengembalikan" in st.flags
    assert not st.in_party("kelana")
    assert "Menyalakan Kembali" not in txt, "ending 1 harus terkunci kalau Kelana dibunuh"
    assert "Mendendangkan" not in txt, "ending 3 harus terkunci kalau Kelana dibunuh"


def test_kelana_dibunuh_mengubah_lintang(tmp_path):
    """Lintang berubah sepanjang Babak 3 kalau ayahnya dibunuh."""
    res, st, wk = jalankan(SEMUA_BABAK3 + ENDING_KEMBALI, 3, tmp_path, kelana_dibunuh=True)
    assert "Aku baik-baik saja, Sela. Jalan." in wk.text
    assert "Rumahnya masih ingat aku" in wk.text


# -- konten opsional --------------------------------------------------------
def test_pulau_hilang_muncul_setelah_tiga_pulau_dan_boleh_ditinggalkan(tmp_path):
    """Pulau Hilang tidak ada di peta Rukmini: ia baru terlihat setelah tiga pulau
    besar disinggahi, dan party boleh mundur dari superboss-nya (GAME_DESIGN §6.3)."""
    steps = KAPAL + PULAU_WAJIB + [
        "Singgah: pulau yang tidak ada di peta",
        "Naik kembali ke kapal",
        "Kembali ke kapal",
        "@k",
    ]
    res, st, wk = jalankan(steps, 3, tmp_path)
    assert "pulau_hilang_terlihat" in st.flags
    assert "Sang Penenun" in wk.text
    assert "penenun_kalah" not in st.flags, "mundur seharusnya tidak menamatkannya"


def test_pulau_hilang_belum_terlihat_di_pelayaran_pertama(tmp_path):
    res, st, wk = jalankan(KAPAL + ["@k"], 3, tmp_path)
    assert "pulau_hilang_terlihat" not in st.flags
    assert "tidak ada di peta" not in wk.text


def test_buruan_cacing_abu_ibu_bisa_ditamatkan(tmp_path):
    """Buruan tingkat 5 (§6.3): lima segmen, hadiahnya senjata Pelita Pertama."""
    data = load_data()
    world = load_world(data)
    st = mulai_babak3(data, 5)
    for h in st.party:                       # Buruan Lv 55: party harus mengejarnya dulu
        h.level = 55
        h.xp = xp_to_reach(55)
        h.restore()
    for cid, senjata, zirah, jalur in (("rimba", "tongkat_lentera", "zirah_lentera", "rimba_kobaran"),
                                       ("sela", "pedang_laut", "zirah_lentera", "sela_benteng"),
                                       ("lintang", "lentera_laut", "jubah_ingatan", "lintang_badai"),
                                       ("bagas", "peluncur_laut", "zirah_lentera", "bagas_montir")):
        h = st.hero(cid)
        h.equipment.update({"senjata": senjata, "zirah": zirah})
        h.jalur = jalur
        h.restore()
    st.wire()
    for h in st.party:
        h.restore()
    for iid, n in (("ramuan_laut", 20), ("abu_pagi", 10), ("guci_nyala", 10)):
        st.add_item(iid, n)
    st.buruan["buruan_8_cacing_ibu"] = "aktif"
    st.area_id, st.room_id = "dataran_abu", "sarang_cacing"
    wk = Walker([], on_command=make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True,
             auto_choice=False, save_dir=tmp_path)
    g.lawan_buruan("buruan_8_cacing_ibu")
    assert st.buruan["buruan_8_cacing_ibu"] == "selesai", wk.text[-2000:]
    assert st.has_item("tongkat_pelita_pertama")
    assert "menutup lukanya" in wk.text or st.count("serpihan_ingatan") >= 3
