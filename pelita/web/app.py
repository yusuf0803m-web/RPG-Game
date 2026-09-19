"""Server Flask untuk antarmuka web Pelita Terakhir.

    python -m pelita.web            # http://127.0.0.1:5000
    python -m pelita --web          # sama

API:
    GET  /                                   halaman permainan
    GET  /api/slots                          ringkasan slot save
    POST /api/session                        {"slot": N|null} → {"id": ...}
    GET  /api/session/<id>/state?since=N     long-poll event (log, room, battle, say, prompt, ...)
    POST /api/session/<id>/input             {"text": "3"}
    POST /api/session/<id>/close             hentikan sesi
"""
from __future__ import annotations

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


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="pelita.web", description="Pelita Terakhir — antarmuka web")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--save-dir", default=str(SAVE_DIR))
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args(argv)
    app = create_app(Path(args.save_dir))
    print(f"Pelita Terakhir — buka http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
