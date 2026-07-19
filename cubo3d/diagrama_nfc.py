#!/usr/bin/env python3
"""Diagrama explicativo: como se embebe el tag NFC con una pausa de impresion."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh

# Parametros reales del modelo
BASE_Y = -28.0
SKIN = 1.2
CAV_H = 1.6
CAV_TOP = BASE_Y + SKIN + CAV_H      # -25.2
PAUSE_Y = CAV_TOP - 0.2              # pausar justo antes de cerrar el techo
LAYER = 0.2

fig, ax = plt.subplots(figsize=(11, 6))

# Contorno del cuerpo (corte en z=0), zona de la base
body = trimesh.load("cuerpo_amarillo.stl")
sec = body.section(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1])
for poly in sec.discrete:
    ax.fill(poly[:, 0], poly[:, 1], facecolor="#f7d84a", edgecolor="#b8941a",
            linewidth=1.5, zorder=1)

# Lineas de capa (cada 0.2 mm)
for i, y in enumerate(np.arange(BASE_Y, BASE_Y + 7, LAYER)):
    ax.plot([-30, 30], [y, y], color="#c9a92a", lw=0.6, alpha=0.55, zorder=2)
ax.text(30.5, BASE_Y + 3, "cada línea =\n1 capa (0.2 mm)", fontsize=8,
        color="#8a6d10", va="center", ha="left")

# Piel solida de la base
ax.axhspan(BASE_Y, BASE_Y + SKIN, xmin=0.10, xmax=0.90, color="#e8b91f",
           alpha=0.55, zorder=2)
ax.text(0, BASE_Y + SKIN/2, "① piel de la base (~1.2 mm) — se imprime primero",
        ha="center", va="center", fontsize=9, zorder=6)

# Cavidad + tag
ax.add_patch(plt.Rectangle((-13, BASE_Y + SKIN), 26, CAV_H, facecolor="white",
             edgecolor="#888", lw=1, zorder=3))
ax.add_patch(plt.Rectangle((-12.5, BASE_Y + SKIN + 0.25), 25, 1.0,
             facecolor="#333", zorder=4))
ax.text(0, BASE_Y + SKIN + 0.75, "TAG NFC", color="white", ha="center",
        va="center", fontsize=9, zorder=5)

# Marca de PAUSA
ax.annotate("", xy=(-13, PAUSE_Y), xytext=(-24, PAUSE_Y),
            arrowprops=dict(arrowstyle="-|>", color="#d12", lw=2.5), zorder=7)
ax.text(-30, PAUSE_Y + 1.1, f"② PAUSA a ~{PAUSE_Y-BASE_Y:.1f} mm",
        color="#d12", fontsize=12, fontweight="bold", ha="left", zorder=7)
ax.text(-30, PAUSE_Y - 1.3, "la impresora se detiene:\npones el tag y reanudas",
        color="#d12", fontsize=9, ha="left", zorder=7)

# Techo que cierra
ax.annotate("③ la impresión cierra el\ntecho encima y sella el tag\n"
            "→ queda invisible y no se saca",
            xy=(9, CAV_TOP + 0.2), xytext=(6, -22.5),
            fontsize=9.5, ha="left",
            arrowprops=dict(arrowstyle="->", color="#333"), zorder=7)

ax.set_xlim(-31, 40)
ax.set_ylim(-29, -20.5)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Cómo se embebe el tag NFC durante la impresión — zoom de la base\n"
             "(cubo impreso de pie sobre su base; se ve el corte lateral)", fontsize=12)

plt.tight_layout()
plt.savefig("diagrama_nfc.png", dpi=120, bbox_inches="tight", facecolor="white")
print(f"Pausa recomendada a ~{PAUSE_Y-BASE_Y:.1f} mm. Guardado diagrama_nfc.png")
