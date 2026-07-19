#!/usr/bin/env python3
"""Vista previa: frontal, base solida (sin orificio) y corte con el tag sellado."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

YELLOW = np.array([0.95, 0.80, 0.16])
CREAM = np.array([0.98, 0.92, 0.80])
BLACK = np.array([0.10, 0.10, 0.10])


def load(path, color, outer_only=False):
    m = trimesh.load(path)
    if outer_only:
        comps = m.split(only_watertight=False)
        if len(comps) > 1:
            m = max(comps, key=lambda c: float(np.prod(c.extents)))  # cascara exterior
    t = m.vertices[m.faces]
    return t, np.tile(color, (len(t), 1))


# Para el render 3D usamos solo la cascara exterior del cuerpo (la cavidad
# interna del NFC no debe "verse" a traves de la piel en el render).
CUBE = [load("cuerpo_amarillo.stl", YELLOW, outer_only=True),
        load("cara_crema.stl", CREAM),
        load("ojos_negro.stl", BLACK)]


def draw(ax, parts, elev, azim, light_dir, center=(0, 0, 0), lim=31, xform=None):
    tris = np.concatenate([p[0] for p in parts], axis=0)
    base = np.concatenate([p[1] for p in parts], axis=0)
    if xform is not None:
        tris = xform(tris)
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    # backface culling: dibujar solo las caras que miran a la camara (sin z-buffer,
    # asi no se "transparentan" las caras traseras / huecos internos)
    front = (n @ view) > 0
    tris, base, n = tris[front], base[front], n[front]
    light = np.array(light_dir, float); light /= np.linalg.norm(light)
    shade = np.clip(n @ light, 0, 1) * 0.7 + 0.3
    colors = np.clip(base * shade[:, None], 0, 1)
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
ax1.set_title("Frontal (carita)", fontsize=11)

# Base real (-Y): rotamos la geometria para que la base mire hacia "arriba"
# de matplotlib (+Z) y la vemos de frente. (x,y,z) -> (x, z, -y)
base_up = lambda t: np.stack([t[..., 0], t[..., 2], -t[..., 1]], axis=-1)
ax2 = fig.add_subplot(1, 3, 2, projection="3d")
draw(ax2, CUBE, elev=88, azim=-90, light_dir=[0.2, 0.2, 0.95], xform=base_up)
ax2.set_title("Base SÓLIDA: sin orificio,\ntag imperceptible por fuera", fontsize=10)

# Panel 3: corte (plano z=0) mostrando el tag embebido y sellado
ax3 = fig.add_subplot(1, 3, 3)
body = trimesh.load("cuerpo_amarillo.stl")
sec = body.section(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1])
for poly in sec.discrete:
    ax3.fill(poly[:, 0], poly[:, 1], facecolor="#f2cd28", edgecolor="#b8941a",
             linewidth=1.2, zorder=1)
# Tag NFC embebido dentro de la cavidad interna (y = -26.8 .. -25.2)
tag_w, tag_t = 25.0, 1.0
tag_y = -28 + 1.2 + 0.2
ax3.add_patch(plt.Rectangle((-tag_w/2, tag_y), tag_w, tag_t,
              facecolor="#333", edgecolor="none", zorder=3, label="tag NFC (sellado)"))
ax3.annotate("piel sólida ~1.2 mm\n(nada de agujero)", xy=(0, -27.4), xytext=(15, -20),
             fontsize=8, ha="left",
             arrowprops=dict(arrowstyle="->", color="#555"))
ax3.annotate("plástico sólido\nsella el tag", xy=(0, -24.6), xytext=(-30, -14),
             fontsize=8, ha="left",
             arrowprops=dict(arrowstyle="->", color="#555"))
ax3.set_aspect("equal"); ax3.axis("off")
ax3.set_xlim(-33, 33); ax3.set_ylim(-33, 33)
ax3.legend(loc="upper right", fontsize=9, frameon=False)
ax3.set_title("Corte: tag NFC embebido y sellado\n(no se ve, no se puede sacar)", fontsize=10)

plt.tight_layout()
plt.savefig("preview.png", dpi=115, bbox_inches="tight", facecolor="white")
print("Guardado preview.png")
