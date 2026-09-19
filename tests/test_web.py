"""Tes lapisan web: sesi, event terstruktur, dan API Flask.

Tes ini memainkan permainan lewat API persis seperti browser: poll event,
baca daftar pilihan dari event ``prompt``, lalu kirim jawabannya.
"""
import re
import time

import pytest

flask = pytest.importorskip("flask", reason="antarmuka web butuh Flask")

from pelita.web.app import create_app  # noqa: E402
from pelita.web.session import SessionStore  # noqa: E402


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    for s in list(app.config["STORE"].sessions.values()):
        s.close()


class Driver:
    """Pemain otomatis lewat HTTP: kumpulkan event, jawab prompt berdasarkan label."""

    def __init__(self, client, sid):
        self.c = client
        self.sid = sid
        self.since = 0
        self.events = []
        self.finished = False
        self.result = None
        self.error = None

    def pump(self, timeout=8.0):
        """Ambil event sampai muncul prompt (atau sesi selesai)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            r = self.c.get(f"/api/session/{self.sid}/state?since={self.since}&timeout=2")
            assert r.status_code == 200, r.data
            d = r.get_json()
            self.since = max(self.since, d["seq"])
            self.events.extend(d["events"])
            self.error = d.get("error") or self.error
            if d["finished"]:
                self.finished = True
                self.result = d.get("result")
                return None
            p = self.last_prompt()
            if p is not None:
                return p
        raise AssertionError("tidak ada prompt dalam batas waktu")

    def last_prompt(self):
        for e in reversed(self.events):
            if e["kind"] == "prompt":
                return e["payload"]
            if e["kind"] in ("log", "say", "text", "room", "battle"):
                continue
        return None

    def send(self, text):
        self.events = [e for e in self.events if e["kind"] != "prompt"]
        r = self.c.post(f"/api/session/{self.sid}/input", json={"text": str(text)})
        assert r.status_code == 200

    def choose(self, needle):
        """Jawab prompt aktif dengan opsi yang labelnya memuat ``needle``."""
        p = self.pump()
        assert p is not None, "sesi sudah selesai"
        for o in p["options"]:
            if needle.lower() in o["label"].lower():
                self.send(o["key"])
                return o
        if not p["options"]:            # prompt Enter / bebas
            self.send("")
            return self.choose(needle)
        raise AssertionError(f"opsi '{needle}' tidak ada di {[o['label'] for o in p['options']]}")

    def kinds(self, kind):
        return [e["payload"] for e in self.events if e["kind"] == kind]

    def all_of(self, kind, seen):
        return [p for p in seen if p]


def advance(d, cond, limit=60):
    """Jawab prompt (pilihan pertama) sampai ``cond(d)`` benar; kembalikan hasilnya."""
    for _ in range(limit):
        got = cond(d)
        if got:
            return got
        p = d.pump()
        if p is None:
            break
        got = cond(d)
        if got:
            return got
        d.send(p["options"][0]["key"] if p["options"] else "")
    return None


def start(client, slot=None):
    r = client.post("/api/session", json=({"slot": slot} if slot else {}))
    assert r.status_code == 200, r.data
    return Driver(client, r.get_json()["id"])


# ── API dasar ────────────────────────────────────────────────────────────
def test_halaman_dan_aset(client):
    assert b"Pelita" in client.get("/").data
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/art.js").status_code == 200


def test_manifest_dan_ikon_pwa(client):
    """Supaya bisa dipasang ke layar utama Android."""
    r = client.get("/manifest.webmanifest")
    assert r.status_code == 200
    assert "manifest" in r.headers["Content-Type"]
    m = r.get_json()
    assert m["display"] == "standalone" and m["start_url"] == "/"
    src = {i["src"] for i in m["icons"]}
    assert src == {"/static/icon-192.png", "/static/icon-512.png"}
    assert any(i.get("purpose") == "maskable" for i in m["icons"])
    for path in sorted(src):
        ic = client.get(path)
        assert ic.status_code == 200 and ic.data[:8] == b"\x89PNG\r\n\x1a\n", path


def test_halaman_siap_untuk_ponsel(client):
    html = client.get("/").data.decode()
    assert 'name="viewport"' in html and "viewport-fit=cover" in html
    assert 'rel="manifest"' in html and 'name="theme-color"' in html


def test_slots_kosong(client):
    d = client.get("/api/slots").get_json()
    assert d["count"] == 5 and all(s is None for s in d["slots"])


def test_sesi_tidak_ada(client):
    assert client.get("/api/session/xxx/state").status_code == 404
    assert client.post("/api/session/xxx/input", json={"text": "1"}).status_code == 404


# ── Alur permainan lewat API ─────────────────────────────────────────────
def test_prolog_mengirim_dialog_dan_pertarungan(client):
    """Dialog Guntur muncul sebagai event ``say``; pertarungan tutorial sebagai ``battle``."""
    d = start(client)
    battles = advance(d, lambda x: x.kinds("battle"))
    assert battles, "pertarungan tutorial harus mengirim snapshot"

    says = d.kinds("say")
    assert any(s["who"] == "Guntur" for s in says)
    assert any("minyaknya tumpah" in s["text"] for s in says)

    b = battles[-1]
    assert [e["key"] for e in b["enemies"]] == ["kunang_kelam", "kunang_kelam"]
    assert {h["key"] for h in b["heroes"]} == {"rimba", "guntur"}
    assert b["enemies"][0]["name"] == "Kunang Kelam A" and b["enemies"][0]["max_hp"] > 0
    assert b["bara_max"] == 0, "Bara belum diperoleh di prolog"
    assert b["round"] >= 1


def test_ruang_dikirim_saat_masuk_dan_diperbarui(client):
    """Snapshot ruang dikirim begitu masuk (sebelum skrip), lalu diperbarui."""
    d = start(client)
    rooms = advance(d, lambda x: x.kinds("room"))
    assert rooms, "event ruang tidak pernah dikirim"
    r = rooms[0]
    assert r["area"] == "Pelita Rendah" and r["room_id"] == "gerbang_timur"
    assert r["area_id"] == "pelita_rendah" and r["fog"] is False
    assert [h["key"] for h in r["party"]] == ["rimba"], "sebelum prolog hanya Rimba"
    assert r["party"][0]["max_hp"] > 0 and r["keping"] >= 0

    # setelah prolog, Guntur ikut dan snapshot berikutnya memuatnya
    rooms2 = advance(d, lambda x: [q for q in x.kinds("room") if len(q["party"]) > 1])
    assert rooms2 and [h["key"] for h in rooms2[-1]["party"]] == ["rimba", "guntur"]


def test_pilihan_muncul_sebagai_opsi(client):
    """Menu ruang sampai ke klien sebagai daftar opsi + pintasan huruf."""
    d = start(client)

    def menu_ruang(x):
        p = x.last_prompt()
        if p and any("jalan desa" in o["label"].lower() for o in p["options"]):
            return p
        return None

    p = advance(d, menu_ruang)
    assert p, "menu ruang tidak muncul"
    assert any(o.get("meta") for o in p["options"]), "pintasan [P]arty dll harus ikut"
    assert all(o["key"] and o["label"] for o in p["options"])


def test_pertarungan_berakhir_dan_melaporkan_hadiah(client):
    d = start(client)
    end = advance(d, lambda x: x.kinds("battle_end"))
    assert end, "tidak ada event battle_end"
    assert end[-1]["outcome"] in ("menang", "kalah", "kabur")
    if end[-1]["outcome"] == "menang":
        assert end[-1]["xp"] > 0
    bs = d.kinds("battle")
    assert any(not e["alive"] for e in bs[-1]["enemies"]), "musuh harus tumbang di snapshot terakhir"


def test_log_pertarungan_bisa_diurai_untuk_angka_damage(client):
    """Klien mengambil angka damage dari baris log; pastikan polanya ada."""
    pola = re.compile(r"^\s*(.+?) terkena (\d+) damage")
    d = start(client)
    hit = advance(d, lambda x: [l for l in (e["text"] for e in x.kinds("log")) if l and pola.match(l)])
    assert hit, "tidak ada baris damage di log"
    nama, angka = pola.match(hit[0]).groups()
    assert nama.strip() and int(angka) > 0


def test_tutup_sesi_menghentikan_thread(client):
    d = start(client)
    d.pump()
    assert client.post(f"/api/session/{d.sid}/close", json={}).status_code == 200
    assert client.get(f"/api/session/{d.sid}/state").status_code == 404


def test_simpan_lalu_muat_slot(client, tmp_path):
    """Simpan di lentera gerbang, lalu mulai sesi baru dari slot itu."""
    d = start(client)

    def lentera(x):
        p = x.last_prompt()
        if not p:
            return None
        return next((o for o in p["options"] if "lentera penjaga" in o["label"].lower()), None)

    opt = advance(d, lentera)
    assert opt, "objek lentera penjaga tidak muncul di menu"
    d.send(opt["key"])
    p = d.pump()                       # skrip lentera → menu slot
    assert p and p["options"], "menu slot tidak muncul"
    d.send(p["options"][0]["key"])
    d.pump()

    slots = client.get("/api/slots").get_json()["slots"]
    assert any(slots), "save tidak tertulis"

    d2 = start(client, slot=1)
    assert advance(d2, lambda x: x.kinds("room")), "sesi yang dimuat harus mengirim ruang"


# ── Unit: WebIO ──────────────────────────────────────────────────────────
def test_webio_mengumpulkan_opsi(tmp_path):
    store = SessionStore(tmp_path)
    s = store.create()
    try:
        io = s.io
        io._pending_options = []
        io.line("  1) Masuk ke jalan desa")
        io.line("  2) Bicara: Bu Ratna")
        io.line("  [P]arty  [I]tem  [K]eluar")
        assert [o["key"] for o in io._pending_options] == ["1", "2", "p", "i", "k"]
        assert io._pending_options[0]["label"] == "Masuk ke jalan desa"
        assert io._pending_options[2]["meta"] is True
    finally:
        store.drop(s.id)


def test_io_terminal_mengabaikan_emit():
    from pelita.ui.terminal import IO
    io = IO(read=lambda p: "", write=lambda s: None)
    assert io.structured is False
    io.emit("battle", {"apa": "saja"})          # tidak boleh melempar
