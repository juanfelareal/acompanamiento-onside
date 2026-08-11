#!/usr/bin/env python3
"""Render rapido (matplotlib, painter's algorithm) de las 4 texturas del cuerpo,
en un montaje 2x2 para comparar el look de un vistazo."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

NAMES = [("facetado", "Facetado / low-poly"),
         ("voxel", "Voxel / pixeles"),
         ("ranurado", "Ranurado / estrias"),
         ("dimples", "Dimples / golf")]

# vista 3/4 frontal: la cara mira +Z, arriba +Y. Camara desde (+X,+Y,+Z).
view = np.array([0.7, 0.55, 1.0]); view = view / np.linalg.norm(view)
up = np.array([0.0, 1.0, 0.0])
right = np.cross(up, view); right /= np.linalg.norm(right)
camup = np.cross(view, right)
light = np.array([0.5, 0.8, 0.9]); light /= np.linalg.norm(light)

fig = plt.figure(figsize=(11, 11), facecolor="#111")
for i, (key, title) in enumerate(NAMES):
    m = trimesh.load(f"cuerpo_{key}.stl")
    if len(m.faces) > 45000:
        try:
            m = m.simplify_quadric_decimation(face_count=45000)
        except TypeError:
            m = m.simplify_quadric_decimation(45000)
    m.vertices -= m.centroid
    V, F = m.vertices, m.faces
    tri = V[F]                                   # (n,3,3)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1
    n = n / ln[:, None]
    facing = n @ view
    vis = facing > -0.05                         # backface cull
    tri, n = tri[vis], n[vis]
    depth = (tri.mean(1) @ view)
    order = np.argsort(depth)
    shade = np.clip(np.abs(n @ light), 0, 1) * 0.8 + 0.2
    base = np.array([0.95, 0.81, 0.16])          # amarillo
    cols = (base[None, :] * shade[:, None])[order]
    cols = np.clip(cols, 0, 1)
    # proyeccion a la camara
    P = np.stack([tri @ right, tri @ camup], axis=-1)[order]

    ax = fig.add_subplot(2, 2, i + 1)
    ax.set_facecolor("#111")
    pc = Poly3DCollection.__mro__  # noqa (keep import used)
    from matplotlib.collections import PolyCollection
    poly = PolyCollection(P, facecolors=cols, edgecolors="none", linewidths=0)
    ax.add_collection(poly)
    r = np.abs(P).max() * 1.05
    ax.set_xlim(-r, r); ax.set_ylim(-r, r)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, color="w", fontsize=15, pad=6)

fig.suptitle("Bloki — 4 texturas para elegir (mismo modelo, base corregida)",
             color="w", fontsize=17, y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("texturas_comparativa.png", dpi=120, facecolor="#111",
            bbox_inches="tight")
print("Guardado texturas_comparativa.png")
