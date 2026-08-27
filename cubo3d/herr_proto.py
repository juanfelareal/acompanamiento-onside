#!/usr/bin/env python3
"""Prototipo 2D de textura CHEVRON / HERRINGBONE (espiga) para igualar la abeja.
Renderiza 4 variantes (fino/grueso, chevron/herringbone) para elegir."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def herr(col, row, bw, w):
    """col,row en unidades de punto. bw = ancho de banda (1 = chevron continuo;
    >1 = herringbone con varias diagonales por banda). w = grosor del hilo."""
    ci = np.floor(col / bw)
    s = 1 - 2 * (ci.astype(int) % 2)          # pendiente alterna +/-1
    cl = col - ci * bw
    u = row - s * cl                           # coordenada diagonal
    f = (u % 1.0)
    d = np.abs(f - 0.5)                         # dist al centro del hilo
    yarn = np.clip(1.0 - (d / w) ** 2, 0.0, 1.0) ** 0.5
    return yarn


def hillshade(H):
    gy, gx = np.gradient(H * 3.2)
    nz = 1.0 / np.sqrt(gx**2 + gy**2 + 1)
    nx, ny = -gx * nz, -gy * nz
    L = np.array([0.32, 0.5, 0.8]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    ao = 0.42 + 0.58 * H
    return np.clip((diff * ao)[..., None] * np.array([0.96, 0.82, 0.2]), 0, 1)


VARIANTS = [("chevron fino", 1.0, 0.34, 12),
            ("chevron grueso", 1.0, 0.34, 8),
            ("herringbone bw2 fino", 2.0, 0.32, 12),
            ("herringbone bw3", 3.0, 0.30, 10)]
fig = plt.figure(figsize=(11, 11), facecolor="#111")
for i, (title, bw, w, NC) in enumerate(VARIANTS):
    NR = int(NC * 1.25)
    px = 700
    xs = np.linspace(0, NC, px); ys = np.linspace(0, NR, int(px * NR / NC))
    C, Rr = np.meshgrid(xs, ys)
    H = herr(C, Rr, bw, w)
    ax = fig.add_subplot(2, 2, i + 1)
    ax.imshow(hillshade(H), origin="lower"); ax.axis("off")
    ax.set_title(title, color="w", fontsize=13)
fig.suptitle("Chevron / Herringbone — variantes", color="w", fontsize=15)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig("herr_proto.png", dpi=110, facecolor="#111", bbox_inches="tight")
print("ok")
