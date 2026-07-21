#!/usr/bin/env python3
"""Ilustracion vectorial FLAT de Bloki (vista frontal), para diseno de la app.
Toma las medidas reales del modelo (generar_cubo) y dibuja cuerpo + cara + ojos +
nariz como formas planas. Exporta PNG transparente (alta res) y SVG vectorial."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse
import generar_cubo as G

# medidas reales (mm), vista frontal, origen al centro del cuerpo
bw, bh = G.W, G.H - G.BASE_CUT        # ancho, alto util del cuerpo
bcy = G.BASE_CUT / 2                  # centro vertical (por el recorte de base)
Rr = G.R
fw, fh, fr = G.FACE_W, G.FACE_H, G.FACE_R
fcy = G.FACE_CY
ex = G.EYE_DX
ey = G.FACE_CY + G.EYE_DY
er = G.EYE_R
ny = G.FACE_CY + G.NOSE_DY
nr = G.NOSE_R

YEL, CREAM, CREAM_D, BLK = "#F4CE2A", "#FAEFD6", "#EAD9B0", "#161616"

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect("equal")
ax.axis("off")


def rrect(cx, cy, w, h, r, fc, z=1, alpha=1):
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2 + r, cy - h / 2 + r), w - 2 * r, h - 2 * r,
        boxstyle=f"round,pad={r},rounding_size=0", fc=fc, ec="none",
        zorder=z, alpha=alpha, mutation_aspect=1))


rrect(0, bcy - 1.2, bw, bh, Rr, "#000000", z=0, alpha=0.13)   # sombra suave
rrect(0, bcy, bw, bh, Rr, YEL, z=1)                           # cuerpo
ax.add_patch(Ellipse((0, bcy + bh * 0.24), bw * 0.62, bh * 0.28,
             fc="#FFFFFF", alpha=0.10, zorder=2))             # highlight superior
rrect(0, fcy, fw + 0.9, fh + 0.9, fr + 0.4, CREAM_D, z=3)     # marco/reveal (recogido)
rrect(0, fcy, fw, fh, fr, CREAM, z=4)                         # panel de la cara
for sx in (-ex, ex):                                          # ojos + brillito
    ax.add_patch(Circle((sx, ey), er, fc=BLK, zorder=5))
    ax.add_patch(Circle((sx - er * 0.32, ey + er * 0.34), er * 0.28,
                 fc="#FFFFFF", alpha=0.9, zorder=6))
ax.add_patch(Circle((0, ny), nr, fc=CREAM_D, ec="#D9C38C", lw=0.6, zorder=5))  # nariz

m = 6
ax.set_xlim(-bw / 2 - m, bw / 2 + m)
ax.set_ylim(bcy - bh / 2 - m - 2, bcy + bh / 2 + m)
plt.savefig("bloki_flat.png", dpi=300, bbox_inches="tight",
            transparent=True, pad_inches=0.06)
plt.savefig("bloki_flat.svg", bbox_inches="tight",
            transparent=True, pad_inches=0.06)
print("Guardado bloki_flat.png (PNG transparente) + bloki_flat.svg (vector)")
