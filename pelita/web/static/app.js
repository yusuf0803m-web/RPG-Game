/* Klien Pelita Terakhir: long-poll event dari server, render adegan & pertarungan,
   kirim pilihan pemain. Semua aturan permainan tetap di server (mesin Python). */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const el = {
    title: $("title-screen"), game: $("game-screen"), titleArt: $("title-art"),
    slotList: $("slot-list"), btnNew: $("btn-new"), btnLoad: $("btn-load"), btnQuit: $("btn-quit"),
    scene: $("scene"), sceneArt: $("scene-art"), sceneArea: $("scene-area"), sceneRoom: $("scene-room"),
    chipKeping: $("chip-keping"), chipLentera: $("chip-lentera"),
    battle: $("battle"), battleRound: $("battle-round"), bara: $("bara"), baraPips: $("bara-pips"),
    enemies: $("enemies"), party: $("party"), log: $("log"),
    choices: $("choices"), promptLabel: $("prompt-label"), choiceGrid: $("choice-grid"),
    freeForm: $("free-input"), freeText: $("free-text"), toast: $("toast")
  };

  const state = {
    id: null, since: 0, polling: false, waiting: false,
    areaId: null, roomKey: null, lastHp: new Map(), battleOn: false, dead: false
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
      el.log.innerHTML = ""; el.enemies.innerHTML = ""; el.party.innerHTML = "";
      el.battle.hidden = true; state.battleOn = false; state.lastHp.clear(); state.roomKey = null;
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

  /* ── Event ────────────────────────────────────────────────────────── */
  function handle(ev) {
    switch (ev.kind) {
      case "room":       onRoom(ev.payload); break;
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

  /* ── Adegan & party ───────────────────────────────────────────────── */
  function setScene(r) {
    if (r.area_id && r.area_id !== state.areaId) {
      state.areaId = r.area_id;
      el.sceneArt.innerHTML = Art.scene(r.area_id);
    }
    el.sceneArea.textContent = r.area || "";
    el.sceneRoom.textContent = r.room || "";
    el.scene.classList.toggle("fog", !!r.fog);
  }

  function onRoom(r) {
    setScene(r);
    el.chipKeping.querySelector("b").textContent = r.keping;
    el.chipLentera.hidden = !r.fog;
    if (r.fog) el.chipLentera.querySelector("b").textContent = r.lentera;
    el.battle.hidden = true; state.battleOn = false;
    renderParty(r.party.map((h) => Object.assign({}, h, { alive: h.hp > 0 })), null);
    // Server mengirim ruang tiap kali menu digambar ulang; tulis deskripsinya
    // hanya saat pemain benar-benar pindah, supaya log tidak terisi ulangan.
    const here = r.area_id + "/" + r.room_id;
    if (r.text && here !== state.roomKey) addNarration(r.text, "room-desc");
    state.roomKey = here;
  }

  function renderParty(heroes, activeKey) {
    el.party.innerHTML = heroes.map((h) => {
      const hpPct = pct(h.hp, h.max_hp);
      const lvl = hpPct <= 25 ? "low" : hpPct <= 55 ? "mid" : "";
      const st = (h.statuses || []).map((s) =>
        `<span class="tag ${s.bad ? "tag-status" : "tag-buff"}">${esc(s.name)}${s.turns ? " " + s.turns : ""}</span>`).join("");
      return `<div class="hero ${h.alive === false || h.hp <= 0 ? "down" : ""} ${h.key === activeKey ? "active" : ""}" data-hero="${h.key}" data-name="${esc(h.name)}">
        <div class="hero-top">
          <div class="hero-portrait">${Art.portrait(h.key)}</div>
          <div class="hero-id">
            <div class="hero-name">${esc(h.name)}${h.guest ? " <small>(tamu)</small>" : ""}</div>
            <div class="hero-lv">LV ${h.level}</div>
          </div>
        </div>
        <div class="bar bar-hp ${lvl}"><i style="width:${hpPct}%"></i></div>
        ${h.max_mp > 0 ? `<div class="bar bar-mp"><i style="width:${pct(h.mp, h.max_mp)}%"></i></div>` : ""}
        <div class="hero-nums"><span>HP ${h.hp}/${h.max_hp}</span>${h.max_mp > 0 ? `<span>MP ${h.mp}/${h.max_mp}</span>` : ""}</div>
        ${st ? `<div class="tags">${st}</div>` : ""}
      </div>`;
    }).join("");
    heroes.forEach((h) => trackHp("hero-" + h.key, h.hp, `.hero[data-hero="${h.key}"]`));
  }

  /* ── Pertarungan ──────────────────────────────────────────────────── */
  function onBattle(b) {
    state.battleOn = true;
    el.battle.hidden = false;
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
      return `<div class="enemy ${e.boss ? "boss" : ""} ${e.alive ? "" : "dead"}" data-enemy="${i}" data-name="${esc(e.name)}">
        <div class="enemy-top">
          <div class="enemy-sprite">${Art.enemy(e.key)}</div>
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
    renderParty(b.heroes, null);
  }

  function onBattleEnd(r) {
    if (r.outcome === "menang" && (r.xp || r.keping)) {
      addLog(`  Menang! +${r.xp} XP, +${r.keping} Keping.`);
    }
    setTimeout(() => { if (!state.battleOn) el.battle.hidden = true; }, 400);
    state.battleOn = false;
  }

  /* HP turun → getar + angka melayang (nilai diambil dari log, lihat addLog). */
  function trackHp(key, hp, selector) {
    const prev = state.lastHp.get(key);
    state.lastHp.set(key, hp);
    if (prev !== undefined && hp < prev) {
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
      popNumber(m[1], m[2], weak ? "weak" : "dmg");
      return push(`<p class="combat ${weak ? "weak" : "hit"}">${esc(trimmed)}</p>`);
    }
    if ((m = RE_HEAL.exec(t))) { popNumber(m[1], "+" + m[2], "heal"); return push(`<p class="combat heal">${esc(trimmed)}</p>`); }
    if ((m = RE_MISS.exec(t))) { popNumber(m[1], "meleset", "miss"); return push(`<p class="combat">${esc(trimmed)}</p>`); }
    if ((m = RE_ABS.exec(t)))  { popNumber(m[1], "serap", "heal"); return push(`<p class="combat big">${esc(trimmed)}</p>`); }

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
  function showPrompt(p) {
    state.waiting = true;
    const prompt = (p.prompt || "").trim();
    const isEnter = /^\(Enter\)/i.test(prompt);
    const isYesNo = /\(y\/N\)|\(Y\/n\)/i.test(prompt);

    el.promptLabel.textContent = isEnter ? "" : (prompt.replace(/[>：:]\s*$/, "") || "Pilih");
    el.freeForm.hidden = true;
    el.choiceGrid.innerHTML = "";

    if (isEnter) {
      addButton("Lanjut ▸", "", "btn btn-primary");
      return;
    }
    if (isYesNo) {
      el.promptLabel.textContent = prompt.replace(/\(y\/N\)|\(Y\/n\)/i, "").trim();
      addButton("Ya", "y", "btn btn-primary");
      addButton("Tidak", "n");
      return;
    }
    if (p.options && p.options.length) {
      p.options.forEach((o) => addButton(o.label, o.key, "btn choice" + (o.meta ? " meta" : ""), o.key));
      return;
    }
    el.freeForm.hidden = false;
    el.freeText.value = "";
    el.freeText.focus();
  }

  function addButton(label, value, cls, keyBadge) {
    const b = document.createElement("button");
    b.className = cls || "btn choice";
    b.innerHTML = (keyBadge ? `<span class="k">${esc(keyBadge)}</span>` : "") + `<span>${esc(label)}</span>`;
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
    if (/^[1-9]$/.test(e.key)) {
      const hit = btns.find((b) => (b.querySelector(".k") || {}).textContent === e.key) || btns[Number(e.key) - 1];
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
    el.freeForm.hidden = true;
    if (p.error) { toast("Kesalahan: " + p.error); }
    addButton("Kembali ke layar judul", "", "btn btn-primary");
    el.choiceGrid.lastElementChild.onclick = backToTitle;
  }
})();
