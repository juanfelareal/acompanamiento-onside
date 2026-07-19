#!/usr/bin/env python3
"""Renderiza vistas previas del STL con matplotlib (sombreado simple)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

mesh = trimesh.load("cubo_personaje.stl")

# Usar malla completa para no perder los hoyuelos de ojos/nariz
m = mesh

V = m.vertices
F = m.faces
tris = V[F]  # (n,3,3)

# Sombreado plano: normal . luz
n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)

BASE = np.array([1.0, 0.82, 0.15])  # amarillo del personaje

FRONT_Z = V[:, 2].max()  # cara frontal

def render(ax, elev, azim, light_dir, depth_shade=False):
    light = np.array(light_dir, float)
    light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.75 + 0.25
    colors = np.clip(BASE[None, :] * shade[:, None], 0, 1)
    if depth_shade:
        # Oscurecer SOLO los grabados de la cara frontal (caras que miran al
        # frente y estan un poco por debajo de z=FRONT_Z). Asi los ojos, la
        # nariz y el contorno se ven, sin oscurecer el borde redondeado.
        zf = tris.mean(axis=1)[:, 2]
        front_facing = n[:, 2] > 0.5
        f = np.clip((zf - (FRONT_Z - 1.3)) / 1.3, 0.45, 1.0)
        f = np.where(front_facing, f, 1.0)
        colors = colors * f[:, None]
    # ordenar por profundidad segun la camara (painter's algorithm aproximado)
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    depth = tris.mean(axis=1) @ view
    order = np.argsort(depth)
    coll = Poly3DCollection(tris[order], facecolors=colors[order],
                            edgecolors="none", linewidths=0)
    ax.add_collection3d(coll)
    lim = 33
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()

fig = plt.figure(figsize=(12, 5), facecolor="white")
# El frente (cara) mira hacia +Z. matplotlib toma +Z como "arriba":
# para ver la cara de frente miramos casi por el eje +Z (elev alto).
ax1 = fig.add_subplot(1, 2, 1, projection="3d")
render(ax1, elev=88, azim=-90, light_dir=[0.3, 0.3, 0.9], depth_shade=True)
ax1.set_title("Vista frontal (la carita, plana)", fontsize=12)

ax2 = fig.add_subplot(1, 2, 2, projection="3d")
render(ax2, elev=32, azim=-60, light_dir=[0.4, -0.5, 0.75])
ax2.set_title("Vista 3/4", fontsize=12)

plt.tight_layout()
plt.savefig("preview.png", dpi=110, bbox_inches="tight", facecolor="white")
print("Guardado preview.png")
