"""Tes sistem latar bergambar (GAME_DESIGN §7.2)."""
import json
from pathlib import Path

import pytest

from pelita.loader import DataError, load_data
from pelita.world.explore import Game
from pelita.world.model import load_world
from pelita.world.state import new_game
from tests.walker import Walker

ASET = Path("pelita/web/static/assets/backgrounds")


@pytest.fixture(scope="module")
def data():
    return load_data()


@pytest.fixture(scope="module")
def world(data):
    return load_world(data)


def test_setiap_ruang_punya_latar_terdaftar(world):
    """Tiap ruang harus memetakan ke gambar yang ada di latar.json — ini yang menangkap salah ketik."""
    for a in world.areas.values():
        for r in a.rooms.values():
            path = world.latar_ruang(a, r, lambda c: False)
            assert path in world.latar, f"{a.id}/{r.id} -> {path}"


def test_varian_memakai_flag_yang_benar_benar_dipakai_cerita(world):
    """Varian yang syaratnya tidak pernah menyala hanya akan jadi gambar mubazir."""
    dipakai = set()
    for a in world.areas.values():
        for cmds in a.scripts.values():
            dipakai |= _flags(cmds)
    for a in world.areas.values():
        for r in a.rooms.values():
            for v in r.latar_varian:
                for cond in v.cond:
                    assert str(cond).lstrip("!") in dipakai, f"{a.id}/{r.id}: flag '{cond}' tidak pernah di-set"


def _flags(cmds) -> set:
    out = set()
    for c in cmds:
        if not isinstance(c, dict):
            continue
        if "set" in c:
            out |= set(c["set"] if isinstance(c["set"], list) else [c["set"]])
        if "once" in c:
            out.add(c["once"])
        for k in ("then", "else", "do", "win", "on_lose", "on_flee"):
            if isinstance(c.get(k), list):
                out |= _flags(c[k])
        for o in c.get("choice", []) or []:
            out |= _flags(o.get("then", []))
    return out


def test_latar_mengikuti_kondisi_dunia(data, world):
    a = world.area("pelita_rendah")
    warung = a.room("warung")
    st = new_game(data)
    assert world.latar_ruang(a, warung, st.check) == "pelita_rendah/warung"
    st.flags.add("guntur_hilang")
    assert world.latar_ruang(a, warung, st.check) == "pelita_rendah/warung_sepi"
    st.flags.add("desa_epilog")
    assert world.latar_ruang(a, warung, st.check) == "pelita_rendah/warung_pulih"


def test_ruang_bisa_berbagi_gambar(world):
    a = world.area("pelita_rendah")
    assert world.latar_ruang(a, a.room("gerbang_barat"), lambda c: False) == "pelita_rendah/gerbang_timur"


def test_snapshot_ruang_membawa_latar(data, world, tmp_path):
    st = new_game(data)
    st.area_id, st.room_id = "pelita_rendah", "warung"
    g = Game(data, world, st, Walker([]).io, auto_battle=True, auto_script=True, save_dir=tmp_path)
    assert g.room_snapshot()["latar"] == "pelita_rendah/warung"
    st.flags.add("guntur_hilang")
    assert g.room_snapshot()["latar"] == "pelita_rendah/warung_sepi"


def test_semua_entri_latar_punya_deskripsi_untuk_penggambar(world):
    for path, info in world.latar.items():
        assert info.get("nama"), path
        assert len(info.get("deskripsi", "")) > 20, f"{path}: deskripsi terlalu pendek untuk digambar"
        assert info.get("kategori") in ("lokasi", "varian", "peristiwa"), path
        assert info.get("prioritas") in (1, 2, 3), path


def test_ilustrasi_peristiwa_dipakai_di_skrip(world):
    """Gambar peristiwa yang tidak pernah dipanggil skrip tidak perlu digambar."""
    dipakai = set()
    for a in world.areas.values():
        for cmds in a.scripts.values():
            dipakai |= _ilustrasi(cmds)
    terdaftar = {p for p, i in world.latar.items() if i["kategori"] == "peristiwa"}
    belum = terdaftar - dipakai
    assert not (dipakai - terdaftar), f"skrip memanggil ilustrasi tak terdaftar: {dipakai - terdaftar}"
    # Sisanya memang disiapkan untuk babak berikutnya; cukup pastikan sebagian sudah dipakai.
    assert len(dipakai) >= 3, f"baru {len(dipakai)} ilustrasi dipakai (belum: {sorted(belum)})"


def _ilustrasi(cmds) -> set:
    out = set()
    for c in cmds:
        if not isinstance(c, dict):
            continue
        if "ilustrasi" in c:
            out.add(c["ilustrasi"])
        if "adegan" in c and c["adegan"].get("latar"):
            out.add(c["adegan"]["latar"])
        for k in ("then", "else", "do", "win", "on_lose", "on_flee"):
            if isinstance(c.get(k), list):
                out |= _ilustrasi(c[k])
        for o in c.get("choice", []) or []:
            out |= _ilustrasi(o.get("then", []))
    return out


def test_latar_salah_ketik_ditolak(data, tmp_path):
    """Kalau seseorang menulis path yang tidak ada di latar.json, dunia harus menolak dimuat."""
    src = Path("pelita/data/world")
    for f in src.glob("*.json"):
        (tmp_path / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    f = tmp_path / "area_01_pelita_rendah.json"
    a = json.loads(f.read_text())
    a["rooms"]["warung"]["latar"] = "pelita_rendah/warung_yang_tidak_ada"
    f.write_text(json.dumps(a, ensure_ascii=False))
    with pytest.raises(DataError):
        load_world(data, tmp_path, use_cache=False)


def test_ilustrasi_muncul_sebagai_event_terstruktur(data, world, tmp_path):
    """Klien web menggambar ilustrasi dari event; terminal mencetak keterangannya."""
    from pelita.world.script import Hooks, ScriptRunner

    st = new_game(data)
    st.area_id, st.room_id = "pelita_rendah", "warung"
    wk = Walker([])
    terkirim = []
    wk.io.emit = lambda kind, payload: terkirim.append((kind, payload))
    runner = ScriptRunner(st, wk.io, Hooks(lambda *a: "menang", lambda: None, lambda s: None,
                                           lambda n: None, lambda r, a: None), auto=True)
    runner.run_commands(world.area("pelita_rendah"),
                        [{"ilustrasi": "events/malam_pertama", "teks": "Malam pertama."},
                         {"adegan": {"latar": "pelita_rendah/warung_sepi", "efek": "gelap"}}])
    jenis = dict((k, v) for k, v in terkirim)
    assert jenis["ilustrasi"]["latar"] == "events/malam_pertama"
    assert jenis["adegan"] == {"latar": "pelita_rendah/warung_sepi", "efek": "gelap"}
    assert any("Malam pertama" in l for l in wk.out)


def test_folder_aset_dan_panduan_ada():
    assert (ASET / "README.md").exists(), "jalankan python tools/daftar_latar.py --tulis"
    teks = (ASET / "README.md").read_text(encoding="utf-8")
    assert "1600×900" in teks and "prosedural" in teks


def test_server_yang_menentukan_gambar_mana_yang_ada(tmp_path, monkeypatch):
    """Klien tidak boleh menebak: server hanya mengirim URL untuk berkas yang benar-benar ada."""
    from pelita.web import session as sesi

    monkeypatch.setattr(sesi, "ASET_LATAR", tmp_path)
    assert sesi.url_latar("pelita_rendah/warung") == ""
    (tmp_path / "pelita_rendah").mkdir()
    (tmp_path / "pelita_rendah" / "warung.webp").write_bytes(b"bukan-gambar-sungguhan")
    assert sesi.url_latar("pelita_rendah/warung") == "/static/assets/backgrounds/pelita_rendah/warung.webp"
    assert sesi.url_latar("") == ""
    assert sesi.url_latar("../../../etc/passwd") == ""


def test_event_ruang_membawa_url_latar(data, world, tmp_path):
    from pelita.web.session import WebSession

    s = WebSession(data, world, new_game(data), tmp_path).start()
    try:
        for _ in range(200):
            ev = [e for e in s.events if e.kind == "room"]
            if ev:
                assert "latar" in ev[0].payload and "latar_url" in ev[0].payload
                return
            import time
            time.sleep(0.02)
        pytest.fail("event ruang tidak pernah dikirim")
    finally:
        s.close()
