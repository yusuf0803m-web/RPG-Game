"""AI musuh (GAME_DESIGN §4.11) dan kebijakan otomatis untuk party (simulasi/demo).

- Musuh biasa: tabel bobot dengan pemicu (``hp_below``, ``every_n_turns``).
- Boss: skrip fase; fase aktif = fase pertama (urut HP menurun) yang ``hp_ratio > hp_above``.
- Goyah: aksi dipaksa jadi Serang biasa (aksi paling lemah) ke sasaran acak.
"""
from __future__ import annotations

from typing import Optional

from ..models import Affinity, Element, Skill, SkillKind, Target
from .engine import Action, Battle, Combatant


def _pick_target(battle: Battle, actor: Combatant, rule: str, target_type: Target) -> list[Combatant]:
    if target_type in (Target.SATU_KAWAN, Target.SEMUA_KAWAN):
        allies = [a for a in battle.allies_of(actor) if a.alive]
        if rule == "kawan_hp_terendah":
            return [min(allies, key=lambda c: c.hp_ratio)]
        return [battle.rng.choice(allies)]
    if target_type == Target.DIRI:
        return [actor]
    foes = [f for f in battle.foes_of(actor) if f.alive]
    if not foes:
        return []
    if rule == "hp_terendah":
        return [min(foes, key=lambda c: c.hp)]
    if rule == "tandai":
        marked = [f for f in foes if f.has("tandai")]
        if marked:
            return [marked[0]]
        return [max(foes, key=lambda c: c.effective("mag"))]
    if rule == "mag_tertinggi":
        return [max(foes, key=lambda c: c.effective("mag"))]
    return [battle.rng.choice(foes)]


def _skill_action(battle: Battle, actor: Combatant, action_id: str, rule: str = "acak") -> Action:
    if action_id == "serang":
        return Action("serang", targets=_pick_target(battle, actor, rule, Target.SATU_MUSUH))
    skill = battle.data.skill(action_id)
    if skill.once_per_battle and skill.id in actor.used_once:
        return Action("serang", targets=_pick_target(battle, actor, rule, Target.SATU_MUSUH))
    if not battle.cost_ok(actor, skill) or (skill.is_magic and not actor.can_use_magic) or not actor.can_use_skills:
        return Action("serang", targets=_pick_target(battle, actor, rule, Target.SATU_MUSUH))
    # Heal hanya kalau ada yang perlu disembuhkan
    if skill.kind == SkillKind.HEAL:
        allies = [a for a in battle.allies_of(actor) if a.alive and a.hp_ratio < 0.7]
        if not allies:
            return Action("serang", targets=_pick_target(battle, actor, "acak", Target.SATU_MUSUH))
        return Action("skill", skill=skill, targets=[min(allies, key=lambda c: c.hp_ratio)])
    return Action("skill", skill=skill, targets=_pick_target(battle, actor, rule, skill.target))


def choose_enemy_action(battle: Battle, actor: Combatant) -> Action:
    edef = actor.edef
    assert edef is not None
    if actor.has("goyah"):
        return Action("serang", targets=_pick_target(battle, actor, "acak", Target.SATU_MUSUH))
    if edef.phases:
        phases = sorted(edef.phases, key=lambda p: -p.hp_above)
        idx = next((i for i, p in enumerate(phases) if actor.hp_ratio > p.hp_above), len(phases) - 1)
        if idx != actor.phase_index:
            actor.phase_index = idx
            actor.pattern_pos = 0
            battle.apply_phase(actor, phases[idx], battle.pending_events)
        pattern = phases[idx].pattern
        action_id = pattern[actor.pattern_pos % len(pattern)]
        actor.pattern_pos += 1
        action_id, _, rule = action_id.partition("@")
        return _skill_action(battle, actor, action_id, rule or "acak")
    cands = []
    for row in edef.ai:
        if row.hp_below is not None and actor.hp_ratio >= row.hp_below:
            continue
        if row.hp_above is not None and actor.hp_ratio <= row.hp_above:
            continue
        if row.every_n_turns and actor.turn_count % row.every_n_turns != 0:
            continue
        cands.append(row)
    if not cands:
        return Action("serang", targets=_pick_target(battle, actor, "acak", Target.SATU_MUSUH))
    row = battle.rng.choices(cands, weights=[r.weight for r in cands], k=1)[0]
    return _skill_action(battle, actor, row.action, row.target_rule)


# ---------------------------------------------------------------------------
# Kebijakan otomatis party (untuk kalibrasi & mode demo)
# ---------------------------------------------------------------------------
def _known_weakness(battle: Battle, enemy: Combatant) -> Optional[Element]:
    for el, aff in battle.bestiary.get(enemy.key).items():
        if aff == Affinity.LEMAH:
            return el
    return None


def _known_bad(battle: Battle, enemy: Combatant, el: Element) -> bool:
    aff = battle.bestiary.get(enemy.key).get(el)
    return aff in (Affinity.TAHAN, Affinity.IMUN, Affinity.SERAP)


def choose_hero_action(battle: Battle, actor: Combatant, policy: str = "pintar") -> Action:
    """Kebijakan sederhana:

    - ``"serang"``: selalu Serang biasa (baseline kalibrasi).
    - ``"pintar"``: heal kalau ada kawan < 35% HP, pakai skill kelemahan yang sudah diketahui,
      coba elemen yang belum diketahui, jurus Bara kalau penuh, dan Serang sebagai cadangan.
    """
    foes = battle.alive_enemies
    if not foes:
        return Action("jaga")
    if policy == "serang":
        return Action("serang", targets=[battle.rng.choice(foes)])
    if policy == "tunggal":
        # ukur rasio "2–3 pukulan per musuh": satu target, skill kelemahan kalau diketahui
        t = max(foes, key=lambda c: c.hp)
        weak = _known_weakness(battle, t)
        for s in battle.usable_skills(actor):
            if s.is_attack and not s.target.is_multi and (s.element == weak or (weak is None and s.element != Element.FISIK
                                                                                 and s.element not in battle.bestiary.get(t.key))):
                return Action("skill", skill=s, targets=[t])
        return Action("serang", targets=[t])

    skills = battle.usable_skills(actor)
    allies = battle.alive_heroes
    boss_present = any(f.is_boss for f in foes)

    # 0. Bangkitkan kawan pingsan (Abu Fajar), prioritas Rimba (pemegang Bara)
    down = [h for h in battle.heroes if not h.alive]
    if down:
        for iid, n in battle.inventory.items():
            it = battle.data.items[iid]
            if n > 0 and it.revive_pct:
                target = next((h for h in down if h.key == "rimba"), down[0])
                return Action("item", item=it, targets=[target])

    # 0b. Tanda eksekusi (Rangga): hapus dengan Cahaya Penunjuk / Garam Bangun, atau tarik dengan Pasang Badan
    marked = [a for a in allies if a.has("tandai")]
    if marked:
        cure = next((s for s in skills if "tandai" in s.cure), None)
        if cure:
            return Action("skill", skill=cure, targets=[marked[0]])
        for iid, n in battle.inventory.items():
            it = battle.data.items[iid]
            if n > 0 and "tandai" in it.cure:
                return Action("item", item=it, targets=[marked[0]])
        taunt = next((s for s in skills if any(i.status == "provokasi" for i in s.self_inflict)), None)
        if taunt and not actor.taunting and actor not in marked:
            return Action("skill", skill=taunt, targets=[])

    # 0c. Tank: Pasang Badan melawan boss saat sehat, agar serangan single-target diarahkan ke tank
    taunt = next((s for s in skills if any(i.status == "provokasi" for i in s.self_inflict)), None)
    if taunt and boss_present and not actor.taunting and actor.hp_ratio > 0.5 and not any(f.ignore_taunt for f in foes):
        others = [a for a in allies if a is not actor]
        if others and min(a.hp_ratio for a in others) < 0.8:
            return Action("skill", skill=taunt, targets=[])

    # 1. Darurat: heal
    #    Kawan yang kena Kutuk TIDAK disembuhkan: penyembuhannya berbalik jadi damage
    #    (GAME_DESIGN §4.8). Bersihkan kutukannya dulu kalau ada yang bisa.
    hurt = [a for a in allies if a.hp_ratio < 0.35]
    terkutuk = [a for a in hurt if a.has("kutuk")]
    if terkutuk:
        pembersih = next((s for s in skills if s.cure and ("kutuk" in s.cure or "*" in s.cure)), None)
        if pembersih:
            return Action("skill", skill=pembersih, targets=[terkutuk[0]])
        obat = next((battle.data.items[i] for i, n in battle.inventory.items()
                     if n > 0 and ("kutuk" in battle.data.items[i].cure
                                   or "*" in battle.data.items[i].cure)), None)
        if obat:
            return Action("item", item=obat, targets=[terkutuk[0]])
    hurt = [a for a in hurt if not a.has("kutuk")]
    if hurt:
        heals = [s for s in skills if s.kind == SkillKind.HEAL]
        if heals:
            return Action("skill", skill=heals[-1], targets=[min(hurt, key=lambda c: c.hp_ratio)])
        pulih = [s for s in battle.usable_bara_skills(actor) if s.id == "nyala_pulih"]
        if pulih and len(hurt) >= 2:
            return Action("skill", skill=pulih[0], targets=allies)
        for iid, n in battle.inventory.items():
            it = battle.data.items[iid]
            if n > 0 and it.heal_hp:
                return Action("item", item=it, targets=[min(hurt, key=lambda c: c.hp_ratio)])

    # 1a. Pertarungan bertahan (segmen ending "Menyalakan Kembali", §2.4): gelombangnya
    #     tidak habis-habis, jadi yang dinilai cuma berdiri sampai rondenya lewat.
    if battle.survive_rounds:
        sakit = [a for a in allies if a.hp_ratio < 0.75 and not a.has("kutuk")]
        heals = [s for s in skills if s.kind == SkillKind.HEAL]
        if sakit and heals:
            return Action("skill", skill=heals[-1], targets=[min(sakit, key=lambda c: c.hp_ratio)])
        pulih = [s for s in battle.usable_bara_skills(actor) if s.id == "nyala_pulih"]
        if len(sakit) >= 2 and pulih:
            return Action("skill", skill=pulih[0], targets=allies)
        if sakit:
            for iid, n in battle.inventory.items():
                it = battle.data.items[iid]
                if n > 0 and (it.heal_hp or it.heal_pct):
                    return Action("item", item=it, targets=[min(sakit, key=lambda c: c.hp_ratio)])
        return Action("jaga")

    # 1b. Lawan yang tidak bisa dilukai apa pun (Kabut Terakhir, GAME_DESIGN §2.4):
    #     memukulnya sia-sia; hanya Lagu dan Kidung yang menguraikannya.
    if any("kabut_terakhir" in f.traits for f in foes):
        lagu = [s for s in skills if "lagu" in s.tags]
        if lagu:
            pilih = min(lagu, key=lambda s: s.cost)
            ts = battle.valid_targets(actor, pilih.target)
            return Action("skill", skill=pilih, targets=ts if pilih.target.is_multi else ts[:1])
        sakit = [a for a in allies if a.hp_ratio < 0.8]
        heals = [s for s in skills if s.kind == SkillKind.HEAL]
        if sakit and heals:
            return Action("skill", skill=heals[-1], targets=[min(sakit, key=lambda c: c.hp_ratio)])
        return Action("jaga")

    # 1c. Lawan yang meminum Bara yang ditabung (Gema Guntur, §6.2 no. 15): belanjakan
    #     sebelum gilirannya, apa pun yang bisa dibelanjakan.
    ambang = min((int(t.split(":")[1]) for f in foes for s in f.skills for t in s.tags
                  if t.startswith("nyala_penjaga:")), default=0)
    if ambang and battle.bara >= ambang - 1:
        kandidat = battle.usable_bara_skills(actor)
        serangan = [s for s in kandidat if s.is_attack
                    and not all(_known_bad(battle, f, s.element) for f in foes)]
        if serangan:
            best = max(serangan, key=lambda s: s.power * (len(foes) if s.target.is_multi else 1))
            ts = foes if best.target.is_multi else [max(foes, key=lambda c: c.hp)]
            return Action("skill", skill=best, targets=ts)
        sembuh = [s for s in kandidat if s.kind == SkillKind.HEAL]
        if sembuh and any(a.hp_ratio < 0.9 for a in allies):
            return Action("skill", skill=sembuh[0], targets=allies)

    # 2. Jurus Bara kalau tersedia dan lawan masih banyak HP-nya
    bara_atk = [s for s in battle.usable_bara_skills(actor) if s.is_attack]
    if bara_atk and (len(foes) >= 2 or foes[0].hp_ratio > 0.5):
        best = max(bara_atk, key=lambda s: s.power * (len(foes) if s.target.is_multi else 1))
        return Action("skill", skill=best, targets=[max(foes, key=lambda c: c.hp)])

    # 3. Skill serangan: prioritas kelemahan yang diketahui, hindari yang diketahui buruk
    attacks = [s for s in skills if s.is_attack]
    target = max(foes, key=lambda c: c.hp) if len(foes) > 1 else foes[0]
    best_score, best_choice = 0.0, None
    for s in attacks:
        ts = foes if s.target.is_multi else [target]
        score = 0.0
        for t in ts:
            weak = _known_weakness(battle, t)
            if _known_bad(battle, t, s.element):
                score -= 5
            elif weak == s.element:
                score += s.power * 1.5
            elif s.element not in battle.bestiary.get(t.key) and s.element != Element.FISIK:
                score += s.power * 1.1   # eksplorasi elemen baru
            else:
                score += s.power * 0.9
        score /= (1 + s.cost / 10)      # hemat MP sedikit
        if score > best_score:
            best_score, best_choice = score, s
    if best_choice and best_score > 1.0:
        ts = foes if best_choice.target.is_multi else [target]
        return Action("skill", skill=best_choice, targets=ts)
    # Serang biasa: pilih sasaran yang tidak diketahui tahan/serap terhadap elemen senjata
    ok_targets = [f for f in foes if not _known_bad(battle, f, actor.weapon_element)]
    if ok_targets:
        target = max(ok_targets, key=lambda c: c.hp) if len(ok_targets) > 1 else ok_targets[0]
    return Action("serang", targets=[target])
