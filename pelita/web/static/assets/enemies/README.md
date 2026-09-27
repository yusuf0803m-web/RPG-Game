# Sprite musuh Pelita Terakhir

Taruh berkas di folder ini dengan nama **id musuh**, mis. `kunang_kelam.webp`.
Semua musuh dengan id itu (Kunang Kelam A, B, C) memakai gambar yang sama.

- **Format & ukuran:** persegi 1:1, minimal 768×768 px; simpan sebagai .webp 640×640 (di bawah ±120 KB).
- **Kalau berkasnya belum ada**, kartu memakai siluet SVG. Tidak ada yang rusak;
  gambar bisa diisi bertahap.
- **Komposisi:** satu makhluk di tengah, seluruh badan, latar gelap polos. Kartu
  memotong gambar seperti jendela lebar (bagian tengah atas paling terlihat) lalu
  memudarkan bagian bawahnya, jadi taruh kepala/wajah di sepertiga atas.
- **Gaya:** sama dengan gambar latar: lukisan digital, cahaya lentera hangat,
  kabut dingin. Pakai prompt di bawah apa adanya supaya semua sprite seragam.
- Sumber prompt: `tools/sprite_prompts.json`. Perbarui daftar ini dengan
  `python tools/daftar_sprite.py --tulis`.

Prioritas 1 = boss (paling lama dilihat pemain). Prioritas 2 = musuh biasa Babak 1
(sampai Mercusuar). Prioritas 3 = musuh Babak 2–3 dan buruan.


## Prioritas 1: Boss (1/22)

- [ ] `boss_hampa_penjaga_hutan.webp` — **Hampa Penjaga Hutan** (Lv 4)  
  Hampa besar bekas penebang kayu.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A towering hollow woodcutter, grey skin like ash-bark, empty eye sockets leaking thin fog, still gripping a notched felling axe. Moss and broken lantern hooks hang from its shoulders; it moves like it forgot why it is chopping. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [x] `boss_raja_katak_lumpur.webp` — **Raja Katak Lumpur** (Lv 8)  
  Raja rawa yang perutnya berpendar lentera-lentera yang ditelannya.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An enormous swamp frog king, bloated and ancient, skin like wet mud and moss, a crude crown of rusted lantern frames on its head. Its swollen belly glows from within with the lanterns it has swallowed. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_ular_cermin.webp` — **Ular Cermin** (Lv 12)  
  Ular sepanjang dermaga yang sisiknya memantulkan orang-orang yang pernah menatapnya.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A serpent as long as a pier, coiled high, every scale a mirror showing the faces of people who once stared at it, eyes like two pale moons, water dripping from its coils. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_kapten_rangga.webp` — **Kapten Rangga** (Lv 15)  
  Kapten Pengawal Mahkota. Loyal pada perintah karena takut pada kekacauan.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A stern human captain of the Crown Guard, in lacquered dark armor with a red sash and a long spear, scar across the cheek, disciplined stance, eyes afraid of chaos rather than enemies. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_juru_kaca_tenggelam.webp` — **Juru Kaca Tenggelam** (Lv 17)  
  Juru kaca tambang yang turun membawa peti dan tidak pernah diperintahkan naik.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A drowned glass-miner in heavy work armor and a cracked diving helmet, dragging an iron chest on a chain, glass shards growing from his back, lantern dead at his belt. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_penambang_raksasa.webp` — **Penambang Raksasa Terlupa** (Lv 19)  
  Beberapa penambang yang meleleh jadi satu, punggungnya berkerak kristal ingatan.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. Several miners melted together into one giant mass, multiple arms holding pickaxes, faces half-merged, a back covered in large glowing memory crystals that change color. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_penjaga_mercusuar.webp` — **Penjaga Mercusuar** (Lv 21)  
  Konstruk batu putih yang dulu dikendalikan Guntur. Sekarang liar.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A towering construct of smooth white stone like bone, lantern-shaped head with a dark empty glass chamber, massive arms, carved runes glowing faintly gold, gone feral. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_baskara.webp` — **Adipati Baskara** (Lv 23)  
  Wali kota Tengara yang memadamkan Mercusuar. Bicara pelan, tidak pernah berteriak.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An elegant middle-aged noble regent in dark batik robes and a gold headpiece, calm half-smile, holding a snuffed lantern, soft-spoken menace, never shouting. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_kelam_berwajah.webp` — **Kelam Berwajah** (Lv 23)  
  Kabut yang selama ini ditahan Baskara di dalam menara, menelan dan membentuknya.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A mass of living fog shaped into a vast face with many hollow eyes, tendrils forming arms, swallowing the light of the tower around it. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_garuda_kelabu.webp` — **Garuda Kelabu** (Lv 26)  
  Garuda sebesar rumah yang menjaga Celah Angin sejak sebelum ada jalan di sana.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A garuda as big as a house, ancient grey feathers, gold-tipped wing edges, a proud crested head, talons gripping a cliff, guardian of the wind pass. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_cacing_abu_purba.webp` — **Cacing Abu Purba** (Lv 29)  
  Cacing yang memakan kota-kota yang terbakar. Abu dataran ini adalah kotorannya.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A colossal ancient ash worm rising from the plain, body scarred with the ruins of burned towns, cavernous toothed maw, embers glowing inside. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_sunan_wirya.webp` — **Sunan Wirya** (Lv 32)  
  Pengkhotbah Ordo yang benar-benar percaya bahwa Pendendang sedang membunuh dunia dengan pelan.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A charismatic preacher of the Order in layered white robes and a tall head wrap, one hand raised in sermon, a lantern staff in the other, sincere burning eyes. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_penjaga_suar_wirasaba.webp` — **Penjaga Suar Wirasaba** (Lv 34)  
  Konstruk setinggi tiga orang yang masih menjaga Suar yang sudah lama padam.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A three-person-tall construct of glass and bronze guarding a long-dead beacon, cracked glass chest with a cold empty core, heavy slow limbs. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_kelana_berzirah.webp` — **Hampa Berzirah** (Lv 36)  
  Hampa berzirah yang menjaga gerobak panen Ordo. Ia menebas siapa pun yang mendekat, tanpa marah.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A hollow knight in heavy dark armor guarding a harvest cart of the Order, a great blade held low, no anger in its posture, only duty, fog behind the visor. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_nyi_pandansari.webp` — **Nyi Pandansari** (Lv 39)  
  Letnan Ordo yang membawa Kaca Pemanen di punggung. Ia pragmatis, dan itu membuatnya lebih sulit dibenci.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A pragmatic lieutenant of the Order, a woman in practical dark armor and a hooded cloak, a large harvesting glass frame on her back glowing faintly, sharp tired eyes. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_nirmala.webp` — **Juru Nyala Nirmala** (Lv 43)  
  Pemimpin Ordo Pelita. Ia tahu persis apa yang dilakukannya, sudah sejak abad ketiga.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The leader of the Order of Pelita, an ageless woman in white robes with a crown of small glass flames, serene and certain, holding a tall beacon staff. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_gema_guntur.webp` — **Gema Guntur** (Lv 47)  
  Tiga ingatan Rimba tentang mentornya, berdiri di pulau lentera dengan bentuk yang sama.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. Three memories of an old lantern-keeper mentor standing together as one figure: an elderly man with a white beard and a lantern staff, his silhouette repeated three times in different ages. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_pelita_ketiga.webp` — **Pelita Ketiga** (Lv 48)  
  Perempuan yang masuk ke rongga Suar ketiga di abad pertama dan masih menunggu penggantinya datang.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A woman who entered the third beacon's glass chamber in the first century and is still waiting for her replacement: glowing, translucent, seated in a glass hollow, patient and tired. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `boss_pelita_pertama.webp` — **Sang Pelita Pertama** (Lv 52)  
  Manusia pertama yang dibakar delapan abad lalu. Kesadarannya tidak hilang; ia menjadi kehendak Kabut.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The first human ever burned into a light eight centuries ago, now the will of the Fog: a vast figure of dark fog with a burning human core, arms spread, crowned with smoke. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kabut_terakhir.webp` — **Kabut Terakhir** (Lv 52)  
  Seluruh Kabut dunia, berdiri sekali saja dalam bentuk yang bisa dihadapi — dan minta dinyanyikan, bukan dibunuh.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. All the fog in the world standing once in a shape that can be faced: an immense soft figure of mist with a sorrowful gentle face, asking to be sung, not killed. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `buruan_cacing_ibu.webp` — **Cacing Abu Ibu** (Lv 55)  
  Yang melahirkan cacing-cacing Dataran Abu. Ia sudah di sana sebelum kota-kotanya terbakar.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The mother of all ash worms, older than the burned cities: a titanic worm coiled beneath ash dunes, body like a mountain range, a maw like a city gate. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `superboss_penenun.webp` — **Sang Penenun** (Lv 58)  
  Yang duduk di Pulau Hilang dan menyusun ulang apa pun yang datang ke sana, termasuk kalian.
  ```
  Dark fantasy Nusantara boss creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The Weaver who sits on the Lost Island rearranging everything that arrives: a figure made of countless threads and looms, many hands weaving, a shape impossible to describe from any angle. Single figure, full body, centered, low angle to feel huge and threatening. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```

## Prioritas 2: Musuh Babak 1 (1/16)

- [x] `kunang_kelam.webp` — **Kunang Kelam** (Lv 2)  
  Kunang-kunang yang cahayanya terbalik: mengeluarkan gelap.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A firefly the size of a fist whose light is inverted: its abdomen emits a small orb of darkness with a faint violet rim, swallowing the light around it. Thin translucent wings, delicate legs. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `serigala_kabut.webp` — **Serigala Kabut** (Lv 4)  
  Serigala dengan bulu seperti asap. Menggigit lalu mundur ke kabut.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A lean wolf whose fur dissolves into drifting smoke at the edges, glowing amber eyes, low stalking pose, half of its hind body already fading into mist. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `lumut_berjalan.webp` — **Lumut Berjalan** (Lv 5)  
  Gundukan lumut dan akar yang dulu tunggul pohon.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A shambling mound of moss, roots and rotten wood that used to be a tree stump, small glowing fungus, root-legs dragging through the mud, two knots like sleepy eyes. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `hampa_pengembara.webp` — **Hampa Pengembara** (Lv 6)  
  Manusia yang ingatannya habis. Masih mengulang gerak pekerjaan lama.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A hollow villager with ash-grey skin and blank white eyes, wearing faded farmer clothes, still repeating the motion of an old chore with an empty basket. Sad, not monstrous. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `katak_rawa_bengkak.webp` — **Katak Rawa Bengkak** (Lv 8)  
  Katak seukuran gerobak yang menelan lentera rawa.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A frog the size of a cart, swollen belly faintly glowing orange from a swallowed swamp lantern, warty mud-green skin, heavy lids, sitting in shallow water. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `ikan_cermin.webp` — **Ikan Cermin** (Lv 10)  
  Ikan pipih yang sisiknya memantulkan wajah penatapnya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A flat, disc-shaped fish whose scales are tiny mirrors reflecting a distorted face of the viewer, fins like thin glass, floating above dark water. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `nelayan_hampa.webp` — **Nelayan Hampa** (Lv 11)  
  Nelayan yang masih menebar jala ke danau yang kini menatap balik.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A hollow fisherman with ash-grey skin, conical woven hat, casting a torn net that trails fog, standing on a small bamboo raft, eyes blank and patient. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `bayang_arsip.webp` — **Bayang Arsip** (Lv 13)  
  Tumpukan gulungan dan tinta yang membacakan nama-nama Pelita.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A tall figure made of stacked scrolls, ledgers and dripping ink, pages fluttering like breath, a mouth of torn paper reciting names, ink trails on the floor. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pengawal_karat.webp` — **Pengawal Karat** (Lv 13)  
  Zirah pengawal kosong yang bergerak sendiri.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An empty suit of rusted palace guard armor moving on its own, dented helmet with nothing inside, rust flaking, a notched spear, faint fog inside the joints. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kendi_ingatan.webp` — **Kendi Ingatan** (Lv 14)  
  Kendi tanah setinggi lutut yang berjalan dengan isinya sendiri. Yang di dalam masih bicara.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A knee-high earthen water jar walking on small clay legs, stopped with faded inked cloth, whispering light leaking from cracks, as if the contents are still talking. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kelelawar_kristal.webp` — **Kelelawar Kristal** (Lv 15)  
  Kelelawar yang sayapnya tumbuh kaca ingatan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A bat whose wings grow shards of pale violet memory-glass, crystals clinking, sharp glowing eyes, hanging upside down in a cave. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `perenang_dasar.webp` — **Perenang Dasar** (Lv 15)  
  Orang yang turun untuk mengambil sesuatu dan tidak pernah memutuskan untuk naik.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A pale deep-water swimmer who went down to retrieve something and never decided to come up: long drifting hair, webbed hands, clutching a small box, bubbles rising. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `serpih_cacat.webp` — **Serpih Kaca Cacat** (Lv 16)  
  Pecahan Kaca Ingatan yang ditolak Ordo, mengeras jadi satu tubuh bersudut.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A creature assembled from rejected shards of memory-glass fused into one angular, jagged body, facets reflecting broken scenes, glowing seams. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penambang_terlupa.webp` — **Penambang Terlupa** (Lv 17)  
  Hampa bertubuh besar, punggung berkerak kristal.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A huge hollow miner with a hunched back crusted with violet memory crystals, pickaxe dragging, headlamp long extinguished, ash-grey skin. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pelita_padam.webp` — **Pelita Padam** (Lv 20)  
  Sisa Pelita lama: sosok cahaya redup berbentuk manusia.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The remnant of an old Pelita: a dim, human-shaped figure of faded light, edges flickering like a dying lamp flame, hollow where the heart should glow. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pengawal_istana.webp` — **Pengawal Istana** (Lv 22)  
  Zirah lapis emas yang tidak lagi berisi siapa pun.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An empty suit of gold-plated palace armor, ornate and ceremonial, moving on its own, fog seeping from the neck, a tall ceremonial halberd. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```

## Prioritas 3: Musuh Babak 2–3 & buruan (0/40)

- [ ] `buruan_kunang_raja.webp` — **Kunang Raja** (Lv 7)  
  Kunang sebesar kepala kerbau. Cahayanya bukan cahaya: lubang berbentuk cahaya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A firefly as big as a buffalo head, its glowing abdomen is not light but a hole shaped like light: a void with a burning violet edge. Huge compound eyes, ragged wings. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `buruan_nelayan_tenggelam.webp` — **Nelayan yang Tidak Pulang** (Lv 12)  
  Perahunya karam dua puluh tahun lalu. Jalanya masih baru.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A drowned fisherman, twenty years under water: bloated grey skin, seaweed hair, yet holding a brand-new, bright fishing net. Water pours from his clothes. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `buruan_zirah_tanpa_nama.webp` — **Zirah Tanpa Nama** (Lv 17)  
  Zirah pengawal istana tanpa lambang, tanpa nama, dan tanpa orang di dalamnya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A palace guard armor with no emblem, no name and no one inside, polished but anonymous, standing perfectly still with a curved blade, darkness in the visor slit. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `elang_badai.webp` — **Elang Badai** (Lv 24)  
  Elang sebesar kerbau yang bersarang di celah angin. Sayapnya membawa suara badai sebelum badainya datang.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An eagle as big as a water buffalo, storm-grey feathers crackling with static, wings spread wide, wind streaks and dust around it. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kambing_batu.webp` — **Kambing Batu** (Lv 25)  
  Kambing gunung bertanduk batu yang tidak pernah mundur, bahkan dari tebing.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A mountain goat with horns of layered stone, craggy hide like cliff rock, planted hooves, stubborn glare, pebbles falling. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `hantu_kafilah.webp` — **Hantu Kafilah** (Lv 27)  
  Sisa pedagang yang mati di jalan dan masih menghitung dagangannya, termasuk milikmu.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The ghost of a caravan merchant, translucent, bent under a pack of phantom goods, fingers counting coins that are not there, ash swirling. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kalajengking_abu.webp` — **Kalajengking Abu** (Lv 27)  
  Kalajengking sepanjang lengan yang warnanya persis abu dataran. Kau tahu ia ada setelah disengat.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A scorpion as long as an arm, exactly the color of grey ash, barely visible against dust, tail raised with a faintly glowing sting. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `cacing_abu_muda.webp` — **Cacing Abu Muda** (Lv 28)  
  Anak cacing abu, baru sepanjang perahu. Induknya tidur di bawah dataran.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A young ash worm as long as a boat, segmented grey body bursting out of ash dunes, ring of teeth, dust pouring off its sides. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `burung_peniru.webp` — **Burung Peniru** (Lv 30)  
  Burung kecil yang menirukan apa saja: suara, langkah, dan penderitaan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A small songbird with feathers of shifting colors, beak open mid-mimicry, eerie human-like eyes, surrounded by faint ghostly sound ripples. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pohon_gema.webp` — **Pohon Gema** (Lv 30)  
  Pohon yang mengulang suara apa pun yang pernah dinyanyikan di dekatnya, termasuk lagu yang bukan untuknya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A tree whose bark is full of open mouths and hollows that echo songs, branches like outstretched arms, faint glowing sound rings in the air. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pendeta_ordo.webp` — **Pendeta Ordo** (Lv 31)  
  Manusia, bukan Hampa. Itu bagian yang membuat pertarungan ini terasa berbeda.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A human priest of the Order of Pelita in white and gold robes, holding a small glass lantern, calm fanatic expression, clearly a living person. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `warga_wirasaba.webp` — **Warga Wirasaba** (Lv 33)  
  Penduduk kota kaca yang masih menjalani hari terakhirnya: menawar, menyapu, menunggu seseorang pulang.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A citizen of a glass city living their last day on repeat: a translucent glassy figure sweeping a doorstep, eyes looking far away, waiting for someone. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `cermin_berjalan.webp` — **Cermin Berjalan** (Lv 34)  
  Cermin setinggi orang yang berjalan sendiri. Yang terlihat di dalamnya bukan kau.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A person-tall standing mirror walking on its own on carved wooden feet, the reflection inside is someone else who is not the viewer. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `konstruk_kaca.webp` — **Konstruk Kaca** (Lv 34)  
  Zirah kaca tanpa isi yang dibuat Ordo untuk menjaga Suar. Di dalamnya, sesuatu masih bergerak pelan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An empty suit of armor made of glass, built by the Order to guard a beacon; inside, something small and dark still moves slowly. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `hampa_beku.webp` — **Hampa Beku** (Lv 37)  
  Hampa yang berhenti di tengah danau dan membeku berdiri. Kabutnya ikut membeku di sekelilingnya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A hollow figure frozen mid-step in the middle of a salt lake, ice and salt crystals growing on it, the fog around it frozen into jagged shapes. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kepiting_garam.webp` — **Kepiting Garam** (Lv 37)  
  Kepiting seukuran perahu yang cangkangnya sudah jadi garam. Ia berjalan miring sepanjang danau.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A crab the size of a boat whose shell has turned into white salt crystal, walking sideways, claws crusted with salt, tiny glints. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pemanen_ordo.webp` — **Pemanen Ordo** (Lv 40)  
  Petugas Ordo dengan gerobak kaca di punggungnya. Pekerjaannya memanen Hampa, dan ia menyebutnya membebaskan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An Order harvester with a glass cage-cart strapped to his back, captured faint lights inside, hooked pole in hand, speaking of liberation. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gerobak_kurungan.webp` — **Gerobak Kurungan** (Lv 41)  
  Gerobak panen Ordo yang rodanya tidak pernah diberi perintah berhenti, dan dua pemanen yang tidak pernah diberi perintah pulang.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An Order harvest cart with glass cages full of faint captured lights, wheels that never stop turning, two harvesters chained to its sides. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pelita_hidup_muda.webp` — **Pelita Hidup Muda** (Lv 41)  
  Anak muda Ordo yang sudah menyerahkan dirinya ke Suar, setengah jalan menjadi cahaya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A young member of the Order halfway turned into light: skin cracking with bright glowing seams, eyes pure flame, ecstatic and afraid. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_pesta.webp` — **Gema Pesta** (Lv 44)  
  Satu pesta pernikahan yang cukup keras diingat sehingga berdiri sendiri tanpa pengantinnya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A wedding feast remembered so loudly it stands on its own: floating plates, garlands, drums and laughing faint silhouettes, but no bride and groom. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_pengantin.webp` — **Gema Pengantin** (Lv 45)  
  Ia masih menunggu di ujung lorong bunga yang sudah tidak ada.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A ghostly bride in traditional wedding attire and a jasmine veil, waiting at the end of a flower aisle that no longer exists, petals drifting. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_prajurit.webp` — **Gema Prajurit** (Lv 45)  
  Perang yang diingat terlalu sering oleh terlalu banyak orang, sampai barisannya berdiri sendiri.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A remembered war standing by itself: a rank of translucent soldiers with spears and shields fused into one marching mass. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `nama_terbakar.webp` — **Nama Terbakar** (Lv 45)  
  Satu nama yang dibacakan waktu ritual, dan tidak pernah selesai dibacakan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A single name that was read aloud in a ritual and never finished: glowing burning letters forming a humanoid shape, smoke trailing. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_abad.webp` — **Penjaga Abad Pertama** (Lv 46)  
  Konstruk penjaga yang dibuat sebelum Ordo punya nama, dan masih menjalankan perintah pertamanya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient guardian construct older than the Order, weathered stone with moss, a faded carved face, still obeying its first command. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `juru_nyala_padam.webp` — **Juru Nyala Padam** (Lv 47)  
  Petugas yang bertugas menjaga api ritual tetap menyala, dan tidak pernah diberi tahu ritualnya sudah berhenti.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A ritual fire-keeper still tending a flame that went out long ago, in old ceremonial robes, holding tongs over cold ashes, devoted and lost. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_ordo.webp` — **Gema Ordo Pertama** (Lv 48)  
  Orang-orang yang menulis aturan pertama, masih membacakannya dengan suara yang sama.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. The first writers of the Order's rules, a group of pale robed figures holding one shared scroll, reading in the same voice, mouths moving together. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `pelita_padam_kuno.webp` — **Pelita Padam Kuno** (Lv 48)  
  Pelita yang dinyalakan di Kota Adiluhung sebelum ada Ordo yang menamainya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient Pelita lit before the Order existed: a tall figure of old faded golden light, crowned with a primitive clay lamp, calm and immense. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `hampa_adiluhung.webp` — **Hampa Adiluhung** (Lv 49)  
  Warga kota pertama, yang sudah delapan abad tidak punya nama untuk ditanya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A citizen of the first city, eight centuries without a name: an elegant ancient hollow in ruined royal-court clothing, face smoothed away. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_angin.webp` — **Penjaga Suar Angin** (Lv 49)  
  Konstruk penjaga Suar ke-4 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of pale stone and bronze, one element only: wind, swirling air and leaves circling its body, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_api.webp` — **Penjaga Suar Api** (Lv 49)  
  Konstruk penjaga Suar ke-1 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of dark stone and bronze, one element only: fire, flames pouring from its joints, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_bumi.webp` — **Penjaga Suar Bumi** (Lv 49)  
  Konstruk penjaga Suar ke-5 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of heavy rock and bronze, one element only: earth, boulders orbiting it, cracked ground, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_cahaya.webp` — **Penjaga Suar Cahaya** (Lv 49)  
  Konstruk penjaga Suar ke-6 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of white stone and gold, one element only: light, radiant beams from its chest, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_es.webp` — **Penjaga Suar Es** (Lv 49)  
  Konstruk penjaga Suar ke-2 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of blue stone and bronze, one element only: ice, frost and icicles on its limbs, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_kelam.webp` — **Penjaga Suar Kelam** (Lv 49)  
  Konstruk penjaga Suar ke-7 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of black stone and bronze, one element only: darkness, violet shadow leaking from its seams, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_petir.webp` — **Penjaga Suar Petir** (Lv 49)  
  Konstruk penjaga Suar ke-3 Kota Adiluhung, satu elemen, satu perintah, delapan abad.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. An ancient beacon guardian construct of grey stone and copper, one element only: lightning, arcs crackling between its horns, a single glowing sigil. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_party.webp` — **Gema Kalian** (Lv 50)  
  Kalian, sebagaimana Kabut mengingat kalian: sedikit lebih muda, dan tidak ragu sama sekali.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A party of four young adventurers remembered by the fog: slightly younger, fearless, their shapes made of pale mist with bright confident eyes. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `gema_penghitung.webp` — **Gema Penghitung** (Lv 50)  
  Sesuatu yang berdiri di tengah laut sambil menghitung, dan yang dihitungnya adalah berapa orang yang lewat dan berapa yang kembali.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. Something standing in the middle of a fog sea, counting: a tall thin figure with many fingers marking tallies in the air, faces of passers-by drifting around it. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `kabut_gelombang.webp` — **Gelombang Kabut** (Lv 50)  
  Kabut yang mengalir kembali ke Sumur, dan segala yang ikut di dalamnya.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A tidal wave of fog flowing back toward a great well, carrying faint objects and faces inside it, curling crest. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `penjaga_suar_kedelapan.webp` — **Penjaga Suar Kedelapan** (Lv 53)  
  Konstruk penjaga untuk Suar kedelapan. Tidak pernah ada Suar kedelapan.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. A guardian construct built for an eighth beacon that never existed: incomplete, parts missing, a blank sigil, standing guard over nothing. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
- [ ] `buruan_cacing_ibu_segmen.webp` — **Segmen Cacing Abu** (Lv 55)  
  Satu ruas tubuh yang cukup besar untuk berkelahi sendiri.
  ```
  Dark fantasy Nusantara creature, painterly digital painting, same style as a moody lantern-lit Indonesian night scene. One segment of a titanic ash worm, large enough to fight on its own: a thick armored ring of grey flesh with legs and embers glowing between plates. Single creature, full body, centered, three-quarter view. Plain very dark blue-black background (#0c0f14), soft warm lantern rim light, cool mist at the bottom. No text, no frame, no border. Square 1:1.
  ```
