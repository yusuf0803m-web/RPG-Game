/* Seni SVG prosedural: panorama per area, potret party, siluet musuh.
   Semua digambar dari kode (tanpa aset gambar) agar repo tetap ringan. */
(function (global) {
  "use strict";

  const svg = (inner, vb = "0 0 800 200", fit = "xMidYMax slice") =>
    `<svg viewBox="${vb}" preserveAspectRatio="${fit}" xmlns="http://www.w3.org/2000/svg">${inner}</svg>`;

  /* Siluet bukit/gunung acak-deterministik dari seed teks. */
  function hillPath(seed, baseY, amp, step = 60) {
    let h = 0;
    for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
    const rnd = () => ((h = (h * 1664525 + 1013904223) >>> 0) / 4294967296);
    let d = `M -20 220 L -20 ${baseY}`;
    for (let x = 0; x <= 840; x += step) {
      d += ` Q ${x + step / 2} ${baseY - amp * (0.35 + rnd())} ${x + step} ${baseY - amp * 0.35 * rnd()}`;
    }
    return d + " L 840 220 Z";
  }

  /* Panel panorama memotong viewBox 800x200 ke rasio yang jauh lebih lebar, jadi
     semuanya tampil ~1.6x. Skala bawaan lentera dikecilkan agar pas. */
  const lantern = (x, y, s = 1, glow = "#f0b45c") => `
    <g transform="translate(${x} ${y}) scale(${s * 0.6})" class="flame">
      <circle cx="0" cy="0" r="26" fill="${glow}" opacity=".13"/>
      <circle cx="0" cy="0" r="12" fill="${glow}" opacity=".26"/>
      <rect x="-5" y="-7" width="10" height="13" rx="2" fill="${glow}"/>
      <path d="M-6 -8 h12 l2 -4 h-16 z" fill="#5d431f"/>
      <rect x="-1" y="-16" width="2" height="6" fill="#5d431f"/>
    </g>`;

  /* Catatan: pakai >>> (tanpa tanda). Dengan >> biasa, nilai di atas 2^31 jadi
     negatif dan radius lingkaran ikut negatif — SVG menolaknya. */
  const stars = (n, seed) => {
    let h = (seed.length * 977) >>> 0, out = "";
    for (let i = 0; i < n; i++) {
      h = (Math.imul(h, 1103515245) + 12345) >>> 0;
      const x = h % 800, y = ((h >>> 9) % 86) + 4, r = ((h >>> 17) % 10) / 9;
      out += `<circle cx="${x}" cy="${y}" r="${(0.35 + r * 0.55).toFixed(2)}" fill="#dfe6f2" opacity="${(0.1 + r * 0.4).toFixed(2)}"/>`;
    }
    return out;
  };

  /* ── Panorama per area ──────────────────────────────────────────── */
  const SCENES = {
    pelita_rendah: () => svg(`
      <defs><linearGradient id="skyV" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1b2433"/><stop offset=".6" stop-color="#2a2a33"/><stop offset="1" stop-color="#191a20"/>
      </linearGradient></defs>
      <rect width="800" height="200" fill="url(#skyV)"/>
      ${stars(40, "desa")}
      <path d="${hillPath("desa-jauh", 150, 40)}" fill="#161b24"/>
      <path d="${hillPath("desa-dekat", 172, 26)}" fill="#11151c"/>
      <g fill="#0e1218">
        <path d="M90 175 v-38 l34 -22 l34 22 v38 z"/><path d="M78 137 l46 -30 l46 30 z" fill="#161b24"/>
        <path d="M250 178 v-30 l28 -18 l28 18 v30 z"/><path d="M240 148 l38 -24 l38 24 z" fill="#161b24"/>
        <path d="M560 176 v-34 l30 -20 l30 20 v34 z"/><path d="M549 142 l41 -26 l41 26 z" fill="#161b24"/>
      </g>
      <rect x="0" y="176" width="800" height="24" fill="#0b0e13"/>
      ${lantern(190, 150, 1.1)} ${lantern(430, 158, .9)} ${lantern(660, 152, 1)}`),

    hutan_kelabu: () => svg(`
      <defs><linearGradient id="skyH" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#20242b"/><stop offset="1" stop-color="#2e3138"/>
      </linearGradient></defs>
      <rect width="800" height="200" fill="url(#skyH)"/>
      <g stroke="#3a3f47" fill="none">
        ${[40,120,210,300,395,480,570,650,740].map((x, i) => `
          <path d="M${x} 200 V${60 + (i % 3) * 18}" stroke-width="${5 + (i % 3)}"/>
          <path d="M${x} ${95 + (i % 3) * 10} l${i % 2 ? 24 : -24} -22" stroke-width="2.5"/>
          <path d="M${x} ${120 + (i % 2) * 12} l${i % 2 ? -20 : 20} -18" stroke-width="2"/>`).join("")}
      </g>
      <ellipse cx="400" cy="185" rx="520" ry="52" fill="#7d8fa6" opacity=".16"/>
      <ellipse cx="260" cy="196" rx="360" ry="34" fill="#7d8fa6" opacity=".2"/>
      <rect x="0" y="182" width="800" height="18" fill="#191c21"/>
      ${lantern(600, 128, .85)}`),

    rawa_suar: () => svg(`
      <defs>
        <linearGradient id="skyR" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#151c26"/><stop offset="1" stop-color="#26303c"/></linearGradient>
        <linearGradient id="airR" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#1d2733"/><stop offset="1" stop-color="#101720"/></linearGradient>
      </defs>
      <rect width="800" height="200" fill="url(#skyR)"/>
      ${stars(22, "rawa")}
      <path d="${hillPath("rawa-jauh", 140, 30)}" fill="#141b24"/>
      <g fill="#10161e">
        <path d="M620 150 v-92 h44 v92 z"/><path d="M612 58 l34 -26 l34 26 z"/>
        <rect x="632" y="46" width="20" height="16" fill="#2a2118"/>
      </g>
      <rect x="0" y="150" width="800" height="50" fill="url(#airR)"/>
      <g stroke="#7d8fa6" stroke-width="1" opacity=".3">
        <path d="M40 166 h120 M220 174 h150 M430 162 h110 M580 180 h160" fill="none"/>
      </g>
      <g fill="#0d1218">
        ${[70,150,330,470,700].map(x => `<path d="M${x} 168 q6 -34 -4 -52 q18 12 20 52 z"/>`).join("")}
      </g>
      <ellipse cx="400" cy="178" rx="480" ry="30" fill="#7d8fa6" opacity=".14"/>
      ${lantern(645, 54, .8, "#8fa7c4")}`),

    danau_cermin: () => svg(`
      <defs>
        <linearGradient id="skyD" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#1a2536"/><stop offset=".55" stop-color="#2d3d52"/><stop offset="1" stop-color="#22303f"/></linearGradient>
        <linearGradient id="airD" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#3a4d63"/><stop offset="1" stop-color="#16202b"/></linearGradient>
      </defs>
      <rect width="800" height="200" fill="url(#skyD)"/>
      ${stars(55, "danau")}
      <circle cx="640" cy="52" r="20" fill="#e8e3d8" opacity=".5"/>
      <path d="${hillPath("danau-bukit", 126, 34)}" fill="#141d28"/>
      <rect x="0" y="126" width="800" height="74" fill="url(#airD)"/>
      <g opacity=".28" fill="#e8e3d8"><circle cx="640" cy="176" r="16"/></g>
      <g stroke="#cfe0f0" stroke-width=".8" opacity=".25" fill="none">
        <path d="M60 148 h180 M300 160 h220 M560 144 h190 M120 176 h240 M470 184 h250"/>
      </g>
      <g fill="#0e151e">
        <rect x="150" y="132" width="90" height="8"/><rect x="163" y="112" width="64" height="22"/>
        <path d="M155 112 l40 -18 l40 18 z"/>
        <rect x="340" y="140" width="70" height="7"/><rect x="352" y="124" width="48" height="17"/>
        <path d="M345 124 l31 -14 l31 14 z"/>
      </g>
      ${lantern(196, 104, .7)} ${lantern(376, 118, .6)}`),

    tengara: () => svg(`
      <defs><linearGradient id="skyT" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#171d29"/><stop offset="1" stop-color="#2b2b34"/></linearGradient></defs>
      <rect width="800" height="200" fill="url(#skyT)"/>
      ${stars(30, "kota")}
      <g fill="#111721">
        <rect x="300" y="14" width="46" height="170"/>
        <path d="M296 14 l27 -14 l27 14 z"/>
        <rect x="310" y="22" width="26" height="20" fill="#2a2a33"/>
      </g>
      <g fill="#0f141c">
        ${[20,90,150,215,390,455,520,600,680,745].map((x, i) => `
          <rect x="${x}" y="${120 + (i % 4) * 14}" width="${44 + (i % 3) * 10}" height="${80 - (i % 4) * 8}"/>`).join("")}
      </g>
      <g fill="#f0b45c" opacity=".55">
        ${[34,104,166,230,404,470,536,614,694,760].map((x, i) => `
          <rect x="${x}" y="${134 + (i % 4) * 14}" width="5" height="7"/>
          <rect x="${x + 14}" y="${148 + (i % 3) * 10}" width="5" height="7"/>`).join("")}
      </g>
      <rect x="0" y="184" width="800" height="16" fill="#0a0d12"/>
      ${lantern(90, 156, .9)} ${lantern(560, 150, .9)}`),

    lorong_bawah: () => svg(`
      <defs>
        <linearGradient id="batuL" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#1a1f27"/><stop offset="1" stop-color="#0b0f14"/></linearGradient>
        <radialGradient id="obor" cx=".5" cy=".5"><stop offset="0" stop-color="#f0b45c" stop-opacity=".3"/>
          <stop offset="1" stop-color="#f0b45c" stop-opacity="0"/></radialGradient>
      </defs>
      <rect width="800" height="200" fill="url(#batuL)"/>
      <g fill="none" stroke="#242c36" stroke-width="3">
        <path d="M120 200 V96 Q400 18 680 96 V200"/>
        <path d="M200 200 V120 Q400 62 600 120 V200"/>
        <path d="M280 200 V142 Q400 104 520 142 V200"/>
      </g>
      <rect x="0" y="168" width="800" height="32" fill="#10161d"/>
      <g stroke="#4a5b6e" stroke-width="1" opacity=".5" fill="none">
        <path d="M0 178 h800 M0 188 h800"/>
      </g>
      <circle cx="400" cy="120" r="110" fill="url(#obor)"/>
      ${lantern(150, 108, .8)} ${lantern(650, 108, .8)}`),

    tambang: () => svg(`
      <defs><linearGradient id="guaT" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#14121a"/><stop offset="1" stop-color="#0a0810"/></linearGradient></defs>
      <rect width="800" height="200" fill="url(#guaT)"/>
      <g fill="#1d1a26">
        <path d="M0 0 h800 v40 l-60 26 l-70 -20 l-80 30 l-90 -26 l-70 24 l-80 -28 l-90 22 l-70 -24 l-70 26 l-50 -20 z"/>
        <path d="M0 200 h800 v-34 l-70 -18 l-60 20 l-90 -24 l-70 18 l-80 -22 l-80 26 l-70 -18 l-70 22 l-70 -20 l-70 24 z"/>
      </g>
      <g opacity=".85">
        ${[[90,120,16],[230,84,11],[340,140,20],[500,96,14],[620,132,17],[730,92,12]].map(([x, y, r], i) => `
          <g transform="translate(${x} ${y}) rotate(${i * 27})">
            <path d="M0 ${-r} L${r * .6} 0 L0 ${r} L${-r * .6} 0 Z" fill="#a98cd8" opacity=".5"/>
            <path d="M0 ${-r} L${r * .6} 0 L0 ${r} Z" fill="#c9b4ec" opacity=".35"/>
            <circle cx="0" cy="0" r="${r * 2.2}" fill="#a98cd8" opacity=".07"/>
          </g>`).join("")}
      </g>
      <g stroke="#2e2636" stroke-width="7" fill="none">
        <path d="M170 200 V104 h120 V200"/><path d="M160 104 h140"/>
      </g>
      ${lantern(420, 118, .9)}`),

    mercusuar: () => svg(`
      <defs>
        <linearGradient id="skyM" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#0e1420"/><stop offset="1" stop-color="#232b36"/></linearGradient>
        <linearGradient id="batuM" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#3f4553"/><stop offset=".45" stop-color="#cfd3da"/><stop offset="1" stop-color="#4a5160"/></linearGradient>
        <radialGradient id="nyalaM" cx=".5" cy=".5">
          <stop offset="0" stop-color="#ffd89a" stop-opacity=".75"/><stop offset="1" stop-color="#f0b45c" stop-opacity="0"/></radialGradient>
      </defs>
      <rect width="800" height="200" fill="url(#skyM)"/>
      ${stars(60, "menara")}
      <path d="${hillPath("menara-gunung", 170, 56)}" fill="#111722"/>
      <g>
        <path d="M356 200 L370 44 h60 L444 200 z" fill="url(#batuM)"/>
        <rect x="364" y="60" width="72" height="4" fill="#2c313c" opacity=".6"/>
        <rect x="360" y="110" width="80" height="4" fill="#2c313c" opacity=".5"/>
        <rect x="356" y="160" width="88" height="4" fill="#2c313c" opacity=".4"/>
        <path d="M366 44 h68 l-10 -18 h-48 z" fill="#5a6273"/>
        <circle cx="400" cy="34" r="46" fill="url(#nyalaM)" class="flame"/>
        <circle cx="400" cy="34" r="8" fill="#ffd89a" class="flame"/>
      </g>
      <rect x="0" y="188" width="800" height="12" fill="#090c11"/>`),

    _default: () => svg(`
      <rect width="800" height="200" fill="#151a22"/>
      <path d="${hillPath("umum", 150, 34)}" fill="#10141b"/>
      ${lantern(400, 140)}`)
  };

  /* ── Potret party ───────────────────────────────────────────────── */
  const fitAll = "xMidYMid meet";
  const face = (skin, hair, extra = "") => `
    <rect width="40" height="40" rx="8" fill="#0e1219"/>
    <circle cx="20" cy="18" r="9" fill="${skin}"/>
    <path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="${hair}"/>
    <path d="M8 40 q2 -13 12 -13 q10 0 12 13z" fill="${hair}" opacity=".55"/>
    ${extra}`;

  const PORTRAITS = {
    rimba:  () => svg(face("#d9b48c", "#3a2a1c",
      `<rect x="30" y="8" width="2.4" height="28" rx="1" fill="#6b4d24"/>
       <circle cx="31" cy="9" r="5" fill="#f0b45c" opacity=".85" class="flame"/>`), "0 0 40 40", fitAll),
    sela:   () => svg(face("#c9a07a", "#241a14",
      `<path d="M4 22 q6 -5 6 6 q0 8 -6 10 q-6 -2 -6 -10 q0 -11 6 -6z" transform="translate(4 2)" fill="#7d8494"/>
       <path d="M33 14 l5 -4 v22 l-5 -3z" fill="#9aa3b3"/>`), "0 0 40 40", fitAll),
    lintang:() => svg(face("#e0c3a4", "#1c2430",
      `<circle cx="20" cy="18" r="13" fill="#7d8fa6" opacity=".14"/>
       <rect x="29" y="22" width="9" height="11" rx="2" fill="#2a3340" stroke="#a98cd8" stroke-width=".8"/>
       <circle cx="33.5" cy="27.5" r="2.4" fill="#a98cd8" opacity=".8" class="flame"/>`), "0 0 40 40", fitAll),
    bagas:  () => svg(face("#c08f63", "#2a2118",
      `<rect x="10" y="15" width="20" height="5" rx="2" fill="#4b4436"/>
       <circle cx="15" cy="17.5" r="3" fill="#8fd0e0" opacity=".65"/><circle cx="25" cy="17.5" r="3" fill="#8fd0e0" opacity=".65"/>
       <rect x="30" y="24" width="8" height="4" rx="1" fill="#6b4d24"/>`), "0 0 40 40", fitAll),
    guntur: () => svg(face("#c6a382", "#c9c4bb",
      `<path d="M13 24 q7 9 14 0 q-2 10 -7 10 q-5 0 -7 -10z" fill="#c9c4bb"/>
       <rect x="30" y="6" width="2.6" height="30" rx="1" fill="#5d431f"/>
       <circle cx="31.3" cy="7" r="6" fill="#ffd89a" opacity=".9" class="flame"/>`), "0 0 40 40", fitAll),
    rangga: () => svg(face("#b88a64", "#1a1410",
      `<rect x="10.5" y="11.5" width="19" height="3" rx="1.2" fill="#8a3b2e"/>
       <path d="M29 12 l5 3 l-4 1z" fill="#8a3b2e"/>
       <path d="M23.5 19 l2.5 3" stroke="#7a4f36" stroke-width=".9"/>
       <path d="M33 10 v26" stroke="#8a7a5e" stroke-width="2"/><path d="M31 10 l2 -5 l2 5z" fill="#c79a60"/>`), "0 0 40 40", fitAll),
    ratih:  () => svg(face("#e2c09c", "#2a1a22",
      `<path d="M11 15 q-3 10 1 18 l3 -2 q-2 -8 -1 -14z M29 15 q3 10 -1 18 l-3 -2 q2 -8 1 -14z" fill="#2a1a22"/>
       <circle cx="27.5" cy="11" r="2.4" fill="#e89ab0"/><circle cx="27.5" cy="11" r="1" fill="#fff1b8"/>
       <path d="M6 30 l9 -6" stroke="#8fe0a8" stroke-width="1.4" stroke-linecap="round"/>`), "0 0 40 40", fitAll),
    kelana: () => svg(face("#a97d5a", "#3b3b46",
      `<path d="M9 20 q0 -15 11 -15 q11 0 11 15 q-2 -7 -11 -8 q-9 1 -11 8z" fill="#23222c"/>
       <circle cx="16.5" cy="18.5" r="1.1" fill="#a483e0"/><circle cx="23.5" cy="18.5" r="1.1" fill="#a483e0"/>
       <path d="M8 40 q2 -12 12 -12 q10 0 12 12z" fill="#23222c"/>`), "0 0 40 40", fitAll),
    _default: () => svg(face("#c9a07a", "#2b2b33"), "0 0 40 40", fitAll)
  };

  /* ── Potret NPC: deterministik dari nama, jadi dialog & menu selalu cocok ── */
  const hashTeks = (t) => { let h = 2166136261; for (const c of t) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
  const KULIT = ["#d9b48c", "#c9a07a", "#b88a64", "#e0c3a4", "#a97d5a"];
  const RAMBUT = ["#241a14", "#3a2a1c", "#1c1c22", "#5a4630", "#8a8680"];
  const KAIN = ["#5a4a3a", "#3f5a44", "#4a4f63", "#6b4f45", "#5d5470", "#40525a"];
  // Varian: 0 polos, 1 kerudung, 2 peci, 3 janggut tua, 4 caping, 5 ikat kepala
  const NPC_VARIAN = { darma: 3, ratna: 1, wira: 2, rukmini: 1, baskara: 3, pandansari: 5, "mbok sari": 1,
    sari: 1, nelayan: 4, penjaja: 4, pedagang: 2, pengawal: 5, penjaga: 5, "juru arena": 5, harun: 2, salim: 2,
    asih: 1, wulan: 1, kirana: 0, sekar: 0, enting: 0, baruna: 4, lelana: 4, "sunan wirya": 3, klawu: 5 };
  const bersihNama = (n) => String(n || "").replace(/\s*\(.*\)\s*$/, "").replace(/^(Pak|Bu|Mbok|Ki|Nyi|Mas|Mbak|Kak)\s+/i, "").trim();
  function potretNpc(nama) {
    const n = bersihNama(nama), k = n.toLowerCase(), h = hashTeks(k);
    if (/^\?+$/.test(n)) return svg(`<rect width="40" height="40" rx="8" fill="#0b0d12"/>
      <circle cx="20" cy="18" r="9" fill="#1a1d25"/><path d="M8 40 q2 -13 12 -13 q10 0 12 13z" fill="#1a1d25"/>
      <text x="20" y="22" text-anchor="middle" font-size="11" font-family="serif" fill="#4a5060">?</text>`, "0 0 40 40", fitAll);
    if (/pelita pertama|gema|penenun|hampa/.test(k)) {
      const w = /penenun/.test(k) ? "#a98cd8" : /gema/.test(k) ? "#ffd89a" : "#f0b45c";
      return svg(`<defs><radialGradient id="roh${h}" cx=".5" cy=".45"><stop offset="0" stop-color="${w}" stop-opacity=".9"/><stop offset="1" stop-color="${w}" stop-opacity="0"/></radialGradient></defs>
        <rect width="40" height="40" rx="8" fill="#0b0d12"/><circle cx="20" cy="19" r="17" fill="url(#roh${h})" class="flame"/>
        <circle cx="20" cy="17" r="7" fill="${w}" opacity=".35"/><path d="M9 40 q2 -12 11 -12 q9 0 11 12z" fill="${w}" opacity=".22"/>`, "0 0 40 40", fitAll);
    }
    const kulit = KULIT[h % KULIT.length], rambut = RAMBUT[(h >>> 3) % RAMBUT.length], kain = KAIN[(h >>> 6) % KAIN.length];
    const v = k in NPC_VARIAN ? NPC_VARIAN[k] : (h >>> 9) % 6;
    const tambah = [
      `<path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="${rambut}"/>`,
      `<path d="M9.5 20 q0 -13 10.5 -13 q10.5 0 10.5 13 v7 q-2 -3 -3 -9 q-3 -5 -7.5 -5 q-4.5 0 -7.5 5 q-1 6 -3 9z" fill="${kain}"/>`,
      `<path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="${rambut}"/><rect x="12" y="6.5" width="16" height="6" rx="1.5" fill="#15171c"/>`,
      `<path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="#c9c4bb"/><path d="M13.5 21 q6.5 9 13 0 q-1.5 9 -6.5 9 q-5 0 -6.5 -9z" fill="#c9c4bb"/>`,
      `<path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="${rambut}"/><path d="M4 13 L20 3 L36 13 z" fill="#b89a5e"/><path d="M4 13 h32" stroke="#7a6438" stroke-width="1"/>`,
      `<path d="M11 15 q9 -11 18 0 q-3 -6 -9 -6 q-6 0 -9 6z" fill="${rambut}"/><rect x="10.5" y="11" width="19" height="3" rx="1.2" fill="${kain}"/>`
    ][v];
    return svg(`<rect width="40" height="40" rx="8" fill="#0e1219"/>
      <path d="M8 40 q2 -13 12 -13 q10 0 12 13z" fill="${kain}"/>
      <circle cx="20" cy="18" r="9" fill="${kulit}"/>${tambah}
      <circle cx="16.8" cy="18.5" r=".9" fill="#1a1410"/><circle cx="23.2" cy="18.5" r=".9" fill="#1a1410"/>`, "0 0 40 40", fitAll);
  }
  /* Warna nama pembicara di kotak dialog. */
  const WARNA_TOKOH = { rimba: "#f0b45c", sela: "#b8c0cc", lintang: "#b9a2e6", bagas: "#8fd0e0", rangga: "#d9a86c",
    ratih: "#8fe0a8", kelana: "#a98ae6", guntur: "#ffd89a" };

  /* ── Siluet musuh (dikelompokkan dari id) ───────────────────────── */
  const shape = (inner) => svg(inner, "0 0 40 40", fitAll);
  const ENEMIES = {
    kunang:   () => shape(`<circle cx="20" cy="20" r="9" fill="#2b2233"/><circle cx="20" cy="20" r="4" fill="#a98cd8" opacity=".85"/>
      <path d="M12 14 q8 -7 16 0" stroke="#6f6080" fill="none" stroke-width="1.5"/>`),
    serigala: () => shape(`<path d="M6 28 q4 -14 14 -14 q10 0 14 14 q-14 5 -28 0z" fill="#495568"/>
      <path d="M12 16 l-2 -7 l6 4z M28 16 l2 -7 l-6 4z" fill="#495568"/>
      <circle cx="15" cy="21" r="1.6" fill="#f0b45c"/><circle cx="25" cy="21" r="1.6" fill="#f0b45c"/>`),
    lumut:    () => shape(`<path d="M7 31 q1 -16 13 -16 q12 0 13 16z" fill="#3f5a44"/>
      <path d="M12 18 q3 -8 6 -3 M24 17 q2 -7 5 -2" stroke="#6fbf8a" stroke-width="1.6" fill="none"/>`),
    hampa:    () => shape(`<path d="M11 33 q0 -20 9 -20 q9 0 9 20z" fill="#2f3743"/>
      <circle cx="20" cy="15" r="6" fill="#39424f"/>
      <circle cx="17.5" cy="15" r="1.4" fill="#0b0e13"/><circle cx="22.5" cy="15" r="1.4" fill="#0b0e13"/>`),
    katak:    () => shape(`<ellipse cx="20" cy="25" rx="14" ry="10" fill="#3d5a4a"/>
      <circle cx="13" cy="15" r="4.6" fill="#4a6b57"/><circle cx="27" cy="15" r="4.6" fill="#4a6b57"/>
      <circle cx="13" cy="15" r="1.8" fill="#f0b45c"/><circle cx="27" cy="15" r="1.8" fill="#f0b45c"/>
      <ellipse cx="20" cy="27" rx="7" ry="4" fill="#f0b45c" opacity=".3"/>`),
    ikan:     () => shape(`<path d="M4 20 q10 -10 22 0 q-10 10 -22 0z" fill="#5b7386"/>
      <path d="M26 20 l9 -7 v14z" fill="#43586a"/><circle cx="12" cy="19" r="1.6" fill="#e8e3d8"/>`),
    zirah:    () => shape(`<path d="M12 33 V16 q8 -6 16 0 v17z" fill="#5a5145"/>
      <path d="M14 16 h12 v5 h-12z" fill="#22262d"/>
      <path d="M20 21 v10" stroke="#3a3529" stroke-width="1.5"/>`),
    bayang:   () => shape(`<path d="M9 32 q2 -18 11 -18 q9 0 11 18z" fill="#2a2633"/>
      <rect x="14" y="17" width="12" height="9" rx="1.5" fill="#d8cfbb" opacity=".75"/>
      <path d="M15 20 h10 M15 23 h8" stroke="#2a2633" stroke-width="1"/>`),
    kelelawar:() => shape(`<path d="M20 22 q-9 -12 -17 -6 q7 2 8 10 q5 3 9 3z" fill="#4a3f59"/>
      <path d="M20 22 q9 -12 17 -6 q-7 2 -8 10 q-5 3 -9 3z" fill="#4a3f59"/>
      <circle cx="20" cy="22" r="4.5" fill="#5f5273"/><circle cx="20" cy="21" r="1.4" fill="#a98cd8"/>`),
    penambang:() => shape(`<path d="M10 34 V17 q10 -7 20 0 v17z" fill="#40372f"/>
      <path d="M13 17 h14 v5 h-14z" fill="#1f1c19"/>
      <path d="M26 12 l7 -6" stroke="#6a5a48" stroke-width="3"/>
      <path d="M12 26 l5 -4 l4 5z" fill="#a98cd8" opacity=".7"/>`),
    pelita:   () => shape(`<circle cx="20" cy="20" r="12" fill="#f0b45c" opacity=".12"/>
      <path d="M13 32 q0 -18 7 -18 q7 0 7 18z" fill="#c9b07c" opacity=".55"/>
      <circle cx="20" cy="16" r="5" fill="#ffd89a" opacity=".6"/>`),
    ular:     () => shape(`<path d="M4 28 q8 -6 14 0 q6 6 14 -2" stroke="#7fa0b5" stroke-width="6" fill="none" stroke-linecap="round"/>
      <circle cx="33" cy="25" r="5" fill="#9ab9cc"/><circle cx="34" cy="24" r="1.5" fill="#0b0e13"/>`),
    manusia:  () => shape(`<path d="M12 34 V18 q8 -5 16 0 v16z" fill="#6b4f45"/>
      <circle cx="20" cy="13" r="5.5" fill="#c9a07a"/>
      <path d="M31 8 v24" stroke="#8a7a5e" stroke-width="2.5"/>`),
    konstruk: () => shape(`<path d="M11 34 V14 h18 v20z" fill="#b9bcc4"/>
      <rect x="15" y="18" width="10" height="4" rx="1" fill="#f0b45c" opacity=".8"/>
      <path d="M11 14 l9 -8 l9 8z" fill="#8f949e"/>`),
    kelam:    () => shape(`<path d="M6 34 q2 -24 14 -24 q12 0 14 24z" fill="#241f2e"/>
      <circle cx="20" cy="18" r="7" fill="#3a3348"/>
      <circle cx="17" cy="17" r="1.6" fill="#f0b45c"/><circle cx="23" cy="17" r="1.6" fill="#f0b45c"/>
      <path d="M16 23 q4 3 8 0" stroke="#0b0e13" stroke-width="1.4" fill="none"/>`),
    _default: () => shape(`<circle cx="20" cy="20" r="11" fill="#39414e"/>
      <circle cx="16.5" cy="18" r="1.6" fill="#0b0e13"/><circle cx="23.5" cy="18" r="1.6" fill="#0b0e13"/>`)
  };

  const ENEMY_MAP = [
    [/kunang/, "kunang"], [/serigala/, "serigala"], [/lumut/, "lumut"],
    [/katak/, "katak"], [/ikan/, "ikan"], [/ular/, "ular"],
    [/pengawal|karat|istana/, "zirah"], [/bayang|arsip/, "bayang"],
    [/kelelawar/, "kelelawar"], [/penambang/, "penambang"], [/pelita_padam/, "pelita"],
    [/hampa|nelayan/, "hampa"], [/rangga|baskara/, "manusia"],
    [/penjaga_mercusuar/, "konstruk"], [/kelam/, "kelam"]
  ];

  global.Art = {
    scene(areaId) { return (SCENES[areaId] || SCENES._default)(); },
    portrait(heroId) { return (PORTRAITS[heroId] || PORTRAITS._default)(); },
    /* Potret siapa pun yang berbicara: tokoh party pakai potretnya, NPC dibuat dari nama. */
    speaker(nama) {
      const k = bersihNama(nama).toLowerCase();
      return PORTRAITS[k] && k !== "_default" ? PORTRAITS[k]() : potretNpc(nama);
    },
    speakerColor(nama) { return WARNA_TOKOH[bersihNama(nama).toLowerCase()] || "#d8cfbb"; },
    isHero(nama) { return bersihNama(nama).toLowerCase() in WARNA_TOKOH; },
    enemy(enemyId) {
      for (const [re, key] of ENEMY_MAP) if (re.test(enemyId)) return ENEMIES[key]();
      return ENEMIES._default();
    },
    titleArt() {
      /* Urutan lapisan: langit → bintang → gunung jauh → menara → bukit depan
         (bukit digambar terakhir supaya kaki menara tersembunyi secara alami). */
      const bintang = stars(120, "judul").replace(/cy="(\d+)"/g, (m, y) => `cy="${Number(y) * 2.6}"`);
      return svg(`
        <defs>
          <linearGradient id="skyJ" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#070a10"/><stop offset=".5" stop-color="#101825"/><stop offset="1" stop-color="#18202d"/></linearGradient>
          <linearGradient id="batuJ" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#333a48"/><stop offset=".45" stop-color="#9aa0ad"/><stop offset="1" stop-color="#3a4150"/></linearGradient>
          <radialGradient id="nyalaJ" cx=".5" cy=".5">
            <stop offset="0" stop-color="#ffd89a" stop-opacity=".85"/><stop offset="1" stop-color="#f0b45c" stop-opacity="0"/></radialGradient>
        </defs>
        <rect width="800" height="520" fill="url(#skyJ)"/>
        <g>${bintang}</g>
        <path d="${hillPath("judul-gunung-jauh", 400, 86)}" fill="#0b1018"/>
        <g>
          <path d="M382 470 L390 150 h20 L418 470 z" fill="url(#batuJ)"/>
          <rect x="386" y="200" width="28" height="3" fill="#1c202a" opacity=".7"/>
          <rect x="384" y="270" width="32" height="3" fill="#1c202a" opacity=".6"/>
          <rect x="382" y="345" width="36" height="3" fill="#1c202a" opacity=".5"/>
          <path d="M388 150 h24 l-5 -12 h-14 z" fill="#4b5262"/>
          <circle cx="400" cy="136" r="88" fill="url(#nyalaJ)" class="flame"/>
          <circle cx="400" cy="136" r="7" fill="#ffd89a" class="flame"/>
        </g>
        <path d="${hillPath("judul-bukit", 476, 40)}" fill="#080c13"/>
        <g opacity=".95">${lantern(118, 452, 1.5)} ${lantern(688, 468, 1.3)}</g>
        <rect x="0" y="504" width="800" height="16" fill="#04060a"/>`, "0 0 800 520", "xMidYMax slice");
    },
    sceneIds() { return Object.keys(SCENES).filter((k) => k[0] !== "_"); }
  };
})(window);
