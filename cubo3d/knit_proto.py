#!/usr/bin/env python3
"""Prototipo 2D de la textura CROCHET/TEJIDO (punto stockinette): filas de 'V'
que se entrelazan. Rapido para afinar el patron antes de aplicarlo al cuerpo."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


W_YARN = 0.33      # grosor del hilo (gordo = lana)


def knit_h(col, row):
    """Punto stockinette: columnas verticales de 'V'. Hilo gordo redondeado; el
    punto (fr=0) de cada V queda bajo la abertura de la V de arriba -> columnas
    continuas de lana."""
    fc = (col % 1.0) - 0.5
    fr = row % 1.0
    d = np.minimum(np.abs(fc - 0.5 * fr), np.abs(fc + 0.5 * fr))   # dist a las 2 piernas
    yarn = np.clip(1.0 - (d / W_YARN) ** 2, 0.0, 1.0) ** 0.5       # tubo redondo gordo
    return yarn


NC, NR = 9, 11                          # celdas chunky (lana gruesa)
px = 900
xs = np.linspace(0, NC, px)
ys = np.linspace(0, NR, int(px * NR / NC))
C, Rr = np.meshgrid(xs, ys)
H = knit_h(C, Rr)

# hillshade con relieve marcado + oclusion en los surcos (mas legible)
zscale = 3.5
gy, gx = np.gradient(H * zscale)
nz = 1.0 / np.sqrt(gx**2 + gy**2 + 1)
nx = -gx * nz; ny = -gy * nz
L = np.array([0.35, 0.55, 0.75]); L /= np.linalg.norm(L)
diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
ao = 0.45 + 0.55 * H                      # surcos mas oscuros
shade = diff * ao
yellow = np.array([0.96, 0.82, 0.20])
img = np.clip(shade[..., None] * yellow, 0, 1)

plt.figure(figsize=(7, 7), facecolor="#111")
plt.imshow(img, origin="lower")
plt.axis("off")
plt.title("Prototipo textura crochet / tejido", color="w")
plt.tight_layout()
plt.savefig("crochet_proto.png", dpi=110, facecolor="#111", bbox_inches="tight")
print("Guardado crochet_proto.png")
