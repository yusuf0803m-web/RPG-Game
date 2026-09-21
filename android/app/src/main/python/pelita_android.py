"""Titik masuk Python di dalam APK.

Dipanggil dari ``MainActivity``. Tugasnya hanya menjalankan aplikasi Flask yang
sama dengan versi desktop; seluruh aturan permainan tetap di paket ``pelita``.
"""
from __future__ import annotations

import os
import sys
import traceback


def jalankan_server(host: str, port: int, dir_simpanan: str) -> None:
    """Jalankan server permainan. Memblokir, jadi panggil dari thread tersendiri."""
    try:
        os.makedirs(dir_simpanan, exist_ok=True)

        from pathlib import Path

        from pelita.web.app import create_app

        app = create_app(Path(dir_simpanan))
        # Server bawaan Werkzeug sudah cukup: satu pemain, satu perangkat, loopback.
        app.run(host=host, port=int(port), threaded=True,
                debug=False, use_reloader=False)
    except Exception:                      # noqa: BLE001 — kirim ke logcat agar bisa didiagnosis
        traceback.print_exc(file=sys.stderr)
        raise


def cek_kesehatan() -> str:
    """Muat data permainan tanpa menyalakan server. Dipakai untuk uji cepat di CI."""
    from pelita.loader import load_data
    from pelita.world.model import load_world

    data = load_data()
    world = load_world(data)
    return (f"pelita siap: {len(data.characters)} karakter, {len(data.enemies)} musuh, "
            f"{len(world.areas)} area")
