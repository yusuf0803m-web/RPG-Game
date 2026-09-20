#!/usr/bin/env python3
"""Proses gambar yang SUDAH dibuat manual lewat ChatGPT Image Generation.

Skrip ini TIDAK membuat gambar apa pun dan TIDAK memanggil API image-generation apa pun.
Tugasnya murni pasca-produksi: mengambil berkas gambar yang sudah kamu unduh dari ChatGPT
dan menaruhnya di folder "incoming", lalu:

  1. mencocokkan tiap berkas ke aset di ``prompts/latar_prompts.json``
  2. memvalidasi dimensinya (menolak yang potret/terlalu jauh dari 16:9)
  3. memotong-dan-mengubah ukuran ke 1600x900 (crop tengah ke rasio target, lalu resize)
  4. mengonversinya ke WebP
  5. mengompresnya bertahap sampai di bawah 250 KB (atau sedekat mungkin)
  6. menyimpannya ke path aset yang benar: pelita/web/static/assets/backgrounds/<asset_path>
  7. melaporkan berkas mana saja yang tidak bisa diproses, dan kenapa

Alur pakai: lihat ``prompts/README.md``. Singkatnya -- generate gambar di ChatGPT, unduh,
lalu simpan/ganti nama berkasnya sebagai ``<asset_id>.<ext>`` (mis.
``pelita_rendah_warung.png``) ke dalam ``prompts/generated_incoming/`` (folder ini dibuat
otomatis kalau belum ada), lalu jalankan skrip ini.

Membutuhkan Pillow (bukan dependensi wajib permainan, murni untuk alat ini):

    pip install Pillow
    # atau: pip install -e ".[images]"

    python tools/prepare_generated_images.py                 # proses semua yang cocok
    python tools/prepare_generated_images.py --dry-run        # laporan saja, tanpa menulis
    python tools/prepare_generated_images.py --priority 1
    python tools/prepare_generated_images.py --category event
    python tools/prepare_generated_images.py --id pelita_rendah_warung
    python tools/prepare_generated_images.py --force           # timpa .webp final yang sudah ada
    python tools/prepare_generated_images.py --incoming /path/lain

Tidak menyentuh pelita/data/world/latar.json, kode gameplay, atau logika pembuatan prompt.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "prompts" / "latar_prompts.json"
DEFAULT_INCOMING = ROOT / "prompts" / "generated_incoming"
ASET_DIR = ROOT / "pelita" / "web" / "static" / "assets" / "backgrounds"

TARGET_WIDTH, TARGET_HEIGHT = 1600, 900
TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT  # 16:9
DEFAULT_MAX_KB = 250
DEFAULT_START_QUALITY = 90
DEFAULT_FLOOR_QUALITY = 35
DEFAULT_QUALITY_STEP = 5
CROP_LOSS_WARN = 0.30  # peringatan kalau crop membuang >30% lebar/tinggi sumber

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

CATEGORY_ALIASES = {"lokasi": "location", "location": "location", "variant": "variant", "event": "event", "all": "all"}


def load_pillow():
    try:
        from PIL import Image
    except ImportError:
        print(
            "Pillow tidak terpasang. Alat ini butuh Pillow untuk resize/convert/compress:\n"
            "  pip install Pillow\n"
            "  # atau: pip install -e \".[images]\"",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return Image


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        print(
            f"Tidak ditemukan: {MANIFEST_PATH.relative_to(ROOT)}. "
            "Jalankan dulu: python tools/generate_latar_prompts.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["assets"]


def select_assets(assets: list[dict], priority: Optional[int], category: str, asset_id: Optional[str]) -> list[dict]:
    out = assets
    if priority is not None:
        out = [a for a in out if a["priority"] == priority]
    if category != "all":
        out = [a for a in out if a["category"] == category]
    if asset_id:
        target = asset_id.strip()
        if target.endswith(".webp"):
            target = target[: -len(".webp")]
        target_flat = target.replace("/", "_")
        out = [a for a in out if a["id"] in (target, target_flat) or a["asset_path"][: -len(".webp")] == target]
    return out


def find_incoming_files(incoming_dir: Path) -> list[Path]:
    if not incoming_dir.exists():
        return []
    return sorted(
        p for p in incoming_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def match_asset(file_path: Path, incoming_dir: Path, by_id: dict[str, dict],
                 by_path_stem: dict[str, dict]) -> Optional[dict]:
    """Cocokkan berkas incoming ke aset lewat dua cara: nama rata (id) atau struktur folder
    yang meniru asset_path (mis. incoming/pelita_rendah/warung.png)."""
    rel = file_path.relative_to(incoming_dir).with_suffix("")
    rel_posix = rel.as_posix()
    if rel_posix in by_path_stem:
        return by_path_stem[rel_posix]
    flat = rel_posix.replace("/", "_")
    if flat in by_id:
        return by_id[flat]
    stem = file_path.stem
    if stem in by_id:
        return by_id[stem]
    if stem in by_path_stem:
        return by_path_stem[stem]
    return None


def fit_to_target(image, target_width: int, target_height: int):
    """Crop tengah ke rasio target, lalu resize pas ke target_width x target_height.

    Mengembalikan (gambar_hasil, fraksi_crop_lebar, fraksi_crop_tinggi).
    """
    w, h = image.size
    target_ratio = target_width / target_height
    src_ratio = w / h
    if src_ratio > target_ratio:
        new_w = round(h * target_ratio)
        x0 = (w - new_w) // 2
        box = (x0, 0, x0 + new_w, h)
        crop_w_frac = 1 - new_w / w
        crop_h_frac = 0.0
    else:
        new_h = round(w / target_ratio)
        y0 = (h - new_h) // 2
        box = (0, y0, w, y0 + new_h)
        crop_w_frac = 0.0
        crop_h_frac = 1 - new_h / h
    cropped = image.crop(box)
    resized = cropped.resize((target_width, target_height))
    return resized, crop_w_frac, crop_h_frac


def save_webp_under_limit(image, out_path: Path, max_kb: int, start_quality: int,
                           floor_quality: int, step: int) -> tuple[int, int, bool]:
    """Simpan sebagai WebP, menurunkan kualitas bertahap sampai di bawah max_kb.

    Mengembalikan (quality_dipakai, ukuran_byte, berhasil_di_bawah_limit).
    """
    quality = start_quality
    last_data = b""
    while quality >= floor_quality:
        buf = io.BytesIO()
        image.save(buf, format="WEBP", quality=quality, method=6)
        data = buf.getvalue()
        last_data = data
        if len(data) <= max_kb * 1024:
            out_path.write_bytes(data)
            return quality, len(data), True
        quality -= step
    out_path.write_bytes(last_data)
    return floor_quality, len(last_data), False


def process_one(Image, src: Path, asset: dict, dry_run: bool, force: bool,
                 max_kb: int, start_quality: int, floor_quality: int, step: int) -> dict:
    out_path = ASET_DIR / asset["asset_path"]
    result = {
        "source": str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src),
        "asset_id": asset["id"],
        "output_path": str(out_path.relative_to(ROOT)),
        "status": None,
        "reason": None,
    }

    if out_path.exists() and not force:
        result["status"] = "skipped_exists"
        result["reason"] = "berkas final sudah ada (pakai --force untuk menimpa)"
        return result

    try:
        image = Image.open(src)
        image.load()
    except Exception as exc:  # noqa: BLE001 -- laporkan apa pun kegagalan baca gambar
        result["status"] = "failed"
        result["reason"] = f"tidak bisa dibaca sebagai gambar: {exc}"
        return result

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
    elif image.mode == "RGBA":
        # WebP mendukung alpha, tapi latar game tidak butuh transparansi -- ratakan ke RGB
        # supaya ukuran berkas & tampilan konsisten dengan aset lain.
        background = Image.new("RGB", image.size, (0, 0, 0))
        background.paste(image, mask=image.split()[3])
        image = background

    w, h = image.size
    if w <= 0 or h <= 0:
        result["status"] = "failed"
        result["reason"] = "dimensi gambar tidak valid"
        return result
    if w < h:
        result["status"] = "failed"
        result["reason"] = (
            f"gambar potret ({w}x{h}) -- tidak bisa dipotong jadi 16:9 tanpa kehilangan "
            "sebagian besar isinya; generate ulang di ChatGPT dengan opsi landscape"
        )
        return result

    fitted, crop_w_frac, crop_h_frac = fit_to_target(image, TARGET_WIDTH, TARGET_HEIGHT)
    crop_note = None
    worst_crop = max(crop_w_frac, crop_h_frac)
    if worst_crop > CROP_LOSS_WARN:
        axis = "lebar" if crop_w_frac > crop_h_frac else "tinggi"
        crop_note = (
            f"crop membuang {worst_crop:.0%} {axis} sumber ({w}x{h} -> {TARGET_WIDTH}x{TARGET_HEIGHT}); "
            "pertimbangkan generate ulang lebih dekat ke 16:9"
        )

    if dry_run:
        result["status"] = "would_process"
        result["reason"] = crop_note
        return result

    out_path.parent.mkdir(parents=True, exist_ok=True)
    quality, size_bytes, under_limit = save_webp_under_limit(
        fitted, out_path, max_kb, start_quality, floor_quality, step
    )
    result["status"] = "processed" if under_limit else "processed_over_limit"
    size_kb = size_bytes / 1024
    notes = [f"{size_kb:.1f}KB @ quality={quality}"]
    if not under_limit:
        notes.append(f"masih di atas {max_kb}KB walau sudah di quality floor {floor_quality}")
    if crop_note:
        notes.append(crop_note)
    result["reason"] = "; ".join(notes)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Proses gambar hasil ChatGPT Image Generation menjadi aset latar final "
            "(resize 1600x900, convert WebP, kompres <250KB). Tidak membuat gambar."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--incoming", type=Path, default=DEFAULT_INCOMING,
                     help=f"folder berisi gambar mentah hasil ChatGPT (bawaan: {DEFAULT_INCOMING.relative_to(ROOT)})")
    ap.add_argument("--priority", type=int, choices=(1, 2, 3), help="batasi ke aset prioritas ini")
    ap.add_argument("--category", choices=("lokasi", "location", "variant", "event", "all"), default="all",
                     help="batasi ke kategori ini ('lokasi' alias 'location')")
    ap.add_argument("--id", dest="asset_id", help="hanya proses satu aset (id)")
    ap.add_argument("--force", action="store_true", help="timpa berkas .webp final yang sudah ada")
    ap.add_argument("--dry-run", action="store_true", help="laporkan saja, jangan menulis berkas apa pun")
    ap.add_argument("--max-kb", type=int, default=DEFAULT_MAX_KB, help=f"target ukuran maksimum (bawaan: {DEFAULT_MAX_KB})")
    ap.add_argument("--start-quality", type=int, default=DEFAULT_START_QUALITY)
    ap.add_argument("--floor-quality", type=int, default=DEFAULT_FLOOR_QUALITY)
    args = ap.parse_args()

    Image = load_pillow()

    assets = load_manifest()
    category = CATEGORY_ALIASES[args.category]
    scoped = select_assets(assets, args.priority, category, args.asset_id)
    if args.asset_id and not scoped:
        print(f"Tidak ada entri untuk --id {args.asset_id!r} di prompts/latar_prompts.json.", file=sys.stderr)
        return 1
    by_id = {a["id"]: a for a in scoped}
    by_path_stem = {a["asset_path"][: -len(".webp")]: a for a in scoped}

    args.incoming.mkdir(parents=True, exist_ok=True)
    files = find_incoming_files(args.incoming)

    results = []
    unmatched: list[str] = []
    for f in files:
        asset = match_asset(f, args.incoming, by_id, by_path_stem)
        if asset is None:
            unmatched.append(str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f))
            continue
        results.append(
            process_one(
                Image, f, asset, args.dry_run, args.force,
                args.max_kb, args.start_quality, args.floor_quality, DEFAULT_QUALITY_STEP,
            )
        )

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print(f"Folder incoming: {args.incoming.relative_to(ROOT) if args.incoming.is_relative_to(ROOT) else args.incoming}")
    print(f"Berkas gambar ditemukan: {len(files)}")
    print(f"Cocok dengan aset: {len(results)}")
    print(f"Tidak cocok (nama tidak dikenali): {len(unmatched)}")
    print()
    for status in ("processed", "processed_over_limit", "would_process", "skipped_exists", "failed"):
        if status in counts:
            print(f"{status}: {counts[status]}")
    print()

    problems = [r for r in results if r["status"] in ("failed", "processed_over_limit")]
    if problems:
        print("Berkas yang perlu perhatian:")
        for r in problems:
            print(f"  - [{r['status']}] {r['source']} -> {r['output_path']}: {r['reason']}")
        print()

    if unmatched:
        print("Berkas yang tidak cocok dengan aset mana pun (ganti nama sesuai asset id):")
        for u in unmatched:
            print(f"  - {u}")
        print()

    if args.dry_run:
        print("(--dry-run: tidak ada berkas yang ditulis)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
