#!/usr/bin/env python3
"""Vista del diseno en 2 piezas: cuerpo (amarillo) + carita que encaja a presion."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

YELLOW = np.array([0.96, 0.80, 0.14])
CREAM = np.array([0.98, 0.93, 0.82])
BLACK = np.array([0.10, 0.10, 0.10])


def load(path, color, outer_only=False, shift=(0, 0, 0)):
    m = trimesh.load(path)
    if outer_only:
        c = m.split(only_watertight=False)
        if len(c) > 1:
            m = max(c, key=lambda x: float(np.prod(x.extents)))
    V = m.vertices + np.array(shift)
    return V[m.faces], np.tile(color, (len(m.faces), 1))


def draw(ax, parts, elev, azim, light_dir, title):
    tris = np.concatenate([p[0] for p in parts])
    base = np.concatenate([p[1] for p in parts])
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])
    fr = (n @ view) > 0
    tris, base, n = tris[fr], base[fr], n[fr]
    light = np.array(light_dir, float); light /= np.linalg.norm(light)
    sh = np.clip(n @ light, 0, 1)*0.7 + 0.3
    col = np.clip(base * sh[:, None], 0, 1)
    o = np.argsort(tris.mean(1) @ view)
    ax.add_collection3d(Poly3DCollection(tris[o], facecolors=col[o], edgecolors="none"))
    lim = 30
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    ax.set_title(title, fontsize=12)


fig = plt.figure(figsize=(13, 6), facecolor="white")

# Ensamblada
asm = [load("cuerpo_amarillo.stl", YELLOW, outer_only=True),
       load("cara_crema.stl", CREAM), load("ojos_negro.stl", BLACK)]
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
draw(ax1, asm, 50, -74, [0.35, 0.5, 0.8], "Ensamblada (carita encajada)")

# Explotada: carita y ojos desplazados hacia +Z (afuera). Los ojos mas lejos.
exp = [load("cuerpo_amarillo.stl", YELLOW, outer_only=True),
       load("cara_crema.stl", CREAM, shift=(0, 0, 12)),
       load("ojos_negro.stl", BLACK, shift=(0, 0, 24))]
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
draw(ax2, exp, 50, -74, [0.35, 0.5, 0.8],
     "Separada: cuerpo + carita + ojos (cada uno 1 color)")

plt.tight_layout()
plt.savefig("preview_2piezas.png", dpi=120, bbox_inches="tight", facecolor="white")
print("Guardado preview_2piezas.png")
