"""Server Flask untuk antarmuka web Pelita Terakhir.

    python -m pelita --web          # hanya komputer ini (http://127.0.0.1:5000)
    python -m pelita --web --lan    # bisa dibuka dari HP di Wi-Fi yang sama

API:
    GET  /                                   halaman permainan
    GET  /api/slots                          ringkasan slot save
    POST /api/session                        {"slot": N|null} → {"id": ...}
    GET  /api/session/<id>/state?since=N     long-poll event (log, room, battle, say, prompt, ...)
    POST /api/session/<id>/input             {"text": "3"}
    POST /api/session/<id>/close             hentikan sesi
"""
from __future__ import annotations

import socket
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, request, send_from_directory

from ..world.state import SAVE_DIR
from .session import SessionStore

STATIC = Path(__file__).parent / "static"


def create_app(save_dir: Optional[Path] = None) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC), static_url_path="/static")
    store = SessionStore(Path(save_dir) if save_dir else SAVE_DIR)
    app.config["STORE"] = store

    @app.get("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.get("/manifest.webmanifest")
    def manifest():
        r = send_from_directory(STATIC, "manifest.webmanifest")
        r.headers["Content-Type"] = "application/manifest+json"
        return r

    @app.get("/api/slots")
    def slots():
        return jsonify({"slots": store.slots(), "count": store.slot_count})

    @app.post("/api/session")
    def create_session():
        body = request.get_json(silent=True) or {}
        slot = body.get("slot")
        try:
            s = store.load_slot(int(slot)) if slot else store.create()
        except (OSError, ValueError, KeyError) as e:
            return jsonify({"error": f"Tidak bisa memuat save: {e}"}), 400
        return jsonify({"id": s.id})

    @app.get("/api/session/<sid>/state")
    def state(sid: str):
        s = store.get(sid)
        if not s:
            return jsonify({"error": "Sesi tidak ada atau sudah berakhir."}), 404
        since = request.args.get("since", type=int, default=0)
        timeout = request.args.get("timeout", type=float, default=25.0)
        return jsonify(s.poll(since, min(max(timeout, 0.0), 30.0)))

    @app.post("/api/session/<sid>/input")
    def send_input(sid: str):
        s = store.get(sid)
        if not s:
            return jsonify({"error": "Sesi tidak ada atau sudah berakhir."}), 404
        body = request.get_json(silent=True) or {}
        s.send(str(body.get("text", "")))
        return jsonify({"ok": True})

    @app.post("/api/session/<sid>/close")
    def close(sid: str):
        store.drop(sid)
        return jsonify({"ok": True})

    return app


def local_ip() -> str:
    """Alamat IP komputer ini di jaringan lokal (untuk dibuka dari HP).

    Memakai soket UDP yang tidak pernah mengirim apa pun; ini hanya cara
    menanyakan ke sistem operasi antarmuka mana yang dipakai untuk keluar.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="pelita.web", description="Pelita Terakhir — antarmuka web")
    ap.add_argument("--host", default="127.0.0.1", help="alamat bind (default: hanya komputer ini)")
    ap.add_argument("--lan", action="store_true",
                    help="izinkan perangkat lain di Wi-Fi yang sama (mis. HP) membuka permainan")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--save-dir", default=str(SAVE_DIR))
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args(argv)

    host = "0.0.0.0" if args.lan else args.host      # noqa: S104 — disengaja, lihat peringatan di bawah
    app = create_app(Path(args.save_dir))
    print("\n  Pelita Terakhir")
    if args.lan or host == "0.0.0.0":
        ip = local_ip()
        print(f"  Di komputer ini : http://127.0.0.1:{args.port}")
        print(f"  Di HP/tablet    : http://{ip}:{args.port}   (harus satu Wi-Fi)")
        print("  Catatan: permainan terbuka bagi siapa pun di jaringan ini dan tidak")
        print("  memakai kata sandi. Jangan pakai --lan di Wi-Fi publik.\n")
    else:
        print(f"  Buka http://{host}:{args.port}")
        print("  Mau main dari HP? Jalankan ulang dengan --lan\n")
    app.run(host=host, port=args.port, debug=args.debug, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
