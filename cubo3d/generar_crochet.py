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
G.BRAND_ON = True               # logo BLOKI grabado en la espalda (abajo)
G.BASE_CUT = 2.5                # base plana del chaflan
G.NFC_CY = -9.0                 # zona ancha, pared sana; lee a ~5 mm de la base
f32 = np.float32
W, H, D, R = G.W, G.H, G.D, G.R
T.W, T.H, T.D, T.R, T.S = W, H, D, R, G.S
F.W, F.H, F.D, F.R = W, H, D, R


def tex_crochet(X, Y, Z):
    """Textura CHEVRON/HERRINGBONE (espiga), como la abeja: bandas de columna con
    diagonal alterna -> zigzag continuo. Filas alrededor (theta), sube en Y."""
    theta = np.arctan2(Z, X).astype(f32)
    Ncols = 64                                   # puntos alrededor (~1.9 mm c/u; par)
    col = theta / (2 * np.pi) * Ncols
    rowH = 1.9                                    # alto de fila (mm)
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
    return (-amp * yarn * yfade * T.pole_fade(X, Z)).astype(f32)


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

    m_face = G.mesh_from_field(feats["panel"], origin, spacing, "cara")
    m_black = G.mesh_from_field(feats["black"], origin, spacing, "ojos")
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
