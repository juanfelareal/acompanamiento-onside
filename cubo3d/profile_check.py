#!/usr/bin/env python3
"""Compara el PERFIL (corte en Z=0) de la parte de abajo del chaflan para varias
suavizaciones, y mide el voladizo maximo (para que siga imprimiendo de pie)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import generar_cubo as G

G.EARS_ON = False
W, H, D, R = G.W, G.H, G.D, G.R


def op_smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def op_smax(a, b, k):
    return -op_smin(-a, -b, k)


def rrect(px, py, hx, hy, r):
    qx = np.abs(px) - hx; qy = np.abs(py) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def profile(X, Y, k_cone, knee, blend, base_cut, base_round):
    """SDF 2D (X-Y) del corte Z=0 del chaflan con parametros dados."""
    body = rrect(X, Y, W / 2 - R, H / 2 - R, R)          # pillowy (redondo arriba y abajo)
    y_knee = knee
    inset = np.clip(y_knee - Y, 0, None) * k_cone
    cone = np.abs(X) - (W / 2 - inset)                    # en Z=0 el cono es solo en X
    body = op_smax(body, cone, blend)                    # bisela la base
    y_base = -H / 2 + base_cut
    if base_round > 0:
        body = op_smax(body, (y_base - Y), base_round)   # redondea el borde de la base
    else:
        body = np.maximum(body, (y_base - Y))
    return body


def max_overhang(xs, ys, field, y_base):
    """Traza el borde derecho x(y) y mide el angulo desde la vertical del muro que
    CRECE hacia afuera al subir (voladizo). Excluye el fileteado justo en la base."""
    xb = np.full(len(ys), np.nan)
    for i in range(len(ys)):
        inside = np.where(field[i] < 0)[0]
        if len(inside):
            xb[i] = xs[inside[-1]]                        # borde derecho
    worst = 0.0
    for i in range(1, len(ys) - 1):
        y = ys[i]
        if y < y_base + 0.8 or y > 0:                     # solo la mitad de abajo
            continue
        if np.isnan(xb[i]) or np.isnan(xb[i - 1]):
            continue
        dxdy = (xb[i] - xb[i - 1]) / (ys[i] - ys[i - 1])
        if dxdy > 0:                                      # crece hacia afuera = voladizo
            worst = max(worst, np.degrees(np.arctan(dxdy)))
    return worst


xs = np.linspace(-W / 2 - 3, W / 2 + 3, 500)
ys = np.linspace(-H / 2 - 3, H / 2 + 3, 500)
X, Y = np.meshgrid(xs, ys)
knee = -(H / 2 - R)

VARIANTS = [
    ("Actual (chaflan recto)", 0.577, knee, 0.9, 2.5, 0.0),
    ("Suave", 0.52, knee + 1.0, 2.4, 2.6, 1.4),
    ("Mas redondo", 0.46, knee + 2.0, 3.2, 3.0, 2.0),
    ("Maximo redondo", 0.40, knee + 3.0, 4.0, 3.4, 2.6),
]
fig, axes = plt.subplots(1, 4, figsize=(16, 6), facecolor="#111")
for ax, (title, k, kn, bl, bc, br) in zip(axes, VARIANTS):
    F = profile(X, Y, k, kn, bl, bc, br)
    ov = max_overhang(xs, ys, F, -H / 2 + bc)
    ax.contourf(X, Y, F, levels=[-100, 0], colors=["#f2cd28"])
    ax.contour(X, Y, F, levels=[0], colors=["#111"], linewidths=1)
    # marcar linea de 45 grados de referencia en la base
    ax.axhline(-H / 2 + bc, color="#0af", lw=0.8, ls="--")
    ax.set_aspect("equal"); ax.axis("off")
    col = "#5f5" if ov <= 52 else "#f66"
    ax.set_title(f"{title}\nvoladizo max ~{ov:.0f} deg", color=col, fontsize=12)
fig.suptitle("Perfil de la base del chaflan (corte lateral) — arriba redondo vs abajo",
             color="w", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig("profile_check.png", dpi=115, facecolor="#111", bbox_inches="tight")
print("ok")
