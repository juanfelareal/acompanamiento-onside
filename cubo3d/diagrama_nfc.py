#!/usr/bin/env python3
"""Diagrama: impresion con la carita ARRIBA + NFC embebido detras de la cara.
Todas las alturas/posiciones se derivan del modelo generado (cualquier escala).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

body = trimesh.load("cuerpo_amarillo.stl")

PLATE_Z = float(body.bounds[0][2])        # cara trasera (va sobre la cama)
TOP_Z = float(body.bounds[1][2])          # frente del cuerpo (donde esta el rebaje)
void = [c for c in body.split(only_watertight=False) if c.volume < 0][0]
vy0, vz0 = float(void.bounds[0][1]), float(void.bounds[0][2])
vy1, vz1 = float(void.bounds[1][1]), float(void.bounds[1][2])
PAUSE_Z = vz1 - 0.2
PANEL_Z = vz1 + 1.2                        # fondo del rebaje (techo del NFC + pared)

def ph(z):
    return z - PLATE_Z

ymin, ymax = float(body.bounds[0][1]), float(body.bounds[1][1])

fig, ax = plt.subplots(figsize=(7.5, 9))

# Corte vertical (plano x=0): perfil Y-Z (Z hacia arriba = direccion de impresion)
# Solo el CUERPO (1 color). El rebaje aparece como una muesca en el frente.
plane = dict(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
sec = body.section(**plane)
if sec is not None:
    for poly in sec.discrete:
        ax.fill(poly[:, 1], poly[:, 2], facecolor="#f7d84a", edgecolor="#b8941a",
                lw=1.2, zorder=1)

# lineas de capa
for z in np.arange(PLATE_Z, TOP_Z + 1, 0.2):
    ax.plot([ymin - 2, ymax + 2], [z, z], color="#c9a92a", lw=0.4, alpha=0.3, zorder=0)

# cama
ax.plot([ymin - 4, ymax + 4], [PLATE_Z, PLATE_Z], color="#444", lw=3)
ax.text((ymin + ymax) / 2, PLATE_Z - 1.6, "CAMA (aquí va la cara trasera)",
        ha="center", fontsize=9, color="#444")

# cavidad + tag (detras de la cara)
ax.add_patch(plt.Rectangle((vy0, vz0), vy1 - vy0, vz1 - vz0, facecolor="white",
             edgecolor="#888", lw=1, zorder=3))
ax.add_patch(plt.Rectangle((vy0 + 0.6, vz0 + 0.1), (vy1 - vy0) - 1.2, 1.5,
             facecolor="#333", zorder=4))          # tag real 1.5 mm
ax.text((vy0 + vy1) / 2, vz0 + 0.85, "TAG NFC", color="white", ha="center",
        va="center", fontsize=8, zorder=5)

# linea de PAUSA
ax.annotate("", xy=(vy1, PAUSE_Z), xytext=(ymax + 3, PAUSE_Z),
            arrowprops=dict(arrowstyle="-|>", color="#d12", lw=2.5), zorder=6)
ax.text(ymax + 4, PAUSE_Z, f"PAUSA\n~{ph(PAUSE_Z):.0f} mm", color="#d12",
        fontsize=11, fontweight="bold", va="center", zorder=6)

# etiquetas
ax.annotate("rebaje: aquí encaja\nla carita (pieza aparte)",
            xy=(4, TOP_Z - 0.5), xytext=(ymax - 2, TOP_Z + 3), fontsize=9, ha="left",
            arrowprops=dict(arrowstyle="->", color="#555"))
ax.text(ymin - 3, (PLATE_Z + PANEL_Z) / 2 - 3,
        "CUERPO amarillo\n(1 solo color,\n0 cambios,\nsin torre de purga)",
        fontsize=9, color="#8a6d10", va="center", ha="right")
ax.annotate("el techo amarillo\nsella el tag",
            xy=(0, PANEL_Z + 0.3), xytext=(ymin - 2, PANEL_Z - 6), fontsize=8.5,
            ha="right", arrowprops=dict(arrowstyle="->", color="#555"))

# flecha direccion de impresion
ax.annotate("", xy=(ymin - 1, TOP_Z), xytext=(ymin - 1, PLATE_Z + 1),
            arrowprops=dict(arrowstyle="-|>", color="#0a7", lw=2))

ax.set_xlim(ymin - 12, ymax + 12)
ax.set_ylim(PLATE_Z - 4, TOP_Z + 6)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("CUERPO (1 solo color) con el tag embebido\n"
             "Pausa para meter el tag; la carita va aparte (encaja a presión)", fontsize=12)

plt.tight_layout()
plt.savefig("diagrama_nfc.png", dpi=120, bbox_inches="tight", facecolor="white")
print(f"Altura total {ph(TOP_Z):.1f} mm | Pausa a ~{ph(PAUSE_Z):.0f} mm. Guardado diagrama_nfc.png")
