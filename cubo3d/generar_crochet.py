#!/usr/bin/env python3
"""Version CROCHET/TEJIDO del bloque con esquinas curvas abajo (forma 'chaflan').
Textura de punto stockinette (filas de 'V' entrelazadas con desfase de medio
punto). Cara y ojos identicos. Imprime de pie sin soportes."""
import numpy as np
import trimesh
import generar_cubo as G
import generar_texturas as T
import generar_formas as F      # trae shape_chaflan / op_smax (mismos parametros)

G.EARS_ON = False
G.VOXEL = 0.18
G.BRAND_ON = False              # el logo se graba en tex_crochet (sigue la superficie)
G.BASE_CUT = 0.0                # la base plana la pone shape_chaflan (borde redondeado)
G.NFC_CY = -9.0                 # zona ancha, pared sana; lee a ~5 mm de la base
f32 = np.float32
W, H, D, R = G.W, G.H, G.D, G.R
T.W, T.H, T.D, T.R, T.S = W, H, D, R, G.S
F.W, F.H, F.D, F.R = W, H, D, R


def tex_crochet(X, Y, Z):
    """Textura CHEVRON/HERRINGBONE (espiga), como la abeja: bandas de columna con
    diagonal alterna -> zigzag continuo. Filas alrededor (theta), sube en Y."""
    theta = np.arctan2(Z, X).astype(f32)
    Ncols = 96                                   # puntos alrededor (~1.4 mm c/u, como la abeja)
    col = theta / (2 * np.pi) * Ncols
    rowH = 1.4                                    # alto de fila (mm)
    row = (Y - (-H / 2)) / rowH
    bw = 1.0                                      # ancho de banda (1 = chevron fino)
    ci = np.floor(col / bw)
    s = (1 - 2 * (ci.astype(np.int32) % 2)).astype(f32)   # pendiente alterna +/-1
    cl = col - ci * bw
    u = row - s * cl                             # coordenada diagonal
    d = np.abs((u % 1.0) - 0.5)                   # dist al centro del hilo
    w = 0.34
    yarn = np.clip(1.0 - (d / w) ** 2, 0.0, 1.0) ** 0.5
    amp = 0.38                                    # relieve del hilo (mm)
    yfade = np.clip((H / 2 - Y) / R, 0.0, 1.0).astype(f32)
    tex = amp * yarn * yfade * T.pole_fade(X, Z)  # magnitud del relieve del tejido

    # --- LOGO BLOKI en la ESPALDA: SOLO las letras grabadas (sin placa) ---
    # Las letras se hunden y se les quita el tejido adentro; el resto queda tejido.
    # Sigue la superficie curva. Subido a Y=-3.5 -> cae en la parte PLANA de la
    # espalda (no en la curva de abajo), para que el grabado salga parejo.
    xs = X[:, 0, 0]; ys = Y[0, :, 0]
    logo2d = G.logo_sdf_2d(xs, ys, "bloki_logo_mask.png", 5.45, 0.0, -3.5)[:, :, None]
    gate = np.clip((-6.0 - Z) / 2.0, 0.0, 1.0).astype(f32)      # solo espalda
    lm = np.clip(0.5 - logo2d / 0.35, 0.0, 1.0).astype(f32) * gate
    DEPTH = 0.8
    disp = -tex * (1.0 - lm) + DEPTH * lm
    return disp.astype(f32)


def build_laminae(X, Y, Z):
    """Dos LAMINAS completas que se apilan y encajan:
      - eyes (negra): placa trasera completa + 2 ojos (cilindro+cupula) que suben.
      - face (crema): placa delantera completa + nariz - 2 huecos por donde ASOMAN
        los ojos de la lamina trasera.
    Ambas tienen el mismo contorno (encajan en el rebaje del cuerpo)."""
    front_z = D / 2.0
    face_top = front_z - G.FACE_RECESS
    pocket_floor = face_top - G.PANEL_T
    PLATE_E = 1.1                         # grosor lamina de ojos (atras)
    mid_z = pocket_floor + PLATE_E        # interfaz entre laminas
    PROT = 0.7                            # cuanto asoma el ojo por delante
    hx = G.FACE_W / 2 - G.FACE_R
    hy = G.FACE_H / 2 - G.FACE_R
    rr = G.sdf_round_rect_2d(X, Y - G.FACE_CY, hx, hy, G.FACE_R)     # contorno panel
    eye_pos = [(-G.EYE_DX, G.FACE_CY + G.EYE_DY), (G.EYE_DX, G.FACE_CY + G.EYE_DY)]
    ER = G.EYE_R
    # cupula esferica de altura PROT sobre base de radio ER
    Rc = (ER ** 2 + PROT ** 2) / (2 * PROT)
    z0 = face_top + PROT - Rc

    # ---- lamina de OJOS (negra) ----
    eyes = G.op_intersect(rr, G.z_slab(Z, pocket_floor, mid_z))     # placa trasera
    holes = None
    for (ex, ey) in eye_pos:
        cyl = G.cylinder_field(X, Y, Z, ex, ey, ER, mid_z, face_top)         # pasa el hueco
        cap = G.op_intersect(G.sphere_field(X, Y, Z, [ex, ey, z0], Rc),
                             (face_top - Z))                                 # cupula que asoma
        eyes = G.op_union(eyes, G.op_union(cyl, cap))
        h = G.cylinder_field(X, Y, Z, ex, ey, ER + G.EYE_CLEAR,
                             mid_z - 0.6, face_top + PROT + 0.6)
        holes = h if holes is None else G.op_union(holes, h)

    # ---- lamina de la CARA (crema) ----
    ny = G.FACE_CY + G.NOSE_DY
    nose_cz = face_top + G.NOSE_PROTRUDE - G.NOSE_R
    nose = G.sphere_field(X, Y, Z, [0.0, ny, nose_cz], G.NOSE_R)
    face = G.op_intersect(rr, G.z_slab(Z, mid_z, face_top))         # placa delantera
    face = G.op_union(face, nose)
    face = G.op_subtract(face, holes)                              # huecos de los ojos
    return face, eyes


def main():
    print("Grilla (VOXEL=%.2f)..." % G.VOXEL)
    X, Y, Z, origin, spacing = G.build_grid()
    X = X.astype(f32); Y = Y.astype(f32); Z = Z.astype(f32)

    print("Piezas comunes...")
    feats = T.build_features(X, Y, Z, origin)

    print("Cuerpo chaflan + textura crochet...")
    body = F.shape_chaflan(X, Y, Z)
    body = body + tex_crochet(X, Y, Z)
    body = T.finish_body(body, feats, Y)
    m = G.mesh_from_field(body, origin, spacing, "cuerpo_crochet")
    del body
    m.export("cuerpo_crochet.stl")
    G.export_3mf_ams([(m, "cuerpo_crochet", "F2CD28")], "cuerpo_crochet.3mf")
    d = m.bounds[1] - m.bounds[0]
    print(f"  dim (mm): {d[0]:.1f} x {d[1]:.1f} x {d[2]:.1f}")

    face_field, eyes_field = build_laminae(X, Y, Z)
    m_face = G.mesh_from_field(face_field, origin, spacing, "cara(lamina)")
    m_black = G.mesh_from_field(eyes_field, origin, spacing, "ojos(lamina)")
    del face_field, eyes_field
    m_face.export("cara_crema.stl"); m_black.export("ojos_negro.stl")
    G.export_3mf_ams([(m_face, "cara_crema", "FAEBCD")], "cara_crema.3mf")
    G.export_3mf_ams([(m_black, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")

    b = m.copy(); b.visual.face_colors = G.COL_BODY
    fa = m_face.copy(); fa.visual.face_colors = G.COL_FACE
    e = m_black.copy(); e.visual.face_colors = G.COL_BLACK
    trimesh.Scene([b, fa, e]).export("bloki_crochet.glb")
    print("\nLISTO: cuerpo_crochet")


if __name__ == "__main__":
    main()
