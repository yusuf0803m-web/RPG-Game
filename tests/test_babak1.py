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
from pelita.models import STAT_NAMES
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
    # Pasar Apung: pemain yang wajar tidak membiarkan siapa pun tetap berzirah kain.
    "#beli:rimba:zirah:zirah_kulit", "#beli:lintang:zirah:zirah_kulit",
    "#beli:sela:aksesori:sabuk_lumut", "#beli:rimba:aksesori:cincin_anti_racun",
    "#stok:ramuan_akar:8", "#stok:tetes_nyala:5", "#stok:penawar:3", "#stok:bekal_kemah:2",
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
    # Pasar Bawah & Tungku Mpu Sarwa: zirah sepantasnya, aksesori temuan dipakai,
    # dan soket senjata akhirnya diisi.
    "#beli:rimba:zirah:zirah_rantai", "#beli:lintang:zirah:zirah_rantai",
    "#beli:sela:zirah:zirah_kaca_lapis",
    "#pasang:rimba:0:kaca_api", "#pasang:sela:0:kaca_petir", "#pasang:lintang:0:kaca_es",
    "#stok:ramuan_akar:10", "#stok:cawan_nyala:5", "#stok:abu_fajar:3",
    "#tukar:hp:sela", "#tukar:bara", "#tukar:soket:rimba",
    "Ke ruang pompa", "Lentera penjaga", "Naik tangga ke gerbang Arsip",
    "Naik ke Balai Arsip",
]
TENGARA_2 = [
    "Lentera penjaga", "Kembali ke Pasar Bawah", "Penginapan", "Mbak Wulan", "Tidak sekarang", "Kembali ke Pasar Bawah",
    "Juragan Salim", "Kami siap",
    # Upah dua quest itu memang aksesori; pemain memakainya, bukan menyimpannya.
    "#equip:lintang:aksesori:jimat_lentera", "#equip:sela:aksesori:gelang_kilat",
    "Ke Gerbang Utara", "Lentera penjaga", "Mendaki ke Tambang",
]
TAMBANG = [
    "Masuk ke lorong atas", "Urat kaca", "Ke ruang lift", "Ke bengkel", "Rak suku cadang",
    "#equip:bagas:senjata:peluncur_kaca",
    "Kembali ke ruang lift", "Lentera penjaga", "Turun dengan lift", "Peti lori",
    "#equip:sela:senjata:pedang_besi_tambang", "#equip:lintang:senjata:lentera_kaca",
    "#beli:bagas:zirah:zirah_kaca_lapis", "#beli:bagas:aksesori:cincin_anti_racun",
    "#pasang:bagas:0:kaca_kilat", "#stok:suku_cadang:20",
    "Ke gua kristal", "Lentera penjaga", "Turun ke lorong bawah", "Ke ruang inti",
    "Naik tangga darurat", "Jalan gunung ke Mercusuar",
]
MERCUSUAR = [
    "Lentera penjaga", "Kita siap?", "Kita siap.",
    "#beli:rimba:zirah:jubah_penyala", "#stok:ramuan_sari:6", "#stok:abu_fajar:5",
    "#stok:cawan_nyala:6", "#tukar:hp:rimba", "#tukar:bara",
    "Masuk dan naik",
    "Naik ke Lantai Pernikahan", "Kotak seserahan", "Naik ke Lantai Pemakaman", "Lentera penjaga",
    "Naik ke Lantai Perang", "Peti batu",
    "#equip:rimba:senjata:tongkat_guntur",
    "#pasang:rimba:0:kaca_fajar", "#pasang:rimba:1:kaca_tajam",
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
            pakai(h, slot, iid)
        if kind == "pakai":
            # "#pakai:cid:slot:item" — pakai barang temuan kalau memang ada. Berbeda
            # dari "#equip" yang memaksa: senjata cerita bisa saja tidak jatuh di
            # jalur yang ditempuh, dan itu bukan kesalahan langkah.
            cid, slot, iid = args
            h = state.hero(cid)
            if h is not None and state.count(iid) > 0:
                pakai(h, slot, iid)
        if kind == "beli":
            # "#beli:cid:slot:item" — belanja di toko lalu dipakai. Harganya benar-benar
            # dibayar, jadi buku kas Keping (§9.5) mengukur pemain yang berbelanja,
            # bukan pemain yang menimbun. Belanja yang belum terjangkau dilewati —
            # daftar yang sama diulang di hub berikutnya, seperti pemain yang
            # menunda membeli sampai kantongnya cukup.
            cid, slot, iid = args
            h = state.hero(cid)
            if h is None or not lebih_baik(h, slot, iid):
                return
            if not bayar(iid):
                return
            state.add_item(iid, 1)
            pakai(h, slot, iid)
        if kind == "stok":
            # "#stok:item:n" — isi ulang bekal di toko terdekat sampai punya n buah.
            iid, n = args[0], int(args[1])
            while state.count(iid) < n and bayar(iid):
                state.add_item(iid, 1)
        if kind == "pasang":
            # "#pasang:cid:soket:kaca" — beli Kaca kalau belum punya, lalu pasang ke soket.
            cid, soket, kid = args[0], int(args[1]), args[2]
            h = state.hero(cid)
            if h is None:
                return
            h.rapikan_soket()          # daftar soket menyesuaikan senjata yang sedang dipakai
            if soket >= len(h.kaca):
                return
            if state.kaca.get(kid, 0) <= 0:
                harga = state.data.kaca[kid].price
                if state.keping < harga:
                    return
                state.ubah_keping(-harga, "kaca")
                state.add_kaca(kid, 1)
            state.add_kaca(kid, -1)
            lama = h.kaca[soket]
            h.kaca[soket] = kid
            if lama:
                state.add_kaca(lama, 1)
        if kind == "tukar":
            # "#tukar:hp:cid" / "#tukar:bara" — penukaran Serpihan Ingatan di Tukang Kaca.
            tukar(args)

    def tukar(args: list[str]) -> None:
        from pelita.party import HP_BONUS_MAKS
        from pelita.world.explore import BARA_MAKS_TERTINGGI, SERPIHAN, SERPIHAN_PER_TUKAR
        if state.count(SERPIHAN) < SERPIHAN_PER_TUKAR:
            return
        jenis = args[0]
        if jenis == "hp":
            h = state.hero(args[1])
            if h is None or h.hp_bonus >= HP_BONUS_MAKS:
                return
            h.hp_bonus += 1
            h.restore()
        elif jenis == "bara":
            if state.bara_max <= 0 or state.bara_max >= BARA_MAKS_TERTINGGI:
                return
            state.bara_max += 1
        elif jenis == "soket":
            h = state.hero(args[1])
            w = h.equipment.get("senjata") if h else None
            if not w or state.slot_bonus.get(w, 0) >= 1:
                return
            state.slot_bonus[w] = state.slot_bonus.get(w, 0) + 1
            h.rapikan_soket()
        else:
            return
        state.add_item(SERPIHAN, -SERPIHAN_PER_TUKAR)

    def nilai(iid) -> int:
        """Bobot kasar sebuah barang: jumlah seluruh bonus stat-nya."""
        it = state.data.items.get(iid) if iid else None
        return sum(it.stats.get(n) for n in STAT_NAMES) if (it and it.stats) else 0

    def lebih_baik(h, slot: str, iid: str) -> bool:
        """Barang toko hanya dibeli kalau ia peningkatan.

        Daftar belanja diulang di tiap hub, dan tanpa aturan ini pengulangannya
        akan membeli ulang senjata toko menimpa senjata cerita dari peti yang
        jauh lebih baik — sesuatu yang tidak akan dilakukan pemain mana pun.
        """
        lama = h.equipment.get(slot)
        return lama != iid and nilai(iid) > nilai(lama)

    def bayar(iid: str) -> bool:
        # Harga penuh, tanpa potongan Kaca Kikir: pengukuran ekonomi (§9.5) sengaja
        # memakai pemain yang tidak menyiasati harga, jadi angkanya batas atas.
        harga = state.data.items[iid].price
        if state.keping < harga:
            return False
        state.ubah_keping(-harga, "toko")
        return True

    def pakai(h, slot: str, iid: str) -> None:
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
    # Serpihan Ingatan sekarang dibelanjakan di Tukang Kaca, bukan ditimbun sampai
    # tamat, jadi yang diperiksa hasilnya — bukan sisanya (§9.5).
    assert st.bara_max >= 6, f"Bara maks {st.bara_max}: penukaran Serpihan tidak jalan"
    assert sum(h.hp_bonus for h in st.party) >= 2
    assert st.count("serpihan_ingatan") + 3 * 3 >= 8
    assert not wk.steps, f"langkah tersisa: {list(wk.steps)}"
