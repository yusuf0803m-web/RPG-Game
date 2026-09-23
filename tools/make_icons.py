"""Menghasilkan ikon PNG untuk PWA tanpa dependensi (zlib + struct saja).

    python tools/make_icons.py

Menulis ``pelita/web/static/icon-192.png`` dan ``icon-512.png``: lentera perunggu
dengan nyala di latar gelap, dengan margin aman agar cocok sebagai ikon *maskable*
Android (sistem boleh memotongnya jadi lingkaran atau kotak bulat).
"""
from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pelita" / "web" / "static"
ANDROID_RES = ROOT / "android" / "app" / "src" / "main" / "res"

#: ikon launcher Android: nama folder mipmap → sisi dalam piksel
MIPMAP = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}

BG = (0x0E, 0x12, 0x19)
BRONZE_DARK = (0x5D, 0x43, 0x1F)
BRONZE = (0x7A, 0x5A, 0x2E)
NYALA = (0xF0, 0xB4, 0x5C)
NYALA_HOT = (0xFF, 0xD8, 0x9A)


def blend(dst, src, a):
    return tuple(int(d + (s - d) * a) for d, s in zip(dst, src))


def write_png(path: Path, pixels: list[list[tuple[int, int, int]]]) -> None:
    h, w = len(pixels), len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)                       # filter type 0 (None)
        for r, g, b in row:
            raw += bytes((r, g, b))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def draw(size: int) -> list[list[tuple[int, int, int]]]:
    """Gambar lentera di tengah. Semua koordinat relatif agar skala bebas."""
    px = [[BG for _ in range(size)] for _ in range(size)]
    cx, cy = size / 2, size / 2
    u = size / 100.0                        # satuan: 1% dari sisi

    def rect(x0, y0, x1, y1, col, radius=0.0):
        for y in range(max(0, int(y0)), min(size, int(y1) + 1)):
            for x in range(max(0, int(x0)), min(size, int(x1) + 1)):
                if radius:
                    dx = max(x0 + radius - x, 0, x - (x1 - radius))
                    dy = max(y0 + radius - y, 0, y - (y1 - radius))
                    if dx * dx + dy * dy > radius * radius:
                        continue
                px[y][x] = col

    # halo cahaya
    glow_r = 34 * u
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy - 2 * u)
            if d < glow_r:
                a = (1 - d / glow_r) ** 2.2 * 0.5
                px[y][x] = blend(px[y][x], NYALA, a)

    # badan lentera (kaca) + tepi
    bw, bh = 15 * u, 20 * u
    rect(cx - bw, cy - bh * 0.35, cx + bw, cy + bh * 0.9, BRONZE_DARK, radius=4 * u)
    rect(cx - bw + 2.2 * u, cy - bh * 0.35 + 2.2 * u, cx + bw - 2.2 * u, cy + bh * 0.9 - 2.2 * u,
         NYALA, radius=3 * u)

    # nyala di dalam kaca
    for y in range(size):
        for x in range(size):
            d = math.hypot((x - cx) * 1.5, y - (cy + 2 * u))
            if d < 7 * u:
                px[y][x] = blend(px[y][x], NYALA_HOT, (1 - d / (7 * u)) ** 1.4)

    # atap trapesium
    top_y, roof_h = cy - bh * 0.35, 7 * u
    for i in range(int(roof_h) + 1):
        t = i / max(roof_h, 1)
        half = bw + 4 * u - (bw + 4 * u - 6 * u) * (1 - t) * 0  # lebar tetap
        half = (6 * u) + (bw + 4 * u - 6 * u) * t
        rect(cx - half, top_y - roof_h + i, cx + half, top_y - roof_h + i + 1, BRONZE)

    # gagang
    rect(cx - 1.2 * u, top_y - roof_h - 7 * u, cx + 1.2 * u, top_y - roof_h + 1, BRONZE_DARK)
    rect(cx - 6 * u, top_y - roof_h - 8.5 * u, cx + 6 * u, top_y - roof_h - 6.5 * u, BRONZE_DARK, radius=1.2 * u)

    # dasar
    rect(cx - bw - 2 * u, cy + bh * 0.9, cx + bw + 2 * u, cy + bh * 0.9 + 3.5 * u, BRONZE, radius=1.5 * u)
    return px


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for size in (192, 512):
        path = OUT / f"icon-{size}.png"
        write_png(path, draw(size))
        print(f"  {path.relative_to(ROOT)}  {path.stat().st_size} bytes")

    if ANDROID_RES.exists() or "--android" in sys.argv:
        for dpi, size in MIPMAP.items():
            d = ANDROID_RES / f"mipmap-{dpi}"
            d.mkdir(parents=True, exist_ok=True)
            px = draw(size)
            write_png(d / "ic_launcher.png", px)
            write_png(d / "ic_launcher_round.png", px)
            print(f"  {(d / 'ic_launcher.png').relative_to(ROOT)}  {size}x{size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
