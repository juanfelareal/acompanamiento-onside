#!/usr/bin/env python3
"""Muestra las dos LAMINAS (cara crema + ojos negra): separadas y ensambladas."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import trimesh

face = trimesh.load("cara_crema.stl"); eyes = trimesh.load("ojos_negro.stl")
CF = np.array([0.98, 0.92, 0.80]); CE = np.array([0.10, 0.10, 0.11])
light = np.array([0.4, 0.6, 0.85]); light /= np.linalg.norm(light)
view = np.array([0.5, 0.35, 1.0]); view /= np.linalg.norm(view)
up = np.array([0, 1.0, 0]); right = np.cross(up, view); right /= np.linalg.norm(right)
camup = np.cross(view, right)


def polys(m, col, dz):
    V = m.vertices.copy(); V[:, 2] += dz
    tri = V[m.faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1); ln[ln == 0] = 1; n /= ln[:, None]
    vis = (n @ view) > -0.05; tri, n = tri[vis], n[vis]
    sh = np.clip(np.abs(n @ light), 0, 1) * 0.8 + 0.2
    c = np.clip(col[None] * sh[:, None], 0, 1)
    P = np.stack([tri @ right, tri @ camup], -1)
    return P, c, tri.mean(1) @ view


SCENES = [("Separadas (asi se apilan)", 9.0), ("Ensambladas", 0.0)]
fig = plt.figure(figsize=(13, 6.6), facecolor="#111")
for i, (title, sep) in enumerate(SCENES):
    Pf, Cf, Df = polys(face, CF, sep)
    Pe, Ce, De = polys(eyes, CE, 0.0)
    P = np.concatenate([Pf, Pe]); C = np.concatenate([Cf, Ce]); Dd = np.concatenate([Df, De])
    o = np.argsort(Dd); P = P - P.reshape(-1, 2).mean(0)
    ax = fig.add_subplot(1, 2, i + 1); ax.set_facecolor("#111")
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors="none"))
    r = np.abs(P).max() * 1.05; ax.set_xlim(-r, r); ax.set_ylim(-r, r)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, color="w", fontsize=15, pad=8)
fig.suptitle("Bloki — laminas: cara (crema) + ojos (negra) que asoman por los huecos",
             color="w", fontsize=15, y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("laminae_render.png", dpi=130, facecolor="#111", bbox_inches="tight")
print("ok")
