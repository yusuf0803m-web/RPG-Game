"""Tes tokoh bergambar (GAME_DESIGN §7.3): registri, pencari aset, dan metadata dialog."""
import json
import shutil
from pathlib import Path

import pytest

from pelita.loader import load_data
from pelita.ui.terminal import IO
from pelita.web.tokoh import ASET_TOKOH, REGISTRI, DaftarTokoh, daftar_tokoh, punya_alpha
from pelita.world.model import load_world
from pelita.world.script import Hooks, ScriptRunner
from pelita.world.state import new_game

EKSPRESI_RIMBA = ("neutral", "happy", "worried", "serious")


@pytest.fixture(scope="module")
def registri():
    return json.loads(REGISTRI.read_text(encoding="utf-8"))


@pytest.fixture()
def tokoh():
    return DaftarTokoh.muat()


# ── Registri ─────────────────────────────────────────────────────────────
def test_registri_memakai_id_stabil_dan_kosakata_tetap(registri):
    kosakata = set(registri["ekspresi"])
    assert "neutral" in kosakata
    for tid, t in registri["tokoh"].items():
        assert tid == tid.lower() and " " not in tid, f"id tokoh harus stabil: {tid}"
        assert t["ekspresi_bawaan"] in kosakata
        assert t.get("sisi", "kanan") in ("kanan", "kiri")
        for eks, isi in t.get("ekspresi", {}).items():
            assert eks in kosakata, f"{tid}: ekspresi '{eks}' di luar kosakata"
            x, y, s = isi["wajah"]
            assert 0 <= x and 0 <= y and x + s <= 720 and y + s <= 960, f"{tid}/{eks}: crop di luar kanvas"


def test_tokoh_terdaftar_punya_gambar_bawaan(registri):
    """Tokoh jangan didaftarkan sebelum ada gambarnya (tidak ada data visual fiktif)."""
    for tid, t in registri["tokoh"].items():
        eks = t["ekspresi_bawaan"]
        assert any((ASET_TOKOH / tid / f"{eks}{ext}").is_file() for ext in (".webp", ".png")), tid


def test_skrip_hanya_memakai_ekspresi_dan_tokoh_yang_dikenal(registri):
    """Salah ketik ``ekspresi``/``tokoh`` di data ditangkap tes, bukan saat bermain."""
    world = load_world(load_data())
    kosakata, ids = set(registri["ekspresi"]), set(registri["tokoh"])
    salah = []

    def jelajah(cmds, where):
        for c in cmds:
            if not isinstance(c, dict):
                continue
            if "say" in c:
                if "ekspresi" in c and c["ekspresi"] not in kosakata:
                    salah.append(f"{where}: ekspresi {c['ekspresi']}")
                if "tokoh" in c and c["tokoh"] not in ids:
                    salah.append(f"{where}: tokoh {c['tokoh']}")
            for k in ("then", "else", "do", "win", "on_lose", "on_flee"):
                if isinstance(c.get(k), list):
                    jelajah(c[k], where)
            for o in c.get("choice", []) or []:
                jelajah(o.get("then", []), where)

    for a in world.areas.values():
        for sid, cmds in a.scripts.items():
            jelajah(cmds, f"{a.id}/{sid}")
    assert not salah, salah


# ── Pencari aset ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("eks", EKSPRESI_RIMBA)
def test_rimba_keempat_ekspresi_ketemu(tokoh, eks):
    v = tokoh.visual("Rimba", None, eks)
    assert v["tokoh"] == "rimba" and v["nama"] == "Rimba" and v["ekspresi"] == eks
    assert v["potret_url"].startswith("/static/assets/characters/rimba/" + eks + ".")
    assert v["sisi"] == "kanan"
    assert set(v["wajah"]) == {"ukuran", "x", "y"}
    assert v["panggung_url"], "panggung selalu punya gambar (ekspresi ini atau bawaan)"


def test_tanpa_ekspresi_pakai_bawaan(tokoh):
    assert tokoh.visual("Rimba")["ekspresi"] == "neutral"


def test_ekspresi_ngawur_jatuh_ke_neutral(tokoh):
    v = tokoh.visual("Rimba", None, "bingung")
    assert v["ekspresi"] == "neutral" and v["potret_url"].endswith("/rimba/neutral.webp")


def test_tokoh_tidak_dikenal_tanpa_visual(tokoh):
    assert tokoh.visual("Pedagang") is None
    assert tokoh.visual("???") is None
    assert tokoh.visual("Sela", "bukan_tokoh", "happy") is None


def test_id_eksplisit_mengalahkan_nama_tampilan(tokoh):
    v = tokoh.visual("???", "rimba", "worried")
    assert v["tokoh"] == "rimba" and v["ekspresi"] == "worried"


def test_alias_tidak_peka_huruf_besar(tokoh):
    assert tokoh.cari_id("RIMBA") == "rimba"


def test_panggung_tidak_memakai_gambar_tanpa_alpha_atau_yang_ditandai(tokoh, registri):
    """Gambar berlatar buram tetap jadi face graphic, tapi panggung jatuh ke bawaan."""
    tanda = registri["tokoh"]["rimba"].get("ekspresi", {})
    for eks in EKSPRESI_RIMBA:
        v = tokoh.visual("Rimba", None, eks)
        berkas = ASET_TOKOH / v["potret_url"].split("/characters/")[1]
        if punya_alpha(berkas) and tanda.get(eks, {}).get("panggung", True):
            assert v["panggung_url"] == v["potret_url"]
        else:
            assert v["panggung_url"].endswith("/rimba/neutral.webp")


def test_keempat_ekspresi_rimba_tampil_di_panggung(tokoh):
    """Pilot selesai: tidak ada lagi ekspresi Rimba yang hanya boleh jadi face graphic."""
    for eks in EKSPRESI_RIMBA:
        v = tokoh.visual("Rimba", None, eks)
        assert v["panggung_url"] == v["potret_url"], eks


def test_tanda_panggung_false(tmp_path, registri):
    reg = json.loads(json.dumps(registri))
    reg["tokoh"]["rimba"].setdefault("ekspresi", {})["serious"] = {"panggung": False}
    v = DaftarTokoh(reg).visual("Rimba", None, "serious")
    assert v["potret_url"].endswith("/rimba/serious.webp")
    assert v["panggung_url"].endswith("/rimba/neutral.webp")


def test_crop_wajah_per_ekspresi_masih_bisa_ditimpa(registri):
    reg = json.loads(json.dumps(registri))
    reg["tokoh"]["rimba"]["ekspresi"] = {"happy": {"wajah": [216, 120, 288]}}
    t = DaftarTokoh(reg)
    assert t.visual("Rimba", None, "happy")["wajah"] == DaftarTokoh.css_wajah([216, 120, 288])
    assert t.visual("Rimba", None, "worried")["wajah"] == DaftarTokoh.css_wajah(reg["tokoh"]["rimba"]["wajah"])


def test_aset_tokoh_dalam_batas_ukuran():
    """Bible §3: WebP ≤ 160 KB per berkas (APK & HP)."""
    for b in ASET_TOKOH.glob("*/*.*"):
        if b.suffix in (".webp", ".png"):
            assert b.stat().st_size <= 160 * 1024, f"{b.name}: {b.stat().st_size} byte"


def test_deteksi_alpha_dari_header(tmp_path):
    rgba = tmp_path / "a.png"
    rgba.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + b"\x00" * 8 + b"\x08\x06" + b"\x00" * 30)
    rgb = tmp_path / "b.png"
    rgb.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + b"\x00" * 8 + b"\x08\x02" + b"\x00" * 30)
    lossy = tmp_path / "c.webp"
    lossy.write_bytes(b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 30)
    assert punya_alpha(rgba) and not punya_alpha(rgb) and not punya_alpha(lossy)
    assert not punya_alpha(tmp_path / "tidak_ada.webp")
    assert punya_alpha(ASET_TOKOH / "rimba" / "neutral.webp")


def test_aset_hilang_tidak_melempar(tmp_path, registri):
    """Folder aset kosong: tokoh tetap dikenali, tapi tanpa URL — dialog tampil biasa."""
    t = DaftarTokoh(registri, aset=tmp_path)
    v = t.visual("Rimba", None, "happy")
    assert v["potret_url"] == "" and v["panggung_url"] == "" and v["wajah"] is None


def test_ekspresi_hilang_jatuh_ke_neutral(tmp_path, registri):
    (tmp_path / "rimba").mkdir()
    shutil.copy(ASET_TOKOH / "rimba" / "neutral.webp", tmp_path / "rimba" / "neutral.webp")
    t = DaftarTokoh(registri, aset=tmp_path)
    v = t.visual("Rimba", None, "worried")
    assert v["ekspresi"] == "neutral" and v["potret_url"].endswith("/rimba/neutral.webp")


def test_registri_rusak_tidak_melempar(tmp_path):
    rusak = tmp_path / "tokoh.json"
    rusak.write_text("{ bukan json", encoding="utf-8")
    assert DaftarTokoh.muat(rusak).visual("Rimba") is None
    assert DaftarTokoh.muat(tmp_path / "tidak_ada.json").visual("Rimba") is None


def test_crop_wajah_dalam_persen():
    assert DaftarTokoh.css_wajah([216, 120, 288]) == {"ukuran": 250.0, "x": 50.0, "y": 17.857}


# ── Skrip & terminal ─────────────────────────────────────────────────────
class Rekam(IO):
    def __init__(self, structured=False):
        self.baris, self.event = [], []
        self.structured = structured
        super().__init__(read=lambda p: "", write=self.baris.append)

    def emit(self, kind, payload):
        self.event.append((kind, payload))


def jalankan(cmds, structured=False):
    data = load_data()
    world = load_world(data)
    io = Rekam(structured)
    hooks = Hooks(battle=lambda *a, **k: "menang", save_menu=lambda: None, shop=lambda s: None,
                  inn=lambda n: None, move=lambda r, a: None)
    ScriptRunner(new_game(data), io, hooks, auto=True).run_commands(next(iter(world.areas.values())), cmds)
    return io


def test_terminal_tidak_berubah_oleh_ekspresi():
    lama = jalankan([{"say": "Rimba", "text": "Aku sudah janji."}])
    baru = jalankan([{"say": "Rimba", "ekspresi": "serious", "tokoh": "rimba", "text": "Aku sudah janji."}])
    assert lama.baris == baru.baris == [" Rimba   : Aku sudah janji."]


def test_dialog_lama_tanpa_metadata_tetap_sama():
    io = jalankan([{"say": "Guntur", "text": "Minyaknya tumpah."}], structured=True)
    assert io.event == [("say", {"who": "Guntur", "text": "Minyaknya tumpah."})]


def test_metadata_ikut_diteruskan_ke_emit():
    io = jalankan([{"say": "Rimba", "ekspresi": "happy", "text": "Masih murah."}], structured=True)
    assert io.event == [("say", {"who": "Rimba", "text": "Masih murah.", "ekspresi": "happy"})]


# ── Web ──────────────────────────────────────────────────────────────────
def test_webio_menambah_visual_hanya_untuk_tokoh_terdaftar(tmp_path):
    pytest.importorskip("flask")
    from pelita.web.session import SessionStore, WebSession
    store = SessionStore(tmp_path)
    s = WebSession(store.data, store.world, new_game(store.data), tmp_path)
    s.io.emit("say", {"who": "Guntur", "text": "a"})
    s.io.emit("say", {"who": "Rimba", "text": "b"})
    for eks in EKSPRESI_RIMBA:
        s.io.emit("say", {"who": "Rimba", "text": eks, "ekspresi": eks})
    says = [e.payload for e in s.events if e.kind == "say"]
    assert says[0] == {"who": "Guntur", "text": "a"}
    assert says[1]["tokoh"] == "rimba" and says[1]["ekspresi"] == "neutral"
    assert [p["ekspresi"] for p in says[2:]] == list(EKSPRESI_RIMBA)
    assert all(p["potret_url"] and p["who"] == "Rimba" for p in says[1:])


def test_aset_potret_bisa_diunduh(tmp_path):
    pytest.importorskip("flask")
    from pelita.web.app import create_app
    app = create_app(tmp_path)
    with app.test_client() as c:
        for eks in EKSPRESI_RIMBA:
            url = daftar_tokoh().visual("Rimba", None, eks)["potret_url"]
            r = c.get(url)
            assert r.status_code == 200, url
            r.close()
    for s in list(app.config["STORE"].sessions.values()):
        s.close()


def test_klien_punya_lapisan_panggung():
    html = Path("pelita/web/static/index.html").read_text(encoding="utf-8")
    js = Path("pelita/web/static/app.js").read_text(encoding="utf-8")
    assert 'id="scene-cast"' in html
    assert "dialog-portrait" in js and "panggung_url" in js
    assert "rimba" not in js.lower(), "klien tidak boleh punya logika khusus tokoh tertentu"


# ── Kelayakan aset untuk panggung (tools/audit_potret.py) ────────────────
def test_aset_tokoh_layak_panggung(registri):
    """Tiap berkas tokoh terdaftar: 720x960, latar benar-benar transparan (bukan papan catur
    atau latar yang tercetak), tanpa lubang di pakaian, dan — kalau landmark wajahnya tercatat —
    garis mata & dagu dalam toleransi Bible terhadap ekspresi bawaan, serta muat di crop wajah."""
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    import sys
    sys.path.insert(0, str(Path("tools").resolve()))
    from audit_potret import audit_tokoh
    for tid in registri["tokoh"]:
        for r in audit_tokoh(tid):
            nama = f"{tid}/{r['ekspresi']}"
            assert r["kanvas"] == [720, 960], nama
            assert r["alpha_min_maks"][0] == 0, f"{nama}: tidak ada piksel transparan"
            assert not r["latar_tercetak"], f"{nama}: latar tercetak ({r['bingkai_opak_pct']}% bingkai opak)"
            assert r["lubang_pakaian_px"] < 50, f"{nama}: {r['lubang_pakaian_px']} px lubang di pakaian"
            if "garis_mata" in r:
                assert r["crop_ok"], f"{nama}: mata/dagu di luar crop wajah {r['crop_wajah']}"
            assert r["panggung_siap"], f"{nama}: {r}"
