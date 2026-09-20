# Image Generation Batch -- Pelita Terakhir

Filter: category=all, id=pelita_rendah_warung
Total assets: 1

Generated from `prompts/latar_prompts.json` by `tools/export_image_generation_batch.py`. This file is deterministic: re-running the same command regenerates the same content.

Workflow: see `prompts/README.md`. Short version -- copy **IMAGE PROMPT** into ChatGPT Image Generation, save the result under **Output path**, then run `tools/prepare_generated_images.py` to resize/convert/compress it to spec.

---

## Priority 1

### Category: Location

#### Region: pelita_rendah

### `pelita_rendah_warung` -- Pelita Rendah — Warung Bu Ratna

- **Asset ID:** `pelita_rendah_warung`
- **Output path:** `pelita/web/static/assets/backgrounds/pelita_rendah/warung.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pelita_rendah
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pelita Rendah — Warung Bu Ratna. [SCENE] a modest hillside village of stilted wooden houses along a packed-earth road, bronze lanterns at gateposts and porches; featuring bamboo construction, weathered armor. [ENVIRONMENT] Environment type: village. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pelita_rendah/warung.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---
