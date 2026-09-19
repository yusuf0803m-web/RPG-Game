# Pelita Terakhir — Dokumen Desain Game (v2, edisi 20 jam)

> RPG teks turn-based bergaya JRPG klasik. Dibangun dengan Python, dimainkan di terminal.
> Target durasi: **18–22 jam** sekali tamat (sekitar 15 jam jalur utama + 5 jam konten sampingan).
> Versi 3 jam sebelumnya tersimpan di riwayat git; v2 memperluasnya menjadi tiga babak.

---

## 0. Ringkasan, Keputusan Desain, dan Peringatan Scope

### 0.1 Keputusan tema/gaya (bisa diganti sebelum implementasi)

| Keputusan | Pilihan di dokumen ini | Alternatif |
|---|---|---|
| Nada cerita | Melankolis-hangat; babak 2 lebih petualang, babak 3 lebih mitis | Lebih ringan, atau lebih gelap |
| Setting | Fantasi bernuansa Nusantara; dunia luar lembah lebih beragam (dataran abu, hutan bernyanyi, kota kaca) | Fantasi Eropa klasik |
| Sumber sihir | Nyala (cahaya dari ingatan) vs Kabut (ingatan tanpa pemilik) | Kristal elemen |
| Ending | 3 ending (dua dari pilihan akhir, satu rahasia dari konten sampingan) | Ending tunggal |
| Bahasa in-game | Indonesia | Inggris / dwibahasa |
| Struktur | 3 babak, tiap babak punya klimaks sendiri dan bisa dirilis bertahap | Satu alur panjang tanpa sekat |

### 0.2 Peringatan scope (penting)

Dari 3 jam ke 20 jam, yang membesar bukan sistemnya, tapi **isinya**: naskah, data musuh, data
skill, dan peta. Perkiraan kasar volume kerja:

| Komponen | v1 (3 jam) | v2 (20 jam) |
|---|---|---|
| Kata naskah (dialog + narasi) | ~15.000 | ~80.000–100.000 |
| Area / dungeon | 5 | 14 utama + 3 opsional |
| Karakter party | 3 | 7 |
| Skill | ~22 | ~110 |
| Musuh biasa / boss | 10 / 7 | 30 / 16 (+2 superboss) |
| Item & equipment | ~35 | ~150 |

Supaya tidak macet di tengah, dokumen ini dirancang **modular per babak**: Babak 1 (Lembah Larung,
~6,5 jam) adalah game utuh dengan klimaks sendiri. Babak 2 dan 3 menambah dunia dan party tanpa
mengubah sistem inti. Rekomendasi: bangun dan mainkan Babak 1 sampai tamat sebelum menulis Babak 2.

---

## 1. Premis & Setting

### 1.1 Lembah Larung dan Dunia di Baliknya

Lembah Larung adalah lembah luas yang dikelilingi pegunungan tak tertembus. Penduduknya percaya
lembah *adalah* dunia. Di tengahnya berdiri **Mercusuar Langit**, menara batu putih yang selama
berabad-abad memancarkan **Nyala**: cahaya hangat yang menjaga lembah terang, subur, dan waras.

Yang tidak diketahui penduduk: Mercusuar hanyalah **satu dari tujuh Suar** yang dibangun sebuah ordo
kuno di seluruh benua. Di balik gunung ada dunia luar yang jauh lebih besar: Kerajaan Wirasaba,
Dataran Abu, Hutan Nyanyi, Danau Garam. Dunia luar itu jatuh lebih dulu.

### 1.2 Nyala, Kabut, dan Rahasia Ordo Pelita

Nyala adalah *ingatan yang dibakar*. Para Suar dinyalakan oleh **Pelita**: orang yang menyerahkan
seluruh ingatan hidupnya sebagai bahan bakar. Rahasia ini dijaga **Ordo Pelita**, ordo pendeta
yang mengelola ketujuh Suar selama delapan abad.

Ingatan yang dibakar tidak lenyap. Ia menjadi cahaya sebentar, lalu mengendap di tepi dunia sebagai
**Kabut Lupa**: ingatan tanpa pemilik, lapar akan tubuh. Selama berabad-abad Kabut naik perlahan.
Dua belas tahun lalu, Kabut melewati ambang: lima Suar di dunia luar padam dalam satu musim, dan
benua tenggelam dalam Kabut. Orang yang berlama-lama di dalamnya kehilangan ingatan dan menjadi
**Hampa**: makhluk kosong yang mengulang kebiasaan lama dan menyerang apa pun yang masih "utuh".

Suar Larung bertahan paling lama. Untuk menahan Kabut sendirian, ia menuntut Pelita bukan lagi
sekali per beberapa dekade, tapi **setiap tahun**. Wali kota Larung, **Adipati Baskara**, menolak
membayar, dan memadamkan menara. Ia memilih lembah mati perlahan dengan tangan bersih.

### 1.3 Konflik Tiga Babak

- **Babak 1 — Lembah Larung**: Rimba, murid Penyala, mewarisi **Bara** (percikan terakhir Nyala)
  dari mentornya yang hilang, dan menempuh lembah untuk menyalakan kembali Mercusuar. Klimaks:
  konfrontasi dengan Adipati Baskara. Menara menyala, dan cahayanya menunjukkan kebenaran pahit:
  lembah adalah pulau terakhir di tengah lautan Kabut, dan Bara hanya cukup untuk beberapa minggu.
- **Babak 2 — Tanah Luar**: party menyeberangi gunung mencari tahu mengapa lima Suar lain padam,
  dan menemukan Ordo Pelita masih hidup, dipimpin **Juru Nyala Nirmala**, yang "memanen" kota-kota
  Hampa sebagai bahan bakar karena menganggap mereka sudah mati. Klimaks: Benteng Ordo Pelita.
  Party menemukan bahwa Kabut dan Nyala adalah zat yang sama.
- **Babak 3 — Ke Tepi Dunia**: berlayar ke **Pusar Kabut**, tempat Kabut berasal: reruntuhan
  **Adiluhung**, kota pertama yang membangun Suar. Di sana menunggu **Sang Pelita Pertama**, orang
  pertama yang pernah dibakar, kini kehendak Kabut itu sendiri, yang ingin seluruh dunia lupa agar
  tak ada lagi yang diingat-tanpa-tubuh. Klimaks: pilihan tentang apa yang dilakukan pada Nyala.

**Tema inti:** mengingat itu ada harganya, dan siapa yang membayarnya. Kabut mengambil ingatan
secara paksa; Nyala memintanya secara sukarela; Ordo mengambilnya dari yang tak bisa menolak.
Pertanyaan game: adakah cara mengingat bersama tanpa membakar siapa pun?

### 1.4 Nada & Contoh Narasi

Nada: melankolis tapi hangat. Dunia meredup, tapi orang-orangnya masih bercanda, memasak, dan
bertengkar soal hal sepele. Humor lahir dari karakter. Babak 2 menambah rasa petualangan
(kafilah, arena, kota asing); Babak 3 lebih sunyi dan mitis.

Layar pertama game:

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

Akhir Babak 1 (menara menyala, party di puncak):

```
Cahaya itu tidak menyilaukan. Ia hangat, seperti dapur di pagi hari.

Lalu ia menjangkau lebih jauh dari yang pernah kau lihat: melewati
Tengara, melewati Rawa, melewati gunung.

Dan di balik gunung, tidak ada apa-apa. Hanya kelabu, rata, sampai
ujung langit.

Sela   : ...Itu bukan awan, kan.
Lintang: Bukan.
Rimba  : Pak Guntur pernah bilang, di balik gunung ada laut.
Lintang: Ini laut.
```

Pos Kafilah Sanggar, Babak 2:

```
Bagas : Tiga keping buat air seember? Di Tengara segitu dapat tempe.
Sela  : Jangan mulai soal tempe.
Pedagang: Tuan, di sini yang mahal bukan airnya. Yang mahal itu
          orang yang masih ingat jalan ke sumurnya.
```

---

## 2. Struktur Dunia

Progres **linear per babak dengan hub**. Tiap babak punya satu kota hub tempat kembali (toko,
penginapan, papan Buruan, side quest). Perpindahan lewat menu lokasi; setelah Babak 2, peta dunia
menampilkan semua area yang sudah dibuka dan bisa dikunjungi ulang (kecuali yang runtuh secara cerita).

### 2.1 Peta Progres

```
BABAK 1 — LEMBAH LARUNG
 [1] Pelita Rendah & Hutan Kelabu
 [2] Rawa Suar
 [3] Danau Cermin & Desa Apung Telaga
 [4] Ibukota Tengara (HUB 1) + Lorong Bawah
 [5] Tambang Kaca Ingatan
 [6] Mercusuar Langit                        ← klimaks Babak 1
      (opsional: Gua Bawah Danau)

BABAK 2 — TANAH LUAR
 [7] Celah Angin
 [8] Dataran Abu & Pos Kafilah Sanggar (HUB 2)
 [9] Hutan Nyanyi & Desa Padasuara
[10] Kota Kaca Wirasaba
[11] Danau Garam & Menara Terapung
[12] Benteng Ordo Pelita                     ← klimaks Babak 2
      (opsional: Reruntuhan Suar Ketiga)

BABAK 3 — KE TEPI DUNIA
[13] Laut Lupa (Kapal Lentera; HUB 3 = kapal)
[14] Pusar Kabut & Kota Adiluhung            ← final
      (opsional: Pulau Hilang, superboss)
```

### 2.2 Babak 1 — Lembah Larung (~6,5 jam, Lv 1–23)

#### [1] Pelita Rendah & Hutan Kelabu (~40 mnt, Lv 1–5)
- Desa perbatasan, rumah Rimba. Tutorial gerak, menu, pertarungan, Bara.
- Pak Guntur ikut sebagai companion tutorial (Lv 10, overpowered).
- Guntur masuk kabut mengejar anak hilang dan tidak kembali; Bara menempel ke Rimba.
- Sela ditemukan terluka di hutan; bergabung sebelum boss.
- **Boss**: Hampa Penjaga Hutan.

#### [2] Rawa Suar (~50 mnt, Lv 5–9)
- Reruntuhan **Suar Lama** (menara sinyal pengulang Nyala). Puzzle urutan tiga lentera rawa.
- Lintang ditemukan di inti Suar, hidup di kabut tanpa jadi Hampa. Bergabung.
- **Boss**: Raja Katak Lumpur.

#### [3] Danau Cermin & Desa Apung Telaga (~50 mnt, Lv 9–12) *(baru)*
- Danau besar yang permukaannya memantulkan ingatan orang yang menatapnya. Desa nelayan apung
  yang bertahan karena air danau menolak Kabut.
- Cerita: penduduk mulai menghilang di malam hari. Party menyelidiki; ternyata **Ular Cermin**,
  makhluk danau, mengumpulkan ingatan penduduk untuk "menjaga" mereka dari Kabut dengan cara
  menelan mereka. Tema: perlindungan yang jadi kurungan.
- Adegan Sela: pantulan danau menunjukkan hari ia menolak perintah. Pemain melihat versi lengkapnya.
- **Boss**: Ular Cermin. Membuka jalan ke ibukota lewat dermaga.
- **Opsional**: Gua Bawah Danau (dungeon opsional Lv 14–17, dibuka setelah Lorong Bawah).

#### [4] Ibukota Tengara — HUB 1 (~60 mnt cerita, Lv 12–15)
- Kota terbesar di lembah. Pasar Bawah, Penginapan Lentera Merah, Balai Arsip, Gerbang Istana,
  **Tukang Kaca** (soket Kaca & spesialisasi), papan Buruan (Babak 1: 3 buruan).
- Party ditolak menemui Adipati. Sela mengaku mantan Pengawal Mahkota yang desersi; Kapten Rangga memburunya.
- **Dungeon**: Lorong Bawah (saluran air, tuas pasang-surut) menuju Arsip. Catatan Pelita ditemukan:
  nama ayah Lintang ada di daftar, dan Guntur adalah Penjaga Mercusuar terakhir.
- **Boss**: Kapten Rangga (duel taktis "Tandai").
- Side quest: 5.

#### [5] Tambang Kaca Ingatan (~55 mnt, Lv 15–19)
- Tambang **Kaca Ingatan**, mineral yang bisa menyimpan Nyala. Struktur vertikal, lift rusak.
- **Bagas** bergabung: mantan juru kaca tambang yang bertahan 12 tahun di dalam dengan alat-alat
  buatannya. Cerewet, praktis, alergi pada kata "takdir".
- Lintang mendengar suara ayahnya dari kristal: ayahnya adalah Pelita yang ritualnya *dibatalkan*
  Adipati di tengah jalan, dan menjadi Hampa pertama.
- Tujuan: Kaca Inti untuk membawa Bara ke puncak menara.
- **Boss**: Penambang Raksasa Terlupa (kristal punggung berganti elemen).

#### [6] Mercusuar Langit (~60 mnt, Lv 19–23)
- Menara 7 lantai bertema kenangan lembah. Point of no return Babak 1 (kembali dibuka setelahnya).
- **Mid-boss**: Penjaga Mercusuar (konstruk Guntur). Sisa kesadaran Guntur bicara: ia masuk kabut
  *sengaja* untuk menjadi Pelita berikutnya, tapi Adipati mengunci menara.
- **Final Babak 1**: Adipati Baskara, dua fase (manusia lalu Kelam Berwajah).
- Rimba menyalakan menara dengan Bara. Cahaya menyingkap lautan Kabut di balik gunung. Baskara,
  sekarat, memberi tahu: Bara Guntur hanya cukup beberapa minggu, dan "Suar tidak pernah dibuat
  untuk berdiri sendirian. Cari yang lain."
- Epilog Babak 1: dewan sementara dibentuk, Rangga ditunjuk mengawal party ke luar lembah.

### 2.3 Babak 2 — Tanah Luar (~8,5 jam, Lv 23–43)

#### [7] Celah Angin (~45 mnt, Lv 23–26)
- Lintasan gunung yang dijaga badai. **Rangga bergabung** (arc penebusan). Elemen Angin & Bumi diperkenalkan.
- Puzzle: menyusun batu penahan angin agar jembatan bisa dilewati.
- **Boss**: Garuda Kelabu (musuh terbang; pemain belajar Bumi/Angin).

#### [8] Dataran Abu & Pos Kafilah Sanggar — HUB 2 (~60 mnt, Lv 26–29)
- Dataran luas berabu, sisa kota-kota yang terbakar saat Kabut datang. Kafilah pedagang yang hidup
  berpindah dengan lentera raksasa di gerobak. Pos Sanggar: pasar, **Arena Kafilah**, papan Buruan (8 buruan),
  Tukang Kaca kedua, dermaga pasir.
- Cerita: kafilah dipimpin **Nyai Rukmini**, yang mengenal Ordo Pelita dan menunjukkan arah ke Wirasaba.
  Ia juga memperkenalkan sistem **Berkemah** (adegan Kenangan party).
- **Boss**: Cacing Abu (boss opsional tapi diarahkan cerita; membuka Buruan tingkat 2).

#### [9] Hutan Nyanyi & Desa Padasuara (~60 mnt, Lv 29–32)
- Hutan yang pohon-pohonnya bergema. Desa **Pendendang**: orang-orang yang menahan Kabut dengan
  **nyanyian ingatan bersama**, tanpa membakar siapa pun. Ini benih ending rahasia.
- **Ratih bergabung**: Pendendang muda yang suaranya "terlalu keras untuk desa". Ingin membuktikan
  lagu bisa menahan Kabut di luar hutan.
- Konflik: Ordo Pelita menganggap Pendendang bidah dan mulai menyerang.
- **Boss**: Pengkhotbah Ordo, Sunan Wirya (manusia + 2 Bayang Arsip; pertarungan pertama melawan Ordo).

#### [10] Kota Kaca Wirasaba (~75 mnt, Lv 32–36)
- Ibukota kerajaan luar yang runtuh; gedung-gedung kaca ingatan, seluruh penduduk kini Hampa
  yang masih menjalani "hari terakhir" mereka berulang. Dungeon terbesar kedua (12 ruang, 3 distrik).
- Suar Wirasaba (Suar kedua) di pusat kota, padam. Ordo "memanen" Hampa di sini.
- Kenangan Bagas: ia lahir di Wirasaba; keluarganya di antara para Hampa.
- **Boss**: Penjaga Suar Wirasaba (konstruk), lalu **Kelana** sebagai mid-boss: Hampa berzirah yang
  menjaga gerobak panen Ordo, dan hanya berhenti saat mendengar suara Lintang.

#### [11] Danau Garam & Menara Terapung (~60 mnt, Lv 36–39)
- Danau garam putih dengan Suar ketiga di atas pulau apung. Kabut di sini "beku": bisa dilewati tapi
  menyerap MP. Mekanik: rakit garam dan arus.
- **Kelana bergabung** setelah party membawanya dari Wirasaba. Ia hanya ingat Lintang. Skill-nya
  memakai HP.
- Cerita: di Menara Terapung, party menemukan "buku besar" Ordo: Kabut naik sejak abad pertama
  pembakaran. Ordo tahu, dan tetap membakar.
- **Boss**: Letnan Ordo, Nyi Pandansari, dengan Kaca Pemanen (menyedot Bara party).

#### [12] Benteng Ordo Pelita (~75 mnt, Lv 39–43)
- Benteng di tebing garam. Dungeon vertikal 3 tingkat, penjaga manusia dan konstruk Nyala.
- **Final Babak 2**: Juru Nyala **Nirmala**, dua fase. Fase 2 ia menyerahkan diri ke Suar Benteng dan
  menjadi **Pelita Hidup**: setengah manusia, setengah cahaya.
- Setelah kalah, Nirmala mengungkap: Kabut adalah ingatan-ingatan yang pernah dibakar. "Setiap
  Pelita yang kami nyalakan menambah lautan itu. Kami tahu sejak abad ketiga. Berhenti berarti
  gelap sekarang. Lanjut berarti gelap nanti. Kami memilih nanti."
- Party memutuskan pergi ke sumber: Pusar Kabut. Kafilah Sanggar menyumbang **Kapal Lentera**.
- **Opsional**: Reruntuhan Suar Ketiga (Lv 45–48, dibuka setelah Benteng).

### 2.4 Babak 3 — Ke Tepi Dunia (~5 jam, Lv 43–52)

#### [13] Laut Lupa (~90 mnt, Lv 43–47)
- Berlayar dengan Kapal Lentera (hub 3: toko, kemah, Tukang Kaca terakhir). Laut Kabut dengan
  pulau-pulau ingatan: tiap pulau adalah satu kenangan besar yang mengeras (pulau pernikahan, pulau
  perang, pulau pasar). 4 pulau wajib, 2 opsional.
- Musuh di sini adalah **Gema**: ingatan yang cukup kuat untuk membentuk tubuh sendiri.
- Kenangan puncak tiap party member terjadi di pulau yang "memanggil" mereka.
- **Boss**: Gema Guntur (pulau lentera; Rimba berhadapan dengan kenangan mentornya).
- **Opsional**: Pulau Hilang (superboss Sang Penenun, Lv 55+).

#### [14] Pusar Kabut & Kota Adiluhung (~90 mnt, Lv 47–52)
- Reruntuhan kota pertama. Point of no return final. Dungeon 5 lapis turun ke Sumur Ingatan.
- Musuh: Pelita Padam kuno, Gema Ordo pertama, Hampa Adiluhung.
- **Mid-boss**: Tujuh Penjaga Suar (satu pertarungan panjang melawan 7 konstruk secara bergelombang).
- **Final**: **Sang Pelita Pertama**, tiga fase (§6.3).
- **Pilihan akhir** (memengaruhi epilog):
  1. **Menyalakan Kembali** — Kelana menawarkan diri sebagai Pelita untuk tujuh Suar sekaligus,
     memakai seluruh Kabut yang mengalir kembali. Dunia terang lagi, Suar hidup, Kelana hilang,
     dan Ordo harus dibangun ulang dengan aturan baru. Lintang menjadi Juru Nyala pertama yang
     berjanji tak akan membakar siapa pun. Ending "terang tapi berutang".
  2. **Mengembalikan** — Rimba memakai Bara untuk membuka semua Suar dan mengalirkan Nyala kembali ke
     Kabut, melarutkan keduanya. Tidak ada lagi Nyala, tidak ada lagi Kabut, tidak ada lagi sihir.
     Semua orang kehilangan *sebagian* ingatan (termasuk party), tapi tidak ada yang jadi Hampa lagi.
     Ending "gelap yang adil".
  3. **Mendendangkan** (rahasia; syarat: semua adegan Kenangan Ratih + 7 Buruan + Padasuara diselamatkan) —
     Ratih memimpin Pendendang dari seluruh dunia (yang ditemui sepanjang side quest) menyanyikan
     Kabut kembali menjadi ingatan yang *dikembalikan ke pemiliknya*. Hampa pulih. Suar tidak
     perlu menyala karena tidak ada lagi yang perlu ditahan. Ending "mengingat bersama".

### 2.5 Anggaran Waktu

| Segmen | Estimasi |
|---|---|
| Babak 1 jalur utama | 6 j 00 m |
| Babak 2 jalur utama | 7 j 15 m |
| Babak 3 jalur utama | 3 j 00 m |
| Side quest (18 buah) | 2 j 00 m |
| Buruan (11) + Arena (5 tingkat) | 1 j 15 m |
| Dungeon opsional (3) | 1 j 30 m |
| Kenangan/Berkemah, belanja, grinding wajar | 1 j 00 m |
| **Total** | **~20–22 jam** (jalur utama saja ~16 jam) |

---

## 3. Karakter

### 3.1 Party (7 anggota; 4 aktif, 3 cadangan)

| # | Nama | Gabung | Peran gameplay | Elemen utama | Senjata |
|---|---|---|---|---|---|
| 1 | **Rimba** (17) | Awal | All-rounder, pemegang Bara | Api, Cahaya | Tongkat lentera |
| 2 | **Sela** (24) | Area 1 | Tank fisik, provokasi | Fisik | Pedang lebar & perisai |
| 3 | **Lintang** (15) | Area 2 | Mage & debuffer | Es, Petir, Kelam | Lentera fokus |
| 4 | **Bagas** (31) | Area 5 | Juru Kaca: gadget, curi, baterai MP | Petir, Bumi (via alat) | Alat kaca (peluncur, jerat) |
| 5 | **Rangga** (35) | Area 7 | Komandan: buff party & fisik berat | Bumi | Tombak & panji |
| 6 | **Ratih** (19) | Area 9 | Pendendang: heal, buff berlapis, Angin | Angin, Cahaya | Kecapi |
| 7 | **Kelana** (~45) | Area 11 | Ksatria Kelam: damage besar berbiaya HP | Kelam, Fisik | Pedang panjang berkarat |

Guest: **Pak Guntur** (prolog, Lv 10). Tidak bisa dikendalikan equipment-nya.

#### Rimba — Penyala
- Protagonis yang *bertanya*, bukan yang selalu punya jawaban. Sopan ke orang tua, keras kepala soal janji.
- Gameplay: satu-satunya pemegang Bara; wajib ada di party aktif (aturan cerita, disebut jelas).
- Jalur Lv 20: **Kobaran** (damage Api area, Bakar) atau **Penuntun** (support Cahaya, heal, Bara lebih cepat).
- Arc: dari "menjaga lentera tetap nyala" ke "memutuskan apa yang boleh dibakar" ke "mencari cara
  agar tak ada yang perlu dibakar".

#### Sela — Pengawal yang Desersi
- Blak-blakan, sinis di permukaan, sangat protektif. Merasa bersalah karena diam terlalu lama.
- Gameplay: HP & DEF tertinggi. Provokasi, counter, pelindung kawan.
- Jalur Lv 20: **Benteng** (counter, mengurangi damage kawan) atau **Algojo** (serangan fisik besar, mengorbankan DEF).
- Arc: menghadapi Rangga di Babak 1, lalu *bekerja bersama* Rangga di Babak 2. Kenangan puncak:
  Pulau Perang di Laut Lupa, tempat ia melihat versi dirinya yang tidak pernah desersi.

#### Lintang — Anak Kabut
- Polos soal hal sehari-hari (tidak tahu tempe), tajam soal hal besar. Kabut "mengenalinya".
- Gameplay: MAG tertinggi, HP terendah. Satu-satunya yang menguasai Kelam sejak awal.
- Jalur Lv 20: **Badai** (Es/Petir area) atau **Bisikan** (Kelam, debuff & status, serap).
- Arc: menemukan ayahnya sebagai Hampa, lalu memutuskan mengingat *untuk* dia.

#### Bagas — Juru Kaca
- Cerewet, praktis, benci kata "takdir". Bertahan 12 tahun di tambang dengan alat buatannya sendiri.
  Lahir di Wirasaba; keluarganya kini Hampa di kota itu.
- Gameplay: **Curi** (item dari musuh, sumber Kaca langka), **Baterai** (pindahkan MP ke kawan),
  gadget elemen (Petir/Bumi) yang tidak memakai MP tapi memakai **Suku Cadang** (item murah).
  Item yang ia pakai berefek ×1.5.
- Jalur Lv 20: **Peretas** (debuff & curi lebih kuat, Goyah tanpa elemen) atau **Montir** (gadget area & sokongan MP).
- Arc: menerima bahwa keluarganya "sudah pergi", lalu menolak keputusan itu di ending 3.

#### Rangga — Kapten yang Kalah
- Loyal pada "perintah" karena takut kekacauan. Setelah Baskara jatuh, ia kehilangan pegangan dan
  memilih mengabdi pada *misi*, bukan orang.
- Gameplay: **Komando**: buff satu baris (ATK/DEF/AGI party), **Panji** yang bertahan beberapa
  giliran, serangan tombak Bumi menembus DEF.
- Jalur Lv 30 (gabung terlambat, jadi jalurnya di Lv 30 & 45): **Panglima** (buff area lebih lama) atau **Penumbuk** (fisik Bumi, Berat).
- Arc: dari mengikuti perintah ke memberi perintah yang bisa ia pertanggungjawabkan. Kenangan puncak:
  menolak perintah Nirmala untuk "menahan" Padasuara.

#### Ratih — Pendendang
- Suaranya "terlalu keras untuk desa": keras kepala, optimis dengan cara yang bikin orang lain lelah,
  tapi benar. Percaya lagu bisa menahan Kabut di mana pun.
- Gameplay: **Lagu**: buff/heal yang berlangsung 3 giliran selama Ratih tidak diserang Bisu.
  Angin untuk musuh terbang & evasif; Cahaya untuk Hampa.
- Jalur Lv 30/45: **Pemulih** (heal & pembersih status) atau **Penggugah** (buff ofensif, Bara lebih cepat untuk Rimba).
- Arc: kunci ending 3. Ia mengumpulkan Pendendang yang tersebar (side quest lintas babak).

#### Kelana — Ayah Lintang, Hampa yang Ingat Satu Nama
- Bicara singkat, sering salah nama orang selain Lintang. Kadang berhenti di tengah pertarungan
  (mekanik: 5% peluang "Terdiam" satu giliran, hilang setelah Kenangan ke-3).
- Gameplay: ATK tertinggi. Skill Kelam berbiaya HP, bukan MP. Tidak bisa disembuhkan skill Cahaya
  (Cahaya melukainya), tapi menyerap Kelam. Memaksa pemain menyusun ulang kebiasaan heal.
- Jalur Lv 40: **Pendekar Sunyi** (single-target ekstrem) atau **Perisai Kabut** (menyerap damage kawan ke HP-nya).
- Arc: memilih hilang untuk yang diingatnya (ending 1), atau pulih (ending 3).

### 3.2 Antagonis

| Nama | Babak | Peran |
|---|---|---|
| **Adipati Baskara** (58) | 1 | Memadamkan Mercusuar untuk menolak harga Pelita. Bukan gila; terjebak mempertahankan keputusan. Bicara pelan. |
| **Kapten Rangga** | 1 | Antagonis sekunder yang berubah jadi party member. |
| **Sunan Wirya** | 2 | Pengkhotbah Ordo yang tulus percaya Pendendang bidah. |
| **Nyi Pandansari** | 2 | Letnan Ordo, pragmatis, memegang Kaca Pemanen. Menyerah setelah kalah dan membelot di Babak 3 (NPC di kapal). |
| **Juru Nyala Nirmala** (61) | 2 | Pemimpin Ordo. Percaya "gelap nanti lebih baik daripada gelap sekarang". Membakar Hampa karena "mereka sudah pergi". Menjadi Pelita Hidup. |
| **Sang Pelita Pertama** | 3 | Manusia pertama yang dibakar delapan abad lalu; kesadarannya bertahan di Kabut dan menjadi kehendaknya. Tidak ingin balas dendam; ingin semua *berhenti diingat* agar tidak ada lagi yang sepertinya. |

Contoh dialog Nirmala (fase 1, sebelum bertarung):

```
Nirmala: Kau menyalakan Suar Larung dengan satu orang. Bagus.
         Berapa lama? Empat minggu? Lima?
Rimba  : Tiga.
Nirmala: Tiga. Dan kau datang ke sini untuk menghakimi kami yang
         menjaga tujuh Suar selama delapan ratus tahun.
Ratih  : Kalian tidak menjaga apa-apa. Kalian menunda.
Nirmala: Nak, seluruh peradaban adalah menunda.
```

Contoh Kelana (Kenangan ke-2, berkemah):

```
Kelana : ...Lintang.
Lintang: Iya, Pak.
Kelana : Yang itu. Yang pakai perisai.
Lintang: Sela.
Kelana : Sela. Dia... dia baik padamu?
Lintang: Iya.
Kelana : Bagus. (jeda panjang) Lintang.
Lintang: Iya, Pak. Masih di sini.
```

---

## 4. Sistem Combat

### 4.1 Prinsip

- **Turn-based murni**, urutan giliran oleh AGI. Semua aksi lewat menu teks.
- **4 aktif + 3 cadangan**. Aksi **Ganti** menukar satu aktif dengan cadangan (memakai giliran karakter
  yang ditukar; karakter masuk langsung dapat giliran di ronde berikutnya). Cadangan menerima 70% XP.
- Musuh 1–5 per encounter. Encounter acak per perpindahan ruang (peluang 30–45%, jaminan tidak
  beruntun dalam 2 langkah). Ada item **Dupa Sunyi** untuk mematikan encounter 30 langkah.
- Durasi target pertarungan biasa: 3–5 giliran. Boss: 10–20 giliran. Superboss: 25–40.
- Pertarungan menekankan **kelemahan elemen**, **status**, dan **manajemen Bara**.

### 4.2 Stat

| Stat | Fungsi |
|---|---|
| HP | Nyawa. 0 = pingsan. Semua aktif pingsan = game over (cadangan tidak otomatis masuk). |
| MP | Bahan bakar skill (kecuali Kelana: HP; Bagas gadget: Suku Cadang). |
| ATK / DEF | Serangan & pertahanan fisik. |
| MAG / RES | Serangan & pertahanan sihir. |
| AGI | Urutan giliran, peluang kena/hindar fisik. |
| LCK | Kritikal, peluang status, peluang Curi. |

Stat dasar Lv 1 (karakter yang gabung belakangan masuk dengan level = Rimba − 1, stat dihitung dari kurva):

| Karakter | HP | MP | ATK | DEF | MAG | RES | AGI | LCK | Pertumbuhan/level (HP, MP, ATK, DEF, MAG, RES, AGI, LCK) |
|---|---|---|---|---|---|---|---|---|---|
| Rimba | 45 | 12 | 8 | 6 | 7 | 6 | 7 | 6 | 7, 2, 1.6, 1.2, 1.4, 1.2, 1.2, 0.8 |
| Sela | 60 | 6 | 10 | 9 | 3 | 5 | 5 | 4 | 9, 1, 1.9, 1.8, 0.4, 1.0, 0.8, 0.6 |
| Lintang | 34 | 18 | 4 | 4 | 10 | 8 | 9 | 7 | 5, 3, 0.6, 0.8, 2.1, 1.6, 1.6, 1.0 |
| Bagas | 42 | 10 | 7 | 6 | 6 | 6 | 10 | 10 | 6, 1.5, 1.3, 1.1, 1.1, 1.1, 1.8, 1.4 |
| Rangga | 55 | 8 | 9 | 8 | 4 | 6 | 6 | 5 | 8, 1.2, 1.8, 1.6, 0.6, 1.2, 1.0, 0.7 |
| Ratih | 38 | 16 | 4 | 5 | 8 | 9 | 8 | 8 | 5.5, 2.8, 0.6, 0.9, 1.7, 1.8, 1.4, 1.1 |
| Kelana | 58 | 0 | 12 | 7 | 6 | 4 | 6 | 3 | 9.5, 0, 2.3, 1.3, 1.0, 0.8, 1.0, 0.5 |

Pertumbuhan pecahan diakumulasi lalu dibulatkan ke bawah (deterministik).

### 4.3 Aksi per Giliran

1. **Serang** — fisik dasar, gratis, elemen Fisik atau elemen Kaca senjata.
2. **Skill** — biaya MP (Kelana: HP; Bagas gadget: Suku Cadang).
3. **Item** — dari inventori.
4. **Jaga** — DEF & RES ×1.5 hingga giliran berikutnya, +5% MP, **+1 Bara** kalau Rimba.
5. **Ganti** — tukar dengan cadangan.
6. **Bara** — jurus pamungkas & Jurus Ganda (hanya kalau Bara cukup).
7. **Kabur** — encounter acak saja. Peluang 50% + (rata AGI party − rata AGI musuh) × 3%, batas 20–90%.

### 4.4 Elemen (8) & Afinitas

| Elemen | Pengguna utama | Lawan alami | Catatan |
|---|---|---|---|
| **Fisik** | Sela, Rangga, Kelana | — | Musuh berzirah/konstruk sering Tahan. |
| **Api** | Rimba | Es | Tumbuhan, es, kabut tipis. Status Bakar. |
| **Es** | Lintang | Api | Makhluk rawa, tambang, gurun. Status Beku. |
| **Petir** | Lintang, Bagas | (diserap Bumi) | Konstruk logam, makhluk air. |
| **Angin** | Ratih | Bumi | Makhluk terbang, evasif. Status Buta. |
| **Bumi** | Rangga, Bagas | Angin | Makhluk terbang jatuh (Berat), menembus DEF. Menyerap Petir. |
| **Cahaya** | Rimba, Ratih | Kelam | Hampa & makhluk Kabut. Diserap Pelita Padam. |
| **Kelam** | Lintang, Kelana | Cahaya | Pelita Padam & konstruk Nyala. Diserap Hampa. |

Pengali afinitas: Lemah ×1.5 (+Goyah, +1 Bara), Normal ×1.0, Tahan ×0.5, Imun ×0, Serap (menyembuhkan musuh).

Kelemahan **tersembunyi sampai dipukul**, lalu dicatat permanen di **Catatan Penyala**. Bagas
punya skill **Pindai** (Lv 22) yang membuka semua afinitas satu musuh sekaligus, sebagai jalan
pintas bagi yang tidak mau menebak.

### 4.5 Bara (Sumber Daya Party) & Jurus Ganda

- Meteran bersama, **0–5 Bara** (naik ke 8 lewat Serpihan Ingatan), pegangan Rimba, reset ke 0 tiap pertarungan
  (kecuali Kalung Bara: mulai 1–2).
- Dapat: pukul kelemahan +1, Rimba Jaga +1, kawan pingsan +2, Lagu Penggugah Ratih +1 per 2 giliran.
- Pakai:
  - **Nyala Pulih** (2): heal semua aktif 30% + hapus status buruk.
  - **Nyala Pamungkas** (3): Rimba, Cahaya semua musuh, kekuatan 2.5, tak bisa dihindari.
  - **Jurus Ganda** (4): dua anggota aktif. Setiap pasangan dibuka lewat **adegan Kenangan** saat Berkemah
    (tidak otomatis), supaya konten sampingan terasa berdampak. Daftar (12 pasangan; pasangan lain tidak punya Jurus):

| Pasangan | Nama | Elemen | Efek |
|---|---|---|---|
| Rimba + Sela | Tebas Berapi | Fisik+Api | Satu target, 3.0 |
| Rimba + Lintang | Fajar Kelabu | Cahaya+Kelam | Semua, 2.0, abaikan Serap |
| Sela + Lintang | Badai Perisai | Petir | Semua, 1.8, Goyah |
| Rimba + Bagas | Lentera Meledak | Api+Petir | Semua, 2.2, Bakar 50% |
| Bagas + Lintang | Sirkuit Beku | Es+Petir | Satu, 3.2, Beku 40% |
| Sela + Rangga | Barisan Perisai | — | Party imun damage 1 ronde + DEF ×1.5 3 giliran |
| Rangga + Rimba | Panji Nyala | Bumi+Cahaya | Semua, 2.0, +1 Bara balik |
| Ratih + Rimba | Nyanyian Fajar | Cahaya | Heal penuh semua aktif + Lagu ofensif 3 giliran |
| Ratih + Lintang | Kidung Kabut | Angin+Kelam | Semua, 2.0, Lelah & Buta 60% |
| Kelana + Lintang | Pulang | Kelam | Satu, 4.0, abaikan RES; Kelana pulih 30% HP |
| Kelana + Sela | Dua Pedang Karat | Fisik+Kelam | Satu, 3.5 |
| Ratih + Kelana | Lagu untuk yang Lupa | Cahaya+Kelam | Semua, 2.4; Kelana tidak terluka Cahaya 5 giliran |

  - **Jurus Empat** (8 Bara, hanya setelah Bara maks 8): **Pelita Terakhir**, seluruh party aktif, semua musuh, kekuatan 5.0, elemen sesuai kelemahan tiap musuh. Sekali per pertarungan.
- Rimba pingsan = Bara membeku.

### 4.6 Pecah (Break) untuk Boss

Boss dan musuh elit punya **meter Ketahanan** (0–100). Pukulan kelemahan −25, Goyah dari skill
non-elemen −15, serangan normal −5. Di 0, boss **Pecah**: melewatkan satu ronde penuh, semua damage
masuk ×1.5, lalu meter pulih penuh. Boss tertentu punya fase yang mengganti kelemahan sehingga
membangun Pecah adalah puzzle utamanya.

### 4.7 Formula Damage

Pembagian dibulatkan ke bawah; damage minimum 1 kecuali Imun/Serap.

```
Fisik : dasar = ATK_penyerang * 2 - DEF_target        (min 1)
Sihir : dasar = MAG_penyerang * 2 - RES_target        (min 1)
damage = dasar * kekuatan_skill * afinitas * kritikal * pecah * acak
```

| Pengali | Nilai |
|---|---|
| kekuatan_skill | Serang 1.0; skill 0.8–4.0; Jurus Empat 5.0 |
| afinitas | 1.5 / 1.0 / 0.5 / 0 / −1.0 |
| kritikal | 1.5; peluang 5% + LCK × 0.5%, maks 35% |
| pecah | 1.5 saat target Pecah, 1.2 saat Goyah |
| acak | seragam 0.90–1.10 |
| Jaga target | DEF/RES ×1.5 (masuk lewat dasar) |
| Tembus DEF (tombak Rangga, Malam Pengingat) | DEF/RES target dihitung 0 |

```
peluang_kena fisik = 92% + (AGI_penyerang - AGI_target) * 1.5%   batas 60–100%
heal = MAG_pengguna * kekuatan_skill + nilai_dasar_skill
```

Kalibrasi target: musuh biasa mati dalam 2–3 aksi kalau kelemahannya dipakai, 4–6 kalau tidak.
Boss punya HP ≈ (total damage party per ronde) × 12.

**Aturan penurunan stat musuh dari formula ini** (dipakai `tools/calibrate.py` dan data Babak 1; boss
akhir Babak 1 dinaikkan 40–60% di atas aturan setelah walkthrough, lihat §9.1):

```
off(L)  = 9.3 + 1.83·(L−1)          ≈ rata-rata ATK/MAG party pada level L
HP      = peran × 7 × off(L)         peran: swarm 0.3 · rapuh 0.5–0.7 · normal 0.9–1.0 · tank 1.3–1.4
HP boss = 30 × off(L)
DEF/RES ≈ 0.55 × off(L)             (tank/zirah lebih tinggi)
ATK     ≈ 7.3 + 1.26·(L−1)          ≈ 18% HP hero per pukulan biasa
XP      = 6·L² (boss 30·L²)          Keping = L² (boss 5·L²)
```

Hasil simulasi Tahap 1 (150 pertarungan per skenario, kebijakan satu-target berbasis kelemahan):
Hutan 2,1 aksi/musuh · Rawa 4,7 (party campuran Lv 6–7 melawan 3 musuh) · Tambang 3,1 ·
Mercusuar 4,5 (Pelita Padam sengaja hanya lemah terhadap Kelam) · boss 4–8 ronde (12–15 aksi party).

### 4.8 Status Efek

| Status | Efek | Durasi | Sumber |
|---|---|---|---|
| Racun | −8% HP maks/giliran | 4 | Lumut, katak, kalajengking abu |
| Bakar | −5% HP/giliran, DEF −20% | 3 | Api |
| Beku | Lewati 1 giliran | 1 | Es (20%) |
| Lelah | ATK & MAG −30% | 3 | Selimut Kabut, dsb. |
| Goyah | Aksi berikutnya acak & lemah; damage masuk ×1.2 | 1 | Kelemahan, Bantingan Perisai |
| Lupa | Tidak bisa Skill | 2 | Hampa, kabut tanpa lentera |
| Tidur | Lewati giliran; bangun kalau dipukul | 3 | Kelelawar, Gema Ninabobo |
| Buta | Peluang kena fisik −40% | 3 | Angin |
| Berat | AGI −50%; musuh terbang jatuh (kehilangan evasi & kelemahan Angin, dapat kelemahan Fisik) | 3 | Bumi |
| Bisu | Lagu Ratih berhenti; tidak bisa skill sihir | 2 | Bayang Arsip, Ordo |
| Kutuk | Heal jadi damage | 3 | Pelita Padam, Gema |
| Provokasi | Serangan single-target musuh diarahkan ke pemasang | 1 | Sela, Rangga |
| Terdiam (Kelana saja) | Lewati giliran, 5% peluang tiap giliran, hilang setelah Kenangan ke-3 | 1 | Bawaan |

Peluang status masuk = peluang skill × (1 − LCK_target × 1%). Boss punya daftar imunitas.

### 4.9 Jalur Spesialisasi

Di level tertentu (§3.1) tiap karakter memilih satu dari dua **Jalur**: membuka 3 skill eksklusif
dan satu pasif. Bisa direset di Tukang Kaca dengan 3 Serpihan Ingatan. Pilihan kedua di Lv 45 menambah
1 skill puncak per jalur.

### 4.10 Daftar Skill

Format: Lv · Nama · biaya · elemen · kekuatan · target · catatan. "J:" menandai skill Jalur.

**Rimba**

| Lv | Skill | MP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 1 | Sulut | 3 | Api | 1.4 | Satu | 30% Bakar |
| 3 | Sinar Lentera | 4 | Cahaya | 1.3 | Satu | — |
| 6 | Kobar | 7 | Api | 1.2 | Semua | 20% Bakar |
| 9 | Tumbuk Nyala | 5 | Fisik | 1.6 | Satu | Elemen senjata |
| 12 | Cahaya Penunjuk | 6 | — | — | Kawan | Hapus Lupa/Tidur/Buta + heal MAG×1.5+30 |
| 15 | Fajar | 12 | Cahaya | 1.8 | Semua | — |
| 18 | Nyala Terakhir | 15 | Api+Cahaya | 2.4 | Satu | ×1.5 kalau HP Rimba <30% |
| 20 J | Kobaran: Lautan Api | 16 | Api | 2.0 | Semua | Bakar 60%, ×1.3 pada target Bakar |
| 20 J | Penuntun: Pelita Kawan | 8 | — | — | Kawan | Kawan dapat +1 Bara tiap giliran 3 giliran |
| 26 J | Kobaran: Bara Amarah | 0 | — | — | Diri | Habiskan 2 Bara: ATK & MAG ×1.5 3 giliran |
| 26 J | Penuntun: Jalan Pulang | 14 | Cahaya | — | Semua kawan | Heal MAG×2+60, hapus semua status |
| 24 | Sinar Menembus | 10 | Cahaya | 1.6 | Satu | Abaikan Tahan (Tahan dihitung Normal) |
| 30 | Nyala Bergilir | 14 | Api/Cahaya | 1.5 | Semua | Elemen dipilih saat cast |
| 36 | Api Ingatan | 18 | Api | 2.6 | Satu | ×1.5 pada Hampa & Gema |
| 42 | Terang Larung | 24 | Cahaya | 2.2 | Semua | +2 Bara |
| 45 J | Kobaran: Puncak Nyala | 30 | Api | 3.6 | Semua | Bakar pasti |
| 45 J | Penuntun: Ingat Aku | 30 | — | — | Semua kawan | Bangkitkan semua yang pingsan 50% HP |
| 48 | Pelita Terakhir (Jurus Empat) | 8 Bara | Adaptif | 5.0 | Semua | Lihat §4.5 |

**Sela**

| Lv | Skill | MP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 1 | Tebas Berat | 3 | Fisik | 1.6 | Satu | Kena −10% |
| 4 | Pasang Badan | 2 | — | — | Diri | Provokasi + DEF ×1.5 |
| 7 | Teriakan Provokasi | 4 | — | — | Semua musuh | Provokasi + 40% Lelah |
| 10 | Bantingan Perisai | 5 | Fisik | 1.3 | Satu | 50% Goyah, −15 Ketahanan |
| 13 | Tebas Menyapu | 8 | Fisik | 1.1 | Semua | — |
| 16 | Tumbal Baja | 0 | — | — | Diri | −25% HP: ATK ×1.5 3 giliran |
| 19 | Sumpah Pengawal | 10 | Fisik | 2.6 | Satu | ×2 kalau ada kawan pingsan |
| 20 J | Benteng: Balas | 6 | — | — | Diri | Counter tiap serangan fisik 3 giliran, kekuatan 1.2 |
| 20 J | Algojo: Tebas Pemenggal | 12 | Fisik | 2.8 | Satu | Kritikal +25%, DEF diri −30% 2 giliran |
| 26 J | Benteng: Perisai Semua | 10 | — | — | Semua kawan | Damage masuk kawan −30% 2 giliran |
| 26 J | Algojo: Tebas Bumi | 14 | Fisik | 1.8 | Semua | Berat 50% |
| 24 | Dinding Perunggu | 8 | — | — | Diri | RES ×1.5 & imun status 2 giliran |
| 30 | Tumbuk Perisai Ganda | 12 | Fisik | 2.0 | Satu | 2 pukulan, masing-masing −10 Ketahanan |
| 36 | Sumpah Pertama | 16 | Fisik | 3.0 | Satu | Provokasi diri 2 giliran setelahnya |
| 42 | Kaki Terpancang | 12 | — | — | Diri | HP tidak bisa <1 selama 2 giliran |
| 45 J | Benteng: Tembok Tengara | 20 | — | — | Semua kawan | Imun damage 1 ronde |
| 45 J | Algojo: Hukuman | 26 | Fisik | 4.0 | Satu | ×1.5 pada target Goyah/Pecah |

**Lintang**

| Lv | Skill | MP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 4 | Serpih Es | 3 | Es | 1.4 | Satu | 20% Beku |
| 4 | Selimut Kabut | 4 | — | — | Semua musuh | 60% Lelah |
| 6 | Kilat Kecil | 4 | Petir | 1.4 | Satu | — |
| 8 | Bisikan Lupa | 5 | Kelam | 0.8 | Satu | 70% Lupa |
| 10 | Rawat Kabut | 5 | — | — | Kawan | Heal MAG×2+20 |
| 12 | Badai Es | 9 | Es | 1.2 | Semua | 10% Beku |
| 14 | Petir Bercabang | 9 | Petir | 1.3 | Semua | — |
| 16 | Tirai Kelam | 8 | Kelam | 1.2 | Semua | Serap 25% ke HP Lintang |
| 19 | Malam Pengingat | 14 | Kelam | 2.2 | Satu | Abaikan RES |
| 20 J | Badai: Salju Sunyi | 14 | Es | 1.8 | Semua | 30% Beku |
| 20 J | Bisikan: Nama yang Hilang | 10 | Kelam | 1.0 | Satu | Lupa + Lelah + Kutuk 60% |
| 26 J | Badai: Guntur Tujuh | 20 | Petir | 2.4 | Semua | — |
| 26 J | Bisikan: Tukar Ingatan | 12 | — | — | Musuh | Pindahkan semua status buruk Lintang ke target |
| 24 | Es Kaca | 12 | Es | 2.0 | Satu | Beku 35% |
| 30 | Kabut Pelindung | 10 | — | — | Semua kawan | RES ×1.5 & serangan sihir musuh −20% 3 giliran |
| 36 | Petir Ingatan | 18 | Petir | 2.6 | Satu | ×1.5 pada konstruk |
| 42 | Gerhana | 26 | Kelam | 2.4 | Semua | Kutuk 50%, abaikan Serap Hampa (Hampa dihitung Normal) |
| 45 J | Badai: Musim Beku | 34 | Es+Petir | 3.4 | Semua | Beku 50% |
| 45 J | Bisikan: Sunyi Total | 30 | Kelam | 3.0 | Satu | Abaikan RES; Bisu, Lupa, Kutuk pasti |

**Bagas** (gadget: biaya "SC" = Suku Cadang, bukan MP)

| Lv | Skill | Biaya | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 15 | Curi | 0 | — | — | Satu | Peluang 40% + LCK×1%; item sesuai tabel musuh |
| 15 | Peluncur Kejut | 1 SC | Petir | 1.4 | Satu | — |
| 17 | Jerat Bumi | 1 SC | Bumi | 1.2 | Satu | Berat 70% |
| 19 | Baterai | 4 MP | — | — | Kawan | Pindahkan 15 MP Bagas ke kawan (ambil dari cadangan MP Bagas) |
| 20 J | Peretas: Bongkar Zirah | 2 SC | — | — | Satu | DEF & RES target −30% 3 giliran, −20 Ketahanan |
| 20 J | Montir: Lentera Portabel | 6 MP | — | — | Semua kawan | Imun Lupa & MP +10/giliran 3 giliran |
| 22 | Pindai | 3 MP | — | — | Satu | Buka semua afinitas & HP target |
| 26 J | Peretas: Copet Ulung | 0 | — | — | Satu | Curi 70%, item langka jika target Pecah |
| 26 J | Montir: Ranjau Ganda | 3 SC | Petir+Bumi | 1.6 | Semua | Goyah 40% |
| 28 | Ledakan Kaca | 3 SC | Api | 1.8 | Semua | Bakar 30% |
| 32 | Perbaiki | 8 MP | — | — | Kawan | Heal MAG×2+50, hapus Berat/Bisu |
| 36 | Serat Kaca | 2 SC | — | — | Semua musuh | AGI −30% 3 giliran |
| 40 | Meriam Ingatan | 5 SC | Petir | 3.0 | Satu | Abaikan Tahan |
| 45 J | Peretas: Kunci Mati | 6 SC | — | — | Satu boss | Meter Ketahanan −50 |
| 45 J | Montir: Nyala Cadangan | 20 MP | — | — | Semua kawan | Pulihkan MP 50% semua aktif |

**Rangga**

| Lv | Skill | MP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 23 | Tusukan Bumi | 5 | Bumi | 1.5 | Satu | Tembus DEF |
| 23 | Komando: Maju | 6 | — | — | Semua kawan | ATK ×1.3 2 giliran |
| 25 | Komando: Tahan | 6 | — | — | Semua kawan | DEF ×1.3 2 giliran |
| 27 | Panji Larung | 10 | — | — | Lapangan | 4 giliran: kawan +10% heal tiap giliran; Provokasi ke Rangga |
| 29 | Tombak Melingkar | 9 | Bumi | 1.2 | Semua | Berat 40% |
| 30 J | Panglima: Komando Ganda | 12 | — | — | Semua kawan | Maju + Tahan sekaligus 3 giliran |
| 30 J | Penumbuk: Hantaman Gempa | 14 | Bumi | 2.4 | Semua | Berat 70%, −20 Ketahanan |
| 33 | Serbu | 8 | Fisik | 2.0 | Satu | Kawan yang AGI-nya di bawah Rangga ikut Serang dasar |
| 37 J | Panglima: Panji Tujuh Suar | 18 | — | — | Lapangan | Panji 6 giliran + AGI ×1.2 |
| 37 J | Penumbuk: Tombak Tanah | 18 | Bumi | 3.0 | Satu | Tembus DEF, Berat pasti |
| 41 | Perintah Terakhir | 20 | — | — | Kawan | Kawan bertindak lagi segera (satu kali per pertarungan) |
| 45 J | Panglima: Barisan Tak Patah | 28 | — | — | Semua kawan | Imun status & damage −40% 3 giliran |
| 45 J | Penumbuk: Runtuhkan Langit | 32 | Bumi | 4.0 | Semua | Berat pasti, −40 Ketahanan |

**Ratih** ("Lagu" berlangsung 3 giliran, berhenti kalau Ratih Bisu/pingsan; hanya satu Lagu aktif)

| Lv | Skill | MP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 29 | Hembus Angin | 4 | Angin | 1.4 | Satu | Buta 30% |
| 29 | Lagu Rawat | 8 | — | — | Semua kawan | Heal MAG×1+20 tiap giliran |
| 31 | Lagu Gugah | 8 | — | — | Semua kawan | ATK & MAG ×1.2; Rimba +1 Bara tiap 2 giliran |
| 33 | Sinar Kidung | 7 | Cahaya | 1.4 | Semua | — |
| 30 J | Pemulih: Lagu Sembuh | 10 | — | — | Semua kawan | Hapus 1 status buruk tiap giliran + heal MAG×1.5 |
| 30 J | Penggugah: Lagu Cepat | 10 | — | — | Semua kawan | AGI ×1.3; Rimba +1 Bara tiap giliran |
| 35 | Badai Bulu | 12 | Angin | 1.6 | Semua | Buta 40%; ×1.5 pada musuh terbang |
| 37 J | Pemulih: Nada Bangkit | 18 | — | — | Kawan | Bangkitkan 60% HP + imun status 2 giliran |
| 37 J | Penggugah: Lagu Berani | 16 | — | — | Semua kawan | Kritikal +20% & ATK ×1.4 |
| 39 | Ninabobo | 9 | — | — | Semua musuh | Tidur 60% |
| 43 | Kidung Tujuh Suar | 22 | Cahaya | 2.4 | Semua | Hapus Kutuk kawan |
| 45 J | Pemulih: Lagu Pulang | 30 | — | — | Semua kawan | Heal penuh sekali + Lagu Rawat 5 giliran |
| 45 J | Penggugah: Lagu Terang | 30 | — | — | Semua kawan | Semua buff sekaligus 3 giliran, +3 Bara |

**Kelana** (biaya dalam % HP maks)

| Lv | Skill | HP | Elemen | Kek. | Target | Catatan |
|---|---|---|---|---|---|---|
| 36 | Tebas Karat | 5% | Kelam | 1.8 | Satu | — |
| 36 | Hisap Kabut | 0 | Kelam | 1.0 | Satu | Serap 50% ke HP Kelana |
| 38 | Sayat Sunyi | 8% | Fisik | 2.2 | Satu | Bisu 50% |
| 40 J | Pendekar Sunyi: Satu Nama | 15% | Kelam | 3.4 | Satu | Abaikan RES |
| 40 J | Perisai Kabut: Tanggung | 0 | — | — | Kawan | 2 giliran, damage ke kawan dialihkan 70% ke Kelana |
| 42 | Bayang Pedang | 12% | Kelam | 1.6 | Semua | Kutuk 40% |
| 44 | Diam | 0 | — | — | Diri | Pulih 25% HP, giliran berikutnya damage ×1.5 |
| 45 J | Pendekar Sunyi: Tebas Lupa | 25% | Kelam+Fisik | 4.2 | Satu | ×2 pada Hampa/Gema |
| 45 J | Perisai Kabut: Dinding Ayah | 20% | — | — | Semua kawan | Damage ke semua kawan dialihkan 100% ke Kelana 1 ronde; Kelana tidak bisa mati ronde ini |
| 48 | Pulang Sendiri | 30% | Kelam | 3.0 | Semua | Kelana pulih 100% kalau ada musuh mati |

### 4.11 AI Musuh

Musuh biasa: tabel bobot dengan pemicu (HP rendah, kawan mati, status tertentu). Elit: bobot + satu
"sikap" yang berganti (agresif/defensif). Boss: skrip fase berdasarkan ambang HP + pola siklik yang
diumumkan (misal "Meriam Nyala mengisi...") supaya pemain bisa merespons.

---

## 5. Sistem Progresi

### 5.1 Leveling

- Level maks **60**. Tamat normal di **Lv 50–52**. Superboss diasumsikan Lv 55+.
- XP dibagi rata ke aktif (100%) dan cadangan (70%), termasuk yang pingsan.
- Anggota baru masuk di level Rimba − 1 dengan Kaca & equipment tahap wilayahnya.
- Kurva: `XP_ke_level_n = 20 * n²`. Total ke Lv 50 ≈ 858.000 XP. XP musuh diskalakan per babak
  (Babak 1: 15–600, Babak 2: 600–3.500, Babak 3: 3.500–9.000; boss 3–5× musuh biasa area).
- Naik level: stat naik, HP/MP pulih 25%, skill baru diumumkan; Lv 20/30/40/45 memicu pilihan Jalur.

### 5.2 Equipment

Slot: **Senjata** (khas per karakter), **Zirah**, **Aksesori ×2** (slot kedua dibuka Babak 2).

Senjata punya **1–3 soket Kaca** (§5.3). Tiap babak punya 3 tahap senjata toko + 1 senjata "puncak"
tersembunyi/cerita per karakter (total 4 tahap × 3 babak = 12 senjata per karakter, dengan tahap
puncak Babak 3 sebagai senjata terbaik). Contoh jalur Rimba:

| Tahap | Nama | Bonus | Soket | Dapat |
|---|---|---|---|---|
| B1-1 | Tongkat Kayu Jati | ATK+3 | 0 | Awal |
| B1-2 | Tongkat Perunggu | ATK+7 MAG+2 | 1 | Rawa/Tengara |
| B1-3 | Tongkat Kaca | ATK+11 MAG+6, Api | 1 | Tengara (setelah Lorong) |
| B1-P | Tongkat Guntur | ATK+16 MAG+10, Cahaya, +1 Bara awal | 2 | Mercusuar (peti) |
| B2-1 | Tongkat Kafilah | ATK+22 MAG+14 | 2 | Sanggar |
| B2-2 | Tongkat Nyanyi | ATK+28 MAG+20, Angin | 2 | Padasuara |
| B2-3 | Tongkat Wirasaba | ATK+36 MAG+26 | 3 | Wirasaba (peti) / Sanggar tk.3 |
| B2-P | Tongkat Juru Nyala | ATK+44 MAG+34, Cahaya, Bara maks +1 | 3 | Benteng (drop Nirmala) |
| B3-1 | Tongkat Garam | ATK+50 MAG+40 | 3 | Kapal |
| B3-P | **Pelita Pertama** | ATK+64 MAG+52, Adaptif, biaya MP −30% | 3 | Buruan Tk.5 / Pulau Hilang |

Zirah: 12 tingkat (Kain → Jubah Adiluhung), beberapa dengan resistensi elemen atau imun status.
Aksesori (~30): Cincin Anti-Racun, Gelang Kilat, Jimat Lentera (imun Lupa), Kalung Bara (+1–2 Bara awal),
Anting Pendendang (Lagu +1 giliran), Sabuk Karat (Kelana: biaya HP −30%), Lensa Juru Kaca (Curi +20%), dsb.

### 5.3 Kaca Ingatan (Soket)

Sistem "materia ringan". Kaca dipasang ke soket senjata, bisa dilepas bebas di Tukang Kaca atau di kemah.
Tiga jenis:

| Jenis | Contoh | Efek |
|---|---|---|
| **Kaca Elemen** | Kaca Api, Kaca Angin, Kaca Kelam | Serang dasar jadi elemen itu. |
| **Kaca Pasif** | Kaca Napas (MP +2/giliran), Kaca Tabah (imun Lupa), Kaca Tajam (kritikal +10%), Kaca Rakus (XP +15%), Kaca Kikir (harga toko −20%) | Pasif selama terpasang. |
| **Kaca Skill** | Kaca Sembuh (Rawat Kabut untuk siapa saja), Kaca Kilat, Kaca Pindai, Kaca Curi | Memberi satu skill dari karakter lain, biaya MP ×1.5. |

Kaca **naik tingkat** (I→III) dengan dipakai (hitung pertarungan), memperkuat efeknya. ~22 jenis Kaca.
Sumber: toko (dasar), Curi (langka), Buruan, peti, Serpihan Ingatan.

### 5.4 Item Konsumsi (ringkas)

Ramuan Daun/Akar/Sari (HP 40/120/400), Tetes/Cawan/Kendi Nyala (MP 20/60/150), Minyak Lentera
(tolak Lupa 20 giliran di area kabut), Penawar, Garam Bangun, Abu Fajar (bangkit 30%), Abu Pagi
(bangkit 100%), Bubuk 8 elemen (kekuatan 1.2, siapa pun), Suku Cadang (gadget Bagas), Dupa Sunyi
(tanpa encounter 30 langkah), Jimat Kabur, Bekal Kemah (buka adegan Kenangan tanpa kembali ke hub).

Uang: **Keping**. Sumber: pertarungan, jual barang, Buruan, Arena.

### 5.5 Serpihan Ingatan

**36 Serpihan** di seluruh dunia (peti, side quest, boss, Buruan). Tukang Kaca menukar tiap 3 Serpihan
dengan satu peningkatan permanen pilihan pemain:

- HP maks +10% (satu karakter, maks 3× per karakter)
- Bara maks +1 (maks 3×, dari 5 ke 8)
- Slot Kaca +1 pada satu senjata (maks 1× per senjata)
- Reset Jalur
- Buka satu **Kaca Skill** langka

### 5.6 Berkemah & Kenangan

Di titik save tertentu dan di kapal, party bisa **Berkemah**: pulih penuh (memakai Bekal Kemah),
lalu pilih dua anggota untuk mengobrol. Obrolan bertingkat (1–4 per pasangan/karakter), dibuka oleh
progres cerita. Kenangan membuka **Jurus Ganda**, dan Kenangan puncak tiap karakter (terjadi di Laut Lupa)
membuka skill Lv 48 mereka. Total 34 adegan Kenangan (~45 menit membaca).

### 5.7 Konten Sampingan

- **Side quest**: 18 (Babak 1: 6, Babak 2: 9, Babak 3: 3). Contoh: "Surat untuk Distrik Sunyi" (Tengara),
  "Kucing Penginapan" (Lorong Bawah), "Pendendang yang Hilang" (rantai 4 bagian lintas Babak 2–3, syarat ending 3),
  "Keluarga Bagas" (Wirasaba), "Kapal yang Tak Pernah Berlayar" (Sanggar).
- **Papan Buruan**: 11 target elit (3 Babak 1, 5 Babak 2, 3 Babak 3), tiap buruan punya mekanik unik
  dan hadiah Kaca/aksesori/Serpihan. Tingkat 5 memberi senjata Pelita Pertama.
- **Arena Kafilah** (Sanggar): 5 tingkat, 3 pertarungan beruntun tanpa item, hadiah Keping & Kaca Rakus.
- **Dungeon opsional**: Gua Bawah Danau (Babak 1), Reruntuhan Suar Ketiga (Babak 2), Pulau Hilang (Babak 3).
- **Catatan Penyala**: bestiary in-game; 100% afinitas satu babak memberi hadiah dari Tukang Kaca.

### 5.8 Sumber Kekuatan (ringkasan)

1. Level (otomatis). 2. Equipment per babak (uang berarti). 3. Kaca & soket (kustomisasi).
4. Jalur (identitas build). 5. Pengetahuan afinitas. 6. Kenangan → Jurus Ganda (konten sampingan berdampak).
7. Serpihan Ingatan (eksplorasi). 8. Komposisi 4 dari 7 dan kapan Ganti.

### 5.9 Save & Kematian

Save di lentera penjaga (2–4 per area) dan otomatis saat masuk hub/kapal. JSON, 5 slot + autosave.
Kalah = kembali ke save terakhir tanpa penalti. Boss & superboss punya opsi "Ulangi pertarungan" langsung.

---

## 6. Bestiary

### 6.1 Musuh Biasa (30)

Kolom: Lemah / Tahan-Serap / Role / Deskripsi singkat. HP adalah HP dasar; musuh varian (mis. Hampa) mengikuti level area.

**Babak 1**

| # | Nama | Area | HP | Lemah | Tahan / Serap | Role & deskripsi |
|---|---|---|---|---|---|---|
| 1 | Kunang Kelam | Hutan | 18 | Cahaya | Serap Kelam | Swarm tutorial. Kunang-kunang yang memancarkan gelap. |
| 2 | Serigala Kabut | Hutan, Rawa | 60 | Api | Tahan Es | Glass cannon cepat; menyasar yang HP-nya terendah. |
| 3 | Lumut Berjalan | Hutan, Rawa | 85 | Api | Tahan Fisik, Es | Tank pelan + Racun. |
| 4 | Hampa Pengembara | Semua | 70+ | Cahaya | Serap Kelam | Musuh ikonik; Sentuhan Lupa. Varian Petani/Pedagang/Prajurit/Warga Wirasaba/Pendeta. |
| 5 | Katak Rawa Bengkak | Rawa | 110 | Petir | Tahan Api, Es | Tank + Racun area. |
| 6 | Ikan Cermin | Danau | 50 | Petir | Tahan Es, Cahaya | Meniru satu skill terakhir yang dipakai party. Mengajarkan hati-hati memakai skill area. |
| 7 | Nelayan Hampa | Danau | 95 | Cahaya | Serap Kelam | Menjerat satu kawan (tidak bisa bertindak sampai penjerat dipukul). |
| 8 | Pengawal Karat | Lorong, Mercusuar | 140 | Petir | Tahan Fisik; Imun Racun, Lupa | Anti-fisik; Sela jadi tank, Lintang jadi pembunuh. |
| 9 | Bayang Arsip | Lorong, Benteng | 90 | Api | Tahan Petir, Es | Support: buff & heal musuh, Bisu. Prioritas target. |
| 10 | Kelelawar Kristal | Tambang | 55 | Petir | Tahan Kelam | Evasif, kuras MP, Tidur. |
| 11 | Penambang Terlupa | Tambang | 160 | Es | Tahan Api | Hard hitter pelan. |
| 12 | Pelita Padam | Mercusuar, Adiluhung | 120 | Kelam | **Serap Cahaya**, Tahan Api | Pembalik aturan; menghukum autopilot Cahaya. |

**Babak 2**

| # | Nama | Area | HP | Lemah | Tahan / Serap | Role & deskripsi |
|---|---|---|---|---|---|---|
| 13 | Elang Badai | Celah Angin | 210 | Bumi | Tahan Angin, Petir | Terbang: evasi 40% sampai Berat. Mengajarkan Bumi. |
| 14 | Kambing Batu | Celah Angin | 320 | Angin | Serap Bumi, Tahan Fisik | Tank yang menyeruduk; Goyah kalau di-Angin. |
| 15 | Kalajengking Abu | Dataran Abu | 260 | Es | Tahan Api, Bumi | Racun kuat + Berat. |
| 16 | Hantu Kafilah | Dataran Abu | 240 | Cahaya | Serap Kelam, Tahan Angin | Mencuri item party (bisa direbut lewat Curi). |
| 17 | Cacing Abu Muda | Dataran Abu | 400 | Es, Petir | Tahan Fisik, Bumi | Menelan satu kawan 2 giliran. |
| 18 | Pohon Gema | Hutan Nyanyi | 350 | Api | Tahan Angin, Bumi | Mengulang skill Ratih untuk musuh (Lagu musuh). |
| 19 | Burung Peniru | Hutan Nyanyi | 180 | Bumi | Tahan Angin | Meniru status yang sedang diderita party ke kawan lain. |
| 20 | Pendeta Ordo | Hutan, Benteng | 300 | Kelam | Tahan Cahaya | Manusia; Bisu & Kutuk; memanggil Pelita Padam. |
| 21 | Warga Wirasaba (Hampa) | Wirasaba | 330 | Cahaya | Serap Kelam | Datang 4–5 sekaligus; masing-masing mengulang satu "kebiasaan" (menawar = curi Keping, menyapu = Buta). |
| 22 | Konstruk Kaca | Wirasaba, Benteng | 480 | Petir | Tahan Fisik, Api; Imun status | Menyerap elemen terakhir yang mengenainya (jadi Serap 2 giliran). |
| 23 | Cermin Berjalan | Wirasaba | 260 | Bumi | Serap Cahaya, Kelam | Memantulkan sihir single-target ke pengguna; harus dipukul fisik/area. |
| 24 | Kepiting Garam | Danau Garam | 420 | Petir | Tahan Es, Bumi, Fisik | Cangkang: Tahan semua sampai di-Pecah (meter 40). |
| 25 | Hampa Beku | Danau Garam | 360 | Api | Serap Es, Kelam | Menyerap MP tiap serangan. |
| 26 | Pemanen Ordo | Menara Terapung, Benteng | 450 | Angin | Tahan Cahaya, Fisik | Menyedot 1 Bara tiap 2 giliran. Prioritas target. |
| 27 | Pelita Hidup Muda | Benteng | 520 | Kelam | Serap Cahaya, Api | Meledak saat mati (damage Cahaya semua). |

**Babak 3**

| # | Nama | Area | HP | Lemah | Tahan / Serap | Role & deskripsi |
|---|---|---|---|---|---|---|
| 28 | Gema Pesta | Laut Lupa | 600 | Berganti tiap giliran (diumumkan) | — | Kelemahan berputar; Bara mudah dikumpulkan tapi mereka menyerang area. |
| 29 | Gema Prajurit | Laut Lupa, Adiluhung | 800 | Kelam | Tahan Fisik, Cahaya | Formasi: DEF ×2 selama ≥2 hidup. |
| 30 | Hampa Adiluhung | Adiluhung | 900 | Cahaya & Kelam (keduanya) | Serap Api, Es, Petir, Angin, Bumi | Hanya bisa dilukai Cahaya/Kelam/Fisik; menguji build akhir. |

### 6.2 Boss Utama (16)

| # | Boss | Area | Lv | Lemah | Mekanik utama |
|---|---|---|---|---|---|
| 1 | Hampa Penjaga Hutan | 1 | 4 | Cahaya, Api | Tutorial: memanggil Kunang tiap 3 giliran; Raung Lupa. |
| 2 | Raja Katak Lumpur | 2 | 8 | Petir | Racun area tiap 4 giliran; menelan kawan saat HP<50% (lepas kalau Goyah). |
| 3 | Ular Cermin | 3 | 12 | Petir, Kelam | Tiap 3 giliran "memantulkan" satu party member: klon yang memakai skill mereka. Klon mati kalau aslinya Jaga. |
| 4 | Kapten Rangga | 4 | 15 | — | "Tandai" lalu Tebas Eksekusi ×3; fase 2 imun Provokasi, dua aksi per giliran. |
| 5 | Penambang Raksasa Terlupa | 5 | 19 | Berganti tiap 3 giliran | Kristal punggung menyerap satu elemen; kelemahan = lawannya. |
| 6 | Penjaga Mercusuar | 6 | 21 | Petir, Kelam | Meriam Nyala (isi 2 giliran, batal jika Goyah/Pecah); memanggil Pelita Padam. |
| 7 | Adipati Baskara → Kelam Berwajah | 6 | 23 | — → Cahaya/Kelam bergantian | F1: Titah (Lupa 3 giliran) + 2 Pengawal Karat. F2: bergantian kabut/Nyala tiap 4 giliran; Padamkan (HP semua jadi 1) di <25%. |
| 8 | Garuda Kelabu | 7 | 26 | Bumi | Terbang; hanya bisa dipukul fisik saat Berat; Badai Sayap Buta semua. |
| 9 | Cacing Abu Purba | 8 | 29 | Es, Petir | Segmen: 3 bagian tubuh, kepala imun sampai 2 segmen mati; menelan kawan. |
| 10 | Sunan Wirya | 9 | 32 | Kelam | Khotbah: Bisu semua tiap 3 giliran (Ratih diam); 2 Bayang Arsip yang terus ia bangkitkan. |
| 11 | Penjaga Suar Wirasaba | 10 | 34 | Petir | Menyerap elemen terakhir; meter Ketahanan 150; Meriam ganda. |
| 12 | Kelana (Hampa Berzirah) | 10 | 36 | Cahaya (tapi cerita: pemain diminta *tidak* membunuhnya) | Pertarungan bertahan 8 giliran; tiap kali Lintang bertindak, Ketahanan −20; Pecah = ia berhenti. Membunuhnya tetap mungkin, tapi mengunci ending 1 dan 3 (game memperingatkan). |
| 13 | Nyi Pandansari | 11 | 39 | Angin | Kaca Pemanen menyedot 2 Bara tiap giliran; harus dihancurkan dulu (target terpisah, 300 HP). |
| 14 | Juru Nyala Nirmala → Pelita Hidup | 12 | 43 | — → Kelam (Serap Cahaya, Api) | F1: Titah Ordo (Kutuk semua), memanggil Pemanen. F2: Nyala Penuh: tiap 3 giliran damage Cahaya besar semua; Kelana harus dijaga dari heal Cahaya. |
| 15 | Gema Guntur | 13 | 47 | Api → Cahaya → Kelam (tiap fase) | Tiga fase = tiga ingatan Rimba tentang Guntur. Nyala Penjaga (heal boss penuh) kalau Bara party ≥5 saat giliran boss: pemain harus *membelanjakan* Bara. |
| 16 | Sang Pelita Pertama | 14 | 52 | F1: Cahaya. F2: Kelam. F3: hanya Jurus Ganda & Jurus Empat yang melukai (serang biasa 1 damage) | F1 "Yang Dibakar": Kutuk & Lupa. F2 "Yang Mengendap": Serap semua elemen kecuali Kelam; memanggil Gema party (klon). F3 "Yang Ingin Dilupakan": HP 9.999; tiap giliran menghapus satu skill acak party sampai pertarungan usai; Lagu Ratih mengembalikan satu. Padamkan Dunia di HP<15%: semua HP jadi 1 + Bara jadi 0; Kenangan yang terbuka memberi Bara balik (1 per Kenangan puncak). |

Mid-boss tambahan: Tujuh Penjaga Suar (Adiluhung, 7 gelombang konstruk masing-masing satu elemen).

### 6.3 Superboss & Buruan Puncak

| Nama | Lokasi | Lv | Mekanik |
|---|---|---|---|
| **Sang Penenun** | Pulau Hilang | 58 | Menenun ulang afinitas party (kelemahan party berubah tiap 5 giliran); 30.000 HP; Ketahanan 300. Hadiah: Kaca Penenun (Serang dasar adaptif). |
| **Cacing Abu Ibu** | Buruan Tk.5, Dataran Abu | 55 | 5 segmen, regenerasi kalau kepala tak dipukul tiap giliran. Hadiah: senjata Pelita Pertama (Rimba) / Serpihan ×3. |

### 6.4 Filosofi Bestiary

Setiap musuh biasa mengajarkan **satu hal** (afinitas, status, prioritas target, atau pembalikan
aturan). Setiap boss menguji pelajaran areanya plus **satu mekanik baru** yang berhubungan dengan
cerita area itu (Ular Cermin = pantulan ingatan, Kelana = pertarungan yang tidak untuk dimenangkan,
Pelita Pertama = kehilangan skill = lupa).

---

## 7. Antarmuka Teks

```
════════════════════════════════════════════════════════════════════
 KOTA KACA WIRASABA — Distrik Pasar
────────────────────────────────────────────────────────────────────
 Warga Wirasaba  A  [████░░░░░░]  lemah: Cahaya   serap: Kelam
 Warga Wirasaba  B  [██████████]  lemah: Cahaya   serap: Kelam
 Konstruk Kaca   C  [████████░░]  lemah: Petir    KETAHANAN [███░░]
────────────────────────────────────────────────────────────────────
 Rimba   HP 412/460  MP  58/ 90   Bara ◆◆◆◇◇◇
 Sela    HP 590/610  MP  22/ 40   [Provokasi]
 Bagas   HP 380/420  MP  41/ 75   SC 14   [Lentera Portabel 2]
 Ratih   HP 300/350  MP  70/110   ♪ Lagu Gugah (2)
 cadangan: Lintang, Rangga
────────────────────────────────────────────────────────────────────
 Giliran Bagas.
  1) Serang  2) Skill  3) Item  4) Jaga  5) Ganti  6) Bara
> _
════════════════════════════════════════════════════════════════════
```

Prinsip: satu layar = satu keputusan. Semua informasi yang dibutuhkan untuk memutuskan ada di layar.

### 7.1 Antarmuka web (tambahan di luar desain awal)

Selain terminal, permainan bisa dimainkan di browser (`python -m pelita --web`). Mesinnya sama
persis; yang berbeda hanya lapisan tampilan. Prinsip §7 tetap berlaku: satu layar, satu keputusan.

Yang ditampilkan secara grafis:

| Unsur | Tampilan web |
|---|---|
| Lokasi | Panorama SVG per area (desa, hutan berkabut, rawa, danau, kota, saluran, tambang, menara) |
| Kabut | Lapisan kabut di panorama + penghitung sisa Minyak Lentera |
| Musuh | Kartu dengan bar HP, meter Ketahanan, label kelemahan/tahan/serap dari Catatan Penyala |
| Party | Kartu dengan potret, bar HP/MP, label status |
| Bara | Deretan belah ketupat yang menyala |
| Damage | Angka melayang di atas kartu yang terkena; merah untuk biasa, kuning untuk LEMAH |
| Dialog | Nama pembicara di kolom kiri, kalimat di kanan; narasi dibedakan dari log pertarungan |

Seni dibuat prosedural (SVG dari kode), tanpa berkas aset dan tanpa internet. Area baru otomatis
memakai panorama bawaan sampai seni khususnya ditambahkan.

**Ponsel.** Antarmuka web adalah cara bermain di HP: tata letak menyesuaikan lebar layar dan
orientasi, target sentuh minimal 48 px, panorama menyusut saat bertarung agar arena dan log tetap
muat, dan halaman bisa dipasang ke layar utama Android (PWA, mode layar penuh). Server dijalankan
dengan `--lan` agar bisa dibuka dari HP di Wi-Fi yang sama, atau langsung di HP lewat Termux.

### 7.2 Latar bergambar & visual storytelling

Di atas panorama SVG prosedural ada **lapisan latar bergambar**: satu gambar per ruang, yang
berubah mengikuti kondisi dunia. Tujuannya bukan mengubah permainan jadi visual novel, melainkan
membuat pemain **melihat** perubahan yang selama ini hanya dibacanya.

Tiga tingkat visual (biar produksi gambarnya tetap masuk akal):

| Tingkat | Kapan | Bentuk |
|---|---|---|
| 1 — Latar ruang | Dialog dan menu biasa | Gambar ruang yang sedang ditempati; tidak berganti per kalimat |
| 2 — Adegan | Peristiwa penting di tengah skrip | `{"adegan": {"latar": "...", "efek": "zoom"\|"flash"\|"shake"\|"gelap"}}` |
| 3 — Ilustrasi | Peristiwa besar cerita | `{"ilustrasi": "events/...", "teks": "..."}` — layar penuh, lalu kembali ke permainan |

**Latar mengikuti kondisi dunia.** Tiap ruang boleh punya `latar_varian`: daftar
`{"if": <kondisi>, "latar": "..."}` yang dievaluasi dengan bahasa kondisi yang sama dengan skrip
(`GameState.check`). Varian pertama yang cocok dipakai. Contoh Warung Bu Ratna: ramai di awal,
`warung_sepi` setelah Pak Guntur hilang, `warung_pulih` setelah desa bangkit lagi.

**Urutan pemilihan:** varian yang cocok → `latar` ruang (dipakai kalau beberapa ruang berbagi
gambar) → bawaan `<area>/<ruang>` → `latar` area.

**Berkas.** `pelita/web/static/assets/backgrounds/<path>.webp`, 1600×900. Daftar lengkap beserta
deskripsi adegan untuk yang menggambar ada di `pelita/data/world/latar.json`; `tools/daftar_latar.py`
mengubahnya jadi daftar belanja beserta status "sudah ada / belum".

**Kalau gambarnya belum ada, tidak ada yang rusak.** Server hanya mengirim URL untuk berkas yang
benar-benar ada; ruang tanpa gambar tetap memakai panorama prosedural, dan peristiwa besar tetap
tampil sebagai layar gelap berteks. Karena itu gambar bisa diisi bertahap tanpa menyentuh kode,
dan permainan tetap bisa dimainkan tanpa satu pun berkas gambar.

**Yang sengaja tidak dibuat:** siklus waktu nyata (pagi/siang/malam) dan musik. Dunia ini gelap
karena Nyala melemah, bukan karena jam — jadi perubahan langit diikat ke progres cerita, bukan ke
waktu. Audio ditunda sebagai pekerjaan tersendiri agar tidak menggemukkan APK setengah jadi.

---

## 8. Yang Sengaja TIDAK Dimasukkan

- Tidak ada crafting bebas (upgrade Kaca lewat pemakaian, bukan resep).
- Tidak ada romance, tidak ada sistem job/kelas bebas (Jalur cukup).
- Tidak ada peta dunia "berjalan"; perpindahan lewat menu.
- Tidak ada minigame selain Arena.
- Tidak ada New Game+ di rilis pertama (kandidat pasca-rilis: NG+ dengan Kaca terbawa).
- Tidak ada party aktif lebih dari 4.

---

## 9. Rencana Pembangunan Bertahap

| Tahap | Isi | Hasil |
|---|---|---|
| 0 | Arsitektur & data: modul `combat`, `party`, `world`, `ui`, `data/` (JSON untuk skill, musuh, item, Kaca) | Kerangka yang bisa dites — **selesai** |
| 1 | Prototipe combat: 3 karakter, 5 musuh, formula §4.7, Bara, Pecah | Rasio "2–3 pukulan" terverifikasi — **selesai** (`tools/calibrate.py`) |
| 2 | **Babak 1 lengkap** (area 1–6, 4 karakter, 7 boss, 6 side quest) | Game 6,5 jam yang bisa tamat — **selesai** (lihat §9.1) |
| 3 | Sistem lanjutan: Ganti/cadangan, Jalur, Kaca, Berkemah/Kenangan, Buruan, Arena | Fondasi Babak 2 — **selesai** (lihat §9.2) |
| 4 | Babak 2 (area 7–12, 3 karakter baru, 7 boss) | Game 15 jam — **selesai** (lihat §9.3) |
| 5 | Babak 3 + 3 ending + superboss | Game 20 jam — **selesai** (lihat §9.4) |
| 6 | Kalibrasi harga, dungeon opsional, side quest sisa, penulisan ulang naskah, playtest | Rilis |

Tahap 2 adalah tonggak terpenting: kalau Babak 1 terasa enak dimainkan, sistemnya terbukti dan
Babak 2–3 tinggal soal isi. Kalau tidak, lebih murah membetulkannya di sana.

### 9.1 Catatan implementasi Tahap 2 (Babak 1)

Yang dibangun: 8 area (Pelita Rendah, Hutan Kelabu, Rawa Suar, Danau Cermin, Tengara, Lorong Bawah,
Tambang, Mercusuar; 55 ruang), 8 boss, 4 party member + Pak Guntur sebagai tamu, 5 side quest
(Kirana, Yang Hilang di Telaga, Hampa Pasar Malam, Surat Distrik Sunyi, Kucing Penginapan),
5 toko, 3 puzzle (tiga lentera, tiga tuas, lift Bagas), 12 Serpihan Ingatan, save/muat 5 slot.
`python -m pelita` memainkannya; `python tools/walkthrough.py --seed N` menjalankan pemain
otomatis dari prolog sampai "Akhir Babak 1" dan mencetak level party di tiap boss.

Penyimpangan dari desain awal, dan alasannya:

- **Lintang bergabung sebelum Raja Katak**, bukan sesudahnya. Boss itu "mengajarkan Petir
  Lintang", jadi ia harus sudah ada. Urutan Rawa: puzzle → inti Suar (Lintang) → kolam (boss).
- **XP musuh = 6·L², boss = 30·L²; Keping = L², boss 5·L².** Nilai awal (15–600) terlalu kecil
  untuk kurva 20·n²: party tidak sampai level boss. Dengan angka ini pemain otomatis tiba di
  Rangga pada Lv 12, Tambang Lv 18, Baskara Lv 23, tamat Lv 24: sesuai rentang §2.2.
- **Pertarungan terskrip** (sekali, saat pertama masuk ruang) ditambahkan di 9 ruang jalur utama
  sebagai penjaga pacing, karena encounter acak saja tidak menjamin XP minimum.
- **Boss dikalibrasi ulang ke atas** setelah walkthrough: Penambang 1.900 HP, Penjaga 2.200,
  Baskara 1.500 (+2 Pengawal Istana), Kelam Berwajah 2.600. Hasil: boss akhir 4–10 ronde.
- **Kelam Berwajah** mengganti "fase" Cahaya/Kelam dengan rotasi tiap 4 giliran (sistem yang sama
  dengan Penambang Raksasa). Ular Cermin memakai pergantian afinitas per fase, bukan klon.
- **Ikan Cermin belum meniru skill**; ia menyerang Es biasa. Tukang Kaca dan penukaran Serpihan
  Ingatan ditunda ke Tahap 3 (soket Kaca). Gua Bawah Danau (dungeon opsional) belum dibuat.
- **Lentera penjaga memulihkan HP/MP penuh** selain menyimpan, supaya boss selalu bisa didekati
  dalam kondisi segar tanpa grinding item.

### 9.2 Catatan implementasi Tahap 3 (sistem lanjutan)

Enam sistem §4.9, §5.3, §5.5, §5.6, §5.7 dibangun di atas Babak 1 yang sudah ada, semuanya
data-driven dan bisa dipakai pemain sekarang juga.

**Kaca Ingatan** (`pelita/data/kaca.json`, 21 jenis: 7 elemen, 10 pasif, 4 skill). Soket datang dari
senjata (`slots` di `items.json`) plus bonus Serpihan. Kaca Elemen menimpa elemen serangan dasar,
Kaca Pasif memberi `Passive` (pengali stat, regen MP, kritikal, XP, potongan harga, potongan biaya MP,
Bara awal, peluang Curi, imun status), Kaca Skill meminjam skill karakter lain dengan biaya MP ×1.5.
Tingkat I→III naik dari **jumlah pertarungan** (12 dan 36) dan menguatkan efek numerik ×1.5/×2,
sekaligus membuat pinjaman skill lebih murah (×1.25 lalu ×1.0). Ganti senjata tidak menghilangkan
Kaca: yang tidak muat dikembalikan ke simpanan.

**Jalur** (`pelita/data/jalur.json`, 14 jalur). Empat karakter Babak 1 memilih di Lv 20 dan mendapat
3 skill + 1 pasif; Rangga/Ratih (Lv 30) dan Kelana (Lv 40) sudah punya data dengan 2 skill per jalur,
menunggu babaknya. Pilihan kedua Lv 45 belum dibuat (Babak 3). Reset lewat Tukang Kaca.

**Cadangan & Ganti.** Empat nama teratas `state.party` adalah barisan aktif; sisanya cadangan yang
dapat **70% XP**. Aksi **Ganti** menukar penyerang dengan cadangan (satu giliran, status yang keluar
dibuang). Rimba terkunci di barisan aktif karena ia pemegang Bara. Pertukaran di dalam pertarungan
tidak mengubah urutan party di luar pertarungan — hanya HP/MP yang ikut tersimpan.

**Tukang Kaca** (Mpu Sarwa, Tengara). Pasang/lepas Kaca, beli Kaca, dan tukar 3 Serpihan Ingatan jadi
HP maks +10% (maks 3× per karakter), Bara maks +1 (sampai 8), soket +1 per senjata, reset Jalur, atau
satu Kaca Skill langka. Bongkar-pasang Kaca di luar bengkel hanya bisa **saat berkemah**.

**Berkemah & Kenangan** (`pelita/data/world/kenangan.json`, 9 adegan Babak 1). Satu Bekal Kemah di
lentera penjaga mana pun memulihkan party dan membuka obrolan berpasangan. **Jurus Ganda sekarang
terkunci sampai Kenangan-nya dilihat** — pemain otomatis menamatkan Babak 1 tanpa satu pun Jurus
Ganda, jadi sistemnya benar-benar bonus, bukan syarat.

**Papan Buruan** (`buruan.json`, 3 kontrak) dan **Arena Kafilah** (`arena.json`, 3 tingkat) ditempel di
Dermaga Kota Tengara setelah Ular Cermin kalah. Tiga target elit baru di `enemies.json`
(Kunang Raja, Nelayan yang Tidak Pulang, Zirah Tanpa Nama), masing-masing dengan mekanik khas:
kawanan lalu aksi ganda; jerat + isian yang bisa dibatalkan Goyah/Pecah; kebal Provokasi + Tandai dan
eksekusi. Arena melarang item (`Battle(allow_items=False)`) dan upahnya hanya diberikan sekali per tingkat.

Penyimpangan dari desain awal, dan alasannya:

- **Arena ditaruh di Tengara, bukan Sanggar.** Sanggar baru ada di Babak 2; kafilah yang singgah di
  dermaga memberi sistemnya tempat sekarang. Dua tingkat sisanya (4–5) menyusul bersama Sanggar.
- **Tingkat Kaca dihitung per jenis, bukan per keping.** Satu tabel `kaca_uses` di state jauh lebih
  sederhana untuk disimpan daripada instance per keping, dan efeknya sama untuk pemain.
- **Pasif Jalur dan Kaca memakai satu tipe `Passive` yang sama.** Satu jalur kode untuk dua sistem;
  menambah efek baru cukup sekali.
- **Kaca Kikir bekerja dari seluruh party**, bukan hanya anggota aktif: potongan harga terbaik yang
  dipakai. Menyiasati ini dengan bongkar-pasang di kemah tidak menyenangkan siapa pun.
- **Pemain tidak dipaksa memilih Jalur saat naik level.** Naik level hanya mengumumkan "bisa memilih
  Jalur"; pilihannya di menu Party, supaya pertarungan tidak terpotong dialog build.

### 9.3 Catatan implementasi: menu sebagai data (perbaikan "permainan sangkut")

Bug yang ditemukan saat bermain di APK: di Warung Bu Ratna pemain bisa membeli tapi tidak bisa
keluar ke jalan desa. Penyebabnya bukan di toko itu, melainkan di lapisan antarmuka. Klien web
dulu **menebak** pilihan dari teks yang sudah dicetak mesin permainan (pola `  N) label`), jadi:

- menu yang memadatkan beberapa opsi dalam satu baris (`1) Beli   2) Jual   0) Pergi`) hanya
  menghasilkan **satu** tombol — dan itu bukan tombol keluarnya;
- menu yang menuliskan judul kolomnya sendiri (`Nomor) Equipment & skill   [S]usun barisan ...`)
  tidak menghasilkan tombol keluar sama sekali.

Di terminal tidak terasa, karena di sana pemain mengetik angkanya sendiri; di layar sentuh yang
hanya punya tombol, pemain terkurung.

Perbaikannya bukan menambal tiap menu, tapi menghapus tebak-tebakannya: **opsi sekarang dibawa
sebagai data.** `pelita/ui/menu.py` (`Option`, `Menu`) adalah satu-satunya tempat daftar pilihan
disusun, dan `IO.menu()` yang memutuskan penyajiannya — terminal mencetak satu opsi per baris,
web mengirim daftarnya apa adanya. Konsekuensinya:

- **Jalan keluar ikut secara bawaan.** `Menu()` selalu menambahkan `0) Kembali`; menu yang memang
  tidak boleh ditinggalkan harus menyebut alasannya lewat `Menu.no_back("aksi pertarungan")`.
  Lupa memberi tombol keluar sekarang butuh tindakan sengaja, bukan kelalaian.
- **Tidak ada lagi prompt jawaban bebas.** Pertanyaan ya/tidak (`IO.confirm`) dan jeda Enter
  (`IO.pause`) punya jenis prompt sendiri (`confirm`, `enter`) yang selalu bertombol. "Tukar
  dengan siapa?" di Susun Barisan — dulu satu-satunya prompt tanpa daftar — kini bermenu juga.
- **Keterangan panjang tidak ikut jadi tombol.** `Option.detail` (deskripsi Buruan, stat karakter
  di menu Party) tercetak sebagai baris keterangan di terminal dan masuk log di web.
- **Menu terkunci bukan tombol.** Tingkat Arena yang belum terbuka masuk sebagai keterangan judul
  (`Menu.info`), jadi pemain tidak menekan tombol yang pasti ditolak.
- **Judul menu juga data.** Lihat di bawah.

#### Judul menu: `Menu.title`, bukan `io.line()`

Gejala kedua dari bug yang sama, terlihat di layar HP: header toko
(`═══ Warung Bu Ratna ═══  Keping: 38`) tercetak sekali lagi **tiap** menu digambar ulang, jadi
log penuh ulangan. Sebabnya sederhana — menu berulang di dalam `while True`, dan headernya ditulis
dengan `io.line()`, yang di web berarti *menambah* baris log.

Perlakuannya kini disamakan dengan deskripsi ruang, yang memang hanya ditulis saat pemain
benar-benar pindah: judul dibawa sebagai data di `Menu.title` / `subtitle` / `note` dan ikut di
dalam payload `prompt`, bukan sebagai event `log`. Karena tiap prompt **mengganti** panel
pilihan di klien, judul yang digambar ulang tiap putaran tidak bisa menumpuk — bukan karena
ada yang menyaring ulangannya, tapi karena ia tidak pernah masuk log sejak awal.

Terminal tidak berubah: `IO.render_options()` tetap mencetak `═══ Judul ═══  Keterangan` di atas
daftar opsi tiap kali menu digambar, karena di layar bergulir itulah yang diharapkan pemain.

`tests/test_menu_web.py` menjaga kelas bug ini, bukan satu kasusnya: pemeriksa dipasang ke `WebIO`
yang asli dan berjalan di **tiap** prompt. Satu tes menamatkan seluruh Babak 1 lewat lapisan web;
tes lain melepas crawler yang menekan setiap tombol yang ditemukannya (tanpa daftar menu yang
ditulis tangan) dan keluar lewat tombol keluar tiap menu — kalau sebuah menu tidak bisa
ditinggalkan, crawler-nya yang tersangkut dan tesnya gagal.

Dua jaring tambahan ikut berjalan di tiap event, jadi berlaku untuk semua menu yang tersentuh
tes mana pun:

- **`periksa_log`** — satu baris log tidak boleh memuat lebih dari satu penanda `N)`. Ini
  menangkap menu yang mencetak pilihannya sendiri tanpa lewat `Menu` sama sekali, yang tidak
  akan terlihat dari daftar opsi (daftarnya kosong atau tidak lengkap).
- **`judul_bukan_log`** — judul sebuah prompt tidak boleh juga muncul sebagai baris log. Ini
  yang menjaga agar header menu tidak kembali ditulis dengan `io.line()`.

### 9.3 Catatan implementasi Tahap 4 (Babak 2)

Enam area baru (Celah Angin, Dataran Abu & Sanggar, Hutan Nyanyi & Padasuara, Kota Kaca Wirasaba,
Danau Garam & Menara Terapung, Benteng Ordo Pelita), 41 ruang, 7 boss, 15 musuh biasa, dan tiga
anggota party terakhir. `python tools/walkthrough.py --babak 2 --seed 5` menjalankannya dari Kaki
Celah sampai Nirmala jatuh; party tamat di **Lv 42–45**, sesuai rentang §2.3.

**Mekanik baru di mesin** (semuanya dipakai isi Babak 2, bukan dibangun untuk nanti):

- **Lagu** Ratih dan **Panji** Rangga: status ber-regen yang memulihkan tiap akhir giliran
  pemiliknya. Hanya satu Lagu boleh aktif; memasang lagu baru mengganti yang lama.
- **Tanggung** Kelana: 70% damage yang mengenai kawan pindah ke Kelana.
- **Perintah Terakhir** Rangga: satu kawan bertindak lagi segera, sekali per pertarungan.
- **Sifat musuh** (`terbang`, `hampa`, `konstruk`, `pantul`) dengan tag skill `vs:<sifat>:<pengali>`;
  Badai Bulu Ratih memakainya untuk melukai musuh terbang 1,5×.
- Musuh bisa **merampas item** dan **menyedot Bara**, **meledak saat mati** (`on_death`), dan
  **Cermin Berjalan** memantulkan sihir satu sasaran kembali ke penggunanya.

Penyimpangan dari desain awal, dan alasannya:

- **Babak 1 tidak lagi berakhir di layar judul.** Ceritanya mengalir langsung ke Celah Angin, dan
  Rangga bergabung di sana. Walkthrough Babak 1 karena itu berhenti di batas babak lewat penanda
  `#stop:babak2_mulai`, bukan lewat `end_chapter`.
- **14 pertarungan terskrip** ditambahkan sebagai penjaga pacing (pola yang sama dengan §9.1), dan
  encounter acak dinaikkan 6 poin. Tanpa itu party tiba di Nirmala sekitar Lv 36 dan kalah.
- **Nirmala fase 2 bertindak sekali per giliran**, bukan dua kali. Dua aksi ditambah Nyala Penuh
  area membunuh party dalam lima ronde tanpa ruang bereaksi; §6.2 memang hanya menyebut "damage
  Cahaya besar tiap 3 giliran".
- **Kebijakan otomatis party tidak lagi menyembuhkan kawan yang terkena Kutuk**, dan membersihkan
  kutukannya dulu kalau bisa. Bug ini menewaskan party di Nirmala: heal 248 berbalik jadi damage.
- **Arena dan papan Buruan Babak 2 ditaruh di Sanggar**, sesuai §2.3 — ini sekaligus menutup catatan
  §9.2 bahwa dua tingkat Arena terakhir menunggu hub kedua. Buruan Babak 2 baru 4 dari 5 yang
  direncanakan; sisanya menyusul bersama dungeon opsional.
- **Kelana bergabung lewat cerita, bukan lewat kemenangan.** Boss "Hampa Berzirah" tetap bisa
  dibunuh, tapi jalur yang disiapkan adalah membuatnya berhenti; konsekuensi ending-nya baru
  dipasang di Babak 3.
- **Keping menumpuk** (±110.000 di akhir Babak 2). Harga toko Babak 2 belum mengejar; ini dicatat
  sebagai pekerjaan kalibrasi Tahap 6, bukan bug.

### 9.4 Catatan implementasi Tahap 5 (Babak 3)

Dua area baru (Laut Lupa, Pusar Kabut & Kota Adiluhung), 25 ruang, boss Gema Guntur, mid-boss
Tujuh Penjaga Suar, final Sang Pelita Pertama, superboss Sang Penenun, Buruan puncak Cacing Abu
Ibu, 7 adegan Kenangan puncak, 56 skill baru (14 puncak Jalur Lv 45, 4 skill bawaan Lv 47,
Jurus Empat, dan 37 skill musuh), dan **tiga ending yang masing-masing punya segmen mainnya
sendiri**.

```
python tools/walkthrough.py --babak 3 --seed 3                     ending "Menyalakan Kembali"
python tools/walkthrough.py --babak 3 --ending kembali --seed 3    ending "Mengembalikan"
python tools/walkthrough.py --babak 3 --ending dendang --seed 3    ending "Mendendangkan"
python tools/walkthrough.py --babak 3 --ending kembali --bunuh-kelana
```

Party tamat di **Lv 51–52**, sesuai rentang §2.4. Lama boss: Gema Guntur 11–19 ronde (lihat
catatan Nyala Penjaga di bawah), Tujuh Penjaga Suar 3–5 ronde per gelombang, Sang Pelita
Pertama 14–16 ronde, segmen bertahan ending 1 tepat 6 ronde, Kabut Terakhir tepat 8 lagu.

**Mekanik baru di mesin** (semuanya dipakai isi Babak 3, bukan dibangun untuk nanti):

- **Jurus Empat** (`tags: ["jurus_empat"]`): satu-satunya jurus Bara tanpa daftar `users` —
  syaratnya keempat anggota barisan aktif hidup, Bara maks 8, dan sekali per pertarungan untuk
  seluruh party (`Battle.used_once_party`, bukan `Combatant.used_once`).
- **`elemen_kelemahan`**: tiap sasaran dipukul dengan elemen kelemahannya sendiri.
- **`formasi`** (Gema Prajurit): DEF/RES ×2 selama dua atau lebih yang sejenis masih berdiri.
- **`nyala_penjaga:N`** (Gema Guntur): boss pulih penuh kalau Bara party ≥ N saat gilirannya.
- **`hanya_jurus`** (sifat fase, bukan sifat musuh): apa pun selain Jurus Ganda/Jurus Empat
  hanya menggores 1 damage. Pukulan kelemahan tetap memberi +1 Bara, jadi serangan biasa
  berubah fungsi dari "melukai" jadi "membiayai".
- **`hapus_skill`** dan tag **`lagu`**: skill party hilang satu per satu; tiap Lagu Ratih
  mengembalikan satu (`Battle.skill_terhapus`).
- **`padamkan_dunia`**: HP semua jadi 1, Bara jadi 0, lalu +1 Bara per Kenangan puncak yang
  sudah dilihat (`Battle.bara_kenangan`, dihitung dari `kenangan.json` bertanda `"puncak": true`).
- **`tenun_afinitas`** (Sang Penenun) dan pasif **`serang_adaptif`** (hadiah Kaca Penenun):
  keduanya menulis ulang afinitas — yang pertama ke party, yang kedua ke serangan dasar.
- **`regen_pct`** pada musuh + sifat `kepala`: segmen Cacing Abu Ibu pulih tiap ronde selama
  kepalanya tidak dipukul.
- **Pertarungan bertahan** (`{"battle": [...], "bertahan": N}`): menang saat ronde ke-N lewat,
  dan gelombangnya berdiri lagi tiap kali dihabisi — menghabisi lawan bukan jalan keluarnya.
- **`{"lucuti": true}`** dan **`{"barisan": [...]}`**: perintah skrip untuk ending 2 dan 3.
- **`{"bara": 8}`**: menaikkan Bara maks lewat cerita, bukan cuma lewat penukaran Serpihan.

Penyimpangan dari desain awal, dan alasannya:

- **Babak 2 tidak lagi berakhir di layar judul.** Sama seperti batas Babak 1 (§9.3): setelah
  Nirmala jatuh, party langsung berdiri di dek Kapal Lentera. `end_chapter` sekarang hanya
  dipakai sekali di seluruh permainan — untuk ending yang dipilih pemain. Walkthrough Babak 2
  karena itu berhenti lewat `#stop:babak_2_selesai`.
- **Tujuh Penjaga Suar = tujuh pertarungan beruntun tanpa jeda**, bukan satu pertarungan berisi
  tujuh musuh. Batas arena adalah lima musuh (`MAX_MUSUH`), dan "bergelombang" di §2.4 memang
  menggambarkan urutan. Tidak ada pemulihan di antaranya, jadi terasanya tetap satu pertarungan
  panjang; pemulihan penuh baru diberikan setelah gelombang ketujuh.
- **Sang Pelita Pertama punya empat fase, bukan tiga.** Fase "Padamkan Dunia" dipisah dari fase
  3 supaya pemicunya benar-benar HP < 15% seperti yang ditulis §6.2, bukan sekadar satu langkah
  di dalam pola fase 3.
- **HP boss dikalibrasi ulang ke atas setelah walkthrough**, pola yang sama dengan §9.1: Gema
  Guntur 4.207 → **7.000**, Sang Pelita Pertama 9.999 → **15.000**, tiap Penjaga Suar 680 →
  **2.200**, Cacing Abu Ibu 2.919 + 4×1.022 → **6.000 + 4×2.000**. Sebabnya rumus §4.7
  memakai `off(L)` sebagai *stat dasar* party, sementara di Lv 50 senjata Babak 3 sendiri
  menyumbang 30–40% serangan; tanpa penyesuaian ini boss akhir jatuh dalam 7 ronde.
  Angka 9.999 di §6.2 tetap benar sebagai *bagian* yang dipegang fase 3–4 kalau dihitung dari
  porsi HP-nya. Sang Penenun tetap 30.000 dan Ketahanan 300 seperti tertulis di §6.3 — hasilnya
  pertarungan ketahanan 60–99 ronde yang baru bisa dimenangkan di Lv 56+, dan itu memang yang
  dimaksud "Lv 58" di §6.3. Cacing Abu Ibu justru sebaliknya: lima sasaran sekaligus membuat
  skill area berkelemahan Lintang sangat efisien, jadi HP-nya dinaikkan ke 14.000 + 4×3.500
  dan tetap jatuh dalam 5–8 ronde. Itu dibiarkan: buruan itu memang hadiah untuk party yang
  sudah membangun barisannya dengan benar.
- **XP musuh biasa Babak 3 = 2·L², bukan 6·L².** Dengan 6·L² party tiba di Sumur Ingatan pada
  Lv 58–60, jauh di atas rentang §2.4. Penyebabnya kurva 20·n²: di Lv 45+ satu level berharga
  ~45.000 XP sementara satu musuh menyumbang ~13.000, jadi dua area saja sudah cukup untuk
  sembilan level. Boss tetap 30·L². Tujuh Penjaga Suar dibayar sebagai **satu** mid-boss yang
  dibagi tujuh (4.800 XP per gelombang), bukan tujuh musuh Lv 49 penuh.
- **Skill Lv 47 bawaan ditambahkan untuk empat karakter Babak 1.** §4.9 hanya menjanjikan satu
  skill puncak per Jalur di Lv 45; tapi Rimba, Sela, Lintang, dan Bagas tidak punya skill
  bawaan baru sejak Lv 18–22, jadi sepanjang Babak 3 mereka cuma menunggu. Masing-masing dapat
  satu skill Lv 47 (Terang Larung, Pedang dan Perisai, Kabut dan Kilat, Peluncur Tujuh Laras).
- **Bara maks 8 diberikan cerita, bukan cuma penukaran Serpihan.** Menaikkan 5 → 8 lewat Tukang
  Kaca berharga 9 Serpihan Ingatan; pemain yang tidak mengumpulkannya tidak akan pernah melihat
  Jurus Empat, padahal itu isi §4.5. Nyai Rukmini melebarkan meteran setelah empat pulau wajib.
  Penukaran Serpihan tetap ada untuk yang sampai 8 lebih awal.
- **Ending 3 disembunyikan total** kalau syaratnya kurang (semua Kenangan Ratih + 7 Buruan
  selesai + Padasuara selamat + Kelana tidak dibunuh). Pilihannya tidak muncul sama sekali —
  bukan "terkunci dengan alasan". Syarat "7 Buruan" dibaca lewat kondisi baru
  `buruan_selesai>=7`, dan "Padasuara selamat" lewat flag `padasuara_selamat` yang dipasang
  saat Sunan Wirya jatuh.
- **Membunuh Kelana adalah pilihan eksplisit berperingatan dua tahap** (§6.2 no. 12): setelah
  Hampa Berzirah jatuh pemain memilih "Turunkan pedangmu" atau "Habisi dia", dan opsi kedua
  mengulang konsekuensinya sekali lagi sebelum dijalankan. Kalau dibunuh: Kelana tidak pernah
  bergabung, Lintang berubah sepanjang Babak 3 (Pulau Sunyi, gerbang Adiluhung, mulut Sumur),
  dan ending 1 & 3 tidak muncul di pilihan akhir.
- **Kenangan puncak adalah renungan satu orang**, bukan obrolan berpasangan seperti Kenangan
  §5.6 lainnya. Tujuh adegan, satu per anggota party, terbuka di pulau yang "memanggil" mereka.
  Keduanya hidup di `kenangan.json` yang sama; yang membedakan cuma panjang `pasangan`.
- **Kebijakan otomatis party dilatih tiga hal baru**, supaya walkthrough menguji desainnya dan
  bukan cuma kesabaran: membelanjakan Bara di depan lawan ber-`nyala_penjaga`, menyanyi alih-alih
  memukul di depan Kabut Terakhir, dan bertahan (Jaga/heal) di pertarungan bertahan.
- **Harga toko Babak 3 sengaja besar** (senjata 9.000, zirah 7.000–8.000, aksesori 6.000–6.500)
  untuk menyerap Keping yang menumpuk di akhir Babak 2. Itu belum menutup catatan §9.3: pemain
  otomatis tetap tamat dengan ~250.000 Keping. Kalibrasi harga menyeluruh tetap pekerjaan Tahap 6.
- **Masih terbuka setelah Tahap 5**: Buruan 8 dari 11, side quest 7 dari 18, dan tiga dungeon
  opsional (Gua Bawah Danau di Babak 1, Reruntuhan Suar Ketiga di Babak 2, dan satu lagi di
  Laut Lupa) belum dibuat. Pulau Hilang dan Cacing Abu Ibu adalah konten opsional Babak 3 yang
  sudah ada.
