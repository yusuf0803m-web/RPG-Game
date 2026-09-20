#!/usr/bin/env python3
"""Ekspor batch prompt siap-pakai untuk ChatGPT Image Generation.

TIDAK menghasilkan gambar apa pun dan TIDAK memanggil API image-generation apa pun.
Skrip ini murni mengubah ``prompts/latar_prompts.json`` (dihasilkan oleh
``tools/generate_latar_prompts.py``) menjadi dua bentuk batch yang mudah dipakai secara
manual di ChatGPT:

  - satu berkas Markdown manusiawi, dikelompokkan Prioritas -> Kategori -> Region, tiap
    aset punya bagian IMAGE PROMPT dan NEGATIVE / AVOID yang terpisah jelas supaya tinggal
    disalin
  - satu berkas JSON yang sama isinya, untuk dipakai alat lain (mis. ``tools/
    prepare_generated_images.py`` setelah gambarnya jadi)

Prompt itu sendiri TIDAK diubah -- skrip ini hanya membaca ulang apa yang sudah dirakit
``tools/generate_latar_prompts.py`` dan menatanya jadi batch. Tidak menyentuh
``pelita/data/world/latar.json``, kode gameplay, atau logika pembuatan prompt yang sudah
ada.

    python tools/export_image_generation_batch.py                       # semua aset
    python tools/export_image_generation_batch.py --priority 1
    python tools/export_image_generation_batch.py --category variant
    python tools/export_image_generation_batch.py --category lokasi     # alias "location"
    python tools/export_image_generation_batch.py --category event
    python tools/export_image_generation_batch.py --id pelita_rendah_warung

Keluaran (selalu ke ``prompts/batches/``, nama berkas ditentukan oleh filter yang aktif
sehingga deterministik dan idempoten -- run yang sama menghasilkan berkas yang sama):

  - ``prompts/batches/<nama-batch>.md``
  - ``prompts/batches/<nama-batch>.json``

Lihat ``prompts/README.md`` untuk alur kerja lengkap bersama ChatGPT Image Generation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "prompts" / "latar_prompts.json"
BATCH_DIR = ROOT / "prompts" / "batches"
ASSET_ROOT = "pelita/web/static/assets/backgrounds"

# ChatGPT Image Generation tidak menawarkan 16:9 secara native; opsi landscape bawaannya
# adalah rasio ~3:2. Ini murni saran alur kerja, tidak mengubah target aset final.
CHATGPT_LANDSCAPE_SIZE = "1536x1024"
TARGET_SIZE = "1600x900"
TARGET_RATIO = "16:9"

CATEGORY_ALIASES = {
    "lokasi": "location",
    "location": "location",
    "variant": "variant",
    "event": "event",
    "all": "all",
}
CATEGORY_ORDER = {"location": 0, "variant": 1, "event": 2}
CATEGORY_LABEL = {"location": "Location", "variant": "Variant", "event": "Event"}

NOTES_BY_CATEGORY = {
    "location": (
        "Reusable in-game background. Keep the lower third of the frame clear -- the "
        "game adds its own dark dialogue gradient there. Do not add prominent characters "
        "unless the prompt explicitly calls for one as an environmental storytelling "
        "detail."
    ),
    "variant": (
        "World-state variant. Must read as the SAME physical location as its base asset "
        "below -- same architecture, camera angle, and landmarks; only lighting, "
        "population, damage, and atmosphere should differ. Keep the lower third clear, "
        "same as a normal location."
    ),
    "event": (
        "Full-screen story illustration ('ilustrasi peristiwa besar'). May include named "
        "characters and dramatic staging -- do not flatten it into an empty environment. "
        "The lower-third-clear rule does not apply here."
    ),
}


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        print(
            f"Tidak ditemukan: {MANIFEST_PATH.relative_to(ROOT)}. "
            "Jalankan dulu: python tools/generate_latar_prompts.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def output_path_for(asset_path: str) -> str:
    return f"{ASSET_ROOT}/{asset_path}"


def variant_base_asset(asset: dict, by_asset_path: dict[str, dict]) -> Optional[dict]:
    variant_of = asset.get("metadata", {}).get("variant_of")
    if not variant_of:
        return None
    return by_asset_path.get(variant_of)


def build_batch_entry(asset: dict, by_asset_path: dict[str, dict]) -> dict:
    category = asset["category"]
    base = variant_base_asset(asset, by_asset_path)
    notes = [NOTES_BY_CATEGORY.get(category, "")]
    notes.append(
        f"Final asset: {TARGET_SIZE} px ({TARGET_RATIO}), WebP, aim under "
        f"{asset['target_max_size_kb']}KB."
    )
    if base:
        notes.append(f"Same location as: {base['asset_path']} ({base['location']}).")
    return {
        "id": asset["id"],
        "output_path": output_path_for(asset["asset_path"]),
        "asset_path": asset["asset_path"],
        "category": category,
        "priority": asset["priority"],
        "region": asset.get("metadata", {}).get("region"),
        "location": asset["location"],
        "variant_of": base["asset_path"] if base else None,
        "variant_of_location": base["location"] if base else None,
        "image_prompt": asset["prompt"],
        "negative_prompt": asset["negative_prompt"],
        "aspect_ratio": TARGET_RATIO,
        "resolution_target": TARGET_SIZE,
        "chatgpt_generation_hint": (
            f"ChatGPT Image Generation has no native {TARGET_RATIO} option -- pick its "
            f"landscape size ({CHATGPT_LANDSCAPE_SIZE}) and resize/crop to {TARGET_SIZE} "
            "afterward (see tools/prepare_generated_images.py)."
        ),
        "notes": " ".join(n for n in notes if n),
    }


def region_sort_key(region: Optional[str]) -> str:
    return region if region else "￿"  # aset tanpa region terdeteksi ditaruh paling akhir


def build_batches(assets: list[dict], by_asset_path: dict[str, dict]) -> list[dict]:
    entries = [build_batch_entry(a, by_asset_path) for a in assets]
    entries.sort(
        key=lambda e: (
            e["priority"],
            CATEGORY_ORDER.get(e["category"], 99),
            region_sort_key(e["region"]),
            e["id"],
        )
    )

    groups: list[dict] = []
    for entry in entries:
        key = (entry["priority"], entry["category"], entry["region"])
        if not groups or (groups[-1]["priority"], groups[-1]["category"], groups[-1]["region"]) != key:
            groups.append({
                "priority": entry["priority"],
                "category": entry["category"],
                "region": entry["region"],
                "assets": [],
            })
        groups[-1]["assets"].append(entry)
    return groups


# ---------------------------------------------------------------------------
# Markdown rendering.
# ---------------------------------------------------------------------------

def render_asset_md(entry: dict) -> str:
    lines = [
        f"### `{entry['id']}` -- {entry['location']}",
        "",
        f"- **Asset ID:** `{entry['id']}`",
        f"- **Output path:** `{entry['output_path']}`",
        f"- **Category:** {entry['category']}",
        f"- **Priority:** {entry['priority']}",
        f"- **Region:** {entry['region'] or '(none detected)'}",
    ]
    if entry["variant_of"]:
        lines.append(
            f"- **Variant base location:** `{entry['variant_of']}` -- {entry['variant_of_location']}"
        )
    lines.extend([
        f"- **Recommended aspect ratio:** {entry['aspect_ratio']}",
        f"- **Recommended resolution:** {entry['resolution_target']} "
        f"(ChatGPT generation hint: use its landscape size {CHATGPT_LANDSCAPE_SIZE}, "
        "then resize/crop -- see `tools/prepare_generated_images.py`)",
        f"- **Notes:** {entry['notes']}",
        "",
        "**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)",
        "",
        "```",
        entry["image_prompt"],
        "```",
        "",
        "**NEGATIVE / AVOID** (mention these as things to avoid in the same request, "
        "or in a follow-up refinement)",
        "",
        "```",
        entry["negative_prompt"],
        "```",
        "",
    ])
    return "\n".join(lines)


def render_markdown(groups: list[dict], filter_desc: str, total: int) -> str:
    out = [
        "# Image Generation Batch -- Pelita Terakhir",
        "",
        f"Filter: {filter_desc}",
        f"Total assets: {total}",
        "",
        "Generated from `prompts/latar_prompts.json` by "
        "`tools/export_image_generation_batch.py`. This file is deterministic: re-running "
        "the same command regenerates the same content.",
        "",
        "Workflow: see `prompts/README.md`. Short version -- copy **IMAGE PROMPT** into "
        "ChatGPT Image Generation, save the result under **Output path**, then run "
        "`tools/prepare_generated_images.py` to resize/convert/compress it to spec.",
        "",
        "---",
        "",
    ]
    current_priority = None
    current_category = None
    for group in groups:
        if group["priority"] != current_priority:
            current_priority = group["priority"]
            current_category = None
            out.append(f"## Priority {current_priority}")
            out.append("")
        if group["category"] != current_category:
            current_category = group["category"]
            out.append(f"### Category: {CATEGORY_LABEL.get(current_category, current_category)}")
            out.append("")
        region_label = group["region"] or "(region not detected)"
        out.append(f"#### Region: {region_label}")
        out.append("")
        for entry in group["assets"]:
            out.append(render_asset_md(entry))
        out.append("---")
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Validation.
# ---------------------------------------------------------------------------

def validate_batch(entries: list[dict], all_assets_by_id: dict[str, dict],
                    all_asset_paths: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        errors.append(f"id duplikat di batch: {dupes}")

    paths = [e["output_path"] for e in entries]
    if len(paths) != len(set(paths)):
        dupes = sorted({p for p in paths if paths.count(p) > 1})
        errors.append(f"output_path duplikat di batch: {dupes}")

    for e in entries:
        if e["id"] not in all_assets_by_id:
            errors.append(f"{e['id']}: tidak ditemukan di latar_prompts.json")
        if not e["image_prompt"]:
            errors.append(f"{e['id']}: image_prompt kosong")
        if not e["output_path"]:
            errors.append(f"{e['id']}: output_path kosong")
        if e["category"] not in CATEGORY_ORDER:
            errors.append(f"{e['id']}: category tidak valid ({e['category']})")
        if e["priority"] not in (1, 2, 3):
            errors.append(f"{e['id']}: priority tidak valid ({e['priority']})")
        if e["resolution_target"] != TARGET_SIZE:
            errors.append(f"{e['id']}: resolution tidak valid ({e['resolution_target']})")
        if e["category"] == "variant":
            if not e["variant_of"]:
                warnings.append(f"{e['id']}: varian tanpa variant_of")
            elif e["variant_of"] not in all_asset_paths:
                errors.append(f"{e['id']}: variant_of '{e['variant_of']}' tidak ada di latar_prompts.json")

    return errors, warnings


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def batch_filename(priority: Optional[int], category: Optional[str], asset_id: Optional[str]) -> str:
    if asset_id:
        return f"batch_id-{asset_id}"
    parts = []
    if priority is not None:
        parts.append(f"priority{priority}")
    if category and category != "all":
        parts.append(f"category-{category}")
    return "batch_" + "_".join(parts) if parts else "batch_all"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Rakit batch prompt siap-tempel untuk ChatGPT Image Generation dari "
            "prompts/latar_prompts.json. Tidak menghasilkan gambar, tidak memanggil API "
            "eksternal apa pun."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--priority", type=int, choices=(1, 2, 3), help="saring berdasarkan prioritas")
    ap.add_argument(
        "--category",
        choices=("lokasi", "location", "variant", "event", "all"),
        default="all",
        help="saring berdasarkan kategori ('lokasi' adalah alias untuk 'location')",
    )
    ap.add_argument("--id", dest="asset_id", help="hanya proses satu aset (id, mis. pelita_rendah_warung)")
    args = ap.parse_args()

    manifest = load_manifest()
    all_assets = manifest["assets"]
    all_assets_by_id = {a["id"]: a for a in all_assets}
    by_asset_path = {a["asset_path"]: a for a in all_assets}
    all_asset_paths = set(by_asset_path)

    category = CATEGORY_ALIASES[args.category]

    assets = all_assets
    if args.priority is not None:
        assets = [a for a in assets if a["priority"] == args.priority]
    if category != "all":
        assets = [a for a in assets if a["category"] == category]
    if args.asset_id:
        target = args.asset_id.strip()
        if target.endswith(".webp"):
            target = target[: -len(".webp")]
        target_flat = target.replace("/", "_")
        assets = [
            a for a in assets
            if a["id"] == target or a["id"] == target_flat or a["asset_path"][: -len(".webp")] == target
        ]
        if not assets:
            print(f"Tidak ada entri untuk --id {args.asset_id!r} di prompts/latar_prompts.json.", file=sys.stderr)
            return 1

    if not assets:
        print("Tidak ada aset yang cocok dengan filter yang diberikan.", file=sys.stderr)
        return 1

    groups = build_batches(assets, by_asset_path)
    entries = [entry for group in groups for entry in group["assets"]]

    errors, warnings = validate_batch(entries, all_assets_by_id, all_asset_paths)

    filter_bits = []
    if args.priority is not None:
        filter_bits.append(f"priority={args.priority}")
    filter_bits.append(f"category={category if category != 'all' else 'all'}")
    if args.asset_id:
        filter_bits.append(f"id={args.asset_id}")
    filter_desc = ", ".join(filter_bits)

    name = batch_filename(args.priority, category, args.asset_id)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    md_path = BATCH_DIR / f"{name}.md"
    json_path = BATCH_DIR / f"{name}.json"

    md_path.write_text(render_markdown(groups, filter_desc, len(entries)), encoding="utf-8")

    json_batch = {
        "version": 1,
        "generated_from": "prompts/latar_prompts.json",
        "filter": {
            "priority": args.priority,
            "category": category if category != "all" else None,
            "id": args.asset_id,
        },
        "total_assets": len(entries),
        "chatgpt_image_generation": {
            "target_resolution": TARGET_SIZE,
            "target_aspect_ratio": TARGET_RATIO,
            "closest_native_option": CHATGPT_LANDSCAPE_SIZE,
            "post_process_with": "tools/prepare_generated_images.py",
        },
        "groups": groups,
    }
    json_path.write_text(json.dumps(json_batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Batch: {name}")
    print(f"Filter: {filter_desc}")
    print(f"Total assets: {len(entries)}")
    by_cat: dict[str, int] = {}
    for e in entries:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + 1
    for cat in ("location", "variant", "event"):
        if cat in by_cat:
            print(f"  {CATEGORY_LABEL[cat]}: {by_cat[cat]}")
    print()
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  - {w}")
    print()
    print(f"Markdown: {md_path.relative_to(ROOT)}")
    print(f"JSON:     {json_path.relative_to(ROOT)}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
