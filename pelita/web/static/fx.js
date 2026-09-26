/* Efek pertarungan Pelita Terakhir.
   Mesin mengirim event "fx" (lihat Battle._fx di pelita/combat/engine.py); app.js
   memasukkannya ke antrean dan memanggil FX.play() satu per satu, jadi animasi
   selalu selesai sebelum baris log dan prompt berikutnya muncul.

   Semua gerakan memakai transform dan opacity (Web Animations API) supaya ringan
   di HP. Pengaturan pemain: Animasi Penuh / Ringan / Mati dan kecepatan 1× / 2×. */
(function () {
  "use strict";

  const WARNA = {
    fisik: "#d8d0c0", api: "#ff7a3d", es: "#86d8f2", petir: "#f5e04a", angin: "#8fe0a8",
    bumi: "#c79a60", cahaya: "#fff1b8", kelam: "#a98ae6", netral: "#e8e3d8"
  };
  const MODE = ["penuh", "ringan", "mati"];
  const LABEL_MODE = { penuh: "Penuh", ringan: "Ringan", mati: "Mati" };

  const simpan = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* mode privat */ } };
  const baca = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };

  const kurangiGerak = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  let mode = MODE.includes(baca("pelita.animasi")) ? baca("pelita.animasi") : (kurangiGerak ? "ringan" : "penuh");
  let speed = baca("pelita.kecepatan") === "2" ? 2 : 1;
  let kejar = false;          // antrean menumpuk → putar tanpa animasi supaya cepat menyusul
  let sasaranTerakhir = null; // asal percik Bara

  let layer = null, flashEl = null;
  function siapkanLayer() {
    if (layer) return;
    layer = document.createElement("div"); layer.className = "fx-layer"; layer.setAttribute("aria-hidden", "true");
    flashEl = document.createElement("div"); flashEl.className = "fx-flash";
    document.body.append(layer, flashEl);
  }

  const modeAktif = () => (kejar ? "mati" : mode);
  const tidur = (ms) => (modeAktif() === "mati" ? Promise.resolve() : new Promise((r) => setTimeout(r, ms / speed)));
  const acak = (a, b) => a + Math.random() * (b - a);

  /* anim(): opsi.berat = hanya di mode Penuh; opsi.selalu = tetap tampil di mode Mati (tanpa gerak). */
  function anim(node, kf, dur, o = {}) {
    const m = modeAktif();
    if (!node || !node.animate) return Promise.resolve();
    if (m === "mati" && !o.selalu) return Promise.resolve();
    if (m === "ringan" && o.berat) return Promise.resolve();
    if (m === "mati") { kf = kf.map((k) => ({ opacity: k.opacity === undefined ? 1 : k.opacity })); }
    return node.animate(kf, {
      duration: dur / speed, delay: (o.delay || 0) / speed,
      easing: o.easing || "ease-out", fill: o.fill || "none"
    }).finished.catch(() => {});
  }

  function kotak(node) {
    const r = node.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height, top: r.top, left: r.left };
  }
  function partikel(css, html) {
    siapkanLayer();
    const d = document.createElement("div"); d.className = "fx-p";
    if (html) d.innerHTML = html;
    Object.assign(d.style, css);
    layer.appendChild(d);
    return d;
  }
  async function terbang(css, kf, dur, o = {}) {
    const m = modeAktif();
    if ((m === "mati" && !o.selalu) || (m === "ringan" && o.berat)) return;
    const d = partikel(css, o.html);
    await anim(d, kf, dur, o);
    d.remove();
  }
  const di = (x, y, w, h, extra) => Object.assign({ left: (x - w / 2) + "px", top: (y - h / 2) + "px", width: w + "px", height: h + "px" }, extra || {});

  function cari(nama) {
    if (!nama) return null;
    const sel = `[data-name="${CSS.escape(nama)}"]`;
    return document.querySelector(".enemy" + sel) || document.querySelector(".hero" + sel);
  }

  /* ── Delapan efek dasar elemen ──────────────────────────────────── */
  function efekElemen(elemen, node) {
    const c = kotak(node), warna = WARNA[elemen] || WARNA.netral, B = { berat: true };
    const s = Math.max(.6, Math.min(1.2, c.w / 220)); // skala menurut ukuran kartu
    const job = [];
    if (elemen === "api") {
      for (let i = 0; i < 14; i++) {
        const a = acak(-Math.PI * .95, -Math.PI * .05), r = acak(40, 100) * s, z = acak(5, 11);
        job.push(terbang(di(c.x + acak(-20, 20), c.y + 8, z, z, { borderRadius: "50%", background: `radial-gradient(#fff3c4, ${warna})`, boxShadow: `0 0 10px ${warna}` }),
          [{ transform: "translate(0,0) scale(1)", opacity: 1 }, { transform: `translate(${Math.cos(a) * r}px,${Math.sin(a) * r}px) scale(.2)`, opacity: 0 }],
          acak(420, 650), Object.assign({ delay: acak(0, 100) }, B)));
      }
    } else if (elemen === "es") {
      for (let i = 0; i < 12; i++) {
        const a = i / 12 * Math.PI * 2, r = acak(55, 105) * s;
        job.push(terbang(di(c.x, c.y, 4, acak(14, 24), { background: `linear-gradient(${warna}, #fff)`, clipPath: "polygon(50% 0,100% 50%,50% 100%,0 50%)" }),
          [{ transform: `rotate(${a + Math.PI / 2}rad) translateY(0)`, opacity: 1 }, { transform: `rotate(${a + Math.PI / 2}rad) translateY(${-r}px)`, opacity: 0 }], 480, B));
      }
    } else if (elemen === "petir") {
      const pts = []; let y = c.top - 50, x = c.x;
      while (y < c.y) { pts.push(`${x - c.left + 40},${y - c.top + 60}`); y += acak(12, 22); x = c.x + acak(-24, 24); }
      pts.push(`${c.x - c.left + 40},${c.y - c.top + 60}`);
      const w = c.w + 80, h = c.h + 120, p = pts.join(" ");
      const html = `<svg width="${w}" height="${h}" style="overflow:visible"><polyline points="${p}" fill="none" stroke="${warna}" stroke-width="4" stroke-linejoin="bevel" style="filter:drop-shadow(0 0 6px ${warna})"/><polyline points="${p}" fill="none" stroke="#fff" stroke-width="1.5"/></svg>`;
      job.push(terbang({ left: (c.left - 40) + "px", top: (c.top - 60) + "px" },
        [{ opacity: 0 }, { opacity: 1, offset: .1 }, { opacity: .2, offset: .3 }, { opacity: 1, offset: .45 }, { opacity: 0, offset: .6 }, { opacity: 1, offset: .7 }, { opacity: 0 }],
        440, Object.assign({ html }, B)));
    } else if (elemen === "angin") {
      for (let i = 0; i < 6; i++) {
        const yy = c.y + acak(-c.h * .35, c.h * .35);
        job.push(terbang(di(c.left - 30, yy, acak(50, 100) * s, 3, { borderRadius: "3px", background: `linear-gradient(90deg, transparent, ${warna}, transparent)` }),
          [{ transform: "translateX(0)", opacity: 0 }, { opacity: 1, offset: .3 }, { transform: `translateX(${c.w + 60}px)`, opacity: 0 }],
          480, Object.assign({ delay: i * 45 }, B)));
      }
    } else if (elemen === "bumi") {
      for (let i = 0; i < 9; i++) {
        const z = acak(7, 14) * s, dx = acak(-c.w * .4, c.w * .4);
        job.push(terbang(di(c.x + dx, c.top + c.h * .95, z, z, { background: warna, borderRadius: "3px", boxShadow: "inset -2px -2px 0 rgba(0,0,0,.35)" }),
          [{ transform: "translateY(0) rotate(0)", opacity: 1 }, { transform: `translateY(${-acak(45, 95) * s}px) rotate(${acak(-160, 160)}deg)`, opacity: 1, offset: .55 },
           { transform: `translateY(${-acak(15, 30)}px) rotate(${acak(-200, 200)}deg)`, opacity: 0 }],
          600, Object.assign({ easing: "cubic-bezier(.2,.7,.4,1)" }, B)));
      }
      job.push(terbang(di(c.x, c.top + c.h * .96, c.w * 1.1, 5, { background: `linear-gradient(90deg, transparent, ${warna}, transparent)` }),
        [{ transform: "scaleX(.1)", opacity: 1 }, { transform: "scaleX(1)", opacity: 0 }], 400, B));
    } else if (elemen === "cahaya") {
      job.push(terbang(Object.assign(di(c.x, c.y - 40, 56 * s, c.h + 110, { background: `linear-gradient(180deg, transparent, ${warna} 40%, #fff 80%, transparent)`, filter: "blur(2px)", transformOrigin: "50% 0" })),
        [{ transform: "scaleY(0) scaleX(.4)", opacity: .9 }, { transform: "scaleY(1) scaleX(1)", opacity: 1, offset: .4 }, { transform: "scaleY(1) scaleX(.1)", opacity: 0 }], 560, B));
    } else if (elemen === "kelam") {
      for (let i = 0; i < 8; i++) {
        const z = acak(34, 70) * s;
        job.push(terbang(di(c.x + acak(-c.w * .3, c.w * .3), c.y + acak(-c.h * .3, c.h * .3), z, z, { borderRadius: "50%", background: `radial-gradient(${warna}, transparent 70%)`, filter: "blur(4px)" }),
          [{ transform: "scale(.3)", opacity: 0 }, { transform: "scale(1)", opacity: .85, offset: .4 }, { transform: "scale(1.5)", opacity: 0 }],
          640, Object.assign({ delay: i * 35 }, B)));
      }
    } else if (elemen === "fisik") {
      job.push(terbang(di(c.x, c.y, 50 * s, 50 * s, { borderRadius: "50%", border: `3px solid ${warna}` }),
        [{ transform: "scale(.2)", opacity: 1 }, { transform: "scale(2)", opacity: 0 }], 340, B));
      job.push(terbang(di(c.x, c.y, Math.min(c.w, 130), 4, { background: "#fff", borderRadius: "2px" }),
        [{ transform: "rotate(-35deg) scaleX(0)", opacity: 1 }, { transform: "rotate(-35deg) scaleX(1)", opacity: 1, offset: .5 }, { transform: "rotate(-35deg) scaleX(1)", opacity: 0 }], 280, B));
    }
    return Promise.all(job);
  }

  /* ── Potongan umpan balik ───────────────────────────────────────── */
  function angka(node, teks, warna, besar, label) {
    const c = kotak(node);
    const html = `<div class="fx-num${besar ? " besar" : ""}" style="color:${warna}">${label ? `<small>${label}</small>` : ""}${teks}</div>`;
    return terbang({ left: (c.x + acak(-c.w * .15, c.w * .15)) + "px", top: (c.top + c.h * .5) + "px" },
      [{ transform: "translateY(0) scale(.6)", opacity: 0 }, { transform: "translateY(-14px) scale(1.12)", opacity: 1, offset: .15 },
       { transform: "translateY(-20px) scale(1)", opacity: 1, offset: .6 }, { transform: "translateY(-44px) scale(1)", opacity: 0 }],
      1000, { html, selalu: true });
  }
  function cap(node, teks, warna, ukuran, miring) {
    const c = kotak(node);
    const html = `<div class="fx-cap" style="color:${warna};font-size:${ukuran}px;text-shadow:0 0 16px ${warna}88,0 3px 0 #000">${teks}</div>`;
    return terbang({ left: c.x + "px", top: c.y + "px" },
      [{ transform: `rotate(${miring}deg) scale(2.1)`, opacity: 0 }, { transform: `rotate(${miring}deg) scale(.95)`, opacity: 1, offset: .18 },
       { transform: `rotate(${miring}deg) scale(1)`, opacity: 1, offset: .75 }, { transform: `rotate(${miring}deg) scale(1.05)`, opacity: 0 }],
      820, { html, selalu: true });
  }
  const guncang = (node, px, dur) => anim(node, [
    { transform: "translate(0,0)" }, { transform: `translate(${-px}px,${px / 3}px)` }, { transform: `translate(${px}px,${-px / 3}px)` },
    { transform: `translate(${-px / 2}px,0)` }, { transform: `translate(${px / 2}px,0)` }, { transform: "translate(0,0)" }], dur, { berat: true });
  function warnai(node, warna, puncak, dur) {
    const t = document.createElement("div"); t.className = "fx-tint"; t.style.background = warna;
    node.appendChild(t);
    return anim(t, [{ opacity: puncak }, { opacity: 0 }], dur).then(() => t.remove());
  }
  const kilat = (puncak, dur) => { siapkanLayer(); return anim(flashEl, [{ opacity: puncak }, { opacity: 0 }], dur, { berat: true }); };

  function setelHp(node, hp, maks) {
    if (hp === undefined || !maks) return;
    const p = Math.max(0, Math.min(100, hp / maks * 100));
    const bar = node.querySelector(".bar-hp");
    if (bar) {
      bar.classList.toggle("low", p <= 25); bar.classList.toggle("mid", p > 25 && p <= 55);
      const i = bar.querySelector("i"); if (i) i.style.width = p + "%";
    }
    const num = node.querySelector(".enemy-hp-num"); if (num) num.textContent = Math.round(p) + "%";
    const nums = node.querySelector(".hero-nums span"); if (nums) nums.textContent = `HP ${Math.max(0, hp)}/${maks}`;
  }

  /* ── Penangan tiap jenis event ──────────────────────────────────── */
  async function hit(p) {
    const node = cari(p.sasaran); if (!node) return;
    sasaranTerakhir = node;
    const warna = WARNA[p.elemen] || WARNA.netral;
    const pahlawan = node.classList.contains("hero");

    if (p.jurus) { await efekElemen(p.elemen, node); kilat(.3, 260); }
    else await efekElemen(p.elemen, node);

    const krit = p.krit ? " · KRITIKAL" : "";
    if (p.afinitas === "serap") {
      warnai(node, "#6fbf8a", .35, 380);
      angka(node, "+" + Math.abs(p.dmg), "#7ee0a0", false, "SERAP");
    } else if (p.afinitas === "lemah") {
      warnai(node, warna, .65, 420);
      anim(node, [{ transform: "rotate(0)" }, { transform: "rotate(-3deg) translateX(-5px)" }, { transform: "rotate(2.5deg) translateX(4px)" },
        { transform: "rotate(-1deg)" }, { transform: "rotate(0)" }], 400, { berat: true });
      angka(node, p.dmg, "#ffd84a", true, (p.pecah ? "LEMAH · PECAH" : "LEMAH") + krit);
    } else if (p.afinitas === "tahan") {
      angka(node, p.dmg, "#b7bcc4", false, "TAHAN" + krit);
      guncang(node, 2, 180);
    } else {
      const jurus = !!p.jurus;
      angka(node, p.dmg, jurus ? "#f0b45c" : (pahlawan ? "#ff9a8a" : "#ff8a78"), jurus || !!p.krit,
        jurus ? "JURUS" + krit : (p.pecah ? "PECAH" + krit : (p.krit ? "KRITIKAL" : "")));
      guncang(node, jurus ? 9 : (pahlawan ? 4 : 5), jurus ? 380 : 240);
      if (jurus) warnai(node, "#f0b45c", .45, 460);
    }
    setelHp(node, p.hp, p.hp_max);
    await tidur(p.afinitas === "lemah" || p.jurus ? 260 : 170);
  }

  async function meleset(p) {
    const node = cari(p.sasaran); if (!node) return;
    angka(node, "meleset", "#8a93a0", false, "");
    await anim(node, [{ transform: "translateX(0)" }, { transform: "translateX(14px)", offset: .35 }, { transform: "translateX(0)" }], 320, { berat: true });
  }

  async function imun(p) {
    const node = cari(p.sasaran); if (!node) return;
    await efekElemen(p.elemen, node);
    angka(node, "IMUN", "#8a93a0", false, "");
    await tidur(160);
  }

  function ketahanan(p) {
    const node = cari(p.sasaran); if (!node) return;
    const i = node.querySelector(".bar-ket > i");
    if (i && p.maks) i.style.width = Math.max(0, p.nilai / p.maks * 100) + "%";
  }

  async function pecah(p) {
    const node = cari(p.sasaran); if (!node) return;
    // hit-stop: tahan pose benturan sebentar
    if (modeAktif() !== "mati") {
      node.style.transform = "translate(6px,-3px) scale(.97)";
      await tidur(150);
      node.style.transform = "";
    }
    const bar = node.querySelector(".bar-ket");
    const serpih = [];
    if (bar) {
      const c = kotak(bar);
      for (let k = 0; k < 12; k++) {
        const w = acak(7, 18);
        serpih.push(terbang({ left: (c.left + acak(0, c.w)) + "px", top: (c.y - 3) + "px", width: w + "px", height: "6px",
          background: "linear-gradient(90deg, #6d5aa0, #d9ccf5)", clipPath: "polygon(0 0,100% 20%,80% 100%,10% 80%)" },
          [{ transform: "translate(0,0) rotate(0)", opacity: 1 }, { transform: `translate(${acak(-90, 90)}px,${acak(15, 100)}px) rotate(${acak(-300, 300)}deg)`, opacity: 0 }],
          acak(550, 850), { berat: true, easing: "cubic-bezier(.2,.6,.5,1)" }));
      }
      bar.style.opacity = "0";
    }
    node.classList.add("pecah");
    kilat(.5, 300);
    guncang(document.getElementById("battle"), 8, 380);
    await Promise.all([cap(node, "PECAH", "#e6dcff", Math.min(46, kotak(node).w * .2), -8)].concat(serpih));
  }

  async function pecahPulih(p) {
    const node = cari(p.sasaran); if (!node) return;
    node.classList.remove("pecah");
    const bar = node.querySelector(".bar-ket");
    if (bar) { bar.style.opacity = ""; const i = bar.querySelector("i"); if (i) i.style.width = "100%"; }
    await tidur(200);
  }

  async function bara(p) {
    const pips = document.querySelectorAll("#bara-pips .pip");
    const idx = Math.min(p.nilai, pips.length) - 1;
    const tujuan = pips[idx];
    if (!tujuan) return;
    const dari = sasaranTerakhir && document.body.contains(sasaranTerakhir) ? sasaranTerakhir : null;
    if (dari && modeAktif() === "penuh") {
      const a = kotak(dari), b = kotak(tujuan);
      const mx = (a.x + b.x) / 2 + acak(-60, 60), my = Math.min(a.y, b.y) - 50;
      await terbang({ left: (a.x - 6) + "px", top: (a.y - 6) + "px" }, [
        { transform: "translate(0,0) scale(.6)" },
        { transform: `translate(${mx - a.x}px,${my - a.y}px) scale(1.3)`, offset: .45 },
        { transform: `translate(${b.x - a.x}px,${b.y - a.y}px) scale(.8)` }],
        520, { html: `<div class="fx-bara"></div>`, easing: "cubic-bezier(.5,0,.3,1)" });
    }
    pips.forEach((x, k) => x.classList.toggle("on", k <= idx));
    anim(tujuan, [{ transform: "rotate(45deg) scale(1.9)", filter: "brightness(2.2)" }, { transform: "rotate(45deg) scale(1)", filter: "brightness(1)" }],
      400, { easing: "cubic-bezier(.2,1.4,.4,1)" });
    await tidur(120);
  }

  async function tumbang(p) {
    const node = cari(p.sasaran); if (!node) return;
    if (p.pahlawan) { node.classList.add("down"); await tidur(200); return; }
    await anim(node, [{ opacity: 1, filter: "brightness(1)" }, { opacity: .32, filter: "brightness(2.4) grayscale(1)" }], 520);
    node.classList.add("dead");
  }

  const PENANGAN = { hit, meleset, imun, ketahanan, pecah, pecah_pulih: pecahPulih, bara, tumbang };

  /* ── Pengaturan ─────────────────────────────────────────────────── */
  function pasangKontrol(tombolMode, tombolKecepatan) {
    const segarkan = () => {
      tombolMode.textContent = "Animasi: " + LABEL_MODE[mode];
      tombolKecepatan.textContent = speed + "×";
      tombolKecepatan.setAttribute("aria-label", "Kecepatan animasi " + speed + " kali");
    };
    tombolMode.onclick = () => { mode = MODE[(MODE.indexOf(mode) + 1) % MODE.length]; simpan("pelita.animasi", mode); segarkan(); };
    tombolKecepatan.onclick = () => { speed = speed === 1 ? 2 : 1; simpan("pelita.kecepatan", String(speed)); segarkan(); };
    segarkan();
  }

  window.FX = {
    /* Mengembalikan Promise yang selesai saat animasi selesai. */
    play(p, opsi) {
      kejar = !!(opsi && opsi.kejar);
      const f = PENANGAN[p && p.t];
      if (!f) return Promise.resolve();
      return Promise.resolve(f(p)).catch((e) => console.error("fx", p.t, e));
    },
    reset() { sasaranTerakhir = null; if (layer) layer.innerHTML = ""; },
    pasangKontrol
  };
})();
