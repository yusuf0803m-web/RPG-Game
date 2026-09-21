# Image Generation Batch -- Pelita Terakhir

Filter: priority=1, category=all
Total assets: 28

Generated from `prompts/latar_prompts.json` by `tools/export_image_generation_batch.py`. This file is deterministic: re-running the same command regenerates the same content.

Workflow: see `prompts/README.md`. Short version -- copy **IMAGE PROMPT** into ChatGPT Image Generation, save the result under **Output path**, then run `tools/prepare_generated_images.py` to resize/convert/compress it to spec.

---

## Priority 1

### Category: Location

#### Region: benteng_ordo

### `benteng_ordo_suar_benteng` -- Benteng Ordo Pelita — Suar Benteng

- **Asset ID:** `benteng_ordo_suar_benteng`
- **Output path:** `pelita/web/static/assets/backgrounds/benteng_ordo/suar_benteng.webp`
- **Category:** location
- **Priority:** 1
- **Region:** benteng_ordo
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Benteng Ordo Pelita — Suar Benteng. [SCENE] a fortress carved directly into a towering salt cliff face, narrow glowing window-slits cut into weathered rock, terraced stone-and-bronze interior halls; featuring memory-glass surfaces. [ENVIRONMENT] Environment type: fortress. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly otherworldly light rather than an ordinary fire. [STORYTELLING DETAILS] Storytelling details: a Suar -- a beacon tower housing a fragment of the Nyala. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: benteng_ordo/suar_benteng.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: celah_angin

### `celah_angin_jalan_angin` -- Celah Angin — Jalan Angin

- **Asset ID:** `celah_angin_jalan_angin`
- **Output path:** `pelita/web/static/assets/backgrounds/celah_angin/jalan_angin.webp`
- **Category:** location
- **Priority:** 1
- **Region:** celah_angin
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Celah Angin — Jalan Angin. [SCENE] a narrow wind-scoured mountain pass between two immense rock walls, sand-laden gusts, exposed vertical stone terrain; featuring weathered stone. [ENVIRONMENT] Environment type: mountain cliff. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: celah_angin/jalan_angin.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: danau_cermin

### `danau_cermin_dermaga_telaga` -- Danau Cermin — Dermaga Desa Apung Telaga

- **Asset ID:** `danau_cermin_dermaga_telaga`
- **Output path:** `pelita/web/static/assets/backgrounds/danau_cermin/dermaga_telaga.webp`
- **Category:** location
- **Priority:** 1
- **Region:** danau_cermin
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Danau Cermin — Dermaga Desa Apung Telaga. [SCENE] a still, mirror-flat lake ringed by unmoving mist, with a floating village of bamboo-raft houses linked by swaying rope walkways; featuring a still lake, a wooden dock, a village, bamboo construction, a bamboo raft, a wooden footbridge. [ENVIRONMENT] Environment type: lake. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: danau_cermin/dermaga_telaga.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: danau_garam

### `danau_garam_ladang_garam` -- Danau Garam — Ladang Garam

- **Asset ID:** `danau_garam_ladang_garam`
- **Output path:** `pelita/web/static/assets/backgrounds/danau_garam/ladang_garam.webp`
- **Category:** location
- **Priority:** 1
- **Region:** danau_garam
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Danau Garam — Ladang Garam. [SCENE] a vast dried salt lake bed, knee-high crystalline salt growth catching the light like glass grass; featuring a still lake, glowing crystal formations, memory-glass surfaces, crystallized salt. [ENVIRONMENT] Environment type: salt flat. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: danau_garam/ladang_garam.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: dataran_abu

### `dataran_abu_pos_sanggar` -- Dataran Abu — Pos Kafilah Sanggar

- **Asset ID:** `dataran_abu_pos_sanggar`
- **Output path:** `pelita/web/static/assets/backgrounds/dataran_abu/pos_sanggar.webp`
- **Category:** location
- **Priority:** 1
- **Region:** dataran_abu
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Dataran Abu — Pos Kafilah Sanggar. [SCENE] an endless grey ash plain with the buried outline of an older, ruined world beneath the drifting ash. [ENVIRONMENT] Environment type: wasteland. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: fine drifting ash. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: dataran_abu/pos_sanggar.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: hutan_kelabu

### `hutan_kelabu_jalan_setapak` -- Hutan Kelabu — Jalan Setapak

- **Asset ID:** `hutan_kelabu_jalan_setapak`
- **Output path:** `pelita/web/static/assets/backgrounds/hutan_kelabu/jalan_setapak.webp`
- **Category:** location
- **Priority:** 1
- **Region:** hutan_kelabu
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Hutan Kelabu — Jalan Setapak. [SCENE] a grey, mist-drowned forest where fog pools knee-to-chest deep between the trunks; featuring dense forest. [ENVIRONMENT] Environment type: forest. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [STORYTELLING DETAILS] Storytelling details: a Suar -- a beacon tower housing a fragment of the Nyala. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: hutan_kelabu/jalan_setapak.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: hutan_nyanyi

### `hutan_nyanyi_padasuara` -- Hutan Nyanyi — Desa Padasuara

- **Asset ID:** `hutan_nyanyi_padasuara`
- **Output path:** `pelita/web/static/assets/backgrounds/hutan_nyanyi/padasuara.webp`
- **Category:** location
- **Priority:** 1
- **Region:** hutan_nyanyi
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Hutan Nyanyi — Desa Padasuara. [SCENE] a singing forest of towering ancient trees whose hollow trunks echo and repeat distant song, a moss-grown stone road from a vanished kingdom beneath the canopy; featuring a village, dense forest, exposed, reaching roots, worn stone or wooden steps. [ENVIRONMENT] Environment type: forest. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No lantern light anywhere in this scene -- the source description explicitly says there are no lanterns here; light it with plausible ambient sources only (moonlight, diffused mist light, faint bioluminescence), and never add a lantern. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: hutan_nyanyi/padasuara.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: laut_lupa

### `laut_lupa_kapal_dek` -- Laut Lupa — Kapal Lentera — Dek

- **Asset ID:** `laut_lupa_kapal_dek`
- **Output path:** `pelita/web/static/assets/backgrounds/laut_lupa/kapal_dek.webp`
- **Category:** location
- **Priority:** 1
- **Region:** laut_lupa
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Laut Lupa — Kapal Lentera — Dek. [SCENE] a fog-bound sea of drifting memory, where the shapes of drowned rooftops and roads surface briefly beneath the hull before another layer covers them again; featuring a village, a wooden ship. [ENVIRONMENT] Environment type: ship. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: Laut Lupa -- the Sea of Forgetting. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: laut_lupa/kapal_dek.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `laut_lupa_laut_kabut` -- Laut Lupa — Laut Kabut

- **Asset ID:** `laut_lupa_laut_kabut`
- **Output path:** `pelita/web/static/assets/backgrounds/laut_lupa/laut_kabut.webp`
- **Category:** location
- **Priority:** 1
- **Region:** laut_lupa
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Laut Lupa — Laut Kabut. [SCENE] a fog-bound sea of drifting memory, where the shapes of drowned rooftops and roads surface briefly beneath the hull before another layer covers them again; featuring a wooden footbridge, a wooden ship. [ENVIRONMENT] Environment type: ship. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: Laut Lupa -- the Sea of Forgetting. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: laut_lupa/laut_kabut.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `laut_lupa_puncak_lentera` -- Laut Lupa — Puncak Pulau Lentera

- **Asset ID:** `laut_lupa_puncak_lentera`
- **Output path:** `pelita/web/static/assets/backgrounds/laut_lupa/puncak_lentera.webp`
- **Category:** location
- **Priority:** 1
- **Region:** laut_lupa
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Laut Lupa — Puncak Pulau Lentera. [SCENE] a fog-bound sea of drifting memory, where the shapes of drowned rooftops and roads surface briefly beneath the hull before another layer covers them again; featuring a high summit. [ENVIRONMENT] Environment type: island. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: Laut Lupa -- the Sea of Forgetting. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: laut_lupa/puncak_lentera.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: lorong_bawah

### `lorong_bawah_saluran_masuk` -- Lorong Bawah — Saluran Masuk

- **Asset ID:** `lorong_bawah_saluran_masuk`
- **Output path:** `pelita/web/static/assets/backgrounds/lorong_bawah/saluran_masuk.webp`
- **Category:** location
- **Priority:** 1
- **Region:** lorong_bawah
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Lorong Bawah — Saluran Masuk. [SCENE] flooded stone tunnels beneath the city, dead machinery, iron ladders and gear-lined chambers; featuring weathered stone. [ENVIRONMENT] Environment type: underground. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: lorong_bawah/saluran_masuk.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: mercusuar

### `mercusuar_kaki_menara` -- Mercusuar Langit — Kaki Menara

- **Asset ID:** `mercusuar_kaki_menara`
- **Output path:** `pelita/web/static/assets/backgrounds/mercusuar/kaki_menara.webp`
- **Category:** location
- **Priority:** 1
- **Region:** mercusuar
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Mercusuar Langit — Kaki Menara. [SCENE] the interior of an immense bone-white tower without visible seams, ancient bas-relief carvings lining its rounded walls; featuring a tall tower, weathered stone, bronze fittings. [ENVIRONMENT] Environment type: tower. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] a closer, more intimate framing, as described in the source. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: the Suar/Nyala sacred flame (region default; not contradicted by the source description). [STORYTELLING DETAILS] Storytelling details: Mercusuar Langit -- the Sky Lighthouse. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: mercusuar/kaki_menara.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `mercusuar_puncak` -- Mercusuar Langit — Lantai 7 — Puncak

- **Asset ID:** `mercusuar_puncak`
- **Output path:** `pelita/web/static/assets/backgrounds/mercusuar/puncak.webp`
- **Category:** location
- **Priority:** 1
- **Region:** mercusuar
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Mercusuar Langit — Lantai 7 — Puncak. [SCENE] the interior of an immense bone-white tower without visible seams, ancient bas-relief carvings lining its rounded walls; featuring a high summit, memory-glass surfaces. [ENVIRONMENT] Environment type: tower. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] The Suar/Nyala here is dark, damaged, or absent per the source description -- do not render it as actively lit; use dim, cold ambient light instead. [STORYTELLING DETAILS] Storytelling details: Mercusuar Langit -- the Sky Lighthouse; the Nyala -- the world's central sacred flame. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: mercusuar/puncak.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: pelita_rendah

### `pelita_rendah_jalan_desa` -- Pelita Rendah — Jalan Desa

- **Asset ID:** `pelita_rendah_jalan_desa`
- **Output path:** `pelita/web/static/assets/backgrounds/pelita_rendah/jalan_desa.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pelita_rendah
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pelita Rendah — Jalan Desa. [SCENE] a modest hillside village of stilted wooden houses along a packed-earth road, bronze lanterns at gateposts and porches; featuring a village. [ENVIRONMENT] Environment type: village. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pelita_rendah/jalan_desa.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `pelita_rendah_rumah_guntur` -- Pelita Rendah — Rumah Pak Guntur

- **Asset ID:** `pelita_rendah_rumah_guntur`
- **Output path:** `pelita/web/static/assets/backgrounds/pelita_rendah/rumah_guntur.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pelita_rendah
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pelita Rendah — Rumah Pak Guntur. [SCENE] a modest hillside village of stilted wooden houses along a packed-earth road, bronze lanterns at gateposts and porches; featuring bronze fittings. [ENVIRONMENT] Environment type: village. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pelita_rendah/rumah_guntur.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

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

#### Region: pusar_kabut

### `pusar_kabut_aula_suar` -- Pusar Kabut & Kota Adiluhung — Aula Tujuh Suar

- **Asset ID:** `pusar_kabut_aula_suar`
- **Output path:** `pelita/web/static/assets/backgrounds/pusar_kabut/aula_suar.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pusar_kabut
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pusar Kabut & Kota Adiluhung — Aula Tujuh Suar. [SCENE] a colossal, slow-spinning vortex of mist with an ancient sunken city clinging in spiralling tiers to its inner wall; featuring memory-glass surfaces. [ENVIRONMENT] Environment type: ancient ruins. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly otherworldly light rather than an ordinary fire. [STORYTELLING DETAILS] Storytelling details: a silent construct standing guard; Kota Adiluhung -- an ancient sunken city; a Suar -- a beacon tower housing a fragment of the Nyala. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pusar_kabut/aula_suar.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `pusar_kabut_sumur_ingatan` -- Pusar Kabut & Kota Adiluhung — Dasar Sumur Ingatan

- **Asset ID:** `pusar_kabut_sumur_ingatan`
- **Output path:** `pelita/web/static/assets/backgrounds/pusar_kabut/sumur_ingatan.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pusar_kabut
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pusar Kabut & Kota Adiluhung — Dasar Sumur Ingatan. [SCENE] a colossal, slow-spinning vortex of mist with an ancient sunken city clinging in spiralling tiers to its inner wall; featuring memory-glass surfaces. [ENVIRONMENT] Environment type: ancient ruins. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [STORYTELLING DETAILS] Storytelling details: Sumur Ingatan -- the Memory Well; Kota Adiluhung -- an ancient sunken city. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pusar_kabut/sumur_ingatan.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `pusar_kabut_tepi_pusar` -- Pusar Kabut & Kota Adiluhung — Tepi Pusar

- **Asset ID:** `pusar_kabut_tepi_pusar`
- **Output path:** `pelita/web/static/assets/backgrounds/pusar_kabut/tepi_pusar.webp`
- **Category:** location
- **Priority:** 1
- **Region:** pusar_kabut
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Pusar Kabut & Kota Adiluhung — Tepi Pusar. [SCENE] a colossal, slow-spinning vortex of mist with an ancient sunken city clinging in spiralling tiers to its inner wall; featuring a wooden footbridge, a wooden ship. [ENVIRONMENT] Environment type: ship. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: drifting mist. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [STORYTELLING DETAILS] Storytelling details: Kota Adiluhung -- an ancient sunken city. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: pusar_kabut/tepi_pusar.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: rawa_suar

### `rawa_suar_rawa_dangkal` -- Rawa Suar — Rawa Dangkal

- **Asset ID:** `rawa_suar_rawa_dangkal`
- **Output path:** `pelita/web/static/assets/backgrounds/rawa_suar/rawa_dangkal.webp`
- **Category:** location
- **Priority:** 1
- **Region:** rawa_suar
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Rawa Suar — Rawa Dangkal. [SCENE] a warm, sulfurous marsh with mangrove trees leaning uniformly away from an old, half-sunk beacon tower, raised bamboo walkways over shallow water; featuring shallow marsh water, a tall tower, towering trees. [ENVIRONMENT] Environment type: swamp. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly otherworldly light rather than an ordinary fire. [STORYTELLING DETAILS] Storytelling details: a Suar -- a beacon tower housing a fragment of the Nyala. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: rawa_suar/rawa_dangkal.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: tambang

### `tambang_lorong_atas` -- Tambang Kaca Ingatan — Lorong Atas

- **Asset ID:** `tambang_lorong_atas`
- **Output path:** `pelita/web/static/assets/backgrounds/tambang/lorong_atas.webp`
- **Category:** location
- **Priority:** 1
- **Region:** tambang
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Tambang Kaca Ingatan — Lorong Atas. [SCENE] a mountainside memory-glass mine, timber-shored tunnels, rusted mine-cart rails, glowing crystal veins in the rock; featuring memory-glass surfaces, rusted mine-cart rails. [ENVIRONMENT] Environment type: mine. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: Kaca Ingatan -- memory-infused glass, an original fictional material. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: tambang/lorong_atas.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: tengara

### `tengara_dermaga_kota` -- Ibukota Tengara — Dermaga Kota

- **Asset ID:** `tengara_dermaga_kota`
- **Output path:** `pelita/web/static/assets/backgrounds/tengara/dermaga_kota.webp`
- **Category:** location
- **Priority:** 1
- **Region:** tengara
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Ibukota Tengara — Dermaga Kota. [SCENE] a walled capital city of andesite stone, tiered markets on the inner slope, bronze lantern-posts along stone docks; featuring a wooden dock, weathered stone, a fortified wall. [ENVIRONMENT] Environment type: city. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: Mercusuar Langit -- the Sky Lighthouse. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: tengara/dermaga_kota.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `tengara_pasar_bawah` -- Ibukota Tengara — Pasar Bawah

- **Asset ID:** `tengara_pasar_bawah`
- **Output path:** `pelita/web/static/assets/backgrounds/tengara/pasar_bawah.webp`
- **Category:** location
- **Priority:** 1
- **Region:** tengara
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Ibukota Tengara — Pasar Bawah. [SCENE] a walled capital city of andesite stone, tiered markets on the inner slope, bronze lantern-posts along stone docks; featuring market stalls, a fortified wall. [ENVIRONMENT] Environment type: city. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] Primary light source: warm amber oil lanterns (region default; not contradicted by the source description), casting warm light against cooler environmental tones. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: tengara/pasar_bawah.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: wirasaba

### `wirasaba_jalan_kaca` -- Kota Kaca Wirasaba — Jalan Kaca

- **Asset ID:** `wirasaba_jalan_kaca`
- **Output path:** `pelita/web/static/assets/backgrounds/wirasaba/jalan_kaca.webp`
- **Category:** location
- **Priority:** 1
- **Region:** wirasaba
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Reusable in-game background. Keep the lower third of the frame clear -- the game adds its own dark dialogue gradient there. Do not add prominent characters unless the prompt explicitly calls for one as an environmental storytelling detail. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Reusable 1600x900 (16:9) in-game background illustration for a JRPG. Not a poster, not a character portrait, not splash art. [LOCATION] Kota Kaca Wirasaba — Jalan Kaca. [SCENE] a city built almost entirely from memory-glass architecture -- walls and towers that faintly replay fragments of the lives once lived inside them; featuring memory-glass surfaces. [ENVIRONMENT] Environment type: city. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] eye-level wide establishing shot. [COMPOSITION] Wide horizontal environmental composition. Keep the lower third of the frame clear of important objects, characters, and dense detail -- the game overlays a dialogue box and a dark gradient there automatically. Do not paint a heavy black gradient at the bottom yourself; the background itself should read as naturally lit and evenly exposed. [LIGHTING] No light source is specified in the source description -- use plausible ambient environmental lighting (moonlight, mist-diffused light, or a cool overcast glow) and do not force a lantern into the scene. [IMPORTANT CONSTRAINTS] Never contradict the source description. Preserve the presence or explicit absence of lanterns exactly as written. Do not add prominent characters, close-up faces, or character portraits -- this is a reusable environment, not a character illustration. Keep any surreal or supernatural element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: wirasaba/jalan_kaca.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
characters, NPCs, protagonist, character portraits, close-up faces, a large dominant protagonist, crowds of NPCs, user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

### Category: Event

#### Region: benteng_ordo

### `events_nirmala_padam` -- Yang Memilih Nanti

- **Asset ID:** `events_nirmala_padam`
- **Output path:** `pelita/web/static/assets/backgrounds/events/nirmala_padam.webp`
- **Category:** event
- **Priority:** 1
- **Region:** benteng_ordo
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Full-screen story illustration ('ilustrasi peristiwa besar'). May include named characters and dramatic staging -- do not flatten it into an empty environment. The lower-third-clear rule does not apply here. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Full-screen 1600x900 (16:9) narrative story illustration ('ilustrasi peristiwa besar') for a JRPG cutscene moment. Not a reusable dialogue background. [LOCATION] Yang Memilih Nanti. [SCENE] a fortress carved directly into a towering salt cliff face, narrow glowing window-slits cut into weathered rock, terraced stone-and-bronze interior halls. [ENVIRONMENT] Environment type: fortress. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] dynamic cinematic staging appropriate to the story beat. [COMPOSITION] Cinematic full-frame composition. Characters and dramatic staging may occupy any part of the frame, including the center and lower frame, since this illustration displays full-screen without a dialogue box overlay. [LIGHTING] Primary light source: the Suar/Nyala sacred flame -- warm, steady, faintly otherworldly light rather than an ordinary fire. [STORYTELLING DETAILS] Storytelling details: a Suar -- a beacon tower housing a fragment of the Nyala. [IMPORTANT CONSTRAINTS] Never contradict the source description. This illustration may include named characters, dramatic poses, and supernatural effects -- do not flatten it into a generic empty environment. Keep any surreal element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: events/nirmala_padam.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: mercusuar

### `events_malam_pertama` -- Malam Pertama

- **Asset ID:** `events_malam_pertama`
- **Output path:** `pelita/web/static/assets/backgrounds/events/malam_pertama.webp`
- **Category:** event
- **Priority:** 1
- **Region:** mercusuar
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Full-screen story illustration ('ilustrasi peristiwa besar'). May include named characters and dramatic staging -- do not flatten it into an empty environment. The lower-third-clear rule does not apply here. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Full-screen 1600x900 (16:9) narrative story illustration ('ilustrasi peristiwa besar') for a JRPG cutscene moment. Not a reusable dialogue background. [LOCATION] Malam Pertama. [SCENE] the interior of an immense bone-white tower without visible seams, ancient bas-relief carvings lining its rounded walls; featuring a tall tower, a village. [ENVIRONMENT] Environment type: tower. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. Time of day: night. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] dynamic cinematic staging appropriate to the story beat. [COMPOSITION] Cinematic full-frame composition. Characters and dramatic staging may occupy any part of the frame, including the center and lower frame, since this illustration displays full-screen without a dialogue box overlay. [LIGHTING] The lanterns described here are extinguished or unlit -- render them dark and cold with only dim ambient light; do not show them burning. [IMPORTANT CONSTRAINTS] Never contradict the source description. This illustration may include named characters, dramatic poses, and supernatural effects -- do not flatten it into a generic empty environment. Keep any surreal element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: events/malam_pertama.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

### `events_mercusuar_padam` -- Nyala Mercusuar Langit Padam

- **Asset ID:** `events_mercusuar_padam`
- **Output path:** `pelita/web/static/assets/backgrounds/events/mercusuar_padam.webp`
- **Category:** event
- **Priority:** 1
- **Region:** mercusuar
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Full-screen story illustration ('ilustrasi peristiwa besar'). May include named characters and dramatic staging -- do not flatten it into an empty environment. The lower-third-clear rule does not apply here. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Full-screen 1600x900 (16:9) narrative story illustration ('ilustrasi peristiwa besar') for a JRPG cutscene moment. Not a reusable dialogue background. [LOCATION] Nyala Mercusuar Langit Padam. [SCENE] the interior of an immense bone-white tower without visible seams, ancient bas-relief carvings lining its rounded walls; featuring a tall tower, a high summit, weathered stone. [ENVIRONMENT] Environment type: tower. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] a closer, more intimate framing, as described in the source. [COMPOSITION] Cinematic full-frame composition. Characters and dramatic staging may occupy any part of the frame, including the center and lower frame, since this illustration displays full-screen without a dialogue box overlay. [LIGHTING] The Suar/Nyala here is dark, damaged, or absent per the source description -- do not render it as actively lit; use dim, cold ambient light instead. [STORYTELLING DETAILS] Storytelling details: Mercusuar Langit -- the Sky Lighthouse; the Nyala -- the world's central sacred flame. [IMPORTANT CONSTRAINTS] Never contradict the source description. This illustration may include named characters, dramatic poses, and supernatural effects -- do not flatten it into a generic empty environment. Keep any surreal element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: events/mercusuar_padam.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---

#### Region: wirasaba

### `events_kelana_berhenti` -- Satu Nama

- **Asset ID:** `events_kelana_berhenti`
- **Output path:** `pelita/web/static/assets/backgrounds/events/kelana_berhenti.webp`
- **Category:** event
- **Priority:** 1
- **Region:** wirasaba
- **Recommended aspect ratio:** 16:9
- **Recommended resolution:** 1600x900 (ChatGPT generation hint: use its landscape size 1536x1024, then resize/crop -- see `tools/prepare_generated_images.py`)
- **Notes:** Full-screen story illustration ('ilustrasi peristiwa besar'). May include named characters and dramatic staging -- do not flatten it into an empty environment. The lower-third-clear rule does not apply here. Final asset: 1600x900 px (16:9), WebP, aim under 250KB.

**IMAGE PROMPT** (copy everything below into ChatGPT Image Generation)

```
[FORMAT] Full-screen 1600x900 (16:9) narrative story illustration ('ilustrasi peristiwa besar') for a JRPG cutscene moment. Not a reusable dialogue background. [LOCATION] Satu Nama. [SCENE] a city built almost entirely from memory-glass architecture -- walls and towers that faintly replay fragments of the lives once lived inside them; featuring memory-glass surfaces, weathered armor. [ENVIRONMENT] Environment type: city. material and architectural language drawn from Southeast Asian / Nusantara-inspired construction where it is consistent with the scene described above -- bamboo, teak wood, rattan, woven fiber, bronze, clay, stone, traditional thatched roofing, hand-built and weathered surfaces; an original fantasy world, never a real-world modern Indonesian village and never generic European medieval fantasy. [ATMOSPHERE] Atmosphere: clear, restrained dark-fantasy atmosphere. [VISUAL STYLE] cinematic dark fantasy Nusantara JRPG environmental concept art, hand-painted fantasy background illustration, atmospheric depth, restrained natural color palette, immersive original-world worldbuilding, painterly but production-ready. [CAMERA] dynamic cinematic staging appropriate to the story beat. [COMPOSITION] Cinematic full-frame composition. Characters and dramatic staging may occupy any part of the frame, including the center and lower frame, since this illustration displays full-screen without a dialogue box overlay. [LIGHTING] Primary light source: warm amber oil lanterns, casting warm light against the cooler environmental tones. [STORYTELLING DETAILS] Storytelling details: a Hampa (a silent, hollow armored construct) standing motionless. [IMPORTANT CONSTRAINTS] Never contradict the source description. This illustration may include named characters, dramatic poses, and supernatural effects -- do not flatten it into a generic empty environment. Keep any surreal element visually clear and intentional, not chaotic. [TARGET ASSET] Target asset: events/kelana_berhenti.webp, 1600x900 px, WEBP, aim under 250KB.
```

**NEGATIVE / AVOID** (mention these as things to avoid in the same request, or in a follow-up refinement)

```
user interface elements, HUD, dialogue box, readable text, logos, watermark, modern technology, electricity, power lines, cars, motorcycles, sci-fi elements, steampunk machinery, generic European medieval architecture, excessive ornate high-fantasy architecture, oversaturated colors, photorealistic photography, heavy black gradient overlay at the bottom
```

---
