"""Walkthrough otomatis seluruh Babak 1: dari prolog sampai Mercusuar menyala.

Pemain otomatis mengikuti jalur terpendek, beristirahat di lentera sebelum boss,
memasang senjata dari peti, dan bertarung dengan kebijakan "pintar".
Tes ini adalah uji penerimaan Tahap 2 (GAME_DESIGN §9).
"""
import random

import pytest

from pelita.loader import load_data
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.walker import Walker

AREA1 = [
    "Masuk ke jalan desa", "Rumah Pak Guntur", "Peti minyak", "Tikar tidur",
    "Keluar ke jalan desa", "Gerbang barat", "Masuk ke Hutan",
    "Ikuti jalan", "Terus ke pohon", "Sesuatu di akar", "Kembali ke jalan setapak", "Terus ke pohon",
    "Lewati pohon", "Lentera penjaga di batu", "Naik ke tepi",
    "Kembali ke lembah", "Kembali ke pohon", "Kembali ke jalan setapak", "Kembali ke tepi hutan",
    "Kembali ke gerbang barat", "Kembali ke jalan desa", "Balai desa",
    "Keluar ke jalan desa", "Gerbang barat", "Masuk ke Hutan", "Ikuti jalan", "Terus ke pohon",
    "Lewati pohon", "Naik ke tepi", "Menyusuri tepi kabut",
]
RAWA = [
    "Lentera penjaga", "Menyeberang jembatan", "Turun ke rawa dangkal", "Ke gubuk nelayan", "Peti di bawah tikar",
    "#equip:rimba:senjata:tongkat_perunggu",
    "Kembali ke rawa dangkal", "Ke tanah tinggi", "Batu berukir", "Lentera Selatan", "Lentera Utara", "Lentera Tengah",
    "Lentera penjaga", "Menembus kabut", "Masuk ke inti Suar",
    "Lentera penjaga", "Keluar ke kolam", "Lentera penjaga", "Jalan setapak utara ke Danau",
]
DANAU = [
    "Ke dermaga Desa Apung", "Rumah Tetua", "Tetua Baruna", "Nanti saja",
    "Kembali ke dermaga", "Sisi danau", "Tatap permukaan", "Kembali ke dermaga",
    "Naik rakit", "Ke pulau batu", "Peti yang terjepit",
    "#equip:sela:senjata:pedang_pengawal", "#equip:lintang:senjata:lentera_rawa",
    "Lentera penjaga", "Turun ke gua",
    "Kembali ke pulau batu", "Kembali ke tengah danau", "Kembali ke dermaga", "Rumah Tetua", "Tetua Baruna",
    "#equip:rimba:aksesori:kalung_bara",
    "Kembali ke dermaga", "Perahu ke Ibukota",
]
TENGARA_1 = [
    "Lentera penjaga", "Masuk ke Pasar Bawah", "Pak Pos Harun", "Kami antar", "Juragan Salim", "Baik, malam ini",
    "Penginapan", "Mbak Wulan", "Tidak sekarang", "Kembali ke Pasar Bawah",
    "Ke Gerbang Istana", "Kembali ke Pasar Bawah", "Ke Distrik Sunyi", "Nenek Asih", "Lentera penjaga",
    "Masuk ke Lorong Bawah",
]
LORONG = [
    "Ke ruang tuas", "Tiga tuas besi", "Tarik tuas kiri", "Tiga tuas besi", "Tarik tuas tengah", "Tiga tuas besi", "Tarik tuas kanan",
    "Lentera penjaga", "Menyelam ke lorong dalam", "Suara mengeong", "Peti pengawal",
    "#equip:sela:zirah:zirah_rantai", "#equip:rimba:senjata:tongkat_kaca",
    "Ke ruang pompa", "Lentera penjaga", "Naik tangga ke gerbang Arsip",
    "Naik ke Balai Arsip",
]
TENGARA_2 = [
    "Lentera penjaga", "Kembali ke Pasar Bawah", "Penginapan", "Mbak Wulan", "Tidak sekarang", "Kembali ke Pasar Bawah",
    "Juragan Salim", "Kami siap", "Ke Gerbang Utara", "Lentera penjaga", "Mendaki ke Tambang",
]
TAMBANG = [
    "Masuk ke lorong atas", "Urat kaca", "Ke ruang lift", "Ke bengkel", "Rak suku cadang",
    "#equip:bagas:senjata:peluncur_kaca",
    "Kembali ke ruang lift", "Lentera penjaga", "Turun dengan lift", "Peti lori",
    "#equip:sela:senjata:pedang_besi_tambang", "#equip:lintang:senjata:lentera_kaca",
    "Ke gua kristal", "Lentera penjaga", "Turun ke lorong bawah", "Ke ruang inti",
    "Naik tangga darurat", "Jalan gunung ke Mercusuar",
]
MERCUSUAR = [
    "Lentera penjaga", "Kita siap?", "Kita siap.", "Masuk dan naik",
    "Naik ke Lantai Pernikahan", "Kotak seserahan", "Naik ke Lantai Pemakaman", "Lentera penjaga",
    "Naik ke Lantai Perang", "Peti batu",
    "#equip:rimba:senjata:tongkat_guntur",
    "Naik ke Lantai Penjaga", "Lentera penjaga", "Naik ke Puncak",
]
# "#stop" menghentikan walkthrough tepat setelah Babak 1 selesai: ceritanya sendiri
# langsung berlanjut ke Celah Angin (Babak 2), yang diuji terpisah.
SEMUA = AREA1 + RAWA + DANAU + TENGARA_1 + LORONG + TENGARA_2 + TAMBANG + MERCUSUAR + ["#stop:babak2_mulai"]


class BerhentiUji(Exception):
    """Langkah "#stop": hentikan walkthrough di batas babak, bukan dengan keluar permainan."""


def make_equipper(state):
    def on_command(cmd: str) -> None:
        kind, *args = cmd.split(":")
        if kind == "stop":
            # "#stop:flag" baru berhenti setelah flag-nya menyala; sebelum itu
            # langkahnya dikembalikan ke antrean (lihat Walker.on_command).
            if args and args[0] not in state.flags:
                return False
            raise BerhentiUji()
        if kind == "equip":
            cid, slot, iid = args
            h = state.hero(cid)
            assert h is not None, cid
            assert state.count(iid) > 0, f"{iid} tidak ada di inventori: {state.inventory}"
            old = h.equipment.get(slot)
            h.equipment[slot] = iid
            state.add_item(iid, -1)
            if old:
                state.add_item(old, 1)
    return on_command


def run_walkthrough(steps, seed, tmp_path):
    data = load_data()
    world = load_world(data)
    st = new_game(data)
    st.rng = random.Random(seed)
    wk = Walker(steps, on_command=make_equipper(st))
    g = Game(data, world, st, wk.io, auto_battle=True, auto_script=True, auto_choice=False, save_dir=tmp_path)
    try:
        res = g.run()
    except BerhentiUji:
        res = "berhenti"
    return res, st, wk


@pytest.mark.parametrize("seed", [11, 23])
def test_babak1_tamat(seed, tmp_path):
    res, st, wk = run_walkthrough(SEMUA, seed, tmp_path)
    txt = wk.text
    assert res == "berhenti", txt[-3000:]
    assert "AKHIR BABAK 1" in txt
    # Cerita mengalir langsung ke Babak 2, bukan kembali ke layar judul.
    assert st.area_id == "celah_angin", f"{st.area_id}/{st.room_id}"
    assert "babak_1_selesai" in st.flags
    # Rangga bergabung begitu party tiba di Celah Angin, di awal Babak 2.
    assert [h.id for h in st.party] == ["rimba", "sela", "lintang", "bagas", "rangga"]
    for flag in ("boss_hutan_kalah", "boss_katak_kalah", "boss_ular_kalah", "boss_rangga_kalah",
                 "boss_penambang_kalah", "boss_penjaga_kalah"):
        assert flag in st.flags, flag
    assert st.quests["mencari_guntur"] == "selesai"
    assert st.quests["kucing_penginapan"] == "selesai"
    assert st.quests["surat_distrik_sunyi"] == "selesai"
    assert st.quests["hampa_pasar_malam"] == "selesai"
    assert st.quests["yang_hilang_di_telaga"] == "selesai"
    assert st.hero("rimba").level >= 18, [(h.id, h.level) for h in st.party]
    assert st.count("serpihan_ingatan") >= 8
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"
