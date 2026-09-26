/* Klien Pelita Terakhir: long-poll event dari server, render adegan & pertarungan,
   kirim pilihan pemain. Semua aturan permainan tetap di server (mesin Python). */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const el = {
    title: $("title-screen"), game: $("game-screen"), titleArt: $("title-art"),
    slotList: $("slot-list"), btnNew: $("btn-new"), btnLoad: $("btn-load"), btnQuit: $("btn-quit"),
    scene: $("scene"), sceneArt: $("scene-art"), scenePhoto: $("scene-photo"),
    sceneArea: $("scene-area"), sceneRoom: $("scene-room"),
    plate: $("plate"), plateImg: $("plate-img"), plateTeks: $("plate-teks"),
    chipKeping: $("chip-keping"), chipLentera: $("chip-lentera"),
    battle: $("battle"), battleRound: $("battle-round"), bara: $("bara"), baraPips: $("bara-pips"),
    enemies: $("enemies"), party: $("party"), log: $("log"),
    choices: $("choices"), promptLabel: $("prompt-label"), choiceGrid: $("choice-grid"),
    promptHead: $("prompt-head"), promptTitle: $("prompt-title"), promptNote: $("prompt-note"),
    freeForm: $("free-input"), freeText: $("free-text"), toast: $("toast")
  };

  const state = {
    id: null, since: 0, polling: false, waiting: false,
    areaId: null, roomKey: null, lastHp: new Map(), battleOn: false, dead: false,
    latar: null,
    fxAktif: false   // server mengirim event "fx" → angka melayang diurus fx.js, bukan dari log
  };

  /* ── Util ─────────────────────────────────────────────────────────── */
  const api = async (path, opts) => {
    const r = await fetch(path, Object.assign({ headers: { "Content-Type": "application/json" } }, opts));
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || `HTTP ${r.status}`);
    return r.json();
  };
  let toastTimer;
  function toast(msg) {
    el.toast.textContent = msg; el.toast.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { el.toast.hidden = true; }, 3200);
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pct = (a, b) => (b > 0 ? Math.max(0, Math.min(100, (a / b) * 100)) : 0);

  FX.pasangKontrol($("fx-mode"), $("fx-speed"));

  /* ── Layar judul ──────────────────────────────────────────────────── */
  el.titleArt.innerHTML = Art.titleArt();

  el.btnNew.onclick = () => startSession({});
  el.btnLoad.onclick = async () => {
    if (!el.slotList.hidden) { el.slotList.hidden = true; return; }
    try {
      const { slots } = await api("/api/slots");
      el.slotList.innerHTML = slots.map((s, i) => s
        ? `<button class="slot" data-slot="${i + 1}"><span><b>Slot ${i + 1}</b><br><small>${esc(s)}</small></span><span>▸</span></button>`
        : `<div class="slot slot-empty"><span><b>Slot ${i + 1}</b><br><small>kosong</small></span></div>`
      ).join("");
      el.slotList.hidden = false;
      el.slotList.querySelectorAll("[data-slot]").forEach((b) => {
        b.onclick = () => startSession({ slot: Number(b.dataset.slot) });
      });
    } catch (e) { toast("Gagal membaca save: " + e.message); }
  };

  async function startSession(body) {
    try {
      const { id } = await api("/api/session", { method: "POST", body: JSON.stringify(body) });
      state.id = id; state.since = 0; state.dead = false;
      antrean.length = 0; state.fxAktif = false; FX.reset();
      el.log.innerHTML = ""; el.enemies.innerHTML = ""; el.party.innerHTML = "";
      el.battle.hidden = true; state.battleOn = false; state.lastHp.clear(); state.roomKey = null;
      el.promptHead.hidden = true; el.choiceGrid.innerHTML = "";
      document.body.classList.remove("in-battle");
      el.title.hidden = true; el.game.hidden = false;
      setScene({ area_id: "pelita_rendah", area: "Lembah Larung", room: "…", fog: false });
      poll();
    } catch (e) { toast("Tidak bisa memulai: " + e.message); }
  }

  el.btnQuit.onclick = async () => {
    if (!confirm("Kembali ke layar judul? Progres yang belum disimpan akan hilang.")) return;
    if (state.id) await api(`/api/session/${state.id}/close`, { method: "POST" }).catch(() => {});
    backToTitle();
  };
  function backToTitle() {
    state.id = null; state.dead = true;
    el.game.hidden = true; el.title.hidden = false; el.slotList.hidden = true;
  }

  /* ── Long-poll ────────────────────────────────────────────────────── */
  async function poll() {
    if (state.polling || !state.id) return;
    state.polling = true;
    try {
      while (state.id && !state.dead) {
        const data = await api(`/api/session/${state.id}/state?since=${state.since}`);
        if (data.seq !== undefined) state.since = Math.max(state.since, data.seq);
        (data.events || []).forEach(handle);
        if (data.error) { toast("Kesalahan: " + data.error); break; }
        if (data.finished) break;
      }
    } catch (e) {
      if (state.id && !state.dead) toast("Koneksi terputus: " + e.message);
    } finally { state.polling = false; }
  }

  /* ── Event ──────────────────────────────────────────────────────────
     Semua event masuk antrean dan diproses berurutan. Event "fx" memutar
     animasi dan ditunggu sampai selesai, jadi log, snapshot pertarungan, dan
     prompt berikutnya baru muncul setelah efeknya habis. */
  const antrean = [];
  let memutar = false;
  function handle(ev) {
    antrean.push(ev);
    if (!memutar) jalankanAntrean();
  }
  async function jalankanAntrean() {
    memutar = true;
    while (antrean.length) {
      const ev = antrean.shift();
      try {
        if (ev.kind === "fx") {
          state.fxAktif = true;
          // Tab sempat di latar belakang dan antrean menumpuk: susul tanpa animasi.
          await FX.play(ev.payload, { kejar: antrean.length > 40 || document.hidden });
        } else {
          proses(ev);
        }
      } catch (e) { console.error(e); }
    }
    memutar = false;
  }
  function proses(ev) {
    switch (ev.kind) {
      case "room":       onRoom(ev.payload); break;
      case "adegan":     onAdegan(ev.payload); break;
      case "ilustrasi":  onIlustrasi(ev.payload); break;
      case "battle":     onBattle(ev.payload); break;
      case "battle_end": onBattleEnd(ev.payload); break;
      case "say":        addDialog(ev.payload.who, ev.payload.text); break;
      case "text":       addNarration(ev.payload.text); break;
      case "log":        addLog(ev.payload.text); break;
      case "prompt":     showPrompt(ev.payload); break;
      case "end":        onEnd(ev.payload); break;
      case "error":      toast(ev.payload.message); break;
      case "finished":   onFinished(ev.payload); break;
    }
  }

  /* ── Latar bergambar ──────────────────────────────────────────────────
     Panorama SVG prosedural selalu digambar sebagai dasar. Kalau berkas
     .webp untuk ruang ini ada, ia ditumpuk di atasnya dengan crossfade;
     kalau belum ada, panorama itulah yang terlihat — permainan tetap utuh. */
  function pasangLatar(url, kunci, efek) {
    if (kunci === state.latar && !efek) return;
    state.latar = kunci;
    if (url) {
      el.scenePhoto.style.backgroundImage = `url("${url}")`;
      el.scenePhoto.classList.add("on");
    } else {
      el.scenePhoto.classList.remove("on");
      el.scenePhoto.style.backgroundImage = "";
    }
    efekAdegan(efek);
  }

  function efekAdegan(efek) {
    el.scene.classList.remove("flash", "shake", "gelap");
    el.scenePhoto.classList.remove("zoom");
    if (!efek || efek === "fade") return;
    if (efek === "zoom") el.scenePhoto.classList.add("zoom");
    else el.scene.classList.add(efek);
    if (efek === "flash" || efek === "shake") {
      setTimeout(() => el.scene.classList.remove("flash", "shake"), 700);
    }
  }

  el.plate.onclick = () => tutupIlustrasi();

  function onAdegan(p) {
    if (p.latar) pasangLatar(p.latar_url || "", p.latar, p.efek);
    else efekAdegan(p.efek);
  }

  function onIlustrasi(p) {
    // Kalau ilustrasinya belum digambar, peristiwa tetap tampil sebagai layar
    // gelap berteks — momennya tidak hilang, hanya belum bergambar.
    el.plateImg.style.backgroundImage = p.latar_url ? `url("${p.latar_url}")` : "none";
    el.plateImg.style.backgroundColor = p.latar_url ? "" : "#11161f";
    el.plateTeks.textContent = p.teks || "";
    el.plate.hidden = false;
  }

  function tutupIlustrasi() {
    if (!el.plate.hidden) { el.plate.hidden = true; return true; }
    return false;
  }

  /* ── Adegan & party ───────────────────────────────────────────────── */
  function setScene(r) {
    if (r.area_id && r.area_id !== state.areaId) {
      state.areaId = r.area_id;
      el.sceneArt.innerHTML = Art.scene(r.area_id);
    }
    el.sceneArea.textContent = r.area || "";
    el.sceneRoom.textContent = r.room || "";
    el.scene.classList.toggle("fog", !!r.fog);
    pasangLatar(r.latar_url || "", r.latar || "");
  }

  function onRoom(r) {
    setScene(r);
    el.chipKeping.querySelector("b").textContent = r.keping;
    el.chipLentera.hidden = !r.fog;
    if (r.fog) el.chipLentera.querySelector("b").textContent = r.lentera;
    el.battle.hidden = true; state.battleOn = false;
    document.body.classList.remove("in-battle");
    renderParty(r.party.map((h) => Object.assign({}, h, { alive: h.hp > 0 })), null);
    // Server mengirim ruang tiap kali menu digambar ulang; tulis deskripsinya
    // hanya saat pemain benar-benar pindah, supaya log tidak terisi ulangan.
    const here = r.area_id + "/" + r.room_id;
    if (r.text && here !== state.roomKey) addNarration(r.text, "room-desc");
    state.roomKey = here;
  }

  // Baris kecil di bawah kartu: Jalur yang ditempuh dan Kaca yang terpasang.
  function extras(h) {
    const bagian = [];
    if (h.jalur) bagian.push(`<span class="tag ${h.jalur === "pilih!" ? "tag-weak" : "tag-buff"}">${esc(h.jalur === "pilih!" ? "Jalur: pilih!" : h.jalur)}</span>`);
    (h.kaca || []).forEach((k) => bagian.push(`<span class="tag tag-kaca">${esc(k)}</span>`));
    return bagian.length ? `<div class="tags">${bagian.join("")}</div>` : "";
  }

  function renderParty(heroes, activeKey) {
    el.party.innerHTML = heroes.map((h) => {
      const hpPct = pct(h.hp, h.max_hp);
      const lvl = hpPct <= 25 ? "low" : hpPct <= 55 ? "mid" : "";
      const st = (h.statuses || []).map((s) =>
        `<span class="tag ${s.bad ? "tag-status" : "tag-buff"}">${esc(s.name)}${s.turns ? " " + s.turns : ""}</span>`).join("");
      return `<div class="hero ${h.alive === false || h.hp <= 0 ? "down" : ""} ${h.key === activeKey ? "active" : ""} ${h.aktif === false ? "reserve" : ""}" data-hero="${h.key}" data-name="${esc(h.name)}">
        <div class="hero-top">
          <div class="hero-portrait">${Art.portrait(h.key)}</div>
          <div class="hero-id">
            <div class="hero-name">${esc(h.name)}${h.guest ? " <small>(tamu)</small>" : ""}${h.aktif === false ? " <small>(cadangan)</small>" : ""}</div>
            <div class="hero-lv">LV ${h.level}</div>
          </div>
        </div>
        <div class="bar bar-hp ${lvl}"><i style="width:${hpPct}%"></i></div>
        ${h.max_mp > 0 ? `<div class="bar bar-mp"><i style="width:${pct(h.mp, h.max_mp)}%"></i></div>` : ""}
        <div class="hero-nums"><span>HP ${h.hp}/${h.max_hp}</span>${h.max_mp > 0 ? `<span>MP ${h.mp}/${h.max_mp}</span>` : ""}</div>
        ${st ? `<div class="tags">${st}</div>` : ""}
        ${extras(h)}
      </div>`;
    }).join("");
    heroes.forEach((h) => trackHp("hero-" + h.key, h.hp, `.hero[data-hero="${h.key}"]`));
  }

  /* ── Pertarungan ──────────────────────────────────────────────────── */
  function onBattle(b) {
    state.battleOn = true;
    el.battle.hidden = false;
    document.body.classList.add("in-battle");
    el.battleRound.textContent = "Ronde " + b.round;
    el.bara.hidden = b.bara_max <= 0;
    el.bara.classList.toggle("frozen", !!b.bara_frozen);
    el.baraPips.innerHTML = Array.from({ length: b.bara_max }, (_, i) =>
      `<span class="pip ${i < b.bara ? "on" : ""}"></span>`).join("");

    el.enemies.innerHTML = b.enemies.map((e, i) => {
      const hpPct = pct(e.hp, e.max_hp);
      const lvl = hpPct <= 25 ? "low" : hpPct <= 55 ? "mid" : "";
      const tags = [
        ...(e.weak.length ? e.weak.map((w) => `<span class="tag tag-weak">lemah ${esc(w)}</span>`) : [`<span class="tag tag-unknown">lemah ?</span>`]),
        ...e.absorb.map((w) => `<span class="tag tag-absorb">serap ${esc(w)}</span>`),
        ...e.resist.map((w) => `<span class="tag tag-resist">tahan ${esc(w)}</span>`),
        ...(e.statuses || []).map((s) => `<span class="tag ${s.bad ? "tag-status" : "tag-buff"}">${esc(s.name)}${s.turns ? " " + s.turns : ""}</span>`)
      ].join("");
      return `<div class="enemy ${e.boss ? "boss" : ""} ${e.alive ? "" : "dead"} ${e.pecah && e.alive ? "pecah" : ""}" data-enemy="${i}" data-name="${esc(e.name)}" data-key="${esc(e.key)}">
        <div class="enemy-stage"><div class="enemy-sprite">${Art.enemy(e.key)}</div></div>
        <div class="enemy-top">
          <span class="enemy-name">${esc(e.name)}</span>
          <span class="enemy-hp-num">${e.alive ? Math.round(hpPct) + "%" : "—"}</span>
        </div>
        <div class="bar bar-hp ${lvl}"><i style="width:${hpPct}%"></i></div>
        ${e.ketahanan_max > 0 && e.alive
          ? (e.pecah ? `<div class="pecah-flag">◆ Pecah</div>`
                     : `<div class="bar bar-ket"><i style="width:${pct(e.ketahanan, e.ketahanan_max)}%"></i></div>`)
          : ""}
        <div class="tags">${tags}</div>
      </div>`;
    }).join("");
    b.enemies.forEach((e, i) => trackHp("enemy-" + i + "-" + e.key, e.hp, `.enemy[data-enemy="${i}"]`));
    renderParty(b.heroes.concat((b.bench || []).map((h) => Object.assign({}, h, { aktif: false }))), b.aktor || null);
  }

  function onBattleEnd(r) {
    if (r.outcome === "menang" && (r.xp || r.keping)) {
      addLog(`  Menang! +${r.xp} XP, +${r.keping} Keping.`);
    }
    setTimeout(() => {
      if (!state.battleOn) { el.battle.hidden = true; document.body.classList.remove("in-battle"); }
    }, 400);
    state.battleOn = false;
  }

  /* HP turun → getar + angka melayang (nilai diambil dari log, lihat addLog). */
  function trackHp(key, hp, selector) {
    const prev = state.lastHp.get(key);
    state.lastHp.set(key, hp);
    if (prev !== undefined && hp < prev && !state.fxAktif) {
      const node = document.querySelector(selector);
      if (node) { node.classList.add("hurt"); setTimeout(() => node.classList.remove("hurt"), 320); }
    }
  }

  function popNumber(name, text, cls) {
    const sel = `[data-name="${CSS.escape(name)}"]`;
    const node = document.querySelector(".enemy" + sel) || document.querySelector(".hero" + sel);
    if (!node) return;
    const p = document.createElement("div");
    p.className = "pop " + cls; p.textContent = text;
    node.appendChild(p);
    setTimeout(() => p.remove(), 1100);
  }

  /* ── Log & narasi ─────────────────────────────────────────────────── */
  const RE_DMG  = /^\s*(.+?) terkena (\d+) damage(.*)$/;
  const RE_HEAL = /^\s*(.+?) pulih (\d+) HP/;
  const RE_MISS = /^\s*\.\.\.meleset dari (.+?)\.$/;
  const RE_ABS  = /^\s*(.+?) MENYERAP/;

  function addLog(text) {
    if (text === undefined || text === null) return;
    const t = String(text);
    const trimmed = t.trim();
    if (!trimmed || /^[═─]+$/.test(trimmed)) { addRule(); return; }

    let m;
    if ((m = RE_DMG.exec(t))) {
      const weak = /LEMAH/.test(m[3]);
      if (!state.fxAktif) popNumber(m[1], m[2], weak ? "weak" : "dmg");
      return push(`<p class="combat ${weak ? "weak" : "hit"}">${esc(trimmed)}</p>`);
    }
    if ((m = RE_HEAL.exec(t))) { popNumber(m[1], "+" + m[2], "heal"); return push(`<p class="combat heal">${esc(trimmed)}</p>`); }
    if ((m = RE_MISS.exec(t))) { if (!state.fxAktif) popNumber(m[1], "meleset", "miss"); return push(`<p class="combat">${esc(trimmed)}</p>`); }
    if ((m = RE_ABS.exec(t)))  { if (!state.fxAktif) popNumber(m[1], "serap", "heal"); return push(`<p class="combat big">${esc(trimmed)}</p>`); }

    if (/tumbang!|Seluruh party/.test(trimmed)) return push(`<p class="combat down">${esc(trimmed)}</p>`);
    if (/PECAH|JURUS GANDA|Bara \+/.test(trimmed)) return push(`<p class="combat big">${esc(trimmed)}</p>`);
    if (/^\*\*/.test(trimmed)) return push(`<p class="sys">${esc(trimmed.replace(/\*\*/g, "").trim())}</p>`);
    if (/^\(Tip:|^\(Catatan Penyala/.test(trimmed)) return push(`<p class="sys tip">${esc(trimmed)}</p>`);
    if (/^\(/.test(trimmed)) return push(`<p class="sys tip">${esc(trimmed)}</p>`);
    if (/^Hasil:/.test(trimmed)) return push(`<p class="combat big">${esc(trimmed)}</p>`);
    push(`<p class="combat">${esc(trimmed)}</p>`);
  }

  function addNarration(text, cls) {
    push(`<p class="narration ${cls || ""}">${esc(text).replace(/\n\n/g, "</p><p class='narration'>")}</p>`);
  }
  function addDialog(who, text) {
    push(`<div class="dialog"><div class="who">${esc(who)}</div><div class="line">${esc(text)}</div></div>`);
  }
  function addRule() {
    if (el.log.lastElementChild && el.log.lastElementChild.classList.contains("rule")) return;
    push(`<hr class="rule">`);
  }
  function push(html) {
    el.log.insertAdjacentHTML("beforeend", html);
    while (el.log.childElementCount > 400) el.log.removeChild(el.log.firstElementChild);
    el.log.scrollTop = el.log.scrollHeight;
  }

  /* ── Prompt ───────────────────────────────────────────────────────── */
  /* Mesin mengirim jenis prompt: "menu" | "confirm" | "enter" | "free".
     Pola teks lama dipakai sebagai cadangan untuk sesi yang belum diperbarui. */
  function promptKind(p, prompt) {
    if (p.kind) return p.kind;
    if (/^\(Enter\)/i.test(prompt)) return "enter";
    if (/\(y\/N\)|\(Y\/n\)/i.test(prompt)) return "confirm";
    return p.options && p.options.length ? "menu" : "free";
  }

  function showPrompt(p) {
    state.waiting = true;
    if (promptKind(p, (p.prompt || "").trim()) !== "enter") tutupIlustrasi();
    const prompt = (p.prompt || "").trim();
    const kind = promptKind(p, prompt);

    /* Judul menu datang bersama prompt, bukan sebagai baris log: panel ini
       diganti tiap prompt, jadi header toko yang digambar ulang tiap putaran
       tidak menumpuk di log (lihat pelita/ui/menu.py). */
    setPromptHead(p);
    el.promptLabel.textContent = kind === "enter"
      ? "" : (prompt.replace(/\(y\/N\)|\(Y\/n\)/i, "").replace(/[>：:]\s*$/, "").trim() || "Pilih");
    el.freeForm.hidden = true;
    el.choiceGrid.innerHTML = "";

    if (kind === "enter") {
      addButton("Lanjut ▸", "", "btn btn-primary");
      return;
    }
    if (kind === "confirm" && !(p.options || []).length) {
      addButton("Ya", "y", "btn btn-primary");
      addButton("Tidak", "n");
      return;
    }
    if (p.options && p.options.length) {
      p.options.forEach((o) => {
        let cls = "btn choice";
        if (o.meta) cls += " meta";
        if (o.back) cls += " back";
        if (kind === "confirm" && o.key === "y") cls = "btn btn-primary";
        addButton(o.label, o.key, cls, o.key);
      });
      return;
    }
    el.freeForm.hidden = false;
    el.freeText.value = "";
    el.freeText.focus();
  }

  function setPromptHead(p) {
    const title = (p.title || "").trim();
    const sub = (p.subtitle || "").trim();
    const note = (p.note || []).map((n) => String(n).trim()).filter(Boolean);
    el.promptHead.hidden = !(title || sub || note.length);
    el.promptTitle.innerHTML = title
      ? esc(title) + (sub ? ` <span class="sub">${esc(sub)}</span>` : "")
      : (sub ? `<span class="sub">${esc(sub)}</span>` : "");
    el.promptNote.textContent = note.join("\n");
  }

  /* Label sasaran dari mesin memakai bar teks "[████░░]" (untuk terminal).
     Di web, ganti dengan bar HP sungguhan. */
  function labelHtml(label) {
    const m = /^(.*?)\s*\[([█░]+)\]\s*$/.exec(label);
    if (!m) return `<span>${esc(label)}</span>`;
    const penuh = (m[2].match(/█/g) || []).length, p = (penuh / m[2].length) * 100;
    const lvl = p <= 25 ? "low" : p <= 55 ? "mid" : "";
    return `<span class="lbl-sasaran"><span>${esc(m[1])}</span><span class="bar bar-hp bar-pilih ${lvl}" aria-label="HP ${Math.round(p)}%"><i style="width:${p}%"></i></span></span>`;
  }

  function addButton(label, value, cls, keyBadge) {
    const b = document.createElement("button");
    b.className = cls || "btn choice";
    b.innerHTML = (keyBadge ? `<span class="k">${esc(keyBadge)}</span>` : "") + labelHtml(String(label));
    b.onclick = () => answer(value);
    el.choiceGrid.appendChild(b);
  }

  el.freeForm.onsubmit = (e) => { e.preventDefault(); answer(el.freeText.value); };

  async function answer(text) {
    if (!state.waiting || !state.id) return;
    state.waiting = false;
    el.choiceGrid.querySelectorAll("button").forEach((b) => b.classList.add("waiting"));
    el.freeForm.hidden = true;
    try {
      await api(`/api/session/${state.id}/input`, { method: "POST", body: JSON.stringify({ text: String(text) }) });
    } catch (e) { toast("Gagal mengirim: " + e.message); state.waiting = true; }
  }

  /* Pintasan angka 1–9 dan Enter. */
  document.addEventListener("keydown", (e) => {
    if (el.game.hidden || !state.waiting) return;
    if (document.activeElement === el.freeText) return;
    const btns = [...el.choiceGrid.querySelectorAll("button")];
    if (e.key === "Enter" && btns.length === 1) { btns[0].click(); e.preventDefault(); return; }
    if (/^[0-9a-z]$/i.test(e.key)) {
      const k = e.key.toLowerCase();
      const hit = btns.find((b) => ((b.querySelector(".k") || {}).textContent || "").toLowerCase() === k)
        || (/^[1-9]$/.test(k) ? btns[Number(k) - 1] : null);
      if (hit) { hit.click(); e.preventDefault(); }
    }
  });

  /* ── Akhir permainan ──────────────────────────────────────────────── */
  function onEnd(p) {
    if (p.result === "chapter_end" && p.text) {
      push(`<div class="chapter">${esc(p.text)}</div>`);
    } else if (p.result === "gameover") {
      push(`<div class="chapter">Seluruh party tumbang.\nLentera terakhir yang kau nyalakan masih menunggu.</div>`);
    }
  }
  function onFinished(p) {
    state.waiting = false;
    el.choiceGrid.innerHTML = "";
    el.promptLabel.textContent = "";
    el.promptHead.hidden = true;
    el.freeForm.hidden = true;
    if (p.error) { toast("Kesalahan: " + p.error); }
    addButton("Kembali ke layar judul", "", "btn btn-primary");
    el.choiceGrid.lastElementChild.onclick = backToTitle;
  }
})();
