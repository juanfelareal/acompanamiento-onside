#!/usr/bin/env python3
"""Vista previa: frontal, base abierta (cavidad NFC) y base cerrada (con tapa)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

YELLOW = np.array([0.95, 0.80, 0.16])
CREAM = np.array([0.98, 0.92, 0.80])
BLACK = np.array([0.10, 0.10, 0.10])


def load(path, color):
    m = trimesh.load(path)
    t = m.vertices[m.faces]
    return t, np.tile(color, (len(t), 1))


CUBE = [load("cuerpo_amarillo.stl", YELLOW),
        load("cara_crema.stl", CREAM),
        load("ojos_negro.stl", BLACK)]
CAP = load("tapa_nfc_amarilla.stl", YELLOW)


def draw(ax, parts, elev, azim, light_dir, center=(0, 0, 0), lim=31):
    tris = np.concatenate([p[0] for p in parts], axis=0)
    base = np.concatenate([p[1] for p in parts], axis=0)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    light = np.array(light_dir, float); light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    colors = np.clip(base * shade[:, None], 0, 1)
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    order = np.argsort(tris.mean(axis=1) @ view)
    ax.add_collection3d(Poly3DCollection(tris[order], facecolors=colors[order],
                                         edgecolors="none", linewidths=0))
    cx, cy, cz = center
    ax.set_xlim(cx - lim, cx + lim); ax.set_ylim(cy - lim, cy + lim)
    ax.set_zlim(cz - lim, cz + lim)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off()


fig = plt.figure(figsize=(15, 5), facecolor="white")

ax1 = fig.add_subplot(1, 3, 1, projection="3d")
draw(ax1, CUBE, elev=88, azim=-90, light_dir=[0.25, 0.2, 0.95])
ax1.set_title("Frontal (carita) — el orificio del\nllavero es el puntico arriba a la derecha", fontsize=10)

ax2 = fig.add_subplot(1, 3, 2, projection="3d")
draw(ax2, CUBE, elev=-86, azim=-90, light_dir=[0.15, -0.95, 0.1])
ax2.set_title("Base ABIERTA: cavidad interna\n(aquí va el tag NFC)", fontsize=10)

# Panel 3: corte transversal (plano z=0) mostrando el tag oculto y la tapa
ax3 = fig.add_subplot(1, 3, 3)
body = trimesh.load("cuerpo_amarillo.stl")
sec = body.section(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1])
for poly in sec.discrete:
    ax3.fill(poly[:, 0], poly[:, 1], facecolor="#f2cd28", edgecolor="#b8941a",
             linewidth=1.2, zorder=1)
# Tag NFC (Ø25, ~1 mm) apoyado en el fondo de la cavidad
tag_w, tag_t = 25.0, 1.0
tag_y = -28 + 1.8 + 0.2   # sobre la zona de la tapa, dentro de la cavidad
ax3.add_patch(plt.Rectangle((-tag_w/2, tag_y), tag_w, tag_t,
              facecolor="#333", edgecolor="none", zorder=3, label="tag NFC"))
# Tapa (Ø25.4 x 1.8 mm) cerrando al ras de la base
ax3.add_patch(plt.Rectangle((-25.4/2, -28), 25.4, 1.8,
              facecolor="#f2cd28", edgecolor="#8a6d10", linewidth=1.0,
              hatch="//", zorder=4, label="tapa"))
ax3.set_aspect("equal"); ax3.axis("off")
ax3.set_xlim(-33, 33); ax3.set_ylim(-33, 33)
ax3.legend(loc="upper right", fontsize=9, frameon=False)
ax3.set_title("Corte: tag NFC escondido\ndentro, tapa cerrando al ras", fontsize=10)

plt.tight_layout()
plt.savefig("preview.png", dpi=115, bbox_inches="tight", facecolor="white")
print("Guardado preview.png")
