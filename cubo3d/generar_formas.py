#!/usr/bin/env python3
"""Dos FORMAS de base imprimibles de pie SIN soportes (resuelven el overhang):
  A) chaflan  -> pillowy arriba + base plana con bisel ~60deg (se ve 'sentadito')
  B) cajita   -> base plana, paredes verticales, solo top+aristas verticales
                 redondeadas (mas 'bloque', el mas limpio de imprimir)
Ambas con la textura RANURADA. Cara y ojos identicos. NFC sigue leyendo por debajo.
"""
import numpy as np
import trimesh
import generar_cubo as G
import generar_texturas as T

G.EARS_ON = False
G.VOXEL = 0.20
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


def make_grid():
    X, Y, Z, origin, spacing = G.build_grid()
    return (X.astype(f32), Y.astype(f32), Z.astype(f32), origin, spacing)


def body_pillowy(X, Y, Z):
    return G.sdf_round_box(np.stack([X, Y, Z], axis=-1),
                           (W / 2 - R, H / 2 - R, D / 2 - R), R).astype(f32)


def shape_chaflan(X, Y, Z):
    """Pillowy, pero el tercio de abajo se reemplaza por un bisel ~60deg desde la
    horizontal (30deg de la vertical) -> imprimible. Base plana la pone finish_body."""
    body = body_pillowy(X, Y, Z)
    y_knee = -(H / 2 - R)                 # donde empezaba el redondeo inferior
    k = 0.577                             # cot(60deg): bisel a 60deg de la horizontal
    inset = (np.clip(y_knee - Y, 0.0, None) * k).astype(f32)
    cone2d = G.sdf_round_rect_2d(X, Z, W / 2 - R - inset, D / 2 - R - inset, R)
    return op_smax(body, cone2d, 0.9)     # bisela la base (transicion suave)


def shape_cajita(X, Y, Z):
    """Base plana + paredes verticales + top y aristas verticales redondeadas (R)."""
    # nucleo rectangular RECTO (r=0); el -R de abajo redondea aristas verticales y top
    d2 = G.sdf_round_rect_2d(X, Z, W / 2 - R, D / 2 - R, 0.0)
    ty = Y - (H / 2 - R)
    ext = np.hypot(np.maximum(d2, 0.0), np.maximum(ty, 0.0))
    ins = np.minimum(np.maximum(d2, ty), 0.0)
    top = ext + ins - R                                       # paredes + top redondeado
    body = op_intersect(top, (-H / 2 - Y))                    # base plana en y=-H/2
    return body.astype(f32)


def build_one(name, shape_fn, nfc_cy, base_cut, X, Y, Z, origin, spacing):
    G.NFC_CY = nfc_cy
    G.BASE_CUT = base_cut
    feats = T.build_features(X, Y, Z, origin)
    body = shape_fn(X, Y, Z)
    body = body + tex_ranurado(X, Y, Z)
    body = T.finish_body(body, feats, Y)
    m = G.mesh_from_field(body, origin, spacing, f"cuerpo_{name}")
    del body
    fn = f"cuerpo_{name}_ranurado"
    m.export(fn + ".stl")
    G.export_3mf_ams([(m, fn, "F2CD28")], fn + ".3mf")
    d = m.bounds[1] - m.bounds[0]
    print(f"  dim (mm): {d[0]:.1f} x {d[1]:.1f} x {d[2]:.1f}")
    return m, feats


def main():
    print("Grilla...")
    X, Y, Z, origin, spacing = make_grid()

    # A: chaflan. NFC un poco mas alto (zona ancha, pared sana), base plana a 2.5 mm.
    print("\n== A: chaflan ==")
    mA, featsA = build_one("chaflan", shape_chaflan, nfc_cy=-9.0, base_cut=2.5,
                           X=X, Y=Y, Z=Z, origin=origin, spacing=spacing)

    # B: cajita. Base plana llega abajo -> NFC a ~2 mm de la base, ancho completo.
    print("\n== B: cajita ==")
    mB, featsB = build_one("cajita", shape_cajita, nfc_cy=-14.0, base_cut=0.0,
                           X=X, Y=Y, Z=Z, origin=origin, spacing=spacing)

    # cara + ojos (identicos) — de featsB
    print("\nCara y ojos...")
    m_face = G.mesh_from_field(featsB["panel"], origin, spacing, "cara")
    m_black = G.mesh_from_field(featsB["black"], origin, spacing, "ojos")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    G.export_3mf_ams([(m_face, "cara_crema", "FAEBCD")], "cara_crema.3mf")
    G.export_3mf_ams([(m_black, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")

    for name, mb in [("chaflan", mA), ("cajita", mB)]:
        b = mb.copy(); b.visual.face_colors = G.COL_BODY
        f = m_face.copy(); f.visual.face_colors = G.COL_FACE
        e = m_black.copy(); e.visual.face_colors = G.COL_BLACK
        trimesh.Scene([b, f, e]).export(f"bloki_{name}.glb")

    print("\nLISTO: cuerpo_chaflan_ranurado, cuerpo_cajita_ranurado")


if __name__ == "__main__":
    main()
