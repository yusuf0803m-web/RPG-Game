#!/usr/bin/env python3
"""Generator prompt gambar latar otomatis untuk Pelita Terakhir (GAME_DESIGN §7.2).

Sumber kebenaran tunggal: ``pelita/data/world/latar.json``. Skrip ini TIDAK berisi satu
pun prompt yang ditulis tangan — ia membaca tiap entri (lokasi, varian kondisi dunia,
ilustrasi peristiwa besar) lalu merakit prompt image-generation yang konsisten memakai
arah seni "dark fantasy Nusantara" secara murni berbasis aturan/template (tanpa API AI
eksternal, tanpa koneksi internet), sehingga deterministik dan otomatis mendukung entri
baru begitu ditambahkan ke ``latar.json`` tanpa perlu menyentuh skrip ini.

    python tools/generate_latar_prompts.py                              # semua entri
    python tools/generate_latar_prompts.py --priority 1                 # prioritas 1 saja
    python tools/generate_latar_prompts.py --category location          # lokasi saja
    python tools/generate_latar_prompts.py --category variant
    python tools/generate_latar_prompts.py --category event
    python tools/generate_latar_prompts.py --id pelita_rendah/warung.webp
    python tools/generate_latar_prompts.py --force

Keluaran:
  - ``prompts/latar_prompts.json``   manifes machine-readable, ditulis ulang penuh tiap run
  - ``prompts/backgrounds/*.md``     satu berkas per entri kategori "lokasi"
  - ``prompts/variants/*.md``        satu berkas per entri kategori "varian"
  - ``prompts/events/*.md``          satu berkas per entri kategori "peristiwa"

Permainan tidak butuh satu pun gambar ini untuk berjalan (panorama SVG prosedural dipakai
selama berkas .webp belum ada — lihat GAME_DESIGN §7.2), jadi skrip ini murni alat
produksi konten dan tidak menyentuh kode gameplay.

``--force`` juga menghapus berkas .md basi (id yang sudah tidak ada lagi di latar.json)
di tiga folder di atas; tanpa ``--force`` berkas basi dibiarkan apa adanya supaya run yang
difilter (mis. ``--priority 1``) tidak pernah menghapus apa pun secara tak sengaja.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
LATAR_JSON = ROOT / "pelita" / "data" / "world" / "latar.json"
OUT_DIR = ROOT / "prompts"
MANIFEST_PATH = OUT_DIR / "latar_prompts.json"
MD_DIRS = {
    "location": OUT_DIR / "backgrounds",
    "variant": OUT_DIR / "variants",
    "event": OUT_DIR / "events",
}

WIDTH, HEIGHT, IMG_FORMAT, MAX_KB = 1600, 900, "webp", 250
STYLE_VERSION = "dark-fantasy-nusantara-v1"

KATEGORI_MAP = {"lokasi": "location", "varian": "variant", "peristiwa": "event"}
JUDUL_KATEGORI = {"location": "Latar lokasi", "variant": "Varian kondisi dunia", "event": "Ilustrasi peristiwa besar"}

MASTER_STYLE = (
    "cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted "
    "fantasy background illustration, atmospheric depth, restrained natural color "
    "palette, immersive original-world worldbuilding, painterly but production-ready"
)

MATERIAL_PALETTE = (
    "material and architectural language drawn from Southeast Asian / Nusantara-inspired "
    "construction where it is consistent with the scene described above -- bamboo, teak "
    "wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, "
    "hand-built and weathered surfaces; an original fantasy world, never a real-world "
    "modern Indonesian village and never generic European medieval fantasy"
)


# ---------------------------------------------------------------------------
# Region profiles: per-region defaults (art direction only -- always overridable
# by what the source description actually says).
# ---------------------------------------------------------------------------

@dataclass
class RegionProfile:
    display: str
    environment_type: str
    flavor: str
    lighting_default: Optional[str] = None


REGION_PROFILES: dict[str, RegionProfile] = {
    "benteng_ordo": RegionProfile(
        "Benteng Ordo Pelita", "fortress",
        "a fortress carved directly into a towering salt cliff face, narrow glowing "
        "window-slits cut into weathered rock, terraced stone-and-bronze interior halls",
        "lantern",
    ),
    "celah_angin": RegionProfile(
        "Celah Angin", "mountain_cliff",
        "a narrow wind-scoured mountain pass between two immense rock walls, sand-laden "
        "gusts, exposed vertical stone terrain",
        None,
    ),
    "danau_cermin": RegionProfile(
        "Danau Cermin", "lake",
        "a still, mirror-flat lake ringed by unmoving mist, with a floating village of "
        "bamboo-raft houses linked by swaying rope walkways",
        "lantern",
    ),
    "danau_garam": RegionProfile(
        "Danau Garam", "salt_flat",
        "a vast dried salt lake bed, knee-high crystalline salt growth catching the "
        "light like glass grass",
        None,
    ),
    "dataran_abu": RegionProfile(
        "Dataran Abu", "wasteland",
        "an endless grey ash plain with the buried outline of an older, ruined world "
        "beneath the drifting ash",
        None,
    ),
    "hutan_kelabu": RegionProfile(
        "Hutan Kelabu", "forest",
        "a grey, mist-drowned forest where fog pools knee-to-chest deep between the "
        "trunks",
        None,
    ),
    "hutan_nyanyi": RegionProfile(
        "Hutan Nyanyi", "forest",
        "a singing forest of towering ancient trees whose hollow trunks echo and repeat "
        "distant song, a moss-grown stone road from a vanished kingdom beneath the canopy",
        None,
    ),
    "lorong_bawah": RegionProfile(
        "Lorong Bawah", "underground",
        "flooded stone tunnels beneath the city, dead machinery, iron ladders and "
        "gear-lined chambers",
        "lantern",
    ),
    "mercusuar": RegionProfile(
        "Mercusuar Langit", "tower",
        "the interior of an immense bone-white tower without visible seams, ancient "
        "bas-relief carvings lining its rounded walls",
        "flame_beacon",
    ),
    "pelita_rendah": RegionProfile(
        "Pelita Rendah", "village",
        "a modest hillside village of stilted wooden houses along a packed-earth road, "
        "bronze lanterns at gateposts and porches",
        "lantern",
    ),
    "rawa_suar": RegionProfile(
        "Rawa Suar", "swamp",
        "a warm, sulfurous marsh with mangrove trees leaning uniformly away from an old, "
        "half-sunk beacon tower, raised bamboo walkways over shallow water",
        None,
    ),
    "tambang": RegionProfile(
        "Tambang Kaca Ingatan", "mine",
        "a mountainside memory-glass mine, timber-shored tunnels, rusted mine-cart "
        "rails, glowing crystal veins in the rock",
        "lantern",
    ),
    "tengara": RegionProfile(
        "Ibukota Tengara", "city",
        "a walled capital city of andesite stone, tiered markets on the inner slope, "
        "bronze lantern-posts along stone docks",
        "lantern",
    ),
    "wirasaba": RegionProfile(
        "Kota Kaca Wirasaba", "city",
        "a city built almost entirely from memory-glass architecture -- walls and "
        "towers that faintly replay fragments of the lives once lived inside them",
        None,
    ),
    "laut_lupa": RegionProfile(
        "Laut Lupa", "ocean",
        "a fog-bound sea of drifting memory, where the shapes of drowned rooftops and "
        "roads surface briefly beneath the hull before another layer covers them again",
        "lantern",
    ),
    "pusar_kabut": RegionProfile(
        "Pusar Kabut & Kota Adiluhung", "ancient_ruins",
        "a colossal, slow-spinning vortex of mist with an ancient sunken city clinging "
        "in spiralling tiers to its inner wall",
        None,
    ),
}

DEFAULT_EVENT_PROFILE = RegionProfile(
    "Pelita Terakhir", "narrative_event",
    "a pivotal cutscene moment in the world of Pelita Terakhir, staged for maximum "
    "emotional and dramatic clarity",
    None,
)

# Regex (searched against nama + deskripsi) -> region key, used only for "peristiwa"
# entries that have no region prefix of their own. First match wins; kept intentionally
# conservative so an ambiguous event stays with the generic event profile instead of a
# guessed region (per the "use null rather than guessing" rule).
EVENT_REGION_HINTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"mercusuar", re.I), "mercusuar"),
    (re.compile(r"kurungan kaca|gudang panen", re.I), "wirasaba"),
    (re.compile(r"tujuh pintu kaca|tujuh menara|\bsumur\b|pusar kabut|kota adiluhung", re.I), "pusar_kabut"),
    (re.compile(r"\bpulau\b", re.I), "laut_lupa"),
    (re.compile(r"rongga.{0,15}suar|perempuan tua berjubah putih", re.I), "benteng_ordo"),
    (re.compile(r"mimbar kayu|desa yang masih menyanyi", re.I), "hutan_nyanyi"),
]


# ---------------------------------------------------------------------------
# Environment-type overrides (per-room, checked before the region default).
# ---------------------------------------------------------------------------

ENV_TYPE_OVERRIDES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bgua\b", re.I), "cave"),
    (re.compile(r"sarang", re.I), "lair"),
    (re.compile(r"reruntuhan", re.I), "ruins"),
    (re.compile(r"menara terapung", re.I), "floating_tower"),
    (re.compile(r"\bpulau\b", re.I), "island"),
    (re.compile(r"\bkapal\b", re.I), "ship"),
]


def classify_environment_type(deskripsi: str, region: RegionProfile) -> str:
    for pattern, env_type in ENV_TYPE_OVERRIDES:
        if pattern.search(deskripsi):
            return env_type
    return region.environment_type


# ---------------------------------------------------------------------------
# Lighting: this is the rule the whole brief hinges on -- never force a lantern
# where the source explicitly has none, always preserve an explicit Suar/Nyala,
# and only fall back to the region's default when the text is silent.
# ---------------------------------------------------------------------------

LIGHT_NONE_RE = re.compile(r"tanpa\s+(?:satu\s+pun\s+)?lentera|tidak\s+ada\s+(?:satu\s+pun\s+)?lentera", re.I)
LIGHT_EXTINGUISHED_RE = re.compile(r"\bpadam\b", re.I)
LIGHT_LANTERN_RE = re.compile(r"lentera", re.I)
LIGHT_BEACON_RE = re.compile(r"\bsuar\b|\bnyala\b", re.I)
LIGHT_ACTIVE_RE = re.compile(r"menyala|berpendar|bercahaya", re.I)
LIGHT_DARK_RE = re.compile(r"kosong|gelap|padam|retak", re.I)
LIGHT_GLOW_MATERIAL_RE = re.compile(r"kaca|kristal", re.I)


def classify_lighting(deskripsi: str, text: str, region: RegionProfile) -> tuple[Optional[str], str]:
    """``deskripsi`` (naratif asli, ketat) menentukan absennya lentera; ``text`` (nama +
    deskripsi) dipakai untuk sinyal yang lebih longgar (Suar/Nyala/kaca/kristal)."""
    if LIGHT_NONE_RE.search(deskripsi):
        return "none", (
            "No lantern light anywhere in this scene -- the source description explicitly "
            "says there are no lanterns here; light it with plausible ambient sources only "
            "(moonlight, diffused mist light, faint bioluminescence), and never add a lantern."
        )
    if LIGHT_LANTERN_RE.search(text):
        if LIGHT_EXTINGUISHED_RE.search(text):
            return "extinguished", (
                "The lanterns described here are extinguished or unlit -- render them dark "
                "and cold with only dim ambient light; do not show them burning."
            )
        return "lantern", (
            "Primary light source: warm amber oil lanterns, casting warm light against the "
            "cooler environmental tones."
        )
    if LIGHT_BEACON_RE.search(text):
        if LIGHT_ACTIVE_RE.search(text) and not LIGHT_DARK_RE.search(text):
            return "flame_beacon", (
                "Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly "
                "otherworldly light rather than an ordinary fire."
            )
        if LIGHT_DARK_RE.search(text):
            return "none", (
                "The Suar/Nyala here is dark, damaged, or absent per the source description -- "
                "do not render it as actively lit; use dim, cold ambient light instead."
            )
        return "flame_beacon", (
            "Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly "
            "otherworldly light rather than an ordinary fire."
        )
    if LIGHT_ACTIVE_RE.search(text) and LIGHT_GLOW_MATERIAL_RE.search(text):
        return "ambient_glow", (
            "Primary light source: a faint internal glow from glass or crystal surfaces "
            "rather than any flame."
        )
    if region.lighting_default == "lantern":
        return "lantern", (
            "Primary light source: warm amber oil lanterns (region default; not contradicted "
            "by the source description), casting warm light against cooler environmental "
            "tones."
        )
    if region.lighting_default == "flame_beacon":
        return "flame_beacon", (
            "Primary light source: the Suar/Nyala sacred flame (region default; not "
            "contradicted by the source description)."
        )
    return None, (
        "No light source is specified in the source description -- use plausible ambient "
        "environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and "
        "do not force a lantern into the scene."
    )


# ---------------------------------------------------------------------------
# Time-of-day: only ever set from an explicit word in the text, never guessed.
# ---------------------------------------------------------------------------

TIME_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bmalam\b", re.I), "night"),
    (re.compile(r"\bsenja\b|\bsore\b", re.I), "dusk"),
    (re.compile(r"\bpagi\b", re.I), "morning"),
    (re.compile(r"\bsiang\b", re.I), "day"),
]


def classify_time(deskripsi: str) -> Optional[str]:
    for pattern, value in TIME_RULES:
        if pattern.search(deskripsi):
            return value
    return None


# ---------------------------------------------------------------------------
# Camera: "eye_level" is a house-style default for reusable backgrounds (a
# production choice, not a guess about content); refined only on explicit cues.
# ---------------------------------------------------------------------------

CAMERA_CLOSE_RE = re.compile(r"dari dekat", re.I)
CAMERA_DISTANT_RE = re.compile(r"dari kejauhan|sejauh mata memandang", re.I)


def classify_camera(deskripsi: str, category: str) -> str:
    if CAMERA_CLOSE_RE.search(deskripsi):
        return "close"
    if CAMERA_DISTANT_RE.search(deskripsi):
        return "wide_distant"
    return "eye_level" if category != "event" else "cinematic"


# ---------------------------------------------------------------------------
# Motif phrase library: deterministic Indonesian-keyword -> English-phrase rules
# used to expand the SCENE/ENVIRONMENT/STORYTELLING sections without ever
# contradicting the source. Each rule fires independently; duplicates within a
# bucket are dropped by text.
# ---------------------------------------------------------------------------

MotifRule = tuple[re.Pattern, str, str]  # pattern, bucket ("objects"|"atmosphere"|"story"), phrase

MOTIF_RULES: list[MotifRule] = [
    (re.compile(r"kabut", re.I), "atmosphere", "drifting mist"),
    (re.compile(r"\bdanau\b", re.I), "objects", "a still lake"),
    (re.compile(r"\brawa\b", re.I), "objects", "shallow marsh water"),
    (re.compile(r"reruntuhan", re.I), "objects", "weathered, abandoned ruins"),
    (re.compile(r"\babu\b", re.I), "atmosphere", "fine drifting ash"),
    (re.compile(r"\bmenara\b", re.I), "objects", "a tall tower"),
    (re.compile(r"\bpuncak\b", re.I), "objects", "a high summit"),
    (re.compile(r"dermaga", re.I), "objects", "a wooden dock"),
    (re.compile(r"\bpasar\b", re.I), "objects", "market stalls"),
    (re.compile(r"\bdesa\b", re.I), "objects", "a village"),
    (re.compile(r"\bhutan\b", re.I), "objects", "dense forest"),
    (re.compile(r"pohon", re.I), "objects", "towering trees"),
    (re.compile(r"\bakar\b|akar-akar", re.I), "objects", "exposed, reaching roots"),
    (re.compile(r"\bbatu\b", re.I), "objects", "weathered stone"),
    (re.compile(r"perunggu", re.I), "objects", "bronze fittings"),
    (re.compile(r"bambu", re.I), "objects", "bamboo construction"),
    (re.compile(r"\brakit\b", re.I), "objects", "a bamboo raft"),
    (re.compile(r"kristal", re.I), "objects", "glowing crystal formations"),
    (re.compile(r"\bkaca\b", re.I), "objects", "memory-glass surfaces"),
    (re.compile(r"konstruk", re.I), "story", "a silent construct standing guard"),
    (re.compile(r"zirah", re.I), "objects", "weathered armor"),
    (re.compile(r"\bhampa\b", re.I), "story", "a Hampa (a silent, hollow armored construct) standing motionless"),
    (re.compile(r"jembatan tali", re.I), "objects", "a swaying rope bridge"),
    (re.compile(r"jembatan(?! tali)", re.I), "objects", "a wooden footbridge"),
    (re.compile(r"\btangga\b", re.I), "objects", "worn stone or wooden steps"),
    (re.compile(r"gerbang", re.I), "objects", "a weathered gate"),
    (re.compile(r"\btembok\b", re.I), "objects", "a fortified wall"),
    (re.compile(r"\bijuk\b", re.I), "objects", "a thatched palm-fiber roof"),
    (re.compile(r"gamelan", re.I), "story", "an implied, unheard gamelan stillness rather than any visible musicians"),
    (re.compile(r"ukiran", re.I), "objects", "detailed relief carvings"),
    (re.compile(r"gulungan", re.I), "objects", "archive scrolls"),
    (re.compile(r"tungku", re.I), "objects", "a furnace or kiln"),
    (re.compile(r"\blift\b", re.I), "objects", "a timber-and-chain lift shaft"),
    (re.compile(r"rel lori", re.I), "objects", "rusted mine-cart rails"),
    (re.compile(r"garam", re.I), "objects", "crystallized salt"),
    (re.compile(r"\bkapal\b", re.I), "objects", "a wooden ship"),
    (re.compile(r"pengantin|pernikahan", re.I), "story", "a frozen wedding tableau, untouched and silent"),
    (re.compile(r"perang|tombak|helm|\bparit\b", re.I), "story", "the silent remains of an ancient war"),
    (re.compile(r"benang", re.I), "objects", "glistening woven threads"),
    (re.compile(r"\bjala\b", re.I), "objects", "hanging fishing nets"),
    (re.compile(r"pilar cahaya", re.I), "atmosphere", "a rising pillar of light"),
    (re.compile(r"pengawal mahkota", re.I), "story", "armored crown guards standing watch"),
    (re.compile(r"kain.{0,12}anak", re.I), "story", "small, child-sized clothing left hanging on a line -- an implied absence, not a rendered child"),
]

ANOMALY_RULES: list[re.Pattern] = [
    re.compile(r"itu masalahnya", re.I),
    re.compile(r"bukan ikan", re.I),
    re.compile(r"tidak ada satu pun yang bergerak", re.I),
    re.compile(r"tidak seharusnya|seharusnya tidak", re.I),
]
ANOMALY_PHRASE = (
    "a quiet, deliberately unexplained wrongness beneath an outwardly ordinary scene -- "
    "normal activity continuing where it should not, with no obvious visual explanation; "
    "keep it visually clear and intentional, not chaotic"
)

PROPER_NOUN_GLOSSES: list[tuple[str, str]] = [
    ("Mercusuar Langit", "Mercusuar Langit -- the Sky Lighthouse"),
    ("Kaca Ingatan", "Kaca Ingatan -- memory-infused glass, an original fictional material"),
    ("Sumur Ingatan", "Sumur Ingatan -- the Memory Well"),
    ("Kota Adiluhung", "Kota Adiluhung -- an ancient sunken city"),
    ("Laut Lupa", "Laut Lupa -- the Sea of Forgetting"),
    ("Nyala", "the Nyala -- the world's central sacred flame"),
    ("Suar", "a Suar -- a beacon tower housing a fragment of the Nyala"),
]

PERSON_KEYWORDS_RE = re.compile(
    r"perempuan|lelaki|\bpria\b|wanita|seseorang|\bnyai\b|pengawal mahkota|\banak\b(?!\s+tangga)",
    re.I,
)


def detect_motifs(deskripsi: str) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {"objects": [], "atmosphere": [], "story": []}
    for pattern, bucket, phrase in MOTIF_RULES:
        if pattern.search(deskripsi) and phrase not in buckets[bucket]:
            buckets[bucket].append(phrase)
    if any(p.search(deskripsi) for p in ANOMALY_RULES):
        buckets["story"].append(ANOMALY_PHRASE)
    return buckets


def detect_glosses(deskripsi: str) -> list[str]:
    out = []
    for term, gloss in PROPER_NOUN_GLOSSES:
        if term in deskripsi and gloss not in out:
            out.append(gloss)
    return out


# ---------------------------------------------------------------------------
# variant_of: strip trailing "_segment"s of the room slug until it matches a
# sibling "lokasi" entry in the same region -- catches every current variant
# (warung_sepi -> warung, jalan_desa_pulih -> jalan_desa, ...) and keeps
# working automatically for future ones with the same "<base>_<state>" shape.
# ---------------------------------------------------------------------------

def guess_variant_of(path: str, location_paths: set[str]) -> Optional[str]:
    if "/" not in path:
        return None
    region, slug = path.split("/", 1)
    parts = slug.split("_")
    for cut in range(len(parts) - 1, 0, -1):
        candidate = f"{region}/{'_'.join(parts[:cut])}"
        if candidate in location_paths:
            return candidate
    return None


def event_region(nama: str, deskripsi: str) -> Optional[str]:
    text = f"{nama} {deskripsi}"
    for pattern, region in EVENT_REGION_HINTS:
        if pattern.search(text):
            return region
    return None


def region_for(path: str, kategori: str, nama: str, deskripsi: str) -> tuple[Optional[str], RegionProfile]:
    region_key = path.split("/", 1)[0] if "/" in path else None
    if kategori == "peristiwa" or region_key not in REGION_PROFILES:
        hinted = event_region(nama, deskripsi)
        if hinted:
            return hinted, REGION_PROFILES[hinted]
        return None, DEFAULT_EVENT_PROFILE
    return region_key, REGION_PROFILES[region_key]


# ---------------------------------------------------------------------------
# Prompt assembly.
# ---------------------------------------------------------------------------

FORMAT_LOCATION = (
    "Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, "
    "not a character portrait, not splash art."
)
FORMAT_EVENT = (
    "Full-screen 1600x900 (16:9) narrative story illustration ('ilustrasi peristiwa besar') "
    "for a JRPG cutscene moment. Not a reusable dialogue background."
)

COMPOSITION_LOCATION = (
    "Wide horizontal environmental composition. Keep the lower third of the frame clear of "
    "important objects, characters, and dense detail -- the game overlays a dialogue box and "
    "a dark gradient there automatically. Do not paint a heavy black gradient at the bottom "
    "yourself; the background itself should read as naturally lit and evenly exposed."
)
COMPOSITION_EVENT = (
    "Cinematic full-frame composition. Characters and dramatic staging may occupy any part "
    "of the frame, including the center and lower frame, since this illustration displays "
    "full-screen without a dialogue box overlay."
)

CAMERA_TEXT = {
    "eye_level": "eye-level wide establishing shot",
    "close": "a closer, more intimate framing, as described in the source",
    "wide_distant": "a wide, distant vantage point, as described in the source",
    "cinematic": "dynamic cinematic staging appropriate to the story beat",
}

CONSTRAINTS_LOCATION = (
    "Never contradict the source description. Preserve the presence or explicit absence of "
    "lanterns exactly as written. Do not add prominent characters, close-up faces, or "
    "character portraits -- this is a reusable environment, not a character illustration. "
    "Keep any surreal or supernatural element visually clear and intentional, not chaotic."
)
CONSTRAINTS_EVENT = (
    "Never contradict the source description. This illustration may include named "
    "characters, dramatic poses, and supernatural effects -- do not flatten it into a "
    "generic empty environment. Keep any surreal element visually clear and intentional, "
    "not chaotic."
)
CONSTRAINTS_VARIANT_EXTRA = (
    "This is the SAME physical location as {base}, shown under a different world state: "
    "preserve its architecture, camera relationship, and major structural landmarks so the "
    "player recognizes it; change only lighting, population, damage, activity, and "
    "atmosphere."
)


def build_negative_prompt(category: str, needs_character: bool) -> str:
    base = [
        "user interface elements", "HUD", "dialogue box", "readable text", "logos",
        "watermark", "modern technology", "electricity", "power lines", "cars",
        "motorcycles", "sci-fi elements", "steampunk machinery",
        "generic European medieval architecture", "excessive ornate high-fantasy "
        "architecture", "oversaturated colors", "photorealistic photography",
        "heavy black gradient overlay at the bottom",
    ]
    if category == "event":
        return ", ".join(base)
    people = ["character portraits", "close-up faces", "a large dominant protagonist", "crowds of NPCs"]
    if not needs_character:
        people = ["characters", "NPCs", "protagonist"] + people
    return ", ".join(people + base)


def build_prompt(path: str, entry: dict, category: str, region_key: Optional[str],
                  region: RegionProfile, variant_of: Optional[str]) -> tuple[str, str, dict]:
    nama = entry["nama"]
    deskripsi = entry["deskripsi"]
    # Klasifikasi memakai nama + deskripsi gabungan -- beberapa sinyal (mis. "Menara
    # Terapung") hanya muncul di nama, tidak diulang di deskripsi. Kemutlakan cahaya
    # (LIGHT_NONE_RE) tetap dicek khusus pada deskripsi di classify_lighting supaya
    # aturan "sumber wins" tetap ketat pada kalimat naratif, bukan judul ruang.
    text = f"{nama} {deskripsi}"
    env_type = classify_environment_type(text, region)
    lighting_tag, lighting_phrase = classify_lighting(deskripsi, text, region)
    time_tag = classify_time(text)
    camera_tag = classify_camera(text, category)
    motifs = detect_motifs(text)
    glosses = detect_glosses(text)
    needs_character = bool(PERSON_KEYWORDS_RE.search(text))

    fmt = FORMAT_EVENT if category == "event" else FORMAT_LOCATION
    location_line = f"{nama}."
    scene_bits = [region.flavor]
    if motifs["objects"]:
        scene_bits.append("featuring " + ", ".join(motifs["objects"][:6]))
    scene = "; ".join(scene_bits) + "."

    environment = (
        f"Environment type: {env_type.replace('_', ' ')}. " + MATERIAL_PALETTE + "."
    )

    atmosphere_bits = motifs["atmosphere"] or ["clear, restrained dark-fantasy atmosphere"]
    atmosphere = "Atmosphere: " + ", ".join(atmosphere_bits) + "."
    if time_tag:
        atmosphere += f" Time of day: {time_tag}."

    visual_style = MASTER_STYLE + "."

    composition = COMPOSITION_EVENT if category == "event" else COMPOSITION_LOCATION

    lighting = lighting_phrase

    story_bits = list(motifs["story"])
    story_bits.extend(g for g in glosses if g not in story_bits)
    if category == "variant" and variant_of:
        story_bits.append(CONSTRAINTS_VARIANT_EXTRA.format(base=f"{variant_of}.webp"))
    storytelling = ("Storytelling details: " + "; ".join(story_bits) + ".") if story_bits else ""

    constraints = CONSTRAINTS_EVENT if category == "event" else CONSTRAINTS_LOCATION

    target = f"Target asset: {path}.webp, {WIDTH}x{HEIGHT} px, {IMG_FORMAT.upper()}, aim under {MAX_KB}KB."

    sections = [
        f"[FORMAT] {fmt}",
        f"[LOCATION] {location_line}",
        f"[SCENE] {scene}",
        f"[ENVIRONMENT] {environment}",
        f"[ATMOSPHERE] {atmosphere}",
        f"[VISUAL STYLE] {visual_style}",
        f"[CAMERA] {CAMERA_TEXT[camera_tag]}.",
        f"[COMPOSITION] {composition}",
        f"[LIGHTING] {lighting}",
    ]
    if storytelling:
        sections.append(f"[STORYTELLING DETAILS] {storytelling}")
    sections.append(f"[IMPORTANT CONSTRAINTS] {constraints}")
    sections.append(f"[TARGET ASSET] {target}")

    prompt = " ".join(sections)
    negative_prompt = build_negative_prompt(category, needs_character)

    metadata = {
        "region": region_key,
        "environment_type": env_type,
        "time": time_tag,
        "lighting": lighting_tag,
        "camera": camera_tag,
        "variant_of": f"{variant_of}.webp" if variant_of else None,
    }
    return prompt, negative_prompt, metadata


# ---------------------------------------------------------------------------
# Asset build / registry.
# ---------------------------------------------------------------------------

def load_registry() -> dict[str, dict]:
    if not LATAR_JSON.exists():
        print(f"Tidak ditemukan: {LATAR_JSON}", file=sys.stderr)
        raise SystemExit(1)
    data = json.loads(LATAR_JSON.read_text(encoding="utf-8"))
    return data.get("gambar", {})


def build_all_assets(registry: dict[str, dict]) -> list[dict]:
    location_paths = {p for p, e in registry.items() if e.get("kategori") == "lokasi"}
    assets = []
    for path, entry in registry.items():
        kategori = entry.get("kategori", "lokasi")
        category = KATEGORI_MAP.get(kategori, "location")
        variant_of = guess_variant_of(path, location_paths) if category == "variant" else None
        region_key, region = region_for(path, kategori, entry.get("nama", ""), entry.get("deskripsi", ""))
        prompt, negative_prompt, metadata = build_prompt(path, entry, category, region_key, region, variant_of)
        asset = {
            "id": path.replace("/", "_"),
            "category": category,
            "priority": entry.get("prioritas", 2),
            "asset_path": f"{path}.webp",
            "location": entry.get("nama", ""),
            "source_description": entry.get("deskripsi", ""),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": WIDTH,
            "height": HEIGHT,
            "format": IMG_FORMAT,
            "target_max_size_kb": MAX_KB,
            "full_screen": category == "event",
            "flags": entry.get("syarat") or None,
            "metadata": metadata,
        }
        assets.append(asset)
    assets.sort(key=lambda a: (a["priority"], a["asset_path"]))
    return assets


# ---------------------------------------------------------------------------
# Markdown rendering.
# ---------------------------------------------------------------------------

def render_markdown(asset: dict) -> str:
    lines = [
        f"# {asset['location']}",
        "",
        "Asset:",
        asset["asset_path"],
        "",
        "Priority:",
        str(asset["priority"]),
        "",
        "## Source Description (Indonesian, verbatim)",
        "",
        asset["source_description"],
        "",
        "## Prompt",
        "",
        asset["prompt"],
        "",
        "## Negative Prompt",
        "",
        asset["negative_prompt"],
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(asset["metadata"], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation.
# ---------------------------------------------------------------------------

def validate(assets: list[dict], registry: dict[str, dict], filtered: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ids = [a["id"] for a in assets]
    if len(ids) != len(set(ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        errors.append(f"id duplikat: {sorted(dupes)}")

    paths = [a["asset_path"] for a in assets]
    if len(paths) != len(set(paths)):
        dupes = {p for p in paths if paths.count(p) > 1}
        errors.append(f"asset_path duplikat: {sorted(dupes)}")

    for a in assets:
        if not a["asset_path"]:
            errors.append(f"{a['id']}: asset_path kosong")
        if not a["prompt"]:
            errors.append(f"{a['id']}: prompt kosong")
        if not a["negative_prompt"]:
            errors.append(f"{a['id']}: negative_prompt kosong")
        if (a["width"], a["height"], a["format"]) != (WIDTH, HEIGHT, IMG_FORMAT):
            errors.append(f"{a['id']}: dimensi/format salah")
        if a["priority"] not in (1, 2, 3):
            errors.append(f"{a['id']}: priority tidak valid ({a['priority']})")
        src = registry.get(a["asset_path"][: -len(".webp")], {}).get("deskripsi", "")
        if a["source_description"] != src:
            errors.append(f"{a['id']}: source_description tidak sama dengan latar.json")
        if len(a["source_description"]) < 20:
            warnings.append(f"{a['id']}: deskripsi sumber sangat pendek (<20 char)")
        if a["category"] == "variant" and not a["metadata"]["variant_of"]:
            warnings.append(f"{a['id']}: varian tanpa variant_of yang bisa ditebak")

    if not filtered:
        expected = {f"{p}.webp" for p in registry}
        got = set(paths)
        missing = expected - got
        if missing:
            errors.append(f"entri latar.json tanpa prompt: {sorted(missing)}")

    return errors, warnings


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def normalize_id_arg(raw: str) -> str:
    s = raw.strip()
    if s.endswith(".webp"):
        s = s[: -len(".webp")]
    return s


def write_manifest(assets: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": 1,
        "generated_from": "pelita/data/world/latar.json",
        "style_version": STYLE_VERSION,
        "assets": assets,
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_markdown_files(assets: list[dict], force: bool) -> dict[str, int]:
    written = {"location": 0, "variant": 0, "event": 0}
    current_ids: dict[str, set[str]] = {k: set() for k in MD_DIRS}
    for asset in assets:
        category = asset["category"]
        out_dir = MD_DIRS[category]
        out_dir.mkdir(parents=True, exist_ok=True)
        current_ids[category].add(asset["id"])
        target = out_dir / f"{asset['id']}.md"
        content = render_markdown(asset)
        target.write_text(content, encoding="utf-8")
        written[category] += 1

    if force:
        for category, out_dir in MD_DIRS.items():
            if not out_dir.exists():
                continue
            for md in out_dir.glob("*.md"):
                if md.stem not in current_ids[category]:
                    md.unlink()
    return written


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Rakit prompt image-generation untuk semua gambar latar terdaftar di "
            "pelita/data/world/latar.json, murni berbasis aturan/template."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--force", action="store_true",
                     help="hapus berkas .md basi (id yang tidak lagi ada di latar.json)")
    ap.add_argument("--priority", type=int, choices=(1, 2, 3), help="saring berdasarkan prioritas")
    ap.add_argument("--category", choices=("location", "variant", "event", "all"), default="all",
                     help="saring berdasarkan kategori (bawaan: all)")
    ap.add_argument("--id", dest="asset_id",
                     help="hanya proses satu aset, mis. pelita_rendah/warung.webp")
    args = ap.parse_args()

    registry = load_registry()
    if not registry:
        print("latar.json kosong atau tidak ada entri 'gambar'.", file=sys.stderr)
        return 1

    all_assets = build_all_assets(registry)

    assets = all_assets
    if args.priority is not None:
        assets = [a for a in assets if a["priority"] == args.priority]
    if args.category != "all":
        assets = [a for a in assets if a["category"] == args.category]
    if args.asset_id:
        target = normalize_id_arg(args.asset_id)
        assets = [a for a in assets if a["asset_path"][: -len(".webp")] == target]
        if not assets:
            print(f"Tidak ada entri untuk --id {args.asset_id!r} di latar.json.", file=sys.stderr)
            return 1

    # Manifes selalu mencerminkan seluruh registry (sumber kebenaran tunggal, satu
    # berkas); filter hanya membatasi berkas markdown mana yang ditulis ulang.
    write_manifest(all_assets)
    written = write_markdown_files(assets, args.force)

    errors, warnings = validate(all_assets, registry, filtered=False)

    def count(cat: str, prio: Optional[int] = None) -> int:
        return sum(1 for a in all_assets if a["category"] == cat and (prio is None or a["priority"] == prio))

    print(f"Generated: {len(assets)} (dari total {len(all_assets)} entri di latar.json)")
    print(f"  ditulis: lokasi={written['location']} varian={written['variant']} peristiwa={written['event']}")
    print()
    print(f"Locations: {count('location')}")
    print(f"Variants: {count('variant')}")
    print(f"Events: {count('event')}")
    print(f"Priority 1: {sum(1 for a in all_assets if a['priority'] == 1)}")
    print(f"Priority 2: {sum(1 for a in all_assets if a['priority'] == 2)}")
    print(f"Priority 3: {sum(1 for a in all_assets if a['priority'] == 3)}")
    print()
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  - {w}")
    print()
    print(f"Manifes: {MANIFEST_PATH.relative_to(ROOT)}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
