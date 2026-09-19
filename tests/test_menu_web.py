"""Tes regresi antarmuka: tiap prompt di web/APK harus punya jalan keluar.

Bug yang ditangkap: di Warung Bu Ratna pemain bisa membeli tapi tidak bisa keluar
ke jalan desa, karena menu toko mencetak ``1) Beli   2) Jual   0) Pergi`` dalam
satu baris dan lapisan web cuma membuat satu tombol dari situ. Di terminal tidak
terasa (pemain mengetik angkanya sendiri); di layar sentuh permainan jadi sangkut.

Yang diperiksa bukan satu menu itu saja, tapi **setiap prompt yang keluar dari
mesin permainan**, lewat lapisan web yang sama dengan browser:

- ``periksa_prompt`` dipasang ke ``WebIO`` asli dan berjalan di tiap prompt;
- ``test_walkthrough_babak1_lewat_web`` memainkan seluruh Babak 1 (semua area,
  toko, penginapan, lentera, pilihan cerita, pertarungan) lewat lapisan web;
- ``test_crawler_menjelajah_semua_menu`` menjelajah sendiri menu Tahap 3
  (party, Tukang Kaca, kemah, Buruan, Arena, item, save) tanpa daftar manual:
  ia menekan setiap tombol yang belum pernah ditekan sampai kehabisan.

Menu yang memang tidak boleh ditinggalkan harus menyatakan alasannya lewat
``Menu.no_back("...")``; alasan yang tidak dikenal membuat tes ini gagal, jadi
menu baru yang lupa tombol keluar ketahuan sendiri.
"""
from __future__ import annotations

import random
import re
from collections import Counter, deque

import pytest

from pelita.loader import load_data
from pelita.ui.menu import Menu
from pelita.web.session import WebIO
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import GameState, new_game
from tests.test_babak1 import SEMUA, make_equipper

#: Satu-satunya prompt yang boleh tampil tanpa tombol keluar, beserta alasannya.
ALASAN_TANPA_KELUAR = {"aksi pertarungan", "pilihan cerita"}

#: Label yang masih menyembunyikan opsi lain di dalamnya ("Beli   2) Jual   0) Pergi").
OPSI_TERSELIP = re.compile(r"\s\d+\)\s")

#: Angka di label (HP, harga, jumlah) diabaikan saat mengenali menu yang sama.
ANGKA = re.compile(r"\d+")


@pytest.fixture(scope="module")
def data():
    return load_data()


@pytest.fixture(scope="module")
def world(data):
    return load_world(data)


def periksa_prompt(p: dict) -> None:
    """Aturan yang harus dipenuhi tiap prompt supaya bisa dimainkan dengan tombol."""
    kind = p["kind"]
    assert kind != "free", (
        f"prompt {p['prompt']!r} menunggu jawaban bebas — di web tidak ada tombolnya")
    if kind in ("enter", "confirm"):
        # klien selalu menggambar "Lanjut" / "Ya"+"Tidak" untuk dua jenis ini
        assert kind == "enter" or [o["key"] for o in p["options"]] == ["y", "n"]
        return

    opsi = p["options"]
    assert opsi, f"prompt {p['prompt']!r} tidak punya satu pun pilihan"
    assert all(o["key"] and o["label"] for o in opsi), f"opsi tanpa key/label: {opsi}"
    assert len({o["key"] for o in opsi}) == len(opsi), f"key opsi bentrok: {opsi}"
    for o in opsi:
        assert not OPSI_TERSELIP.search(o["label"]), (
            f"label {o['label']!r} memuat beberapa opsi sekaligus — satu opsi satu tombol")
    if any(o["back"] for o in opsi):
        return
    assert p.get("required") in ALASAN_TANPA_KELUAR, (
        f"prompt {p['prompt']!r} tidak punya jalan keluar dan tidak menyebut alasannya; "
        f"opsi: {[o['label'] for o in opsi]}")


class FakeSession:
    """Pengganti ``WebSession`` tanpa thread: event dikumpulkan, jawaban dari kebijakan.

    ``WebIO`` asli yang dipakai — jadi yang diuji benar-benar jalur yang dipakai
    browser, bukan tiruannya.
    """

    def __init__(self, jawab) -> None:
        self.jawab = jawab
        self.events: list[tuple[str, dict]] = []
        self.prompts: list[dict] = []
        self.io = WebIO(self)

    def push(self, kind: str, payload: dict) -> None:
        self.events.append((kind, payload))
        if kind == "prompt":
            periksa_prompt(payload)
            self.prompts.append(payload)

    def wait_for_input(self) -> str:
        return self.jawab(self.prompts[-1])

    @property
    def log(self) -> list[str]:
        return [p["text"] for k, p in self.events if k == "log"]

    def menus(self) -> set[tuple]:
        """Tanda pengenal tiap menu yang pernah tampil (prompt + label opsinya)."""
        return {(p["prompt"], tuple(o["label"] for o in p["options"]))
                for p in self.prompts if p["kind"] == "menu"}


def siap(data, world, jawab, tmp_path, seed=5, **kw) -> tuple[Game, GameState, FakeSession]:
    st = new_game(data)
    st.rng = random.Random(seed)
    sesi = FakeSession(jawab)
    g = Game(data, world, st, sesi.io, save_dir=tmp_path, **kw)
    return g, st, sesi


# ── Unit: aturannya sendiri ──────────────────────────────────────────────
def test_aturan_menangkap_menu_tanpa_jalan_keluar():
    """Kalau ``periksa_prompt`` sendiri rusak, tes di bawah jadi tidak berarti."""
    tanpa_keluar = {"prompt": "> ", "kind": "menu", "required": None,
                    "options": [{"key": "1", "label": "Beli", "meta": False, "back": False}]}
    with pytest.raises(AssertionError, match="jalan keluar"):
        periksa_prompt(tanpa_keluar)

    sebaris = {"prompt": "> ", "kind": "menu", "required": None, "options": [
        {"key": "1", "label": "Beli   2) Jual   0) Pergi", "meta": False, "back": False},
        {"key": "0", "label": "Pergi", "meta": False, "back": True}]}
    with pytest.raises(AssertionError, match="satu opsi satu tombol"):
        periksa_prompt(sebaris)

    with pytest.raises(AssertionError, match="jawaban bebas"):
        periksa_prompt({"prompt": "dengan siapa> ", "kind": "free", "options": [], "required": None})

    tanpa_keluar["required"] = "aksi pertarungan"          # pengecualian yang disengaja
    periksa_prompt(tanpa_keluar)


def test_menu_baru_tanpa_jalan_keluar_ketahuan(tmp_path):
    """Menu baru yang lupa tombol keluar harus gagal, lewat jalur WebIO yang asli."""
    sesi = FakeSession(lambda p: "1")
    m = Menu().no_back()                      # lupa alasan, lupa jalan keluar
    m.add("Beli")
    with pytest.raises(AssertionError, match="jalan keluar"):
        m.ask(sesi.io, "> ")


def test_menu_selalu_menambah_jalan_keluar():
    m = Menu()
    m.add("Beli")
    m.add("Jual")
    opsi = m.build()
    assert [o.key for o in opsi] == ["1", "2", "0"]
    assert opsi[-1].back and opsi[-1].label == "Kembali"
    assert [o.text for o in opsi] == ["  1) Beli", "  2) Jual", "  0) Kembali"]
    assert Menu().no_back("pilihan cerita").required == "pilihan cerita"


# ── Seluruh Babak 1 lewat lapisan web ────────────────────────────────────
class WebWalker:
    """Pemain otomatis yang memilih dari daftar opsi terstruktur, seperti browser."""

    def __init__(self, steps, on_command=None) -> None:
        self.steps = deque(steps)
        self.on_command = on_command
        self.macet = 0

    def __call__(self, p: dict) -> str:
        if p["kind"] == "enter":
            return ""
        while self.steps and str(self.steps[0]).startswith("#"):
            cmd = self.steps.popleft()
            if self.on_command:
                self.on_command(cmd[1:])
        if not self.steps:
            return "n" if p["kind"] == "confirm" else "0"
        step = self.steps[0]
        if p["kind"] == "confirm":
            return "n"
        for o in p["options"]:
            if step.lower() in o["label"].lower():
                self.steps.popleft()
                self.macet = 0
                return o["key"]
        self.macet += 1
        assert self.macet < 200, f"macet mencari {step!r}; opsi: {[o['label'] for o in p['options']]}"
        keluar = next((o["key"] for o in p["options"] if o["back"] and not o["meta"]), None)
        return keluar if keluar is not None else p["options"][0]["key"]


def test_walkthrough_babak1_lewat_web(data, world, tmp_path):
    """Babak 1 ditamatkan lewat lapisan web; tiap prompt di jalan itu ikut diperiksa."""
    st = new_game(data)
    st.rng = random.Random(11)
    walker = WebWalker(SEMUA, on_command=make_equipper(st))
    sesi = FakeSession(walker)
    g = Game(data, world, st, sesi.io, auto_battle=True, auto_script=True,
             auto_choice=False, auto_menus=False, save_dir=tmp_path)
    assert g.run() == "chapter_end"
    assert not walker.steps, f"langkah tersisa: {list(walker.steps)}"
    assert len(sesi.menus()) > 50, "walkthrough seharusnya melewati puluhan menu berbeda"


# ── Crawler: tekan semua tombol yang ada ─────────────────────────────────
class Crawler:
    """Menjelajah menu sendiri: tekan tiap tombol sekali, lalu keluar dari menu itu.

    Tidak ada daftar menu yang ditulis tangan — submenu ditemukan dari tombol yang
    muncul, jadi menu baru otomatis ikut terjelajah (dan ikut diperiksa). Tanda
    pengenal menu mengabaikan angka ("punya 2" = "punya 3") supaya menu yang
    labelnya berubah tiap pembelian tetap dianggap menu yang sama dan penjelajahan
    tidak berputar selamanya.

    Kalau semua tombol di sebuah menu sudah pernah ditekan, crawler keluar lewat
    tombol keluarnya — itulah yang membuktikan menu tersebut bisa ditinggalkan.
    Menu ruang adalah kekecualian: "keluarnya" berarti berhenti main, jadi di sana
    crawler berjalan acak (terarah, ber-seed) sampai jatah langkahnya habis,
    supaya ruang yang tadi hanya dilewati sempat dijelajahi juga.
    """

    def __init__(self, budget: int = 700, seed: int = 1) -> None:
        self.budget = budget
        self.rng = random.Random(seed)
        self.dicoba: set[tuple] = set()
        self.langkah = 0

    @staticmethod
    def tanda(p: dict) -> tuple:
        return (p["prompt"], tuple(ANGKA.sub("#", o["label"]) for o in p["options"]))

    def __call__(self, p: dict) -> str:
        self.langkah += 1
        if self.langkah >= self.budget:
            raise SelesaiMenjelajah()
        if p["kind"] == "enter":
            return ""
        if p["kind"] == "confirm":
            kunci = (p["prompt"], "confirm")
            if kunci not in self.dicoba:                  # coba "Ya" sekali per pertanyaan
                self.dicoba.add(kunci)
                return "y"
            return "n"
        sig = self.tanda(p)
        for o in p["options"]:
            if o["back"] or self.berhenti_main(o):
                continue
            if (sig, o["key"]) in self.dicoba:
                continue
            self.dicoba.add((sig, o["key"]))
            return o["key"]
        keluar = next((o for o in p["options"] if o["back"]), None)
        if keluar is not None and not self.berhenti_main(keluar):
            return keluar["key"]
        lain = [o for o in p["options"] if not self.berhenti_main(o)]
        if lain:
            return self.rng.choice(lain)["key"]
        return p["options"][0]["key"]                     # menu wajib: ambil yang pertama

    @staticmethod
    def berhenti_main(o: dict) -> bool:
        """[K]eluar menutup permainan — bukan "jalan keluar" yang mau kita uji."""
        return bool(o["meta"]) and o["key"] == "k"


class SelesaiMenjelajah(Exception):
    """Jatah langkah crawler habis — bukan kegagalan."""


def jelajahi(g, sesi) -> None:
    """Jalankan permainan sampai crawler kehabisan jatah langkah."""
    from pelita.world.explore import QuitGame
    try:
        g.run()
    except (SelesaiMenjelajah, QuitGame):
        pass


def kaya(data, st) -> None:
    """State dengan semua sistem Tahap 3 terbuka, supaya menunya bisa dijelajahi."""
    st.bara_max = 5
    st.flags.update({"bara", "boss_hutan_kalah", "boss_katak_kalah", "boss_ular_kalah",
                     "boss_rangga_kalah", "boss_penambang_kalah"})
    for cid in ("sela", "lintang", "bagas"):
        st.join(cid, 30)
    st.party[0].level = 30
    st.keping = 9000
    st.party[0].equipment["senjata"] = "tongkat_kaca"
    st.party[0].rapikan_soket()
    for iid, n in (("ramuan_daun", 5), ("dupa_sunyi", 2), ("bekal_kemah", 3),
                   ("serpihan_ingatan", 6), ("pedang_sumpah", 1)):
        st.add_item(iid, n)
    for kid in ("kaca_api", "kaca_tajam"):
        st.add_kaca(kid, 1)
    st.buruan["buruan_1_kunang"] = "aktif"
    st.arena = 1
    st.wire()


@pytest.mark.parametrize("pintu", [
    ("desa & warung Bu Ratna", "pelita_rendah", "jalan_desa"),
    ("pasar kota & Tukang Kaca", "tengara", "pasar_bawah"),
    ("distrik sunyi", "tengara", "distrik_sunyi"),
])
def test_crawler_menjelajah_semua_menu(data, world, tmp_path, pintu):
    """Dari satu ruang, tekan semua tombol yang bisa ditekan; tiap prompt diperiksa.

    Pemeriksaannya ada di ``FakeSession.push`` → ``periksa_prompt``, jadi menu apa
    pun yang ditemukan crawler ikut diuji tanpa perlu disebut di sini.
    """
    nama, area_id, room_id = pintu
    sesi = FakeSession(Crawler())
    st = new_game(data)
    st.rng = random.Random(3)
    kaya(data, st)
    st.area_id, st.room_id = area_id, room_id
    g = Game(data, world, st, sesi.io, auto_battle=True, auto_script=True,
             auto_choice=True, auto_menus=False, save_dir=tmp_path)
    jelajahi(g, sesi)
    assert len(sesi.menus()) >= 8, f"{nama}: crawler nyaris tidak menemukan menu"


def test_crawler_menemukan_menu_penting(data, world, tmp_path):
    """Jaring pengaman: penjelajahan harus benar-benar sampai ke menu-menu dalam.

    Kalau crawler berhenti terlalu dini, tes di atas bisa lulus tanpa memeriksa
    apa-apa; daftar di sini memastikan jangkauannya tidak menyusut diam-diam.
    """
    sesi = FakeSession(Crawler(budget=1500))
    st = new_game(data)
    st.rng = random.Random(3)
    kaya(data, st)
    st.area_id, st.room_id = "pelita_rendah", "jalan_desa"
    g = Game(data, world, st, sesi.io, auto_battle=True, auto_script=True,
             auto_choice=True, auto_menus=False, save_dir=tmp_path)
    jelajahi(g, sesi)
    prompts = {p["prompt"] for p in sesi.prompts}
    for wajib in ("slot>", "item>", "beli>", "jual>", "siapa>", "tukar siapa>", "pasang>"):
        assert wajib in prompts, f"crawler tidak sampai ke prompt {wajib!r}: {sorted(prompts)}"


@pytest.mark.parametrize("hub, panggil", [
    ("Tukang Kaca", lambda g: g.tukang_kaca("kios_sarwa")),
    ("Berkemah", lambda g: g.kemah()),
    ("Papan Buruan", lambda g: g.papan_buruan()),
    ("Arena Kafilah", lambda g: g.arena()),
    ("Toko", lambda g: g.shop("warung_ratna")),
    ("Party", lambda g: g.party_menu()),
    ("Item", lambda g: g.item_menu()),
    ("Simpan", lambda g: g.save_menu()),
])
def test_hub_tahap3_bisa_ditinggalkan(data, world, tmp_path, hub, panggil):
    """Tiap hub Tahap 3 dijelajahi sampai tuntas, lalu harus bisa ditinggalkan."""
    sesi = FakeSession(Crawler(budget=400))
    st = new_game(data)
    st.rng = random.Random(9)
    kaya(data, st)
    st.area_id, st.room_id = "tengara", "pasar_bawah"
    g = Game(data, world, st, sesi.io, auto_battle=True, auto_script=True,
             auto_choice=True, auto_menus=False, save_dir=tmp_path)
    try:
        panggil(g)                       # kembali sendiri = ada jalan keluarnya
    except SelesaiMenjelajah:
        pytest.fail(f"{hub}: crawler tidak pernah bisa keluar dalam batas langkah")
    assert sesi.prompts, f"{hub}: tidak ada prompt sama sekali"


def test_toko_bu_ratna_bisa_ditinggalkan(data, world, tmp_path):
    """Kasus yang dilaporkan: tombol Beli, Jual, dan Pergi harus terpisah."""
    dilihat: list[dict] = []

    def jawab(p):
        dilihat.append(p)
        if p["kind"] != "menu":
            return "" if p["kind"] == "enter" else "n"
        pergi = next((o["key"] for o in p["options"] if o["back"]), None)
        return pergi if pergi is not None else p["options"][0]["key"]

    g, st, sesi = siap(data, world, jawab, tmp_path)
    st.keping = 500
    g.shop("warung_ratna")

    toko = dilihat[0]
    assert [o["label"] for o in toko["options"]] == ["Beli", "Jual", "Pergi"]
    assert toko["options"][-1]["back"] is True
    assert len(dilihat) == 1, "sekali tekan 'Pergi' harus langsung keluar dari toko"
