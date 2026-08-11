#!/usr/bin/env python3
"""Cuatro siluetas NUEVAS imprimibles de pie sin soportes:
  1) huevo    -> gota/huevito (mas ancho abajo, afina arriba) - la mas imprimible
  2) domo     -> base recta + cupula grande arriba (tombstone)
  3) trapecio -> apenas mas ancho en la base (draft sutil), look 'plantado'
  4) bisel    -> chaflan arriba Y abajo (gema/farol geometrico)
Todas con textura ranurada. Un 'face-boss' garantiza el frente plano del panel
en cualquier silueta (para que la cara siempre encaje). Cara y ojos identicos.
"""
import numpy as np
import trimesh
import generar_cubo as G
import generar_texturas as T

G.EARS_ON = False
G.VOXEL = 0.20
G.NFC_CY = -13.0        # cabe en las 4 siluetas; lee a ~3 mm de la base
G.BASE_CUT = 0.0        # cada silueta ya trae su base plana
f32 = np.float32
W, H, D, R = G.W, G.H, G.D, G.R
T.W, T.H, T.D, T.R, T.S = W, H, D, R, G.S
op_intersect, op_subtract, op_union = G.op_intersect, G.op_subtract, G.op_union


def op_smax(a, b, k):
    return -G.op_smin(-a, -b, k)


def tex_ranurado(X, Y, Z):
    N, amp = 30, 0.40
    theta = np.arctan2(Z, X).astype(f32)
    groove = 0.5 + 0.5 * np.cos(N * theta)
    yfade = np.clip((H / 2 - Y) / R, 0.0, 1.0).astype(f32)
    return (amp * groove * yfade * T.pole_fade(X, Z)).astype(f32)


def face_boss(X, Y, Z):
    """Columna con el footprint del panel (un pelin mayor) desde el centro hasta
    el frente (Z=D/2). Unida al cuerpo, asegura un frente PLANO para el panel."""
    m = 1.6
    rr = G.sdf_round_rect_2d(X, Y - G.FACE_CY, G.FACE_W / 2 - G.FACE_R,
                             G.FACE_H / 2 - G.FACE_R, G.FACE_R + m)
    return op_intersect(rr, G.z_slab(Z, 0.0, D / 2))


# ---- siluetas ----
def taper_body(X, Y, Z, t):
    core = G.sdf_round_rect_2d(X, Z, (W / 2) * t - R, (D / 2) * t - R, 0.0)
    ty = Y - (H / 2 - R)
    ext = np.hypot(np.maximum(core, 0.0), np.maximum(ty, 0.0))
    ins = np.minimum(np.maximum(core, ty), 0.0)
    top = ext + ins - R
    return op_intersect(top, (-H / 2 - Y)).astype(f32)      # base plana


def shape_huevo(X, Y, Z):
    u = np.clip((Y + H / 2) / H, 0.0, 1.0).astype(f32)
    t = (1.0 - 0.30 * u ** 1.4).astype(f32)                 # ancho abajo, afina arriba
    return taper_body(X, Y, Z, t)


def shape_trapecio(X, Y, Z):
    u = np.clip((Y + H / 2) / H, 0.0, 1.0).astype(f32)
    t = (1.06 - 0.16 * u).astype(f32)                       # draft sutil
    return taper_body(X, Y, Z, t)


def shape_domo(X, Y, Z):
    y0 = -H / 2
    domH = D / 2 * 1.05
    y_sh = H / 2 - domH
    core = G.sdf_round_rect_2d(X, Z, W / 2 - R, D / 2 - R, 0.0)
    wall2d = core - R
    walls = op_intersect(wall2d, G.z_slab(Y, y0, y_sh))     # paredes rectas
    ex = (X / (W / 2)) ** 2 + ((Y - y_sh) / domH) ** 2 + (Z / (D / 2)) ** 2
    dome = (np.sqrt(ex) - 1.0) * min(W / 2, D / 2)
    body = G.op_smin(walls, dome.astype(f32), 2.0)
    return op_intersect(body, (-H / 2 - Y)).astype(f32)


def shape_bisel(X, Y, Z):
    core = G.sdf_round_rect_2d(X, Z, W / 2 - R, D / 2 - R, 0.0)
    prism = core - R
    kneeB, kneeT, k = -H / 2 + 5.0, H / 2 - 5.0, 0.84
    inset = ((np.clip(kneeB - Y, 0.0, None) +
              np.clip(Y - kneeT, 0.0, None)) * k).astype(f32)
    cone = G.sdf_round_rect_2d(X, Z, W / 2 - R - inset, D / 2 - R - inset, R)
    body = op_smax(prism, cone, 0.8)
    return op_intersect(body, G.z_slab(Y, -H / 2, H / 2)).astype(f32)


SHAPES = [("huevo", shape_huevo), ("domo", shape_domo),
          ("trapecio", shape_trapecio), ("bisel", shape_bisel)]


def main():
    print("Grilla...")
    X, Y, Z, origin, spacing = G.build_grid()
    X = X.astype(f32); Y = Y.astype(f32); Z = Z.astype(f32)

    print("Piezas comunes (una vez)...")
    feats = T.build_features(X, Y, Z, origin)
    boss = face_boss(X, Y, Z)

    made = []
    for name, fn in SHAPES:
        print(f"\n== {name} ==")
        body = fn(X, Y, Z)
        body = op_union(body, boss)              # frente plano garantizado
        body = body + tex_ranurado(X, Y, Z)
        body = T.finish_body(body, feats, Y)
        m = G.mesh_from_field(body, origin, spacing, f"cuerpo_{name}")
        del body
        fnm = f"cuerpo_{name}"
        m.export(fnm + ".stl")
        G.export_3mf_ams([(m, fnm, "F2CD28")], fnm + ".3mf")
        d = m.bounds[1] - m.bounds[0]
        print(f"  dim (mm): {d[0]:.1f} x {d[1]:.1f} x {d[2]:.1f}")
        made.append((name, m))

    print("\nCara y ojos...")
    m_face = G.mesh_from_field(feats["panel"], origin, spacing, "cara")
    m_black = G.mesh_from_field(feats["black"], origin, spacing, "ojos")
    m_face.export("cara_crema.stl"); m_black.export("ojos_negro.stl")
    G.export_3mf_ams([(m_face, "cara_crema", "FAEBCD")], "cara_crema.3mf")
    G.export_3mf_ams([(m_black, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")

    for name, mb in made:
        b = mb.copy(); b.visual.face_colors = G.COL_BODY
        f = m_face.copy(); f.visual.face_colors = G.COL_FACE
        e = m_black.copy(); e.visual.face_colors = G.COL_BLACK
        trimesh.Scene([b, f, e]).export(f"bloki_{name}.glb")

    print("\nLISTO:", ", ".join(n for n, _ in made))


if __name__ == "__main__":
    main()
