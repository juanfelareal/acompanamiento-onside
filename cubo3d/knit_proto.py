#!/usr/bin/env python3
"""Prototipo 2D de la textura CROCHET/TEJIDO (punto stockinette): filas de 'V'
que se entrelazan. Rapido para afinar el patron antes de aplicarlo al cuerpo."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def knit_h(col, row):
    """Altura del hilo (punto stockinette): cada celda es una 'V' de dos piernas
    de hilo redondeado que suben hacia las esquinas superiores y encajan con la
    fila de arriba."""
    ri = np.floor(row)
    col2 = col + 0.5 * ri               # desfase de medio punto por fila (ladrillo)
    fc = (col2 % 1.0) - 0.5
    fr = row % 1.0
    spread = 0.5                        # las piernas llegan a las esquinas
    d1 = np.abs(fc - spread * fr)       # pierna /
    d2 = np.abs(fc + spread * fr)       # pierna \
    d = np.minimum(d1, d2)
    w = 0.24                            # grosor del hilo
    yarn = np.clip(1.0 - (d / w) ** 2, 0.0, 1.0) ** 0.5   # media-cana redondeada
    return yarn


NC, NR = 11, 15                         # columnas y filas (celda mas ancha que alta)
px = 900
xs = np.linspace(0, NC, px)
ys = np.linspace(0, NR, int(px * NR / NC))
C, Rr = np.meshgrid(xs, ys)
H = knit_h(C, Rr)

# hillshade simple
gy, gx = np.gradient(H)
nz = 1.0 / np.sqrt(gx**2 + gy**2 + 1)
nx = -gx * nz; ny = -gy * nz
L = np.array([0.4, 0.6, 0.7]); L /= np.linalg.norm(L)
shade = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1) * 0.8 + 0.2
yellow = np.array([0.96, 0.82, 0.20])
img = np.clip(shade[..., None] * yellow, 0, 1)

plt.figure(figsize=(7, 7), facecolor="#111")
plt.imshow(img, origin="lower")
plt.axis("off")
plt.title("Prototipo textura crochet / tejido", color="w")
plt.tight_layout()
plt.savefig("crochet_proto.png", dpi=110, facecolor="#111", bbox_inches="tight")
print("Guardado crochet_proto.png")
