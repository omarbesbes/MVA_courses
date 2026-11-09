#!/usr/bin/env python3
"""Reencrage : transforme le PDF "marqueurs" (LuaLaTeX) en fiche qui a l'air ecrite au stylo.

Etapes, pour chaque page rendue a 600 dpi :
  1. separation des encres (marqueurs : bleu pur, rouge pur, vert pur, noir, cyan = violet,
     magenta = crayon) ;
  2. deformation elastique multi-echelle (meme champ pour toutes les encres) :
     rotation globale, derive lente de la page, lignes qui ondulent et penchent chacune a sa facon,
     mots legerement decales, forme de chaque lettre legerement alteree ;
  3. reencrage : squelette des traits puis repasse "au stylo" avec une largeur de pointe quasi
     constante (toutes les polices -- texte, maths, symboles -- ont alors le meme stylo), qui varie
     doucement le long du trait ; petits depots d'encre aux debuts/fins de traits ;
  4. pression et texture de l'encre, crayon a papier grainé pour les traits de colonnes ;
  5. composition soustractive sur blanc pur (le fond reste exactement blanc a l'impression).

Sorties : <base>_impression.pdf (sans quadrillage, a imprimer de preference sur papier petits
carreaux) et <base>_quadrille.pdf (petits carreaux 5 mm dessines, pour l'ecran ou papier blanc).

usage : python3 ../../outils_manuscrit/reencrage.py fiche_xxx_realiste.pdf [--dpi 600] [--seed 11]
dependances : numpy scipy scikit-image opencv-python-headless img2pdf pillow, poppler (pdftoppm)
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile
import time

import cv2
import img2pdf
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

# ------------------------------------------------------------------ encres
# marqueur (RGB 0-1) -> couleur finale (RGB 0-1), facteur de largeur de pointe, type
INKS = {
    "bleu":   dict(marker=(0, 0, 1), color=(0.106, 0.180, 0.560), pen=1.00, kind="stylo"),
    "rouge":  dict(marker=(1, 0, 0), color=(0.780, 0.110, 0.150), pen=1.07, kind="stylo"),
    "vert":   dict(marker=(0, 1, 0), color=(0.090, 0.450, 0.200), pen=1.00, kind="stylo"),
    "noir":   dict(marker=(0, 0, 0), color=(0.110, 0.110, 0.130), pen=1.00, kind="stylo"),
    "violet": dict(marker=(0, 1, 1), color=(0.400, 0.180, 0.520), pen=1.00, kind="stylo"),
    "crayon": dict(marker=(1, 0, 1), color=(0.420, 0.420, 0.440), pen=0.70, kind="crayon"),
}
ORDER = ["crayon", "bleu", "vert", "noir", "violet", "rouge"]   # ordre de pose (soustractif : peu importe)


def mm(x, dpi):
    return x * dpi / 25.4


# ------------------------------------------------------------------ bruits lisses
def smooth_noise(shape, Lx, Ly, rng):
    """Champ gaussien lisse, ecart-type 1, longueurs de correlation ~Lx, Ly (pixels)."""
    H, W = shape
    sx, sy = max(Lx / 2.0, 1.0), max(Ly / 2.0, 1.0)
    gh, gw = int(np.ceil(H / sy)) + 4, int(np.ceil(W / sx)) + 4
    g = rng.standard_normal((gh, gw)).astype(np.float32)
    g = ndi.gaussian_filter(g, 1.0, mode="wrap")
    g /= g.std() + 1e-9
    # agrandissement bicubique (on recadre pour eviter les bords)
    big = cv2.resize(g, (int(gw * sx), int(gh * sy)), interpolation=cv2.INTER_CUBIC)
    oy, ox = int(2 * sy), int(2 * sx)
    big = big[oy:oy + H, ox:ox + W]
    return big / (big.std() + 1e-9)


def displacement(shape, dpi, rng, strength=1.0):
    """Champ de deplacement (dx, dy) en pixels : somme de plusieurs echelles."""
    H, W = shape
    m = lambda v: mm(v, dpi)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # rotation globale (la feuille n'est jamais parfaitement droite) + legere derive d'echelle
    th = np.deg2rad(rng.normal(0, 0.22))
    cy, cx = H / 2, W / 2
    dx = (np.cos(th) - 1) * (xx - cx) - np.sin(th) * (yy - cy)
    dy = np.sin(th) * (xx - cx) + (np.cos(th) - 1) * (yy - cy)
    del xx, yy
    comps = [
        # (Lx mm, Ly mm, amplitude x mm, amplitude y mm)
        (70, 70, 0.50, 0.50),     # derive lente de la page (colonnes pas tout a fait droites)
        (22, 2.6, 0.16, 0.21),    # chaque ligne ondule / penche a sa facon, debut de ligne irregulier
        (1.7, 1.7, 0.045, 0.050), # mots
        (0.50, 0.50, 0.030, 0.032),  # forme des lettres
    ]
    for Lx, Ly, ax, ay in comps:
        dx += strength * m(ax) * smooth_noise(shape, m(Lx), m(Ly), rng)
        dy += strength * m(ay) * smooth_noise(shape, m(Lx), m(Ly), rng)
    return dx.astype(np.float32), dy.astype(np.float32)


# ------------------------------------------------------------------ etapes
def separate(img):
    """img float32 (H,W,3) dans [0,1] -> dict encre -> alpha (H,W) dans [0,1]."""
    A = 1.0 - img                                     # "absorbance"
    names = list(INKS)
    a = np.array([1.0 - np.array(INKS[n]["marker"], np.float32) for n in names])  # (k,3)
    proj = np.einsum("hwc,kc->hwk", A, a) / (a * a).sum(1)                      # alpha par encre
    resid = np.stack([np.linalg.norm(A - proj[..., k:k + 1] * a[k], axis=2) for k in range(len(names))], -1)
    best = resid.argmin(-1)
    alpha_all = np.clip(np.take_along_axis(proj, best[..., None], -1)[..., 0], 0, 1)
    ink = np.linalg.norm(A, axis=2) > 0.02
    out = {}
    for k, n in enumerate(names):
        al = np.where(ink & (best == k), alpha_all, 0).astype(np.float32)
        if al.max() > 0.3:
            out[n] = al
    return out


def warp(alpha, dx, dy):
    H, W = alpha.shape
    gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    return cv2.remap(alpha, gx + dx, gy + dy, interpolation=cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def pen_radius_map(r_local, r0):
    """Largeur de pointe : on rapproche toutes les epaisseurs de celle du stylo (r0),
    on garde le gras plus epais et les formes pleines (puces) telles quelles."""
    x = r_local / r0
    xp = np.array([0.0, 0.55, 0.85, 1.15, 1.30, 1.75, 2.2, 50.0])
    fp = np.array([0.5, 0.78, 0.96, 1.05, 1.20, 1.38, 2.2, 50.0])
    return r0 * np.interp(x, xp, fp)


def reink(alpha, r0, pen, kind, dpi, rng):
    """Squelette + repasse au stylo. Renvoie la nouvelle couverture (H,W)."""
    H, W = alpha.shape
    mask = alpha > 0.42
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return np.zeros_like(alpha)
    pad = int(6 * r0) + 8
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, H)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, W)
    msk = mask[y0:y1, x0:x1]
    skel = skeletonize(msk)
    inside = ndi.distance_transform_edt(msk)                    # demi-largeur locale
    dist, (iy, ix) = ndi.distance_transform_edt(~skel, return_indices=True)
    r_local = np.maximum(inside[iy, ix] - 0.35, 0.5)
    shape = msk.shape
    r = pen_radius_map(r_local, r0) * pen
    # la pointe ne laisse pas un trait parfaitement regulier
    r *= 1 + 0.085 * smooth_noise(shape, mm(1.3, dpi), mm(1.3, dpi), rng) \
           + 0.035 * smooth_noise(shape, mm(0.25, dpi), mm(0.25, dpi), rng)
    # petits depots d'encre aux extremites des traits (pose / leve du stylo)
    nb = ndi.convolve(skel.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - 1
    ends = skel & (nb == 1)
    if ends.any():
        d_end = ndi.distance_transform_edt(~ends)
        bump = np.exp(-(d_end / (1.6 * r0)) ** 2)
        keep = rng.random(shape) < 1.0
        r *= 1 + 0.16 * bump * keep
    new = np.clip(r + 0.5 - dist, 0, 1).astype(np.float32)
    out = np.zeros_like(alpha)
    out[y0:y1, x0:x1] = new
    return out


def texture(cov, kind, dpi, rng):
    shape = cov.shape
    if kind == "crayon":
        grain = smooth_noise(shape, 1.2, 1.2, rng)
        cov = cov * np.clip(0.76 + 0.17 * grain, 0.40, 1.0)
        return cov * np.clip(0.9 + 0.1 * smooth_noise(shape, mm(4, dpi), mm(4, dpi), rng), 0.7, 1.0)
    # pression : plus clair par endroits, jamais plus fonce que l'encre pleine
    press = 1 - 0.10 * np.abs(smooth_noise(shape, mm(2.5, dpi), mm(2.5, dpi), rng)) \
              - 0.05 * smooth_noise(shape, mm(0.45, dpi), mm(0.45, dpi), rng)
    grain = smooth_noise(shape, 1.4, 1.4, rng)
    return cov * np.clip(press - 0.025 * grain, 0.66, 1.0)


def grid_layer(shape, dpi, rng):
    H, W = shape
    step = mm(5, dpi)
    g = np.ones((H, W), np.float32)
    lw = max(1, int(round(mm(0.09, dpi))))
    ox, oy = rng.uniform(0, step), rng.uniform(0, step)
    for x in np.arange(ox, W, step):
        g[:, int(x):int(x) + lw] = 0
    for y in np.arange(oy, H, step):
        g[int(y):int(y) + lw, :] = 0
    return g   # 0 sur les lignes


def process_page(png, dpi, rng, log):
    t0 = time.time()
    img = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32) / 255.0
    layers = separate(img)
    del img
    shape = next(iter(layers.values())).shape
    dx, dy = displacement(shape, dpi, rng)
    # largeur de pointe de reference : celle de l'encre majoritaire (le texte courant)
    main = max(layers, key=lambda n: float(layers[n].sum()))
    ref = warp(layers[main], dx, dy) > 0.42
    sk = skeletonize(ref[::1, ::1])
    r0 = float(np.median(ndi.distance_transform_edt(ref)[sk])) - 0.35
    del ref, sk
    log(f"    encres : {', '.join(layers)} ; demi-largeur de pointe r0 = {r0:.2f} px")
    out = np.ones(shape + (3,), np.float32)
    for name in ORDER:
        if name not in layers:
            continue
        p = INKS[name]
        cov = warp(layers.pop(name), dx, dy)
        cov = reink(cov, r0, p["pen"], p["kind"], dpi, rng)
        cov = texture(cov, p["kind"], dpi, rng)
        col = np.array(p["color"], np.float32)
        out *= 1 - cov[..., None] * (1 - col)
    out[out.min(2) > 0.985] = 1.0             # fond exactement blanc
    log(f"    page traitee en {time.time() - t0:.0f} s")
    return out


GRID_COLOR = (0.78, 0.84, 0.93)


def ink_palette(grid=False):
    """Palette explicite (uint8, N x 3) : blanc pur + chaque encre a 40 niveaux de couverture
    (+ quadrillage). Une quantification automatique ferait disparaitre les encres rares."""
    cols = [(1.0, 1.0, 1.0)]
    levels = np.linspace(0.028, 1.0, 36)
    for p in INKS.values():
        C = np.array(p["color"])
        cols += [tuple(1 - a * (1 - C)) for a in levels]
    if grid:
        G = np.array(GRID_COLOR)
        cols.append(tuple(G))
        for ink in ("bleu", "noir"):          # encre courante sur une ligne du quadrillage
            C = np.array(INKS[ink]["color"])
            cols += [tuple(G * (1 - a * (1 - C))) for a in levels[2::3]]
    assert len(cols) <= 256
    return np.round(255 * np.array(cols)).astype(np.uint8)


_LUT = {}


def palette_lut(grid):
    """Table 64x64x64 -> indice de la couleur de palette la plus proche (calcul exact)."""
    if grid not in _LUT:
        pal = ink_palette(grid).astype(np.float32)
        c = np.arange(64, dtype=np.float32) * 4 + 1.5
        cells = np.stack(np.meshgrid(c, c, c, indexing="ij"), -1).reshape(-1, 3)
        idx = np.empty(len(cells), np.uint8)
        for i in range(0, len(cells), 16384):
            d = ((cells[i:i + 16384, None, :] - pal[None]) ** 2).sum(-1)
            idx[i:i + 16384] = d.argmin(1)
        _LUT[grid] = idx.reshape(64, 64, 64)
    return _LUT[grid]


def to_png(arr, path, dpi, grid=False):
    """PNG a palette (encres connues) : ~3x plus leger que le RGB, aucune difference visible,
    fond EXACTEMENT blanc (indice 0 = 255,255,255)."""
    u8 = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    idx = palette_lut(grid)[u8[..., 0] >> 2, u8[..., 1] >> 2, u8[..., 2] >> 2]
    idx[(u8 >= 252).all(2)] = 0
    pal = ink_palette(grid)
    flat = pal.reshape(-1).tolist() + [255] * (768 - pal.size)
    im = Image.fromarray(idx, mode="P")
    im.putpalette(flat)
    im.save(path, dpi=(dpi, dpi), optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--pages", default=None, help="ex. 1 ou 1-2")
    ap.add_argument("--out", default=None, help="prefixe de sortie")
    args = ap.parse_args()
    log = lambda s: print(s, flush=True)
    rng = np.random.default_rng(args.seed)
    base = args.out or os.path.splitext(args.pdf)[0]
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["pdftoppm", "-r", str(args.dpi), "-png", "-aa", "yes", "-aaVector", "yes"]
        if args.pages:
            a, _, b = args.pages.partition("-")
            cmd += ["-f", a, "-l", b or a]
        subprocess.run(cmd + [args.pdf, os.path.join(tmp, "p")], check=True)
        pages = sorted(glob.glob(os.path.join(tmp, "p-*.png")))
        imp, quad = [], []
        for i, png in enumerate(pages, 1):
            log(f"  page {i}/{len(pages)}")
            out = process_page(png, args.dpi, rng, log)
            p1 = os.path.join(tmp, f"imp-{i}.png")
            to_png(out, p1, args.dpi)
            imp.append(p1)
            g = grid_layer(out.shape[:2], args.dpi, rng)
            gcol = np.array(GRID_COLOR, np.float32)
            outq = out * (1 - (1 - g)[..., None] * (1 - gcol))
            p2 = os.path.join(tmp, f"quad-{i}.png")
            to_png(outq, p2, args.dpi, grid=True)
            quad.append(p2)
            del out, outq, g
        a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
        layout = img2pdf.get_layout_fun(a4)
        with open(base + "_impression.pdf", "wb") as f:
            f.write(img2pdf.convert(imp, layout_fun=layout))
        with open(base + "_quadrille.pdf", "wb") as f:
            f.write(img2pdf.convert(quad, layout_fun=layout))
        if os.environ.get("REENCRAGE_KEEP_PNG"):
            import shutil
            for p in imp + quad:
                shutil.copy(p, os.path.dirname(os.path.abspath(base)))
    log(f"ecrit : {base}_impression.pdf et {base}_quadrille.pdf")


if __name__ == "__main__":
    sys.exit(main())
