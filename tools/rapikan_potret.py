"""Rapikan potret tokoh tanpa menggambar ulang (GAME_DESIGN §7.3).

Empat operasi, semuanya deterministik dan hanya memakai piksel yang sudah ada:

1. ``--papan-catur``: latar papan catur yang tercetak sebagai piksel opak diganti
   transparansi sungguhan. Tepi karakter di-matte terhadap dua nada latar yang
   diketahui: alpha dari proyeksi warna piksel ke garis latar→karakter, dan warna
   tepi dibersihkan dari sisa latar.
2. ``--tutup-lubang``: lubang transparan di pakaian ditutup kembali dengan
   mengembalikan alpha ke 255. Hanya aman kalau RGB di bawah lubang masih utuh
   (pencocokan latar yang salah menghapus alpha, bukan warnanya) — periksa dulu.
3. ``--selaraskan``: skala + geser (tanpa rotasi, tanpa warp) supaya landmark wajah
   cocok dengan master. Landmark berkas sumber dari ``tools/landmark_potret.json``
   (``--landmark tokoh@sumber``); transformnya
   kuadrat-terkecil atas pupil, hidung, dagu, telinga.

4. ``--transplantasi MASTER``: wajah bagian dalam (alis–mata–hidung–mulut–pipi, poligon di
   ``tools/zona_ekspresi.json``) dari berkas masuk ditempel ke master; di luar zona, keluaran
   = master piksel demi piksel. Dipakai supaya semua ekspresi memakai rambut, kepala, bahu,
   dan pakaian yang sama persis dengan master.

Pemakaian:

    python tools/rapikan_potret.py MASUK.webp KELUAR.webp --tokoh rimba --ekspresi happy \\
        [--papan-catur] [--tutup-lubang] [--selaraskan --landmark rimba@rilis2]

Butuh Pillow dan numpy. Laporan transform dicetak sebagai JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_potret import LANDMARK, lubang_pakaian  # noqa: E402

TITIK = ("pupil_kiri", "pupil_kanan", "hidung", "dagu", "telinga")


# ── 1. Papan catur ───────────────────────────────────────────────────────
def _kandidat_latar(rgb: np.ndarray) -> np.ndarray:
    """Abu netral terang: dua nada papan catur (~250 & ~208) dan transisinya."""
    c = rgb.max(2).astype(int) - rgb.min(2)
    return (c <= 16) & (rgb.mean(2) >= 180)


def _tersambung_ke_tepi(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    peta = np.full((h + 2, w + 2), 255, np.uint8)       # bingkai = kandidat, menyambung semua tepi
    peta[1:-1, 1:-1] = np.where(mask, 255, 0)
    img = Image.fromarray(peta).copy()
    ImageDraw.floodfill(img, (0, 0), 128)
    return np.array(img)[1:-1, 1:-1] == 128


def _lebarkan(mask: np.ndarray, r: int) -> np.ndarray:
    img = Image.fromarray((mask * 255).astype(np.uint8))
    while r > 0:
        k = min(r, 5)
        img = img.filter(ImageFilter.MaxFilter(2 * k + 1))
        r -= k
    return np.array(img) > 0


def _sempitkan(mask: np.ndarray, r: int) -> np.ndarray:
    return ~_lebarkan(~mask, r)


def _rata_terbobot(nilai: np.ndarray, bobot: np.ndarray, r: int) -> tuple[np.ndarray, np.ndarray]:
    """Rata-rata lokal (kotak (2r+1)^2) hanya dari piksel berbobot 1; plus penanda 'ada data'."""
    def kotak(a):
        k = 2 * r + 1
        pad = np.pad(a, ((r + 1, r), (r + 1, r)) + ((0, 0),) * (a.ndim - 2))
        s = pad.cumsum(0).cumsum(1)
        return s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]
    b = bobot.astype(np.float64)
    atas = kotak(nilai.astype(np.float64) * b[..., None])
    bawah = kotak(b)[..., None]
    return np.where(bawah > 0, atas / np.maximum(bawah, 1e-9), nilai), bawah[..., 0] > 0


def hapus_papan_catur(rgba: np.ndarray, jangkau_kantong: int = 20,
                      batas_kepala: int = 0) -> tuple[np.ndarray, dict]:
    """Latar papan catur tercetak → alpha sungguhan.

    Latar = abu netral terang yang tersambung ke tepi kanvas, ditambah kantong abu
    netral di sela helai rambut yang berjarak ≤ ``jangkau_kantong`` px dari latar
    luar (gigi, kerah, dan sorot cahaya jauh di dalam siluet tidak tersentuh).
    Di pita tepi, tiap piksel dianggap campuran warna karakter F (rata-rata lokal
    piksel karakter pasti) dan salah satu dari dua nada latar; alpha diambil dari
    nada yang residunya paling kecil.
    """
    rgb = rgba[..., :3].astype(np.float64)
    kandidat = _kandidat_latar(rgba[..., :3])
    luar = _tersambung_ke_tepi(kandidat)
    dekat = _lebarkan(luar, jangkau_kantong)
    # Dekat latar luar, kompresi mencemari abu latar dengan warna rambut yang hangat: ambang
    # dilonggarkan — tapi tidak untuk piksel kebiruan, karena itu cahaya rim di tepi karakter.
    c = rgb.max(2) - rgb.min(2)
    longgar = (c <= 40) & (rgb.mean(2) >= 165) & (rgb[..., 2] - rgb[..., 0] <= 6)
    latar = luar | ((kandidat | longgar) & dekat)

    v = rgb[latar].mean(1)
    terang = float(np.median(v[v > 229])) if (v > 229).any() else 250.0
    gelap = float(np.median(v[v <= 229])) if (v <= 229).any() else 208.0

    latar_pasti = _sempitkan(latar, 1)
    fg_pasti = ~_lebarkan(latar, 3)
    ragu = ~latar_pasti & ~fg_pasti

    F, ada = _rata_terbobot(rgb, fg_pasti, 4)
    F2, _ = _rata_terbobot(rgb, fg_pasti, 10)
    F = np.where(ada[..., None], F, F2)

    alpha = np.where(fg_pasti, 1.0, 0.0)
    terbaik = np.full(alpha.shape, np.inf)
    for nada in (terang, gelap):
        B = np.full_like(rgb, nada)
        d = F - B
        a = np.clip(((rgb - B) * d).sum(2) / np.maximum((d * d).sum(2), 1e-6), 0, 1)
        sisa = np.linalg.norm(rgb - (a[..., None] * F + (1 - a[..., None]) * B), axis=2)
        lebih_baik = ragu & (sisa < terbaik)
        alpha = np.where(lebih_baik, a, alpha)
        terbaik = np.where(lebih_baik, sisa, terbaik)

    # Latar papan catur abu netral sempurna, jadi "warna" piksel campuran berbanding lurus
    # dengan alpha: C − rata(C) = α·(F − rata(F)). Ini menyelamatkan tepi yang berwarna
    # (rim light biru, kulit, rambut oranye) yang proyeksi dua-nada di atas salah tafsirkan
    # sebagai campuran dengan latar putih — tanpa mengeraskan anti-aliasing-nya.
    dev_c = np.linalg.norm(rgb - rgb.mean(2, keepdims=True), axis=2)
    dev_f = np.linalg.norm(F - F.mean(2, keepdims=True), axis=2)
    alpha_kroma = np.clip(dev_c / np.maximum(dev_f, 1e-6), 0, 1)
    alpha = np.where(ragu & (dev_f >= 15), np.maximum(alpha, alpha_kroma), alpha)

    # Sisa papan catur di ujung helai: abu netral sempurna (r≈g≈b) yang terang dan menempel ke
    # latar. Sorot cahaya di mata/gigi tidak tersentuh karena jauh dari latar.
    netral_sempurna = ((np.abs(rgb[..., 0] - rgb[..., 1]) <= 6) & (np.abs(rgb[..., 2] - rgb[..., 0]) <= 6)
                       & (rgb.mean(2) >= 180))
    sisa_papan = netral_sempurna & _lebarkan(alpha < 0.5, 6) & (alpha > 0)
    # Kantong latar di sela helai rambut: abu terang berkroma rendah di tengah rambut yang
    # warnanya pekat (hitam/biru/oranye). Hanya di area kepala di atas kerah, supaya kemeja,
    # gigi, dan putih mata tidak tersentuh.
    if batas_kepala:
        pucat = (rgb.mean(2) > 150) & ((rgb.max(2) - rgb.min(2)) < 60)
        kepala = np.zeros_like(pucat)
        kepala[:batas_kepala] = True
        sisa_papan |= pucat & kepala & _lebarkan(alpha < 0.5, jangkau_kantong) & (alpha > 0)
    alpha = np.where(sisa_papan, 0.0, alpha)

    keluar = rgba.copy()
    bersih = np.where(ragu[..., None], F, rgb)          # warna tepi tanpa sisa latar
    keluar[..., :3] = np.clip(np.round(bersih), 0, 255).astype(np.uint8)
    keluar[..., 3] = np.round(alpha * 255).astype(np.uint8)
    keluar[..., :3][keluar[..., 3] == 0] = 0
    return keluar, {"nada_latar": [round(terang, 1), round(gelap, 1)],
                    "piksel_latar": int(latar.sum()), "piksel_kantong_rambut": int((latar & ~luar).sum()),
                    "piksel_tepi_dimatte": int(ragu.sum()), "sisa_papan_dibuang": int(sisa_papan.sum()),
                    "residu_rata_tepi": round(float(terbaik[ragu].mean()), 1) if ragu.any() else 0.0}


# ── 2. Lubang pakaian ────────────────────────────────────────────────────
def tutup_lubang(rgba: np.ndarray) -> tuple[np.ndarray, dict]:
    lubang = lubang_pakaian(rgba[..., 3])
    lebar = np.array(Image.fromarray((lubang * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    # Pinggiran lubang ikut dipulihkan, tapi hanya di dalam badan (bukan ke latar luar).
    dalam = lubang_pakaian(np.where(lebar, 255, rgba[..., 3]).astype(np.uint8)) | lebar
    dalam &= lebar
    keluar = rgba.copy()
    keluar[..., 3] = np.where(dalam, 255, rgba[..., 3])
    rgb_lubang = rgba[..., :3][lubang].astype(int)
    return keluar, {"piksel_lubang": int(lubang.sum()), "piksel_dipulihkan": int(dalam.sum()),
                    "rgb_rata_di_lubang": rgb_lubang.mean(0).round(1).tolist() if len(rgb_lubang) else None}


# ── 3. Penyelarasan ──────────────────────────────────────────────────────
def fit_skala_geser(sumber: dict, sasaran: dict) -> tuple[float, float, float, float]:
    """s, tx, ty yang meminimalkan Σ|s·p + t − q|²; plus galat rata-rata (px)."""
    P = np.array([sumber[k] for k in TITIK], float)
    Q = np.array([sasaran[k] for k in TITIK], float)
    pm, qm = P.mean(0), Q.mean(0)
    s = ((P - pm) * (Q - qm)).sum() / ((P - pm) ** 2).sum()
    t = qm - s * pm
    galat = np.linalg.norm(s * P + t - Q, axis=1).mean()
    return float(s), float(t[0]), float(t[1]), float(galat)


def terapkan(rgba: np.ndarray, s: float, tx: float, ty: float) -> np.ndarray:
    """Skala + geser di ruang alpha-premultiplied (tanpa halo gelap di tepi)."""
    img = Image.fromarray(rgba, "RGBA").convert("RGBa")
    # PIL memetakan keluaran → masukan: x_in = (x_out − tx)/s
    hasil = img.transform(img.size, Image.AFFINE, (1 / s, 0, -tx / s, 0, 1 / s, -ty / s),
                          resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    return np.array(hasil.convert("RGBA"))


# ── 4. Transplantasi zona ekspresi ke master ─────────────────────────────
ZONA = Path(__file__).resolve().parent / "zona_ekspresi.json"


def _poligon(poligon, shape) -> np.ndarray:
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([tuple(p) for p in poligon], fill=255)
    return np.array(img) > 0


def _blur(mask: np.ndarray, sigma: float) -> np.ndarray:
    img = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
    return np.array(img.filter(ImageFilter.GaussianBlur(sigma))).astype(np.float64) / 255


def _ke_lab(rgb):
    return np.array(Image.fromarray(rgb.astype(np.uint8)).convert("LAB")).astype(np.float64)


def _dari_lab(lab):
    return np.array(Image.fromarray(np.clip(np.round(lab), 0, 255).astype(np.uint8), "LAB").convert("RGB"))


def transplantasi(master: np.ndarray, eks: np.ndarray, s: float, tx: float, ty: float,
                  poligon: list, poni: list) -> tuple[np.ndarray, dict]:
    """Master utuh + wajah bagian dalam dari ``eks`` (Bible A6).

    1. ``eks`` diskalakan/digeser supaya pupil & hidungnya jatuh di pupil & hidung master.
    2. Warna kulitnya disamakan dengan master di cincin tepi zona (rata-rata & sebaran Lab).
    3. Dicampur ke master lewat zona yang dihaluskan dan dikecilkan ke dalam, jadi tepi
       zona tetap 100% master; helai poni master di kotak ``poni`` tetap di atas.
    Di luar poligon, keluaran = master piksel demi piksel.
    """
    h, w = master.shape[:2]
    Ew = terapkan(eks, s, tx, ty)[..., :3].astype(np.float64)
    M = master[..., :3].astype(np.float64)
    m = _poligon(poligon, (h, w))

    luar = _lebarkan(m, 7) & ~_sempitkan(m, 7) & m
    lum_m, lum_e = M.mean(2), Ew.mean(2)
    kulit = luar & (lum_m > 90) & (lum_e > 90)
    la, lb = _ke_lab(Ew), _ke_lab(M)
    ma, sa = la[kulit].mean(0), la[kulit].std(0) + 1e-3
    mb, sb = lb[kulit].mean(0), lb[kulit].std(0) + 1e-3
    E = _dari_lab((la - ma) * np.clip(sb / sa, 0.85, 1.15) + mb).astype(np.float64)

    x0, y0, x1, y1 = poni
    kotak = np.zeros((h, w), bool)
    kotak[y0:y1, x0:x1] = True
    rambut = _lebarkan(kotak & m & (lum_m < 85), 1)

    alpha = _blur(_sempitkan(m, 8), 4) * (1 - _blur(rambut, 1.0))
    alpha = np.where(m, alpha, 0.0)[..., None]
    keluar = master.copy()
    keluar[..., :3] = np.round(alpha * E + (1 - alpha) * M).astype(np.uint8)
    berubah = np.abs(keluar.astype(int) - master.astype(int)).max(2) > 0
    return keluar, {"geser_warna_lab": np.round(mb - ma, 1).tolist(),
                    "piksel_zona": int(m.sum()), "piksel_poni_master_dipertahankan": int(rambut.sum()),
                    "piksel_berubah": int(berubah.sum()),
                    "piksel_berubah_di_luar_zona": int((berubah & ~m).sum())}


def fit_mata_hidung(sumber: dict, sasaran: dict) -> tuple[float, float, float, list]:
    """Similarity dari pupil & hidung saja (wajah bagian dalam), bukan telinga/dagu."""
    k = ("pupil_kiri", "pupil_kanan", "hidung")
    P = np.array([sumber[x] for x in k], float)
    Q = np.array([sasaran[x] for x in k], float)
    pm, qm = P.mean(0), Q.mean(0)
    s = ((P - pm) * (Q - qm)).sum() / ((P - pm) ** 2).sum()
    t = qm - s * pm
    return float(s), float(t[0]), float(t[1]), np.round(np.linalg.norm(s * P + t - Q, axis=1), 1).tolist()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("masuk")
    ap.add_argument("keluar")
    ap.add_argument("--tokoh", required=True)
    ap.add_argument("--ekspresi", required=True)
    ap.add_argument("--master", default="neutral")
    ap.add_argument("--landmark", help="kunci landmark berkas sumber, mis. rimba@rilis2 (bawaan: --tokoh)")
    ap.add_argument("--papan-catur", action="store_true")
    ap.add_argument("--tutup-lubang", action="store_true")
    ap.add_argument("--selaraskan", action="store_true")
    ap.add_argument("--transplantasi", metavar="MASTER",
                    help="tempel wajah bagian dalam MASUK ke berkas master (zona dari tools/zona_ekspresi.json)")
    ap.add_argument("--kualitas", type=int, default=85)
    ap.add_argument("--batas-kepala", type=int, default=0,
                    help="y kerah di berkas sumber; di atasnya kantong latar di sela rambut ikut dibuang")
    a = ap.parse_args(argv)

    rgba = np.array(Image.open(a.masuk).convert("RGBA"))
    laporan: dict = {"berkas": Path(a.keluar).name}
    if a.papan_catur:
        rgba, laporan["papan_catur"] = hapus_papan_catur(rgba, batas_kepala=a.batas_kepala)
    if a.tutup_lubang:
        rgba, laporan["tutup_lubang"] = tutup_lubang(rgba)
    if a.selaraskan:
        lm = json.loads(LANDMARK.read_text(encoding="utf-8"))[a.landmark or a.tokoh]
        s, tx, ty, galat = fit_skala_geser(lm[a.ekspresi], lm[a.master])
        rgba = terapkan(rgba, s, tx, ty)
        laporan["selaraskan"] = {"skala": round(s, 4), "geser_x": round(tx, 1), "geser_y": round(ty, 1),
                                 "galat_landmark_px": round(galat, 1)}
    if a.transplantasi:
        lm = json.loads(LANDMARK.read_text(encoding="utf-8"))
        zona = json.loads(ZONA.read_text(encoding="utf-8"))[a.tokoh]
        s, tx, ty, galat = fit_mata_hidung(lm[a.landmark or a.tokoh][a.ekspresi], lm[a.tokoh][a.master])
        master = np.array(Image.open(a.transplantasi).convert("RGBA"))
        rgba, laporan["transplantasi"] = transplantasi(master, rgba, s, tx, ty, zona["poligon"], zona["poni"])
        laporan["transplantasi"].update({"skala": round(s, 4), "geser_x": round(tx, 1), "geser_y": round(ty, 1),
                                         "galat_pupil_hidung_px": galat})
    Image.fromarray(rgba, "RGBA").save(a.keluar, "WEBP", quality=a.kualitas, alpha_quality=100, method=6)
    laporan["kb"] = round(Path(a.keluar).stat().st_size / 1024, 1)
    print(json.dumps(laporan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
