#!/usr/bin/env python3
"""Genera el CUERPO de Bloki (modelo original, SIN orejas) en 4 TEXTURAS
intencionales, para elegir cual gusta mas. Reusa toda la maquinaria SDF de
generar_cubo.py (mismas medidas, mismo sistema de encaje, NFC, llavero y logo).

Texturas (cada una en su propio .stl y .3mf):
  1. facetado  -> low-poly / cristalino (caras planas grandes)
  2. voxel     -> bloques/pixeles en relieve (on-brand con "Bloki")
  3. ranurado  -> estrias verticales (fluting), esconde las capas
  4. dimples   -> hoyuelos suaves tipo pelota de golf

Ademas corrige la base: BASE_CUT baja de 2.0 -> 1.0 mm para que las esquinas
inferiores se vean redondas (antes se veian 'cortadas').
La cara y los ojos son identicos en las 4 (se generan una sola vez).
"""
import numpy as np
import trimesh
import generar_cubo as G

# ---- Ajustes para esta corrida ----
G.EARS_ON = False          # modelo original, SIN orejas
G.BASE_CUT = 1.0           # <-- arreglo: esquinas inferiores casi 100% redondas
G.VOXEL = 0.22             # un pelin mas grueso: la textura lo tapa y ahorra RAM/tiempo

# recalcular lo que dependia de BASE_CUT (se fijo al importar con 2.0)
G.NFC_CY = -G.H / 2 + G.BASE_CUT + G.NFC_READ + G.NFC_CAV_H / 2

# atajos
W, H, D, R = G.W, G.H, G.D, G.R
S = G.S
op_intersect, op_subtract, op_union = G.op_intersect, G.op_subtract, G.op_union
op_smin = G.op_smin


# ----------------------------------------------------------------------------
# TEXTURAS: perturbaciones del campo SDF (positivo = talla hacia adentro,
# negativo = sobresale). Se aplican SOLO al cuerpo redondeado, antes de recortar
# la base y de restar rebaje/NFC/llavero/logo (asi esas zonas quedan limpias).
# ----------------------------------------------------------------------------
def pole_fade(X, Z):
    """Atenua la textura cerca del eje vertical (coronilla) para no hacer un
    remolino en el polo. rho = radio horizontal."""
    rho = np.hypot(X, Z)
    return np.clip((rho - 2.0) / 4.0, 0.0, 1.0).astype(np.float32)


def tex_ranurado(X, Y, Z):
    """Estrias VERTICALES (fluting) alrededor de todo el cuerpo. Talla canales
    donde el coseno es alto -> quedan costillas entre canal y canal. Como corren
    verticales, cruzan las lineas de capa (horizontales) y las disimulan."""
    N = 32                                  # numero de estrias alrededor
    amp = 0.34                              # profundidad del canal (mm)
    theta = np.arctan2(Z, X).astype(np.float32)
    groove = 0.5 + 0.5 * np.cos(N * theta)  # 0..1
    # las estrias viven en las PAREDES verticales y se apagan en el domo superior
    # (asi no convergen en un remolino en la coronilla) y en el eje (rho pequeno).
    yfade = np.clip((H / 2 - Y) / R, 0.0, 1.0).astype(np.float32)  # 1 en paredes, 0 en apice
    return (amp * groove * yfade * pole_fade(X, Z)).astype(np.float32)


def tex_dimples(X, Y, Z):
    """Hoyuelos tipo pelota de golf: pozos en una reticula 3D (aparecen parejos
    en todas las caras porque el patron es volumetrico)."""
    p = 2.3
    amp = 0.42
    b = ((0.5 + 0.5 * np.cos(2 * np.pi * X / p)) *
         (0.5 + 0.5 * np.cos(2 * np.pi * Y / p)) *
         (0.5 + 0.5 * np.cos(2 * np.pi * Z / p)))
    return (amp * (b ** 0.6) * pole_fade(X, Z)).astype(np.float32)


def tex_voxel(X, Y, Z):
    """Bloques/pixeles en RELIEVE: tablero de ajedrez 3D -> cubos que sobresalen
    en patron alterno. Da el look 'voxel' coherente con el nombre Bloki."""
    p = 2.5
    amp = 0.5
    c = (np.sin(np.pi * X / p) * np.sin(np.pi * Y / p) *
         np.sin(np.pi * Z / p)).astype(np.float32)
    raised = 0.5 * (1.0 + np.tanh(7.0 * c))     # ~1 medio cubo, ~0 el otro
    return (-amp * raised * pole_fade(X, Z)).astype(np.float32)


# ----------------------------------------------------------------------------
def build_features(X, Y, Z, origin):
    """Construye (una sola vez) las piezas comunes a las 4 texturas: rebaje de la
    carita, cavidad NFC, orificio del llavero y grabado del logo. Devuelve tambien
    los campos para generar la cara y los ojos."""
    front_z = D / 2.0
    face_top = front_z - G.FACE_RECESS
    pocket_floor = face_top - G.PANEL_T
    hx = G.FACE_W / 2 - G.FACE_R
    hy = G.FACE_H / 2 - G.FACE_R
    rr = G.sdf_round_rect_2d(X, Y - G.FACE_CY, hx, hy, G.FACE_R)

    # ojos tipo remache + huecos (identico a generar_cubo)
    FLANGE_T = G.PANEL_T * 0.45
    eye_step_z = pocket_floor + FLANGE_T
    eye_pos = [(-G.EYE_DX, G.FACE_CY + G.EYE_DY), (G.EYE_DX, G.FACE_CY + G.EYE_DY)]
    black = None
    eye_holes = None
    for (ex, ey) in eye_pos:
        flange = G.cylinder_field(X, Y, Z, ex, ey, G.EYE_R + G.EYE_FLANGE,
                                  pocket_floor, eye_step_z)
        neck = G.cylinder_field(X, Y, Z, ex, ey, G.EYE_R, eye_step_z, face_top)
        head = op_intersect(G.sphere_field(X, Y, Z, [ex, ey, face_top], G.EYE_R),
                            (face_top - Z))
        eye = op_union(op_union(flange, neck), head)
        black = eye if black is None else op_union(black, eye)
        hole_neck = G.cylinder_field(X, Y, Z, ex, ey, G.EYE_R + G.EYE_CLEAR,
                                     eye_step_z, face_top + 1.0)
        hole_bore = G.cylinder_field(X, Y, Z, ex, ey,
                                     G.EYE_R + G.EYE_FLANGE + G.EYE_FLANGE_CLEAR,
                                     pocket_floor - 1.0, eye_step_z)
        hole = op_union(hole_neck, hole_bore)
        eye_holes = hole if eye_holes is None else op_union(eye_holes, hole)

    ny = G.FACE_CY + G.NOSE_DY
    nose_cz = face_top + G.NOSE_PROTRUDE - G.NOSE_R
    nose_bump = G.sphere_field(X, Y, Z, [0.0, ny, nose_cz], G.NOSE_R)

    # rebaje escalonado del cuerpo
    pocket_deep = op_intersect(rr - G.FIT_CLEAR,
                               G.z_slab(Z, pocket_floor, face_top))
    pocket_mouth = op_intersect(rr - (G.FIT_CLEAR + G.FACE_OFFSET), (face_top - Z))
    pocket = op_union(pocket_deep, pocket_mouth)

    # cavidad NFC (disco acostado cerca de la base)
    nfc_radial = np.hypot(X - 0.0, Z - G.NFC_CZ) - G.NFC_DIAM / 2.0
    nfc_yslab = np.abs(Y - G.NFC_CY) - 0.5 * G.NFC_CAV_H
    nfc = op_intersect(nfc_radial, nfc_yslab)

    # orificio del llavero (esquina superior trasera)
    Cc = np.array([-(W / 2 - R), H / 2 - R, -(D / 2 - R)])
    nvec = np.array([-1.0, 1.0, -1.0]) / np.sqrt(3)
    A = Cc + G.KR_A * nvec
    u = np.array([1.0, 1.0, 0.0]) / np.sqrt(2)
    kr = G.cylinder_axis_field(X, Y, Z, A, u, G.KR_R)
    kr = op_intersect(kr, G.sphere_field(X, Y, Z, Cc, R + 3))

    # logo grabado en la espalda
    r0x, r0y = W / 2 - R, H / 2 - R
    z_dome = -D / 2 + 0.0 * X            # espalda plana (BACK_DOME=0)
    engrave = None
    if G.BRAND_ON:
        xs = X[:, 0, 0]
        ys = Y[0, :, 0]
        brand2d = G.logo_sdf_2d(xs, ys, G.BRAND_LOGO, G.BRAND_H, 0.0, G.BRAND_CY)
        z_cut = z_dome + G.BRAND_DEPTH
        engrave = op_intersect(brand2d[:, :, None], (Z - z_cut))

    # cara (crema) y ojos (negro) ya listos como campos
    panel = op_intersect(rr, G.z_slab(Z, pocket_floor, face_top))
    panel = op_union(panel, nose_bump)
    panel = op_subtract(panel, eye_holes)

    return dict(pocket=pocket, nfc=nfc, kr=kr, engrave=engrave,
                panel=panel, black=black)


def finish_body(body, feats, Y):
    """Aplica base plana + resta rebaje/NFC/llavero/logo a un cuerpo texturizado."""
    y_base = -H / 2 + G.BASE_CUT
    body = op_intersect(body, y_base - Y)          # base plana
    body = op_subtract(body, feats["pocket"])
    body = op_subtract(body, feats["nfc"])
    body = op_subtract(body, feats["kr"])
    if feats["engrave"] is not None:
        body = op_subtract(body, feats["engrave"])
    return body


def main():
    print("Construyendo grilla (VOXEL=%.2f)..." % G.VOXEL)
    X, Y, Z, origin, spacing = G.build_grid()
    X = X.astype(np.float32); Y = Y.astype(np.float32); Z = Z.astype(np.float32)

    print("Piezas comunes (rebaje/NFC/llavero/logo/cara/ojos)...")
    feats = build_features(X, Y, Z, origin)

    # cuerpo redondeado base (sin textura)
    def round_body():
        return G.sdf_round_box(np.stack([X, Y, Z], axis=-1),
                               (W / 2 - R, H / 2 - R, D / 2 - R), R).astype(np.float32)

    variants = [
        ("ranurado", tex_ranurado, "F2CD28"),
        ("voxel",    tex_voxel,    "F2CD28"),
        ("dimples",  tex_dimples,  "F2CD28"),
    ]

    made = []
    for name, tex, hexc in variants:
        print(f"\n== textura: {name} ==")
        body = round_body()
        body = body + tex(X, Y, Z)                  # aplica textura
        body = finish_body(body, feats, Y)
        m = G.mesh_from_field(body, origin, spacing, f"cuerpo_{name}")
        del body
        fn = f"cuerpo_{name}"
        m.export(fn + ".stl")
        G.export_3mf_ams([(m, fn, hexc)], fn + ".3mf")
        made.append((name, m))

    # --- FACETADO: cuerpo liso decimado a pocas caras (look low-poly) ---
    print("\n== textura: facetado (low-poly) ==")
    body = round_body()
    body = finish_body(body, feats, Y)
    m = G.mesh_from_field(body, origin, spacing, "cuerpo_facetado_smooth")
    del body
    target = 1600
    try:
        mf = m.simplify_quadric_decimation(face_count=target)
    except TypeError:
        mf = m.simplify_quadric_decimation(target)
    trimesh.repair.fix_normals(mf)
    print(f"  [facetado] caras={len(mf.faces):,}  watertight={mf.is_watertight}")
    mf.export("cuerpo_facetado.stl")
    G.export_3mf_ams([(mf, "cuerpo_facetado", "F2CD28")], "cuerpo_facetado.3mf")
    made.append(("facetado", mf))

    # --- cara + ojos (identicos para las 4) ---
    print("\nCara y ojos (comunes)...")
    m_face = G.mesh_from_field(feats["panel"], origin, spacing, "cara")
    m_black = G.mesh_from_field(feats["black"], origin, spacing, "ojos")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    G.export_3mf_ams([(m_face, "cara_crema", "FAEBCD")], "cara_crema.3mf")
    G.export_3mf_ams([(m_black, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")

    # --- GLB a color por textura (cuerpo + cara + ojos) para previsualizar ---
    for name, mb in made:
        b = mb.copy(); b.visual.face_colors = G.COL_BODY
        f = m_face.copy(); f.visual.face_colors = G.COL_FACE
        e = m_black.copy(); e.visual.face_colors = G.COL_BLACK
        trimesh.Scene([b, f, e]).export(f"bloki_{name}.glb")

    print("\nLISTO. Cuerpos:", ", ".join(n for n, _ in made))
    dims = made[0][1].bounds
    d = dims[1] - dims[0]
    print(f"Dim cuerpo (mm): {d[0]:.1f} x {d[1]:.1f} x {d[2]:.1f}  (base plana {G.BASE_CUT} mm)")


if __name__ == "__main__":
    main()
