#!/usr/bin/env python3
"""Render del cuerpo crochet desde 2 angulos (frente 3/4 y lateral/atras) para
apreciar el tejido."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import trimesh

VIEWS = [("Frente 3/4", np.array([0.45, 0.32, 1.0])),
         ("Lateral / espalda", np.array([1.0, 0.28, -0.35]))]
PARTS = [("cuerpo_crochet.stl", (0.96, 0.82, 0.20)),
         ("cara_crema.stl", (0.98, 0.92, 0.80)),
         ("ojos_negro.stl", (0.11, 0.11, 0.11))]
light = np.array([0.4, 0.7, 0.9]); light /= np.linalg.norm(light)

meshes = []
for path, col in PARTS:
    m = trimesh.load(path)
    if len(m.faces) > 120000:
        try:
            m = m.simplify_quadric_decimation(face_count=120000)
        except TypeError:
            m = m.simplify_quadric_decimation(120000)
    meshes.append((m, np.array(col)))

fig = plt.figure(figsize=(13, 6.6), facecolor="#111")
for i, (title, view) in enumerate(VIEWS):
    view = view / np.linalg.norm(view)
    up = np.array([0.0, 1.0, 0.0])
    right = np.cross(up, view); right /= np.linalg.norm(right)
    camup = np.cross(view, right)
    allP, allC, allD = [], [], []
    for m, col in meshes:
        V, F = m.vertices, m.faces
        tri = V[F]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1
        n = n / ln[:, None]
        vis = (n @ view) > -0.05
        tri, n = tri[vis], n[vis]
        shade = np.clip(np.abs(n @ light), 0, 1) * 0.8 + 0.2
        c = np.clip(col[None, :] * shade[:, None], 0, 1)
        allP.append(np.stack([tri @ right, tri @ camup], axis=-1))
        allC.append(c); allD.append(tri.mean(1) @ view)
    P = np.concatenate(allP); C = np.concatenate(allC); Dd = np.concatenate(allD)
    order = np.argsort(Dd)
    P = P - P.reshape(-1, 2).mean(0)
    ax = fig.add_subplot(1, 2, i + 1); ax.set_facecolor("#111")
    ax.add_collection(PolyCollection(P[order], facecolors=C[order], edgecolors="none"))
    r = np.abs(P).max() * 1.03
    ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, color="w", fontsize=15, pad=8)

fig.suptitle("Bloki CROCHET — bloque con esquinas curvas + textura tejido",
             color="w", fontsize=16, y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("crochet_render.png", dpi=130, facecolor="#111", bbox_inches="tight")
print("Guardado crochet_render.png")
