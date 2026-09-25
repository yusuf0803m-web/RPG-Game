"""Audit potret tokoh (GAME_DESIGN §7.3, Character Visual Bible §3–4).

Mengukur tiap berkas di ``pelita/web/static/assets/characters/<id>/`` dan
melaporkan apakah berkas itu layak tampil di panggung:

- kanvas, ukuran berkas, kanal alpha, bounding box piksel opak
- puncak kepala (crown), badan sampai tepi bawah, lebar bahu di y=600
- latar tercetak: piksel opak di bingkai 4 px tepi kanvas (papan catur, latar hitam, dst.)
- lubang pakaian: piksel transparan di bawah leher (y >= 480) yang sepenuhnya dikelilingi
  karakter; celah yang tembus ke tepi kanvas (lengan-badan) bukan lubang
- identitas dengan master di luar zona ekspresi (``tools/zona_ekspresi.json``, Bible A6):
  selisih piksel rata-rata & persentil 99 harus setara derau encode ulang WebP
- landmark wajah (pupil, dagu) dari ``landmark_potret.json`` yang diukur manual,
  lalu kecocokannya dengan crop wajah di ``tokoh.json`` dan dengan master (neutral).
  Landmark disimpan di ``tools/landmark_potret.json`` (koordinat kanvas 720x960).

Pemakaian:

    python tools/audit_potret.py                 # semua tokoh
    python tools/audit_potret.py rimba           # satu tokoh
    python tools/audit_potret.py rimba --json    # keluaran mesin

Butuh Pillow dan numpy (alat pengembang; permainan sendiri tidak memakainya).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

AKAR = Path(__file__).resolve().parent.parent
ASET = AKAR / "pelita" / "web" / "static" / "assets" / "characters"
REGISTRI = AKAR / "pelita" / "data" / "tokoh.json"
LANDMARK = Path(__file__).resolve().parent / "landmark_potret.json"
ZONA = Path(__file__).resolve().parent / "zona_ekspresi.json"
# Derau encode ulang WebP q85 pada master Rimba: rata-rata 3,0, p99 10. Di atas ini = gambar lain.
LUAR_ZONA_RATA = 4.0
LUAR_ZONA_P99 = 14

KANVAS = (720, 960)
BATAS_KB = 160
Y_PAKAIAN = 480          # di bawah garis ini = leher/pakaian; celah rambut di atasnya bukan lubang
Y_BAHU = 600
ZONA_PANGGUNG = 672
TEPI_BAWAH = 40          # baris terbawah: tepi badan yang memudar/bergerigi (di bawah zona panggung), bukan lubang
TOLERANSI_MATA = 4       # px, Bible A2: garis mata ±4
TOLERANSI_DAGU = 12      # px, Bible A2: dagu ±12


def lubang_tertutup(alpha: np.ndarray, y0: int = Y_PAKAIAN) -> np.ndarray:
    """Lubang pakaian untuk audit: piksel transparan di bawah leher yang TIDAK terhubung ke
    tepi kanvas, yaitu sepenuhnya dikelilingi piksel opak.

    Transparansi yang tembus ke tepi kanvas (celah antara lengan dan badan, tepi bawah yang
    memudar) adalah celah terbuka, bukan lubang.
    """
    h, w = alpha.shape
    transparan = Image.fromarray(((alpha < 128) * 255).astype(np.uint8)).copy()
    tepi = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    for p in tepi:
        if transparan.getpixel(p) == 255:
            ImageDraw.floodfill(transparan, p, 128)        # terhubung ke luar kanvas = celah terbuka
    hasil = np.array(transparan) == 255
    hasil[:y0] = False
    return hasil


def lubang_pakaian(alpha: np.ndarray, y0: int = Y_PAKAIAN) -> np.ndarray:
    """Piksel transparan di dalam rentang badan, di bawah leher. Dipakai
    ``rapikan_potret.py --tutup-lubang`` untuk menemukan piksel yang dipulihkan; audit memakai
    ``lubang_tertutup`` karena rentang baris juga menangkap celah terbuka lengan-badan.

    Bust-up dari dada ke atas: tiap baris badan adalah satu rentang tanpa celah
    (lengan menempel ke badan). Jadi "di dalam badan" = di antara piksel opak
    terkiri dan terkanan pada baris itu. Baris paling bawah yang memudar ke
    transparan (badan tipis di tepi bawah) tidak dihitung: hanya baris yang
    lebarnya minimal 60% dari lebar badan biasa.
    """
    h, w = alpha.shape
    opak = alpha >= 128
    hasil = np.zeros_like(opak)
    jumlah = opak.sum(1)
    acuan = np.median(jumlah[y0:min(h, y0 + 300)]) if h > y0 else 0
    for y in range(y0, h - TEPI_BAWAH):
        if acuan == 0 or jumlah[y] < 0.6 * acuan:
            continue
        xs = np.nonzero(opak[y])[0]
        hasil[y, xs[0]:xs[-1] + 1] = ~opak[y, xs[0]:xs[-1] + 1]
    return hasil


def ukur(berkas: Path) -> dict:
    im = Image.open(berkas)
    rgba = np.array(im.convert("RGBA"))
    a = rgba[..., 3]
    h, w = a.shape
    opak = a > 8
    ys, xs = np.nonzero(opak)
    # Bingkai 4 px di atas, kiri, dan kanan (tepi bawah memang boleh tertutup badan;
    # sisi kiri/kanan hanya sampai y=700 karena lengan boleh menyentuh tepi di bawah).
    idx = np.zeros_like(a, bool)
    idx[:4, :] = True
    idx[:700, :4] = True
    idx[:700, -4:] = True
    opak_bingkai = a[idx] >= 250
    rgb_bingkai = rgba[..., :3][idx].astype(int)
    netral_terang = ((rgb_bingkai.max(1) - rgb_bingkai.min(1)) <= 14) & (rgb_bingkai.mean(1) >= 185)
    lubang = lubang_tertutup(a)
    baris_bahu = np.nonzero(a[Y_BAHU] >= 128)[0]
    return {
        "berkas": berkas.name,
        "kanvas": [w, h],
        "kb": round(berkas.stat().st_size / 1024, 1),
        "mode": im.mode,
        "alpha_min_maks": [int(a.min()), int(a.max())],
        "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None,
        "crown": int(ys.min()) if len(ys) else None,
        "bawah": int(ys.max()) if len(ys) else None,
        "bahu_y600": [int(baris_bahu[0]), int(baris_bahu[-1])] if len(baris_bahu) else None,
        "bingkai_opak_pct": round(100 * opak_bingkai.mean(), 1),
        "latar_tercetak": bool(opak_bingkai.mean() > 0.2),
        "papan_catur": bool(opak_bingkai.mean() > 0.2 and netral_terang[opak_bingkai].mean() > 0.8),
        "lubang_pakaian_px": int(lubang.sum()),
        "semi_transparan_pct": round(100 * ((a > 8) & (a < 247)).mean(), 2),
    }


def muat_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def audit_tokoh(tid: str) -> list[dict]:
    reg = muat_json(REGISTRI).get("tokoh", {}).get(tid, {})
    lm_semua = muat_json(LANDMARK).get(tid, {})
    bawaan = reg.get("ekspresi_bawaan", "neutral")
    wajah_tokoh = reg.get("wajah", muat_json(REGISTRI).get("wajah_bawaan", [216, 120, 288]))
    hasil = []
    for berkas in sorted((ASET / tid).glob("*.*")):
        if berkas.suffix not in (".webp", ".png"):
            continue
        eks = berkas.stem
        r = ukur(berkas)
        r["ekspresi"] = eks
        conf = reg.get("ekspresi", {}).get(eks, {})
        r["panggung_false"] = conf.get("panggung") is False
        x, y, s = conf.get("wajah", wajah_tokoh)
        r["crop_wajah"] = [x, y, s]
        lm = lm_semua.get(eks)
        if lm:
            mata_y = (lm["pupil_kiri"][1] + lm["pupil_kanan"][1]) / 2
            mata_x = (lm["pupil_kiri"][0] + lm["pupil_kanan"][0]) / 2
            r["garis_mata"] = round(mata_y, 1)
            r["dagu"] = lm["dagu"][1]
            r["mata_ke_dagu"] = round(lm["dagu"][1] - mata_y, 1)
            r["crop_ok"] = bool(x <= mata_x <= x + s and y + 0.3 * s <= mata_y <= y + 0.5 * s
                                and lm["dagu"][1] <= y + s)
            r["zona_panggung_ok"] = bool(lm["dagu"][1] <= ZONA_PANGGUNG)
        hasil.append(r)
    zona = muat_json(ZONA).get(tid)
    berkas_master = next((b for b in (ASET / tid).glob(f"{bawaan}.*") if b.suffix in (".webp", ".png")), None)
    if zona and berkas_master:
        M =np.array(Image.open(berkas_master).convert("RGBA")).astype(int)
        img = Image.new("L", KANVAS, 0)
        ImageDraw.Draw(img).polygon([tuple(p) for p in zona["poligon"]], fill=255)
        dalam = np.array(img.filter(ImageFilter.MaxFilter(9))) > 0        # + pita 4 px derau di tepi zona
        for r in hasil:
            if r["ekspresi"] == bawaan:
                continue
            X = np.array(Image.open(ASET / tid / r["berkas"]).convert("RGBA")).astype(int)
            if X.shape != M.shape:
                continue
            luar = ~dalam & ((M[..., 3] > 0) | (X[..., 3] > 0))
            d = np.abs(X - M).max(2)[luar]
            r["luar_zona_rata"] = round(float(d.mean()), 2)
            r["luar_zona_p99"] = float(np.percentile(d, 99))
            r["luar_zona_sama"] = bool(r["luar_zona_rata"] <= LUAR_ZONA_RATA and r["luar_zona_p99"] <= LUAR_ZONA_P99)
    master = next((r for r in hasil if r["ekspresi"] == bawaan and "garis_mata" in r), None)
    for r in hasil:
        if master and "garis_mata" in r:
            r["geser_mata_vs_master"] = round(r["garis_mata"] - master["garis_mata"], 1)
            r["geser_dagu_vs_master"] = round(r["dagu"] - master["dagu"], 1)
            r["skala_vs_master"] = round(r["mata_ke_dagu"] / master["mata_ke_dagu"], 3)   # info saja
        r["panggung_siap"] = bool(
            r.get("luar_zona_sama", True) and
            r["kanvas"] == list(KANVAS) and r["alpha_min_maks"][0] == 0 and not r["latar_tercetak"]
            and r["lubang_pakaian_px"] < 50 and r["kb"] <= BATAS_KB
            and (not master or r is master or (
                abs(r.get("geser_mata_vs_master", 99)) <= TOLERANSI_MATA
                and abs(r.get("geser_dagu_vs_master", 99)) <= TOLERANSI_DAGU)))
    return hasil


def main(argv: list[str]) -> int:
    ids = [a for a in argv if not a.startswith("--")] or sorted(
        p.name for p in ASET.iterdir() if p.is_dir())
    semua = {tid: audit_tokoh(tid) for tid in ids}
    if "--json" in argv:
        print(json.dumps(semua, indent=1))
        return 0
    kolom = ["ekspresi", "kanvas", "kb", "alpha_min_maks", "crown", "garis_mata", "dagu", "bawah",
             "bahu_y600", "geser_mata_vs_master", "geser_dagu_vs_master", "skala_vs_master", "latar_tercetak",
             "papan_catur", "lubang_pakaian_px", "luar_zona_rata", "luar_zona_p99", "crop_ok", "zona_panggung_ok", "panggung_siap"]
    for tid, rows in semua.items():
        print(f"== {tid}")
        for r in rows:
            print("  " + "  ".join(f"{k}={r.get(k, '-')}" for k in kolom))
    gagal = [f"{t}/{r['ekspresi']}" for t, rows in semua.items() for r in rows if not r["panggung_siap"]]
    print("belum siap panggung:", ", ".join(gagal) if gagal else "tidak ada")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
