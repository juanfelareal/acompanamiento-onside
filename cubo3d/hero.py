#!/usr/bin/env python3
"""Render 'hero' del Bloki terminado (3/4) para la guia."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

YELLOW = np.array([0.96, 0.80, 0.14])
CREAM = np.array([0.98, 0.93, 0.82])
BLACK = np.array([0.10, 0.10, 0.10])


def load(path, color, outer_only=False):
    m = trimesh.load(path)
    if outer_only:
        c = m.split(only_watertight=False)
        if len(c) > 1:
            m = max(c, key=lambda x: float(np.prod(x.extents)))
    t = m.vertices[m.faces]
    return t, np.tile(color, (len(t), 1))


parts = [load("cuerpo_amarillo.stl", YELLOW, outer_only=True),
         load("cara_crema.stl", CREAM),
         load("ojos_negro.stl", BLACK)]
tris = np.concatenate([p[0] for p in parts])
base = np.concatenate([p[1] for p in parts])
n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9

fig = plt.figure(figsize=(6, 6), facecolor="white")
ax = fig.add_subplot(111, projection="3d")
elev, azim = 52, -74
e, a = np.deg2rad(elev), np.deg2rad(azim)
view = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])
front = (n @ view) > 0
tris, base, nn = tris[front], base[front], n[front]
light = np.array([0.35, 0.5, 0.8]); light /= np.linalg.norm(light)
shade = np.clip(nn @ light, 0, 1) * 0.7 + 0.3
colors = np.clip(base * shade[:, None], 0, 1)
order = np.argsort(tris.mean(1) @ view)
ax.add_collection3d(Poly3DCollection(tris[order], facecolors=colors[order],
                                     edgecolors="none"))
lim = 30
ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
plt.tight_layout()
plt.savefig("hero.png", dpi=130, bbox_inches="tight", facecolor="white")
print("Guardado hero.png")
