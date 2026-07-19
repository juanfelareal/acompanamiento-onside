#!/usr/bin/env python3
"""Vista previa a color: frontal, esquina (llavero) y base (NFC)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

PARTS = [
    ("cuerpo_amarillo.stl", np.array([0.95, 0.80, 0.16])),
    ("cara_crema.stl",      np.array([0.98, 0.92, 0.80])),
    ("ojos_negro.stl",      np.array([0.10, 0.10, 0.10])),
]

tris_list, base_list = [], []
for path, color in PARTS:
    m = trimesh.load(path)
    t = m.vertices[m.faces]
    tris_list.append(t)
    base_list.append(np.tile(color, (len(t), 1)))

tris = np.concatenate(tris_list, axis=0)
base = np.concatenate(base_list, axis=0)

n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)


def render(ax, elev, azim, light_dir, center=(0, 0, 0), lim=31):
    light = np.array(light_dir, float)
    light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    colors = np.clip(base * shade[:, None], 0, 1)
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    order = np.argsort(tris.mean(axis=1) @ view)
    coll = Poly3DCollection(tris[order], facecolors=colors[order],
                            edgecolors="none", linewidths=0)
    ax.add_collection3d(coll)
    cx, cy, cz = center
    ax.set_xlim(cx - lim, cx + lim); ax.set_ylim(cy - lim, cy + lim)
    ax.set_zlim(cz - lim, cz + lim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


fig = plt.figure(figsize=(15, 5), facecolor="white")

ax1 = fig.add_subplot(1, 3, 1, projection="3d")
render(ax1, elev=88, azim=-90, light_dir=[0.25, 0.2, 0.95])
ax1.set_title("Frontal (carita)", fontsize=12)

ax2 = fig.add_subplot(1, 3, 2, projection="3d")
render(ax2, elev=22, azim=-52, light_dir=[0.5, 0.5, 0.55],
       center=(19, 17, 12), lim=15)
ax2.set_title("Esquina sup. (orificio cuerdita, primer plano)", fontsize=11)

ax3 = fig.add_subplot(1, 3, 3, projection="3d")
render(ax3, elev=-86, azim=-90, light_dir=[0.15, -0.95, 0.1])
ax3.set_title("Base (alojamiento NFC Ø26)", fontsize=12)

plt.tight_layout()
plt.savefig("preview.png", dpi=115, bbox_inches="tight", facecolor="white")
print("Guardado preview.png")
