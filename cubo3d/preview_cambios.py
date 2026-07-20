#!/usr/bin/env python3
"""Vista de los cambios: ojos mas separados, nariz +15%, cara abombada."""
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
    return m.vertices[m.faces], np.tile(color, (len(m.faces), 1))


PARTS = [load("cuerpo_amarillo.stl", YELLOW, outer_only=True),
         load("cara_crema.stl", CREAM),
         load("ojos_negro.stl", BLACK)]
T = np.concatenate([p[0] for p in PARTS])
B = np.concatenate([p[1] for p in PARTS])


def draw(ax, elev, azim, light_dir, xform=None, title="", lim=30):
    tris = xform(T) if xform else T
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])
    fr = (n @ view) > 0
    tris, base, n = tris[fr], B[fr], n[fr]
    light = np.array(light_dir, float); light /= np.linalg.norm(light)
    sh = np.clip(n @ light, 0, 1) * 0.72 + 0.28
    col = np.clip(base * sh[:, None], 0, 1)
    o = np.argsort(tris.mean(1) @ view)
    ax.add_collection3d(Poly3DCollection(tris[o], facecolors=col[o], edgecolors="none"))
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    ax.set_title(title, fontsize=11)


fig = plt.figure(figsize=(15, 5), facecolor="white")

ax1 = fig.add_subplot(1, 3, 1, projection="3d")
draw(ax1, 88, -90, [0.25, 0.2, 0.95], title="Frontal (ojos + separados, nariz +15%)")

ax2 = fig.add_subplot(1, 3, 2, projection="3d")
draw(ax2, 50, -74, [0.35, 0.5, 0.8], title="3/4 (se ve la carita abombada)")

# Corte horizontal a la altura de los ojos: muestra la curva del panel
ax3 = fig.add_subplot(1, 3, 3)
plane = dict(plane_origin=[0, 2.0, 0], plane_normal=[0, 1, 0])
b = trimesh.load("cuerpo_amarillo.stl").section(**plane)
for poly in b.discrete:
    ax3.fill(poly[:, 0], poly[:, 2], facecolor="#f7d84a", edgecolor="#b8941a",
             lw=1.2, zorder=1)
c = trimesh.load("cara_crema.stl").section(**plane)
for poly in c.discrete:
    ax3.fill(poly[:, 0], poly[:, 2], facecolor="#f6ecd0", edgecolor="#c9a24a",
             lw=1.2, zorder=2)
ax3.annotate("la cara se curva\n(centro más saliente)", xy=(0, 24.5), xytext=(-26, 27),
             fontsize=9, ha="left", arrowprops=dict(arrowstyle="->", color="#a06"))
ax3.plot([-19, 19], [23, 23], "--", color="#888", lw=1)
ax3.text(-19, 22.2, "nivel del cuerpo (plano)", fontsize=8, color="#666")
ax3.set_aspect("equal"); ax3.axis("off")
ax3.set_xlim(-24, 24); ax3.set_ylim(18, 29)
ax3.set_title("Corte por los ojos: la cara es convexa", fontsize=11)

plt.tight_layout()
plt.savefig("preview_cambios.png", dpi=118, bbox_inches="tight", facecolor="white")
print("Guardado preview_cambios.png")
