#!/usr/bin/env python3
"""Render ensamblado (cuerpo texturizado + cara + ojos) de las dos texturas
finales, vista frontal 3/4, para ver el personaje terminado."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import trimesh

TEX = [("ranurado", "Ranurado / estrias"), ("dimples", "Dimples / golf")]
COLS = {"body": (0.95, 0.81, 0.16), "face": (0.98, 0.92, 0.80),
        "eye": (0.11, 0.11, 0.11)}

view = np.array([0.42, 0.32, 1.0]); view /= np.linalg.norm(view)
up = np.array([0.0, 1.0, 0.0])
right = np.cross(up, view); right /= np.linalg.norm(right)
camup = np.cross(view, right)
light = np.array([0.35, 0.7, 1.0]); light /= np.linalg.norm(light)

fig = plt.figure(figsize=(12, 6.6), facecolor="#111")
for i, (key, title) in enumerate(TEX):
    parts = [(f"cuerpo_{key}_final.stl", COLS["body"]),
             ("cara_crema.stl", COLS["face"]),
             ("ojos_negro.stl", COLS["eye"])]
    allP, allC, allD = [], [], []
    for path, col in parts:
        m = trimesh.load(path)
        if len(m.faces) > 60000:
            try:
                m = m.simplify_quadric_decimation(face_count=60000)
            except TypeError:
                m = m.simplify_quadric_decimation(60000)
        V, F = m.vertices, m.faces
        tri = V[F]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1
        n = n / ln[:, None]
        vis = (n @ view) > -0.05
        tri, n = tri[vis], n[vis]
        shade = np.clip(np.abs(n @ light), 0, 1) * 0.78 + 0.22
        c = np.clip(np.array(col)[None, :] * shade[:, None], 0, 1)
        P = np.stack([tri @ right, tri @ camup], axis=-1)
        allP.append(P); allC.append(c); allD.append(tri.mean(1) @ view)
    P = np.concatenate(allP); C = np.concatenate(allC); Dd = np.concatenate(allD)
    order = np.argsort(Dd)
    # centrar
    ctr = P.reshape(-1, 2).mean(0)
    P = P - ctr

    ax = fig.add_subplot(1, 2, i + 1)
    ax.set_facecolor("#111")
    ax.add_collection(PolyCollection(P[order], facecolors=C[order],
                                     edgecolors="none"))
    r = np.abs(P).max() * 1.03
    ax.set_xlim(-r, r); ax.set_ylim(-r, r)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, color="w", fontsize=16, pad=8)

fig.suptitle("Bloki terminado — texturas finales (cuerpo + cara + ojos)",
             color="w", fontsize=17, y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("texturas_final_ensamblado.png", dpi=125, facecolor="#111",
            bbox_inches="tight")
print("Guardado texturas_final_ensamblado.png")
