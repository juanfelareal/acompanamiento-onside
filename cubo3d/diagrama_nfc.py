#!/usr/bin/env python3
"""Diagrama: impresion DE PIE (cara al frente) + NFC embebido ACOSTADO en la
cabeza. La direccion de impresion es +Y (hacia arriba). Todas las alturas se
derivan del modelo generado (cualquier escala)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

body = trimesh.load("cuerpo_amarillo.stl")

PLATE_Y = float(body.bounds[0][1])        # base (va sobre la cama al imprimir de pie)
TOP_Y = float(body.bounds[1][1])          # coronilla (ultimo en imprimirse)
void = [c for c in body.split(only_watertight=False) if c.volume < 0][0]
vz0, vy0 = float(void.bounds[0][2]), float(void.bounds[0][1])
vz1, vy1 = float(void.bounds[1][2]), float(void.bounds[1][1])
PAUSE_Y = vy1 - 0.1                        # pausa justo bajo el techo de la cavidad


def ph(y):
    return y - PLATE_Y


zmin, zmax = float(body.bounds[0][2]), float(body.bounds[1][2])

fig, ax = plt.subplots(figsize=(8, 9))

# Corte vertical (plano x=0): perfil Z-Y (Y hacia arriba = direccion de impresion).
# Solo el CUERPO (1 color). La cavidad del NFC aparece como una ranura horizontal.
plane = dict(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
sec = body.section(**plane)
if sec is not None:
    for poly in sec.discrete:
        ax.fill(poly[:, 2], poly[:, 1], facecolor="#c9a6f0", edgecolor="#7b4fc0",
                lw=1.2, zorder=1)

# lineas de capa (horizontales, perpendiculares a la direccion de impresion Y)
for y in np.arange(PLATE_Y, TOP_Y + 1, 0.2):
    ax.plot([zmin - 2, zmax + 2], [y, y], color="#b79be0", lw=0.4, alpha=0.3, zorder=0)

# cama (abajo)
ax.plot([zmin - 4, zmax + 4], [PLATE_Y, PLATE_Y], color="#444", lw=3)
ax.text((zmin + zmax) / 2, PLATE_Y - 1.8, "CAMA (Bloki de pie, cara al frente)",
        ha="center", fontsize=9, color="#444")

# cavidad + tag (acostado, disco horizontal)
ax.add_patch(plt.Rectangle((vz0, vy0), vz1 - vz0, vy1 - vy0, facecolor="white",
             edgecolor="#888", lw=1, zorder=3))
ax.add_patch(plt.Rectangle((vz0 + 0.1, vy0 + 0.1), (vz1 - vz0) - 0.2, 1.5,
             facecolor="#333", zorder=4))          # tag real 1.5 mm acostado
ax.text((vz0 + vz1) / 2, vy0 + 0.85, "TAG NFC (acostado)", color="white",
        ha="center", va="center", fontsize=8, zorder=5)

# flecha de la PAUSA (viene desde arriba: se apoya el tag)
ax.annotate("", xy=((vz0 + vz1) / 2, vy1 + 0.2), xytext=((vz0 + vz1) / 2, TOP_Y + 5),
            arrowprops=dict(arrowstyle="-|>", color="#d12", lw=2.5), zorder=6)
ax.text((vz0 + vz1) / 2, TOP_Y + 5.6, f"PAUSA a ~{ph(PAUSE_Y):.0f} mm\n"
        "(apoyar el tag plano\ny reanudar)", color="#d12", fontsize=10.5,
        fontweight="bold", ha="center", va="bottom", zorder=6)

# el techo solido de la cabeza sella el tag
ax.annotate("la cabeza solida\nde encima sella el tag",
            xy=(vz1 - 2, vy1 + 0.2), xytext=(zmax + 2, (vy1 + TOP_Y) / 2),
            fontsize=8.5, ha="left", arrowprops=dict(arrowstyle="->", color="#555"))

# la cara va al FRENTE (pared vertical -> textura lisa)
ax.annotate("la CARA va al frente\n(pared vertical = lisa)",
            xy=(zmax - 0.5, 4), xytext=(zmax + 2, PLATE_Y + 4), fontsize=9, ha="left",
            arrowprops=dict(arrowstyle="->", color="#7b4fc0"))

ax.text(zmin - 3, (PLATE_Y + TOP_Y) / 2,
        "CUERPO (1 solo color)\nimpreso DE PIE:\nfrente y cara salen\nlisos (vertical)",
        fontsize=9, color="#5a3a90", va="center", ha="right")

# flecha direccion de impresion
ax.annotate("", xy=(zmin - 1, TOP_Y), xytext=(zmin - 1, PLATE_Y + 1),
            arrowprops=dict(arrowstyle="-|>", color="#0a7", lw=2))
ax.text(zmin - 1.4, (PLATE_Y + TOP_Y) / 2, "impresion", color="#0a7", fontsize=8,
        rotation=90, va="center", ha="right")

ax.set_xlim(zmin - 12, zmax + 12)
ax.set_ylim(PLATE_Y - 4, TOP_Y + 12)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Impresion DE PIE (cara al frente) + tag NFC acostado en la cabeza\n"
             "Pausa casi al final para apoyar el tag; el techo lo sella (oculto y fijo)",
             fontsize=11.5)

plt.tight_layout()
plt.savefig("diagrama_nfc.png", dpi=120, bbox_inches="tight", facecolor="white")
print(f"Altura total {ph(TOP_Y):.1f} mm | Pausa a ~{ph(PAUSE_Y):.0f} mm. Guardado diagrama_nfc.png")
