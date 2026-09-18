# Pelita Terakhir — Dokumen Desain Game

> RPG teks turn-based bergaya JRPG klasik. Dibangun dengan Python, dimainkan di terminal.
> Target durasi: **2–4 jam** sekali tamat. Scope kecil-menengah, linear dengan satu kota hub.

---

## 0. Ringkasan & Keputusan Desain yang Perlu Persetujuan

Dokumen ini menetapkan beberapa arah tema/gaya. Semua bisa diganti tanpa membongkar sistem;
yang terikat ke tema hanya nama, flavor text, dan susunan elemen.

| Keputusan | Pilihan di dokumen ini | Alternatif kalau mau diganti |
|---|---|---|
| Nada cerita | Melankolis-hangat (dunia meredup, tapi fokus ke orang-orang kecil yang bertahan) | (a) lebih ringan/komedik ala JRPG 16-bit, (b) lebih gelap/tragis |
| Setting | Fantasi lembah terpencil bernuansa Nusantara (nama, flora, arsitektur) | (a) fantasi Eropa klasik, (b) steampunk |
| Sumber sihir | "Nyala" — cahaya yang dipelihara di lentera, berbahan bakar ingatan | Kristal elemen klasik |
| Ending | Satu ending utama + satu variasi kecil dari pilihan akhir | Ending tunggal saja (lebih mudah dibuat) |
| Bahasa in-game | Indonesia | Inggris, atau dua bahasa |

Kalau tidak ada keberatan, implementasi tahap berikutnya mengikuti tabel ini apa adanya.

---

## 1. Premis & Setting

### 1.1 Dunia: Lembah Larung

Lembah Larung adalah lembah luas yang dikelilingi pegunungan tak tertembus. Penduduknya tidak
tahu ada apa di balik gunung; bagi mereka, lembah *adalah* dunia. Di tengah lembah berdiri
**Mercusuar Langit**, menara batu putih setinggi awan yang selama berabad-abad memancarkan
**Nyala** — cahaya hangat yang menjaga lembah tetap terang, subur, dan waras.

Nyala bukan sekadar cahaya. Nyala adalah *ingatan yang dibakar*. Mercusuar dulu dinyalakan oleh
para **Pelita**: orang-orang yang secara sukarela menyerahkan ingatan hidupnya untuk menjadi bahan
bakar menara. Rahasia ini hanya diketahui segelintir orang di lingkaran istana.

### 1.2 Latar Waktu: Tahun ke-12 Musim Redup

Dua belas tahun lalu, Mercusuar padam tanpa penjelasan. Sejak itu, dari tepi lembah merayap
**Kabut Lupa**: kabut kelabu yang perlahan menghapus ingatan siapa pun yang berlama-lama di
dalamnya. Orang yang kehilangan seluruh ingatannya berubah menjadi **Hampa**: makhluk kosong
yang bergerak mengikuti sisa-sisa kebiasaan lama, dan menyerang apa pun yang masih "utuh".

Manusia bertahan di kantong-kantong cahaya: kota dan desa yang dikelilingi **lentera penjaga**
berisi sisa Nyala. Lentera-lentera itu makin redup setiap tahun. Tugas paling dihormati sekaligus
paling berbahaya di lembah adalah **Penyala**: orang yang berkeliling menjaga lentera tetap hidup.

Teknologi: setara abad pertengahan akhir. Ada roda gigi, pompa air, dan kaca, tapi tanpa mesiu.
Estetika: rumah panggung kayu, atap ijuk, jembatan bambu, batu andesit gelap, dan lentera perunggu
dengan ukiran sulur. Nama tempat dan orang memakai rasa Nusantara tanpa merujuk ke tempat nyata.

### 1.3 Konflik Utama

**Adipati Baskara**, wali kota ibukota sekaligus penguasa de facto lembah, ternyata *sengaja*
memadamkan Mercusuar. Ia mengetahui rahasia Pelita dan memutuskan bahwa harga menyalakan menara
(mengorbankan ingatan seseorang setiap beberapa dekade) terlalu mahal. Ia memilih membiarkan kabut
datang perlahan, sambil mencari cara lain yang tak kunjung ketemu. Dua belas tahun kemudian,
lembah sekarat dan Baskara semakin terpojok dan tertutup.

Protagonis, **Rimba**, seorang murid Penyala dari desa perbatasan, tanpa sengaja mewarisi
**Bara**: percikan terakhir Nyala asli yang ditinggalkan mentornya. Perjalanan Rimba adalah
perjalanan mengetahui *mengapa* menara padam, dan memutuskan apa yang mau dibayar untuk
menyalakannya kembali.

**Tema inti:** apa yang layak dikorbankan agar orang lain bisa mengingat? Kabut menghapus ingatan
secara paksa; Nyala meminta ingatan secara sukarela. Keduanya mengambil hal yang sama.

### 1.4 Nada & Contoh Narasi

Nada: melankolis tapi hangat. Dunia sedang meredup, tapi orang-orangnya masih bercanda, memasak,
dan bertengkar soal hal sepele. Humor muncul dari karakter, bukan dari lelucon keempat-dinding.

Contoh narasi pembuka (layar pertama game):

```
Lentera di gerbang timur berkedip dua kali, lalu tenang lagi.

Kau menghitung dalam hati. Tiga hari lalu, kedipannya hanya satu.

"Rimba! Jangan bengong, minyaknya tumpah!"

Pak Guntur menyodorkan kaleng perunggu tanpa menoleh. Tangannya yang
keriput tak pernah gemetar saat menuang. Tanganmu masih sering.

"Kalau lentera ini padam," katanya pelan, "bukan kabutnya yang
kutakutkan. Yang kutakutkan, orang-orang lupa kenapa dulu kita
menyalakannya."
```

Contoh dialog santai di kota hub:

```
Sela  : Kau tahu berapa harga sepotong tempe di kota sekarang?
Rimba : ...tiga keping?
Sela  : Delapan. DELAPAN. Aku pernah menjaga gerbang istana dan
        gajiku sebulan cuma cukup buat tempe dua minggu.
Lintang: Apa itu tempe?
Sela  : ...Oke, ini prioritas. Kita cari warung dulu.
```

---

## 2. Struktur Dunia

Progres bersifat **linear dengan hub**: lima area utama, dilalui berurutan, dengan ibukota
sebagai pusat kembali (toko, penginapan, side quest kecil). Tidak ada peta dunia terbuka;
perpindahan lewat menu pilihan lokasi.

### 2.1 Peta Progres

```
[1] Pelita Rendah & Hutan Kelabu
        │
        ▼
[2] Rawa Suar
        │
        ▼
[3] Ibukota Tengara  ◄──────────────┐  (hub: bisa kembali kapan saja
        │                           │   setelah pertama kali tiba)
        ▼                           │
[4] Tambang Kaca Ingatan ───────────┘
        │
        ▼
[5] Mercusuar Langit  (final dungeon, point of no return)
```

### 2.2 Rincian Area

#### Area 1 — Pelita Rendah & Hutan Kelabu (Prolog, ~25 menit, Lv 1–4)

- **Pelita Rendah**: desa perbatasan kecil, rumah Rimba. Lima bangunan: rumah Pak Guntur,
  warung, balai desa, gerbang timur, gerbang barat. Tutorial gerak, menu, dan pertarungan pertama.
- **Hutan Kelabu**: hutan tepi kabut, 4 "ruang" (screen) linear. Kabut tipis: setiap 10 giliran
  di dalam hutan, party terkena status *Lupa* ringan kecuali membawa lentera saku (item tutorial).
- **Kejadian kunci**: Pak Guntur masuk kabut mengejar seorang anak yang hilang dan tidak kembali.
  Rimba menemukan lentera Guntur tergeletak dengan Bara di dalamnya. Bara "menempel" ke Rimba.
- **Boss**: *Hampa Penjaga Hutan* (Hampa besar bekas penebang kayu). Mengajarkan mekanik kelemahan
  elemen dan Bara.
- **Party join**: Sela ditemukan terluka di hutan, bertarung bersama sejak boss.

#### Area 2 — Rawa Suar (~35 menit, Lv 4–8)

- Rawa berkabut dengan reruntuhan **Suar Lama**, menara sinyal kuno yang dulu meneruskan Nyala
  dari Mercusuar ke desa-desa. Enam ruang, dua di antaranya bercabang (opsional, peti harta).
- **Puzzle ringan**: tiga lentera rawa harus dinyalakan dalam urutan yang benar (petunjuk dari
  ukiran di reruntuhan) untuk membuka jalan ke inti Suar.
- **Kejadian kunci**: di inti Suar, party menemukan **Lintang**, gadis yang hidup sendirian di
  dalam kabut tanpa jadi Hampa. Ia hanya ingat namanya dan satu kalimat: "Bapak bilang tunggu
  di sini." Ia bisa menggunakan kabut sebagai sihir.
- **Boss**: *Raja Katak Lumpur*. Mengajarkan manajemen status (racun) dan pentingnya Petir.
- **Party join**: Lintang.

#### Area 3 — Ibukota Tengara (Hub, ~30 menit cerita + waktu bebas, Lv 8–11)

- Kota terbesar di lembah, di kaki Mercusuar. Tembok tinggi, lentera besar di setiap sudut,
  tapi separuh distrik luar sudah ditinggalkan. Lokasi: Pasar Bawah (toko senjata, zirah, item),
  Penginapan Lentera Merah, Balai Arsip, Gerbang Istana, dan **Lorong Bawah** (dungeon saluran air).
- **Kejadian kunci**: party mencoba menemui Adipati untuk melapor soal Guntur, ditolak.
  Sela terpaksa membuka masa lalunya: ia mantan Pengawal Mahkota yang desersi setelah menolak
  perintah "mengamankan" warga yang mempertanyakan Adipati. Mantan kaptennya, **Kapten Rangga**,
  masih memburunya.
- **Dungeon**: Lorong Bawah, jalur rahasia menuju Balai Arsip istana. Lima ruang, mekanik air
  pasang-surut (beberapa jalur hanya terbuka setelah menarik tuas). Di Arsip, party menemukan
  catatan Pelita: daftar nama orang yang "dibakar", termasuk nama ayah Lintang, dan catatan bahwa
  Guntur adalah **Penjaga Mercusuar terakhir**.
- **Boss**: *Kapten Rangga* (duel manusia pertama; agresif, memakai taktik "tandai lalu tebas").
- **Side quest (opsional, 3 buah)**: mengantar surat ke distrik terbengkalai, mencari kucing
  penginapan di Lorong Bawah, mengalahkan Hampa di pasar malam. Hadiah: aksesori & Serpihan Ingatan.

#### Area 4 — Tambang Kaca Ingatan (~35 menit, Lv 11–15)

- Tambang di lereng utara, tempat ditambangnya **Kaca Ingatan**: mineral bening yang bisa
  menyimpan Nyala. Semua lentera di lembah memakai kaca dari sini. Tambang ditutup 12 tahun lalu,
  tepat saat menara padam.
- Tujuan: mengambil **Kaca Inti**, satu-satunya wadah yang cukup besar untuk menampung Bara
  agar bisa dibawa ke puncak Mercusuar.
- Delapan ruang, struktur vertikal (turun lewat lift tambang rusak, naik lewat tangga darurat).
  Kristal di dinding memutar potongan ingatan penambang saat disentuh: lore opsional.
- **Kejadian kunci**: Lintang mendengar suara ayahnya dari kristal. Ia ingat: ayahnya
  adalah Pelita terakhir yang *dibatalkan*: Adipati menghentikan ritual di tengah jalan, sehingga
  ayahnya tidak jadi bahan bakar tapi juga tidak kembali utuh. Ia menjadi Hampa pertama.
  Lintang dibawa ayahnya ke Suar Lama sebelum kehilangan sisa dirinya.
- **Boss**: *Penambang Raksasa Terlupa* (Hampa gabungan beberapa penambang, tubuh berkerak kristal).
  Mekanik: kristal di punggung menyerap satu elemen yang berganti tiap 3 giliran.

#### Area 5 — Mercusuar Langit (Final, ~30–40 menit, Lv 15–20)

- Menara 7 lantai (lantai 1–5 eksplorasi, 6 boss penjaga, 7 final). Setiap lantai bertema
  satu "kenangan lembah": panen, pernikahan, pemakaman, perang lama, dan lantai kosong.
- **Point of no return** ditandai jelas; ada peti penyimpanan dan pedagang keliling di lantai 1.
- **Mid-boss (lantai 6)**: *Penjaga Mercusuar*, konstruk batu yang dulu dikendalikan Guntur.
  Sekarang liar. Di dalamnya ada sisa kesadaran Guntur yang sempat berbicara setelah kalah:
  ia masuk kabut *dengan sengaja* karena ingin menjadi Pelita berikutnya, tapi Adipati mengunci menara.
- **Final (lantai 7)**: Adipati Baskara menunggu. Dialog konfrontasi, lalu pertarungan dua fase
  (lihat §6.3). Setelah kalah, Baskara menyerahkan kunci ruang inti.
- **Pilihan akhir** (memengaruhi epilog, bukan gameplay):
  1. **Rimba menyalakan Mercusuar dengan Bara** (ingatan Guntur). Lembah terang lagi, Guntur
     hilang sepenuhnya. Epilog: Rimba menjadi Penjaga baru, tahu suatu hari harus ada Pelita berikutnya.
  2. **Rimba membagi Bara ke semua lentera desa**, bukan ke menara. Kabut tertahan tapi tidak
     mundur. Epilog: lembah hidup dalam kantong-kantong cahaya, tapi tidak ada lagi yang harus dibakar.
     Lintang menjadi Penyala keliling.
  Keduanya sah; game tidak menghakimi.

### 2.3 Anggaran Waktu

| Segmen | Estimasi |
|---|---|
| Area 1 | 25 mnt |
| Area 2 | 35 mnt |
| Area 3 (cerita + Lorong Bawah) | 30 mnt |
| Area 4 | 35 mnt |
| Area 5 | 35 mnt |
| Side quest, grinding, belanja | 20–60 mnt |
| **Total** | **~3 jam (2 jam 40 mnt – 3 jam 40 mnt)** |

---

## 3. Karakter

### 3.1 Protagonis — Rimba (17 th)

- **Peran naratif**: murid Penyala, pewaris Bara. Tipe protagonis yang *bertanya*, bukan yang
  selalu punya jawaban. Sopan ke orang tua, keras kepala soal janji.
- **Peran gameplay**: all-rounder condong ke serangan Api/Cahaya. Punya sumber daya unik
  **Bara** (lihat §4.5) yang membuka jurus pamungkas party.
- **Senjata**: tongkat lentera (dipukulkan, bisa dinyalakan untuk serangan elemen).
- **Arc**: dari "aku cuma harus menjaga lentera tetap nyala" ke "aku harus memutuskan apa
  yang boleh dibakar."

Contoh suara Rimba:

```
Rimba : Pak Guntur selalu bilang, lentera itu bukan buat mengusir
        kabut. Lentera itu buat orang tahu jalan pulang.
Sela  : Dan kalau tidak ada yang pulang?
Rimba : ...Tetap dinyalakan. Siapa tahu.
```

### 3.2 Party Member — Sela (24 th)

- **Naratif**: mantan Pengawal Mahkota yang desersi. Blak-blakan, sinis di permukaan, sangat
  protektif. Merasa bersalah karena diam terlalu lama sebelum melawan perintah.
- **Gameplay**: **tank / fisik berat**. HP dan DEF tertinggi. Skill *Pasang Badan* (tarik semua
  serangan satu giliran), *Tebas Berat*, *Teriakan Provokasi*. Tidak punya sihir elemen; lemah
  terhadap musuh yang tahan fisik, mendorong pemain memanfaatkan anggota lain.
- **Senjata**: pedang lebar & perisai bundar.
- **Arc**: menghadapi Kapten Rangga, mantan atasannya, dan menerima bahwa "melawan perintah"
  bukan pengkhianatan.

### 3.3 Party Member — Lintang (15 th)

- **Naratif**: gadis yang bertahan di dalam kabut tanpa jadi Hampa. Ingatan bolong-bolong,
  polos soal hal sehari-hari (tidak tahu tempe), tapi tajam soal hal besar. Kabut "mengenalinya".
- **Gameplay**: **mage / debuffer**. MAG dan AGI tinggi, HP terendah. Menguasai elemen **Es**,
  **Petir**, dan **Kelam** (kabut). Satu-satunya yang bisa menyerang musuh tipe Pelita Padam
  di Mercusuar yang menyerap Cahaya. Skill debuff: *Selimut Kabut* (turunkan ATK musuh),
  *Bisikan Lupa* (status Lupa).
- **Senjata**: lentera kecil retak (fokus sihir).
- **Arc**: menemukan siapa ayahnya, dan memilih untuk mengingat meski menyakitkan.

### 3.4 Party Member Opsional — Pak Guntur (hanya di prolog, ~15 menit)

Tutorial companion di Area 1 sebelum hilang. Level 10 saat party masih level 1, sengaja
overpowered supaya pemain merasakan "seperti apa Penyala sejati", lalu kehilangannya terasa.
Menghilang dari party setelah masuk kabut. Skill: *Nyala Penjaga* (heal seluruh party), *Pukulan Lentera*.

### 3.5 Antagonis Utama — Adipati Baskara (58 th)

- **Naratif**: bukan penjahat gila. Ia orang yang membuat keputusan mengerikan dengan alasan
  yang bisa dimengerti, lalu terjebak mempertahankannya selama 12 tahun. Semakin lembah sekarat,
  semakin ia merasa harus terus benar. Bicara pelan, tidak pernah berteriak.
- **Motivasi**: "Menara ini memakan orang. Aku lebih rela dunia kami habis pelan-pelan
  dengan tangan bersih daripada terang dengan tangan berdarah."
- **Gameplay**: boss dua fase (§6.3). Fase 1 manusia dengan tongkat kekuasaan dan penjaga.
  Fase 2: kabut yang selama ini ia tahan di dalam menara menelan dan membentuknya menjadi
  **Kelam Berwajah**: Hampa raksasa dengan wajah Baskara.

Contoh dialog konfrontasi:

```
Baskara: Kau membawa Bara Guntur. Berarti kau sudah tahu apa isinya.
Rimba  : Ingatan Pak Guntur.
Baskara: Dan kau tetap naik ke sini untuk membakarnya. Kalau begitu
         kita tidak berbeda, Nak. Aku hanya lebih dulu lelah.
Lintang: ...Bapakku tidak pernah selesai dibakar. Kau berhenti di
         tengah. Itu bukan tangan bersih. Itu tangan gemetar.
```

### 3.6 Antagonis Sekunder — Kapten Rangga (35 th)

Kapten Pengawal Mahkota, mantan atasan Sela. Loyal ke Adipati karena percaya "tanpa perintah,
lembah bubar". Mid-boss Area 3. Tidak jahat; setelah kalah, ia membiarkan party lewat dan
memilih tetap menjaga kota. Muncul lagi di epilog.

---

## 4. Sistem Combat

### 4.1 Prinsip

- **Turn-based murni**, urutan giliran ditentukan AGI (bukan ATB). Semua aksi dipilih lewat menu teks.
- Party maksimal **3 anggota aktif** (Rimba, Sela, Lintang). Musuh 1–4 per encounter.
- Encounter **acak** saat berpindah ruang di dungeon (peluang 35–50% per perpindahan, dengan
  jaminan tidak ada dua encounter berturut-turut dalam 2 langkah). Boss selalu fixed.
- Durasi target satu pertarungan biasa: **3–5 giliran** (sekitar 30–60 detik). Boss: 8–15 giliran.
- Pertarungan menekankan **kelemahan elemen** dan **status**, bukan angka mentah.

### 4.2 Stat

| Stat | Singkatan | Fungsi |
|---|---|---|
| Health Point | HP | Nyawa. 0 = pingsan. Semua pingsan = game over (kembali ke save terakhir). |
| Mana Point | MP | Bahan bakar skill. Pulih di penginapan, item, dan sedikit tiap naik level. |
| Serangan | ATK | Kekuatan serangan fisik. |
| Pertahanan | DEF | Mengurangi damage fisik. |
| Sihir | MAG | Kekuatan skill sihir/elemen. |
| Ketahanan | RES | Mengurangi damage sihir. |
| Kelincahan | AGI | Urutan giliran, peluang menghindar. |
| Keberuntungan | LCK | Peluang kritikal, peluang status masuk/menghindar status. |

Stat dasar level 1 dan pertumbuhan per level:

| Karakter | HP | MP | ATK | DEF | MAG | RES | AGI | LCK | Pertumbuhan/level |
|---|---|---|---|---|---|---|---|---|---|
| Rimba | 45 | 12 | 8 | 6 | 7 | 6 | 7 | 6 | HP+7, MP+2, ATK+1.6, DEF+1.2, MAG+1.4, RES+1.2, AGI+1.2, LCK+0.8 |
| Sela | 60 | 6 | 10 | 9 | 3 | 5 | 5 | 4 | HP+9, MP+1, ATK+1.9, DEF+1.8, MAG+0.4, RES+1.0, AGI+0.8, LCK+0.6 |
| Lintang | 34 | 18 | 4 | 4 | 10 | 8 | 9 | 7 | HP+5, MP+3, ATK+0.6, DEF+0.8, MAG+2.1, RES+1.6, AGI+1.6, LCK+1.0 |

(Pertumbuhan pecahan diakumulasi lalu dibulatkan ke bawah, supaya kurva halus tanpa RNG.)

### 4.3 Aksi per Giliran

1. **Serang** — serangan fisik dasar, gratis, elemen Fisik (atau elemen senjata kalau ada).
2. **Skill** — pilih dari daftar skill karakter, biaya MP.
3. **Item** — pakai item dari inventori (tidak habiskan MP).
4. **Jaga** — DEF & RES ×1.5 sampai giliran berikutnya, pulihkan 5% MP, dan **+1 Bara** (Rimba saja).
5. **Kabur** — hanya di encounter acak. Peluang = 50% + (AGI rata-rata party − AGI rata-rata musuh) × 3%, dibatasi 20–90%.

### 4.4 Elemen & Kelemahan

Enam elemen serangan:

| Elemen | Sumber utama | Catatan |
|---|---|---|
| **Fisik** | Serang dasar, skill Sela | Beberapa musuh berzirah tahan Fisik. |
| **Api** | Rimba | Melawan tumbuhan, es, kabut tipis. Bisa memicu *Bakar*. |
| **Es** | Lintang | Melawan makhluk rawa & tambang. Bisa memicu *Beku* (lewati 1 giliran, peluang rendah). |
| **Petir** | Lintang | Melawan konstruk logam & makhluk air. |
| **Cahaya** | Rimba (Bara) | Melawan Hampa & makhluk kabut. Diserap oleh Pelita Padam. |
| **Kelam** | Lintang | Melawan Pelita Padam & konstruk Nyala. Diserap oleh Hampa. |

Pengali afinitas:

| Afinitas | Pengali | Efek tambahan |
|---|---|---|
| Lemah | ×1.5 | Musuh terkena **Goyah**: aksinya di giliran berikutnya dipilih acak dari aksi paling lemah, dan Rimba mendapat **+1 Bara** |
| Normal | ×1.0 | — |
| Tahan | ×0.5 | — |
| Imun | ×0 | Pesan "Tidak berpengaruh." |
| Serap | −1.0 (menyembuhkan musuh) | Pesan peringatan warna berbeda pertama kali terjadi |

Kelemahan musuh **tersembunyi sampai dipukul** dengan elemen yang tepat, lalu dicatat permanen
di bestiary in-game (menu "Catatan Penyala"). Tidak ada skill "analisis", supaya pemain
bereksperimen. Musuh yang sudah dicatat menampilkan ikon kelemahan di layar pertarungan.

### 4.5 Bara (Sumber Daya Party)

- Meteran bersama **0–5 Bara**, dipegang Rimba, di-reset ke 0 di awal setiap pertarungan.
- Cara mendapat: memukul kelemahan (+1), Rimba **Jaga** (+1), party member pingsan (+2, "nyala dari amarah").
- Cara memakai:
  - **Nyala Pamungkas** (3 Bara): Rimba, serangan Cahaya ke semua musuh, kekuatan 2.5, tidak bisa dihindari.
  - **Jurus Ganda** (4 Bara): dua karakter hidup melakukan serangan gabungan. Kombinasinya tetap:
    - Rimba+Sela: *Tebas Berapi* — Fisik+Api, satu target, kekuatan 3.0
    - Rimba+Lintang: *Fajar Kelabu* — Cahaya+Kelam, semua musuh, kekuatan 2.0, abaikan afinitas Serap
    - Sela+Lintang: *Badai Perisai* — Petir, semua musuh, kekuatan 1.8 + Goyah
  - **Nyala Pulih** (2 Bara): heal semua party 30% HP + hapus semua status buruk.
- Kalau Rimba pingsan, Bara membeku (tidak bertambah, tidak bisa dipakai) sampai ia dibangunkan.

### 4.6 Formula Damage

Semua pembagian dibulatkan ke bawah; damage minimum 1 kecuali afinitas Imun/Serap.

**Serangan fisik (Serang & skill fisik):**

```
dasar   = ATK_penyerang * 2 - DEF_target        (min 1)
damage  = dasar * kekuatan_skill * afinitas * kritikal * jaga * acak
```

**Serangan sihir (skill elemen):**

```
dasar   = MAG_penyerang * 2 - RES_target        (min 1)
damage  = dasar * kekuatan_skill * afinitas * kritikal * jaga * acak
```

Keterangan pengali:

| Pengali | Nilai |
|---|---|
| `kekuatan_skill` | Serang dasar = 1.0. Skill 0.8–3.0 (lihat tabel skill). |
| `afinitas` | 1.5 / 1.0 / 0.5 / 0 / −1.0 |
| `kritikal` | 1.5 kalau kena kritikal, 1.0 kalau tidak. Peluang kritikal = 5% + LCK_penyerang × 0.5%, maks 30%. |
| `jaga` | 1/1.5 kalau target sedang Jaga (dihitung lewat DEF/RES, bukan pengali terpisah; tabel ini untuk kejelasan). |
| `acak` | Seragam 0.90–1.10 |

**Peluang kena (fisik saja; sihir selalu kena kecuali Imun):**

```
peluang_kena = 92% + (AGI_penyerang - AGI_target) * 1.5%     dibatasi 60%–100%
```

**Penyembuhan:**

```
heal = MAG_pengguna * kekuatan_skill + nilai_dasar_skill
```

Contoh angka kalibrasi (Rimba Lv 5, ATK 14, memukul Serigala Kabut DEF 6 dengan Serang dasar):
dasar = 28 − 6 = 22, acak ~1.0 → **22 damage**, HP serigala 60, jadi ~3 pukulan. Dengan skill
*Sulut* (Api, kekuatan 1.4, kelemahan serigala) dari MAG 13 vs RES 4: dasar = 22, × 1.4 × 1.5 =
**46 damage**, jadi 2 kali. Ini rasio target: menggunakan kelemahan mempercepat pertarungan ~2×.

### 4.7 Status Efek

| Status | Efek | Durasi | Sumber umum |
|---|---|---|---|
| **Racun** | Kehilangan 8% HP maks tiap akhir giliran | 4 giliran | Lumut Berjalan, Katak Rawa |
| **Bakar** | Kehilangan 5% HP maks tiap giliran, DEF −20% | 3 giliran | Skill Api |
| **Beku** | Lewati 1 giliran | 1 giliran | Skill Es (peluang 20%) |
| **Lelah** | ATK & MAG −30% | 3 giliran | Selimut Kabut, beberapa musuh |
| **Goyah** | Aksi berikutnya acak & lemah; damage masuk ×1.2 | Sampai giliran berikutnya | Pukulan kelemahan |
| **Lupa** | Tidak bisa memakai Skill (hanya Serang/Item/Jaga) | 2 giliran | Hampa, kabut tanpa lentera |
| **Tidur** | Lewati giliran, bangun kalau dipukul | 3 giliran | Kelelawar Kristal |
| **Provokasi** | Semua serangan musuh single-target diarahkan ke Sela | 1 giliran | Skill Sela |

Peluang status masuk = peluang dasar skill × (1 − LCK_target × 1%). Boss punya daftar imunitas sendiri.

### 4.8 Daftar Skill (per karakter, level unlock)

**Rimba**

| Lv | Skill | MP | Elemen | Kekuatan | Target | Catatan |
|---|---|---|---|---|---|---|
| 1 | Sulut | 3 | Api | 1.4 | Satu | 30% Bakar |
| 3 | Sinar Lentera | 4 | Cahaya | 1.3 | Satu | — |
| 6 | Kobar | 7 | Api | 1.2 | Semua | 20% Bakar |
| 9 | Tumbuk Nyala | 5 | Fisik | 1.6 | Satu | Memakai ATK, elemen senjata |
| 12 | Cahaya Penunjuk | 6 | — | — | Satu kawan | Sembuhkan Lupa & Tidur + heal kecil |
| 15 | Fajar | 12 | Cahaya | 1.8 | Semua | — |
| 18 | Nyala Terakhir | 15 | Api+Cahaya | 2.4 | Satu | Damage ×1.5 lagi kalau HP Rimba < 30% |

**Sela**

| Lv | Skill | MP | Elemen | Kekuatan | Target | Catatan |
|---|---|---|---|---|---|---|
| 1 | Tebas Berat | 3 | Fisik | 1.6 | Satu | Peluang kena −10% |
| 4 | Pasang Badan | 2 | — | — | Diri | Status Provokasi + DEF ×1.5 satu giliran |
| 7 | Teriakan Provokasi | 4 | — | — | Semua musuh | Provokasi + 40% Lelah pada musuh |
| 10 | Bantingan Perisai | 5 | Fisik | 1.3 | Satu | 50% Goyah tanpa syarat elemen |
| 13 | Tebas Menyapu | 8 | Fisik | 1.1 | Semua | — |
| 16 | Tumbal Baja | 0 | — | — | Diri | Habiskan 25% HP: ATK ×1.5 selama 3 giliran |
| 19 | Sumpah Pengawal | 10 | Fisik | 2.6 | Satu | Damage ×2 kalau ada kawan pingsan |

**Lintang**

| Lv | Skill | MP | Elemen | Kekuatan | Target | Catatan |
|---|---|---|---|---|---|---|
| 4 | Serpih Es | 3 | Es | 1.4 | Satu | 20% Beku |
| 4 | Selimut Kabut | 4 | — | — | Semua musuh | 60% Lelah |
| 6 | Kilat Kecil | 4 | Petir | 1.4 | Satu | — |
| 8 | Bisikan Lupa | 5 | Kelam | 0.8 | Satu | 70% Lupa |
| 10 | Rawat Kabut | 5 | — | — | Satu kawan | Heal: MAG × 2 + 20 |
| 12 | Badai Es | 9 | Es | 1.2 | Semua | 10% Beku |
| 14 | Petir Bercabang | 9 | Petir | 1.3 | Semua | — |
| 16 | Tirai Kelam | 8 | Kelam | 1.2 | Semua | Serap: heal Lintang 25% dari damage |
| 19 | Malam Pengingat | 14 | Kelam | 2.2 | Satu | Abaikan RES target |

### 4.9 Perilaku AI Musuh

Musuh biasa memakai **tabel bobot**: tiap aksi punya bobot, dipilih acak berbobot, dengan
beberapa aturan pemicu (misal: "kalau HP < 30%, bobot Kabur/Heal naik"). Boss memakai
**skrip fase**: urutan aksi tetap per fase yang berganti di ambang HP tertentu. Ini cukup
untuk terasa "cerdas" tanpa perlu sistem AI kompleks.

---

## 5. Sistem Progresi

### 5.1 Leveling

- Level maks **25**. Party tamat normal di **Lv 18–20**. Grinding tidak wajib kalau pemain
  memakai kelemahan dan tidak kabur dari semua encounter.
- **XP dibagi rata** ke semua anggota party termasuk yang pingsan (menghindari siklus "yang lemah makin tertinggal").
- Anggota yang bergabung belakangan masuk dengan level = level Rimba − 1.
- Kurva XP: `XP_ke_level_n = 20 * n^2` (Lv 2 = 80, Lv 10 = 2000, Lv 20 = 8000). Total sampai
  Lv 20 ≈ 57.000 XP. Encounter biasa memberi 15–350 XP tergantung area; boss 2–4× encounter biasa.
- Tiap naik level: stat naik sesuai tabel §4.2, HP/MP pulih 25%, skill baru diumumkan.

### 5.2 Equipment

Tiga slot per karakter: **Senjata**, **Zirah**, **Aksesori**. Tiap karakter punya tipe senjata
sendiri (tidak bisa saling tukar). Zirah dan aksesori bebas.

Contoh progresi senjata (satu jalur per karakter, dibeli di toko atau ditemukan):

| Tahap | Rimba (Tongkat Lentera) | Sela (Pedang) | Lintang (Lentera Fokus) | Dapat di |
|---|---|---|---|---|
| 1 | Tongkat Kayu Jati (ATK+3) | Pedang Latihan (ATK+5) | Lentera Retak (MAG+4) | Awal |
| 2 | Tongkat Perunggu (ATK+7, MAG+2) | Pedang Pengawal (ATK+10) | Lentera Rawa (MAG+8, +Es) | Rawa / Toko Tengara |
| 3 | Tongkat Kaca (ATK+11, MAG+6, elemen Api) | Pedang Besi Tambang (ATK+16) | Lentera Kaca (MAG+14) | Toko Tengara (setelah Lorong Bawah) / Tambang |
| 4 | **Tongkat Guntur** (ATK+16, MAG+10, Cahaya, +1 Bara awal) | **Pedang Sumpah** (ATK+24, LCK+5) | **Lentera Bapak** (MAG+22, Kelam, MP biaya −20%) | Peti tersembunyi Mercusuar / side quest / cerita |

Zirah: 5 tingkat (Kain, Kulit, Rantai, Kaca Lapis, Jubah Penyala) dengan DEF/RES bertahap,
beberapa dengan resistensi elemen. Aksesori (~10 jenis): Cincin Anti-Racun, Gelang Kilat (AGI+4),
Jimat Lentera (imun Lupa), Kalung Bara (+1 Bara di awal pertarungan), dsb.

### 5.3 Item Konsumsi

| Item | Efek | Harga |
|---|---|---|
| Ramuan Daun | HP +40 | 15 |
| Ramuan Akar | HP +120 | 45 |
| Tetes Nyala | MP +20 | 30 |
| Minyak Lentera | Tolak Lupa 20 giliran di area kabut; wajib untuk eksplorasi | 10 |
| Penawar | Sembuhkan Racun/Bakar | 12 |
| Garam Bangun | Sembuhkan Tidur/Lupa | 12 |
| Abu Fajar | Bangunkan kawan pingsan, HP 30% | 80 |
| Bubuk Petir / Es / Api | Serangan elemen kekuatan 1.2, siapa pun bisa pakai | 25 |
| Jimat Kabur | Kabur pasti berhasil | 40 |

Uang: **Keping** (keping perunggu). Diperoleh dari pertarungan dan menjual barang.

### 5.4 Serpihan Ingatan (Collectible)

Sebanyak **12 Serpihan** tersebar di dunia (peti tersembunyi, side quest, boss). Diserahkan ke
**Tukang Kaca** di Ibukota Tengara, tiap 3 Serpihan bisa ditukar satu **peningkatan permanen**
yang dipilih pemain: HP maks +10% untuk satu karakter, atau +1 Bara maks (hanya sekali), atau
membuka satu skill tambahan. Ini adalah "reward eksplorasi" tanpa memaksa 100% completion.

### 5.5 Sumber Kekuatan Pemain (ringkasan)

1. **Level** — pertumbuhan stat & skill baru (sumber utama, otomatis).
2. **Equipment** — lompatan kekuatan di tiap kota/area (membuat uang berarti).
3. **Pengetahuan** — kelemahan musuh yang dicatat & dipahami (sumber "gratis" yang membedakan
   pemain yang memperhatikan).
4. **Serpihan Ingatan** — peningkatan permanen dari eksplorasi opsional.
5. **Komposisi & Bara** — memilih kapan menabung Bara untuk Jurus Ganda vs memakai Nyala Pulih.

### 5.6 Save & Kematian

- Save di **lentera penjaga** (titik save eksplisit, ada di tiap area 2–3 buah) dan otomatis
  saat masuk kota. Save = file JSON tunggal, 3 slot.
- Kalah = kembali ke save terakhir. Tidak ada penalti tambahan; ini game cerita, bukan roguelike.

---

## 6. Bestiary

### 6.1 Musuh Biasa

| # | Nama | Area | HP | Lemah | Tahan/Serap | Role gameplay | Deskripsi |
|---|---|---|---|---|---|---|---|
| 1 | **Kunang Kelam** | Hutan Kelabu | 18 | Cahaya | Serap Kelam | *Swarm/tutorial.* Muncul 3–4 sekaligus, damage kecil. Mengajarkan serangan area & kelemahan. | Kunang-kunang yang cahayanya terbalik: mengeluarkan gelap. Berkerumun di sekitar lentera yang hampir padam. |
| 2 | **Serigala Kabut** | Hutan, Rawa | 60 | Api | Tahan Es | *Glass cannon cepat.* AGI tinggi, bergerak duluan, sering menyerang Lintang. Mengajarkan Pasang Badan Sela. | Serigala dengan bulu seperti asap. Menggigit lalu mundur ke kabut. |
| 3 | **Lumut Berjalan** | Hutan, Rawa | 85 | Api | Tahan Fisik, Tahan Es | *Tank pelan + status.* DEF tinggi, menyemburkan Racun. Menghukum pemain yang hanya pakai Serang. | Gundukan lumut dan akar yang dulu tunggul pohon. Bergerak hanya kalau tak ada yang melihat. |
| 4 | **Hampa Pengembara** | Semua area | 70 (+level scaling) | Cahaya | Serap Kelam | *Musuh ikonik / status.* Menyerang dengan *Sentuhan Lupa* (status Lupa). Muncul sepanjang game dengan varian (Petani, Pedagang, Prajurit). | Manusia yang ingatannya habis. Masih mengulang gerak pekerjaan lama: mencangkul udara, menawar ke kosong. Tidak menyerang karena benci, tapi karena tak ingat cara berhenti. |
| 5 | **Katak Rawa Bengkak** | Rawa Suar | 110 | Petir | Tahan Api, Tahan Es | *Tank + area.* Serangan *Lompatan Lumpur* ke semua, peluang Racun. Mengajarkan Petir Lintang. | Katak seukuran gerobak yang menelan lentera rawa. Perutnya berpendar lemah. |
| 6 | **Pengawal Karat** | Lorong Bawah, Mercusuar | 140 | Petir | Tahan Fisik, Imun Racun/Lupa | *Anti-fisik.* Sela hampir tidak berguna menyerang; ia harus jadi tank sementara Lintang membunuh. | Zirah pengawal kosong yang bergerak sendiri, digerakkan sisa Nyala yang tersesat. Berderit setiap melangkah. |
| 7 | **Kelelawar Kristal** | Tambang | 55 | Petir | Tahan Kelam | *Evasif + pengganggu.* AGI sangat tinggi, serangannya menguras MP dan bisa menyebabkan Tidur. Mendorong pemain pakai skill area / Bantingan Perisai (Goyah). | Kelelawar yang sayapnya tumbuh kaca ingatan. Suaranya terdengar seperti bisikan orang yang kau kenal. |
| 8 | **Penambang Terlupa** | Tambang | 160 | Es | Tahan Api | *Hard hitter.* ATK tinggi, serangan *Ayunan Beliung* satu target damage besar; pelan. Mengajarkan Jaga & manajemen HP. | Hampa bertubuh besar, punggung berkerak kristal. Masih mengayunkan beliung ke dinding yang sudah tidak ada. |
| 9 | **Pelita Padam** | Mercusuar | 120 | Kelam | **Serap Cahaya**, Tahan Api | *Pembalik aturan.* Satu-satunya musuh yang dilawan dengan Kelam. Menghukum pemain yang autopilot Nyala Pamungkas. | Sisa Pelita lama: sosok cahaya redup berbentuk manusia. Kalau diberi cahaya, ia menyerapnya dengan lapar dan makin kuat. |
| 10 | **Bayang Arsip** | Lorong Bawah, Mercusuar | 90 | Api | Tahan Petir, Tahan Es | *Support musuh.* Tidak menyerang kuat, tapi memberi buff ATK ke musuh lain dan menyembuhkan. Prioritas target. | Tumpukan gulungan dan tinta yang bergerak. Membacakan nama-nama Pelita tanpa henti. |

### 6.2 Boss

| Boss | Area | HP | Lemah | Mekanik utama |
|---|---|---|---|---|
| **Hampa Penjaga Hutan** | Area 1 | 220 | Cahaya, Api | Tutorial boss. Tiap 3 giliran memanggil 2 Kunang Kelam. Pola: Serang, Serang, *Raung Lupa* (Lupa ke semua). |
| **Raja Katak Lumpur** | Area 2 | 480 | Petir | Muntahkan Racun ke semua tiap 4 giliran; saat HP < 50% menelan satu party member (hilang 2 giliran, keluar kalau boss di-Goyah). |
| **Kapten Rangga** | Area 3 | 650 | — (manusia, semua normal) | Duel taktis. *Tandai*: memilih satu target, giliran berikutnya *Tebas Eksekusi* damage ×3 ke target itu. Pasang Badan Sela adalah jawabannya. Fase 2 (HP<40%): Provokasi imun, dua serangan per giliran. |
| **Penambang Raksasa Terlupa** | Area 4 | 900 | Berganti | Kristal punggung menyerap satu elemen, berganti tiap 3 giliran (diumumkan). Kelemahan = elemen "lawan" dari yang diserap (Api↔Es, Petir↔Fisik, Cahaya↔Kelam). |
| **Penjaga Mercusuar** | Area 5 lt.6 | 1100 | Petir, Kelam | Konstruk. Tiap 2 giliran mengisi *Nyala Meriam* (damage besar area giliran berikutnya, bisa dibatalkan dengan Goyah). Memanggil 1 Pelita Padam saat HP < 50%. |
| **Adipati Baskara** (Fase 1) | Area 5 lt.7 | 700 | — | Manusia + 2 Pengawal Karat. Skill *Titah*: paksa satu party member Lupa 3 giliran. Sela harus tank, Lintang bunuh pengawal dengan Petir. |
| **Kelam Berwajah** (Fase 2) | Area 5 lt.7 | 1600 | Cahaya (fase A), Kelam (fase B, bergantian tiap 4 giliran) | Bergantian "menjadi kabut" (lemah Cahaya, serap Kelam) dan "menjadi Nyala curian" (lemah Kelam, serap Cahaya). Mengharuskan Rimba dan Lintang saling bergantian jadi damage dealer, dengan Jurus Ganda *Fajar Kelabu* sebagai jawaban universal (abaikan Serap). Serangan pamungkas *Padamkan* di HP < 25%: semua HP party jadi 1 (tidak membunuh), lalu giliran bebas untuk pemain: momen untuk Nyala Pulih. |

### 6.3 Filosofi Bestiary

Setiap musuh biasa punya **satu pelajaran** (kelemahan, status, target priority, atau pembalikan
aturan), dan setiap boss **menguji pelajaran dari areanya** ditambah satu mekanik baru. Tidak ada
musuh yang murni "kantong HP".

---

## 7. Antarmuka Teks (Gambaran Awal)

Bukan bagian sistem inti, tapi menentukan rasa. Contoh layar pertarungan target:

```
════════════════════════════════════════════════════════════
 RAWA SUAR — Inti Suar Lama
────────────────────────────────────────────────────────────
 Serigala Kabut  A   [██████░░░░]  ~ lemah: Api
 Lumut Berjalan  B   [██████████]  ~ lemah: ?
────────────────────────────────────────────────────────────
 Rimba    HP  62/ 71   MP 11/ 18   Bara ◆◆◇◇◇
 Sela     HP  90/ 96   MP  4/  9   [Provokasi]
 Lintang  HP  31/ 44   MP 20/ 27   [Racun]
────────────────────────────────────────────────────────────
 Giliran Rimba.
  1) Serang   2) Skill   3) Item   4) Jaga   5) Bara
> _
════════════════════════════════════════════════════════════
```

Prinsip: satu layar = satu keputusan; tidak ada informasi yang butuh scroll ke atas.

---

## 8. Yang Sengaja TIDAK Dimasukkan (Scope Guard)

- Tidak ada crafting, tidak ada sistem pekerjaan/job, tidak ada romance.
- Tidak ada peta dunia terbuka atau backtracking wajib selain hub.
- Tidak ada party lebih dari 3 karakter aktif atau karakter opsional keempat.
- Tidak ada minigame; puzzle dibatasi pada urutan/tuas sederhana.
- Tidak ada New Game+ di rilis pertama (bisa ditambah kalau ada waktu).

---

## 9. Langkah Berikutnya (setelah dokumen disetujui)

1. Konfirmasi tabel keputusan di §0.
2. Tulis rancangan arsitektur kode (modul: `combat`, `world`, `party`, `data/`, `ui`) dengan
   data musuh/skill/item sebagai file data (JSON/YAML) agar angka mudah dikalibrasi.
3. Prototipe pertarungan tunggal dengan formula §4.6 dan uji rasio "2–3 pukulan per musuh biasa".
4. Baru setelah itu: cerita & area, mulai dari Area 1.
