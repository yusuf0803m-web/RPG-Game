/* Kotak dialog bergaya novel visual untuk Pelita Terakhir.
   app.js memanggil Cerita.tampil() untuk tiap event "say"/"text" dan menunggu
   Promise-nya: satu baris per ketukan, teks diketik, potret pembicara di kiri.
   Semua baris tetap dicatat di log (lihat app.js), jadi riwayatnya tidak hilang.

   Kontrol: ketuk di mana saja = selesaikan ketikan / baris berikutnya,
   "Auto" = lanjut sendiri setelah waktu baca, "Lewati" = sisa adegan langsung ke log. */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const simpan = (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* mode privat */ } };
  const baca = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };

  let el = null;
  let terbuka = false, lewati = false, auto = baca("pelita.auto") === "1";
  let selesaiKetik = null;   // fungsi untuk menuntaskan ketikan yang sedang berjalan
  let lanjut = null;         // resolve Promise baris yang sedang tampil
  let timerAuto = null;

  function siapkan() {
    if (el) return;
    el = {
      lapis: $("dialog-lapis"), kotak: $("dlg"), potret: $("dlg-potret"), nama: $("dlg-nama"),
      teks: $("dlg-teks"), tanda: $("dlg-lanjut"), auto: $("dlg-auto"), lewati: $("dlg-lewati"), notif: $("notif")
    };
    el.lapis.addEventListener("click", ketuk);
    el.auto.addEventListener("click", (e) => {
      e.stopPropagation();
      auto = !auto; simpan("pelita.auto", auto ? "1" : "0"); segarkanTombol();
      if (auto && !selesaiKetik && lanjut) jadwalAuto(el.teks.textContent.length);
    });
    el.lewati.addEventListener("click", (e) => {
      e.stopPropagation();
      lewati = true;
      if (selesaiKetik) selesaiKetik();
      maju();
    });
    document.addEventListener("keydown", (e) => {
      if (!terbuka) return;
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); ketuk(); }
    });
    segarkanTombol();
  }
  function segarkanTombol() {
    el.auto.setAttribute("aria-pressed", String(auto));
    el.auto.classList.toggle("on", auto);
  }

  const kecepatan = () => (window.FX && FX.kecepatan ? FX.kecepatan() : 1);
  const tanpaGerak = () => (window.FX && FX.modeAnimasi ? FX.modeAnimasi() === "mati" : false);

  function ketuk() {
    if (selesaiKetik) { selesaiKetik(); return; }  // ketukan pertama menuntaskan ketikan
    maju();
  }
  function maju() {
    clearTimeout(timerAuto);
    const f = lanjut; lanjut = null;
    if (f) f();
  }
  function jadwalAuto(n) {
    clearTimeout(timerAuto);
    timerAuto = setTimeout(maju, (900 + n * 38) / kecepatan());
  }

  /* Ketik teks huruf demi huruf; jeda sedikit lebih lama di tanda baca. */
  function ketik(teks) {
    return new Promise((beres) => {
      el.teks.textContent = "";
      if (tanpaGerak() || lewati) { el.teks.textContent = teks; beres(); return; }
      let i = 0, t = null;
      const tuntas = () => { clearTimeout(t); el.teks.textContent = teks; selesaiKetik = null; beres(); };
      selesaiKetik = tuntas;
      const langkah = () => {
        if (i >= teks.length) { tuntas(); return; }
        const c = teks[i++];
        el.teks.textContent = teks.slice(0, i);
        const jeda = /[.!?…]/.test(c) ? 140 : /[,;:—]/.test(c) ? 70 : 20;
        t = setTimeout(langkah, jeda / kecepatan());
      };
      langkah();
    });
  }

  function buka() {
    siapkan();
    if (terbuka) return;
    terbuka = true; lewati = false;
    el.lapis.hidden = false;
    document.body.classList.add("berdialog");
  }

  window.Cerita = {
    aktif: () => terbuka,

    /* kind "say": {who, text} · kind "text": {text} (narasi). Selesai saat pemain maju. */
    async tampil(p, kind) {
      buka();
      if (lewati) return;
      const narasi = kind !== "say";
      el.kotak.classList.toggle("narasi", narasi);
      el.tanda.classList.remove("siap");
      if (narasi) {
        el.potret.innerHTML = ""; el.nama.textContent = "";
      } else {
        el.potret.innerHTML = Art.speaker(p.who);
        el.nama.textContent = p.who;
        el.kotak.style.setProperty("--tokoh", Art.speakerColor(p.who));
        el.kotak.classList.toggle("kawan", Art.isHero(p.who));
      }
      el.kotak.classList.remove("masuk"); void el.kotak.offsetWidth; el.kotak.classList.add("masuk");
      const teks = String(p.text || "").replace(/\s*\n\s*\n\s*/g, "\n\n").trim();
      const tunggu = new Promise((r) => { lanjut = r; });
      await ketik(teks);
      if (lewati) { lanjut = null; return; }
      el.tanda.classList.add("siap");
      if (auto) jadwalAuto(teks.length);
      await tunggu;
    },

    tutup() {
      if (!terbuka) return;
      terbuka = false; lewati = false;
      clearTimeout(timerAuto);
      if (selesaiKetik) selesaiKetik();
      maju();
      el.lapis.hidden = true;
      document.body.classList.remove("berdialog");
    },

    /* Pengumuman singkat di atas layar (quest, item didapat, anggota bergabung). */
    notif(teks) {
      siapkan();
      const t = String(teks).replace(/\*\*/g, "").trim();
      if (!t) return;
      const jenis = /^Quest/i.test(t) ? "quest" : /^Dapat|diserahkan|Keping/i.test(t) ? "item"
        : /bergabung|naik ke Lv|Jalur|Bara/i.test(t) ? "tokoh" : "umum";
      const d = document.createElement("div");
      d.className = "notif " + jenis;
      d.textContent = t.replace(/^Quest:\s*/i, "Quest · ");
      el.notif.appendChild(d);
      while (el.notif.childElementCount > 3) el.notif.firstElementChild.remove();
      setTimeout(() => { d.classList.add("pergi"); setTimeout(() => d.remove(), 400); }, 2800);
    }
  };
})();
