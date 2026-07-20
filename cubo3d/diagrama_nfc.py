#!/usr/bin/env python3
"""Diagrama: impresion con la carita ARRIBA + NFC embebido detras de la cara."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

PLATE_Z = -23.0                 # cara trasera (va sobre la cama)
CAV_Z0, CAV_Z1 = 18.4, 20.0     # cavidad del NFC (detras de la cara)
PAUSE_Z = CAV_Z1 - 0.2          # altura de pausa
PANEL_Z = 21.2                  # fondo del panel de la cara

def ph(z):  # altura de impresion desde la cama
    return z - PLATE_Z

fig, ax = plt.subplots(figsize=(7.5, 9))

# Corte vertical (plano x=0): perfil Y-Z, con Z hacia arriba (direccion de impresion)
plane = dict(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
for f, fc, ec in [("cuerpo_amarillo.stl", "#f7d84a", "#b8941a"),
                  ("cara_crema.stl", "#f6ecd0", "#c9a24a")]:
    sec = trimesh.load(f).section(**plane)
    if sec is None:
        continue
    for poly in sec.discrete:
        ax.fill(poly[:, 1], poly[:, 2], facecolor=fc, edgecolor=ec, lw=1.2, zorder=1)

# lineas de capa
for z in np.arange(PLATE_Z, 26, 0.2):
    ax.plot([-30, 30], [z, z], color="#c9a92a", lw=0.4, alpha=0.35, zorder=0)

# cama
ax.plot([-32, 32], [PLATE_Z, PLATE_Z], color="#444", lw=3)
ax.text(0, PLATE_Z - 1.5, "CAMA (aquí va la cara trasera)", ha="center", fontsize=9, color="#444")

# cavidad + tag (detras de la cara)
ax.add_patch(plt.Rectangle((-13, CAV_Z0), 26, CAV_Z1 - CAV_Z0, facecolor="white",
             edgecolor="#888", lw=1, zorder=3))
ax.add_patch(plt.Rectangle((-12.5, CAV_Z0 + 0.2), 25, 1.0, facecolor="#333", zorder=4))
ax.text(0, CAV_Z0 + 0.7, "TAG NFC", color="white", ha="center", va="center", fontsize=8, zorder=5)

# linea de PAUSA
ax.annotate("", xy=(13, PAUSE_Z), xytext=(26, PAUSE_Z),
            arrowprops=dict(arrowstyle="-|>", color="#d12", lw=2.5), zorder=6)
ax.text(28, PAUSE_Z, f"PAUSA\n~{ph(PAUSE_Z):.0f} mm", color="#d12", fontsize=11,
        fontweight="bold", va="center", zorder=6)

# etiquetas
ax.annotate("carita (crema + ojos)\nse imprime al final",
            xy=(6, 23.5), xytext=(20, 27), fontsize=9, ha="left",
            arrowprops=dict(arrowstyle="->", color="#555"))
ax.text(-29, 0, "cuerpo amarillo\n(se imprime casi\ntodo primero,\nsin cambios\nde color)",
        fontsize=9, color="#8a6d10", va="center")
ax.annotate("la cara sella el tag\n(queda oculto detrás)",
            xy=(0, PANEL_Z + 1), xytext=(-30, 14), fontsize=8.5, ha="left",
            arrowprops=dict(arrowstyle="->", color="#555"))

# flecha direccion de impresion
ax.annotate("", xy=(-27, 24), xytext=(-27, PLATE_Z + 1),
            arrowprops=dict(arrowstyle="-|>", color="#0a7", lw=2))
ax.text(-28.5, 0, "imprime →", color="#0a7", fontsize=9, rotation=90, va="center")

ax.set_xlim(-34, 40); ax.set_ylim(PLATE_Z - 4, 30)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Impresión EFICIENTE: carita hacia arriba\n"
             "El tag se embebe detrás de la cara (pausa cerca del final)", fontsize=12)

plt.tight_layout()
plt.savefig("diagrama_nfc.png", dpi=120, bbox_inches="tight", facecolor="white")
print(f"Pausa a ~{ph(PAUSE_Z):.0f} mm. Guardado diagrama_nfc.png")
