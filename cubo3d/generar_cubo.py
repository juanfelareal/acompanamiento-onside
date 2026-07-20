#!/usr/bin/env python3
"""
Genera un personaje 3D tipo cubo redondeado (como el de la foto de referencia),
SIN paticas, MULTICOLOR y en 3 piezas registradas (misma posicion) para
impresion 3D a color:

  1. cuerpo_amarillo.stl -> el cubo (amarillo)
  2. cara_crema.stl      -> el panel de la carita + la naricita, al ras (crema)
  3. ojos_negro.stl      -> los dos ojos, EN RELIEVE (negro)

Las 3 piezas encajan como un rompecabezas (no se solapan). En tu slicer las
cargas juntas y le asignas un filamento a cada una; o las imprimes por separado
y se ensamblan.

Tambien exporta:
  - cubo_personaje.glb  -> modelo a color para previsualizar/compartir
  - cubo_personaje.3mf  -> proyecto multicolor (si el exportador esta disponible)

Metodo: funciones de distancia con signo (SDF) + marching cubes.

Uso:
  python3 generar_cubo.py
"""

import zipfile
import numpy as np
from skimage import measure
import trimesh

# ----------------------------------------------------------------------------
# PARAMETROS (en milimetros)
# ----------------------------------------------------------------------------
# ESCALA GLOBAL: el diseno de referencia da un Bloki de 56 mm de alto. Se
# escala todo proporcionalmente para que la ALTURA final sea TARGET_H.
# El tag NFC y el orificio del cordon NO se escalan (son piezas/funciones reales).
TARGET_H = 38.0            # altura final del Bloki (mm) - minimo para el tag NFC
S = TARGET_H / 56.0        # factor de escala proporcional

# Cuerpo (cubo redondeado)
W = 60.0 * S   # ancho  (X)
H = 56.0 * S   # alto   (Y) = TARGET_H
# Fondo (Z): al imprimir DE PIE, el tag NFC va ACOSTADO en la cabeza y necesita
# ~26 mm libres en la profundidad -> el fondo lo define el tag (no se escala).
D = 50.0 * S   # fondo  (Z) ~34 mm  -> la cara mira hacia +Z
R = 13.0 * S   # redondeo de esquinas/aristas (pillowy, como el referente)
# Redondeo de las TAPAS (frente/atras). Al imprimir DE PIE (cara al frente) el
# frente sale liso aunque sea pillowy, asi que se deja = R (sin achatar).
# Se puede achatar la coronilla (RZ del +Y) si el escalonado de arriba molesta.
RZ_FRONT = 13.0 * S
RZ_BACK = 13.0 * S

# Panel de la cara (crema), embutido en la cara frontal
FACE_W = 41.8 * S
FACE_H = 23.1 * S
FACE_R = 6.6 * S
FACE_CY = 4.5 * S    # desplazamiento vertical del centro del panel (+ = arriba)
PANEL_T = 2.8        # grosor del panel (mm) - mas grueso: aloja el encaje de ojos
# Cara PLANA (FACE_BULGE=0): una superficie plana sale lisa en FDM. Un abombado
# suave produce anillos de capas horribles, por eso se deja plana.
FACE_BULGE = 0.0     # 0 = plana (lisa). >0 abomba pero sale con anillos de capas.
# La cara queda un poco HUNDIDA respecto al cuerpo (sutil), no al ras ni saliente.
FACE_RECESS = 0.6    # mm que se hunde la cara bajo la superficie del cuerpo
# Borde limpio: por encima de la cara el rebaje es un poco mas ancho (un reveal
# uniforme) -> la cara centrada deja un marco parejo, sin "trocito" desigual.
FACE_OFFSET = 0.5    # mm de reveal (marco visible) alrededor de la cara hundida

# La carita encaja a presion en el rebaje del cuerpo (centrada por el ajuste).
FIT_CLEAR = 0.06   # holgura por lado carita<->rebaje (apretado, sujeta sin pegar)

# OJOS: encajan DESDE ATRAS de la carita, con TOPE y CLIC. Cada ojo es tipo
# remache: cabeza semiesferica visible al frente + vastago + PESTANA trasera
# (mas ancha que el hueco) que hace de tope. El hueco de la carita es escalonado
# (frente estrecho para el vastago + avellanado trasero para la pestana). La
# pestana entra a presion en el avellanado (clic) y el cuerpo la respalda.
EYE_CLEAR = 0.12       # holgura del vastago en el hueco del frente
EYE_FLANGE = 1.0       # cuanto mas ancha es la pestana (radio) que el vastago
EYE_FLANGE_CLEAR = 0.10  # holgura de la pestana en el avellanado (para el clic)

# Ojos y nariz EN RELIEVE
RELIEF = 1.2 * S     # cuanto sobresalen los ojos
EMBED = 1.0 * S      # cuanto se hunden dentro del panel

EYE_DX = 13.0 * S    # separacion horizontal de los ojos
EYE_DY = -0.5 * S    # altura de los ojos respecto al centro
EYE_R = 2.46 * S     # radio del ojo

# Nariz: bolita (esferita) crema que sobresale de la cara
NOSE_DY = -6.0 * S       # altura de la nariz respecto al centro del panel
NOSE_R = 1.6 * S         # radio de la bolita de la nariz
NOSE_PROTRUDE = 1.5 * S  # cuanto sobresale la bolita

# Cavidad INTERNA para el tag NFC, en la CABEZA (parte alta) de Bloki.
# TAMANO REAL (NO se escala): tag de 25 mm de diametro x 1.5 mm de alto.
# IMPRESION DE PIE (cara al frente): el tag va ACOSTADO (disco horizontal, eje Y)
# y la cavidad abre hacia ARRIBA. Cerca del final de la impresion se hace una
# PAUSA, se apoya el tag plano y al reanudar el techo solido lo sella. Queda
# imperceptible y no removible. Se ubica atras (Z-) para no chocar con la carita.
NFC_DIAM = 26.0   # diametro de la cavidad (tag 25 mm + 1 mm holgura)
NFC_CAV_H = 1.7   # ALTO de la cavidad en Y (tag 1.5 mm + 0.2 mm holgura)
NFC_CY = 7.0      # centro en Y (en la cabeza, bajo el redondeo superior)
NFC_CZ = -1.5     # centro en Z (hacia atras, libre de la carita)
NFC_SKIN = 1.2    # techo solido minimo que sella el tag (por encima de la cavidad)

# Orificio para cordon (llavero) que atraviesa una esquina superior.
# El radio NO se escala (debe seguir pasando un cordon); la posicion si.
# Mas SUTIL (radio menor): sigue pasando un cordon fino pero se nota menos.
KR_R = 1.1        # radio del orificio (~2.2 mm) -> mas discreto
KR_A = 9.5 * S    # cercania a la punta de la esquina (escala con la esquina)

# Resolucion de la grilla (mm/voxel). Mas pequeno = superficie mas lisa y mas lento.
# 0.16 -> curvas geometricamente perfectas (sin facetas) para un acabado premium.
VOXEL = 0.16

# Colores (solo para previsualizacion .glb/.3mf)
COL_BODY = [242, 205, 40, 255]     # amarillo
COL_FACE = [250, 235, 205, 255]    # crema
COL_BLACK = [30, 30, 30, 255]      # negro

# ----------------------------------------------------------------------------
# SDF helpers
# ----------------------------------------------------------------------------
def sdf_round_box(P, half, r):
    q = np.abs(P) - np.asarray(half)
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=-1)
    inside = np.minimum(np.max(q, axis=-1), 0.0)
    return outside + inside - r


def sdf_round_box_aniso(X, Y, Z, hx, hy, hz, rv, rz):
    """Caja con esquinas VERTICALES de radio rv y redondeo de las TAPAS (Z) rz.
    La silueta frontal (XY) es un rect redondeado de radio rv y NO depende de rz;
    rz solo controla que tan 'pillowy' es la transicion de la cara frontal/trasera
    hacia las paredes. rz menor -> tapa mas plana -> menos escalonado al imprimir.
    Con rz = rv se reduce a una caja redondeada isotropica de radio rv.
    """
    d2 = sdf_round_rect_2d(X, Y, hx - rz, hy - rz, rv - rz)
    dz = np.abs(Z) - (hz - rz)
    outside = np.hypot(np.maximum(d2, 0.0), np.maximum(dz, 0.0))
    inside = np.minimum(np.maximum(d2, dz), 0.0)
    return outside + inside - rz


def sdf_round_rect_2d(px, py, hx, hy, r):
    """SDF 2D de rectangulo redondeado en XY (footprint del panel)."""
    qx = np.abs(px) - hx
    qy = np.abs(py) - hy
    outside = np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0))
    inside = np.minimum(np.maximum(qx, qy), 0.0)
    return outside + inside - r


def z_slab(Z, z0, z1):
    """SDF de la loza z0<=z<=z1 (negativo dentro)."""
    zc = 0.5 * (z0 + z1)
    hz = 0.5 * (z1 - z0)
    return np.abs(Z - zc) - hz


def op_union(a, b):
    return np.minimum(a, b)


def op_subtract(a, b):
    return np.maximum(a, -b)


def op_intersect(a, b):
    return np.maximum(a, b)


def cylinder_field(X, Y, Z, cx, cy, r, z0, z1):
    """Cilindro (disco) con eje Z entre z0 y z1."""
    radial = np.hypot(X - cx, Y - cy) - r
    return op_intersect(radial, z_slab(Z, z0, z1))


def cylinder_axis_field(X, Y, Z, A, u, r):
    """Cilindro infinito de radio r con eje que pasa por A en direccion u (unitaria)."""
    px, py, pz = X - A[0], Y - A[1], Z - A[2]
    dot = px * u[0] + py * u[1] + pz * u[2]
    ex, ey, ez = px - dot * u[0], py - dot * u[1], pz - dot * u[2]
    return np.sqrt(ex * ex + ey * ey + ez * ez) - r


def sphere_field(X, Y, Z, C, r):
    return np.sqrt((X - C[0])**2 + (Y - C[1])**2 + (Z - C[2])**2) - r


def export_3mf_ams(parts, path):
    """Escribe un .3mf multicolor listo para AMS (Bambu Studio).

    parts: lista de (mesh, nombre, hex 'RRGGBB'). Se arma UN objeto con varias
    PARTES (una por color) usando el formato de Bambu (Metadata/model_settings).
    Asi Bambu no fusiona nada: ves un objeto con 3 partes y le asignas un
    filamento (AMS) a cada parte.
    """
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '</Types>')
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        '</Relationships>')

    # 3dmodel.model: cada parte es un objeto-mesh; un objeto "ensamblaje" los
    # agrupa como componentes -> Bambu lo abre como 1 objeto con varias partes.
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
           '<resources>', '<basematerials id="1">']
    for _, name, hexc in parts:
        out.append(f'<base name="{name}" displaycolor="#{hexc.upper()}FF"/>')
    out.append('</basematerials>')

    ids = []
    oid = 2
    for i, (mesh, name, hexc) in enumerate(parts):
        V, F = mesh.vertices, mesh.faces
        vtx = "".join("<vertex x=\"%.4f\" y=\"%.4f\" z=\"%.4f\"/>" % (x, y, z)
                      for x, y, z in V)
        tri = "".join("<triangle v1=\"%d\" v2=\"%d\" v3=\"%d\"/>" % (a, b, c)
                      for a, b, c in F)
        out.append(f'<object id="{oid}" type="model" pid="1" pindex="{i}">'
                   f'<mesh><vertices>{vtx}</vertices>'
                   f'<triangles>{tri}</triangles></mesh></object>')
        ids.append(oid)
        oid += 1
    assembly_id = oid
    out.append(f'<object id="{assembly_id}" type="model"><components>')
    for j in ids:
        out.append(f'<component objectid="{j}"/>')
    out.append('</components></object>')
    out.append('</resources>')
    out.append(f'<build><item objectid="{assembly_id}"/></build>')
    out.append('</model>')
    model = "".join(out)

    # Metadata de Bambu: asigna un filamento (extruder) a cada parte y marca el
    # objeto como ensamblaje. Esto es lo que hace que Bambu muestre las 3 partes
    # con su color/filamento por separado (sin fusionar).
    identity = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"
    ms = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>',
          f'<object id="{assembly_id}">',
          '<metadata key="name" value="Bloki"/>',
          '<metadata key="extruder" value="1"/>']
    for k, (mesh, name, hexc) in enumerate(parts):
        ms.append(f'<part id="{ids[k]}" subtype="normal_part">'
                  f'<metadata key="name" value="{name}"/>'
                  f'<metadata key="matrix" value="{identity}"/>'
                  f'<metadata key="extruder" value="{k + 1}"/>'
                  '<mesh_stat edges_fixed="0" degenerate_facets="0" '
                  'facets_removed="0" facets_reversed="0" backwards_edges="0"/>'
                  '</part>')
    ms.append('</object></config>')
    model_settings = "".join(ms)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", model_settings)


# ----------------------------------------------------------------------------
# Malla desde un campo SDF
# ----------------------------------------------------------------------------
def mesh_from_field(field, origin, spacing, name, min_vol_mm3=1.0):
    verts, faces, _, _ = measure.marching_cubes(field, level=0.0, spacing=spacing)
    verts = verts + np.asarray(origin)
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    # 1) limpieza -> malla cerrada
    m.update_faces(m.unique_faces())
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    # 2) descartar componentes minusculos (artefactos de mallado) conservando
    #    piezas reales (p.ej. los dos ojos son 2 componentes validos)
    comps = m.split(only_watertight=False)
    if len(comps) > 1:
        keep = [c for c in comps if abs(c.volume) >= min_vol_mm3]
        if keep:
            m = trimesh.util.concatenate(keep)
    print(f"  [{name}] caras={len(m.faces):,}  piezas={m.body_count}  "
          f"watertight={m.is_watertight}  vol={m.volume/1000:.2f} cm3")
    return m


def build_grid():
    # float32 -> mitad de memoria (a 0.16 mm la precision sobra) para no agotar RAM
    pad = R + 5.0
    xs = np.arange(-W / 2 - pad, W / 2 + pad + VOXEL, VOXEL, dtype=np.float32)
    ys = np.arange(-H / 2 - pad, H / 2 + pad + VOXEL, VOXEL, dtype=np.float32)
    # dejar espacio al frente para el relieve de ojos/nariz
    zs = np.arange(-D / 2 - pad, D / 2 + RELIEF + pad + VOXEL, VOXEL, dtype=np.float32)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    origin = (float(xs[0]), float(ys[0]), float(zs[0]))
    spacing = (VOXEL, VOXEL, VOXEL)
    return X, Y, Z, origin, spacing


def main():
    print("Construyendo grilla...")
    X, Y, Z, origin, spacing = build_grid()

    front_z = D / 2.0                       # superficie frontal del cuerpo
    face_top = front_z - FACE_RECESS        # cara HUNDIDA (queda bajo el cuerpo)
    pocket_floor = face_top - PANEL_T       # fondo del rebaje (respaldo de la carita)
    hx = FACE_W / 2 - FACE_R
    hy = FACE_H / 2 - FACE_R
    rr = sdf_round_rect_2d(X, Y - FACE_CY, hx, hy, FACE_R)  # footprint del panel

    # --- Ojos tipo REMACHE: encajan DESDE ATRAS con TOPE y CLIC ---
    # Cada ojo (negro) tiene 3 partes en un solo eje Z:
    #   1) CABEZA semiesferica al frente (visible, sobresale como la nariz)
    #   2) CUELLO fino (radio EYE_R) que atraviesa el hueco de la carita
    #   3) PESTANA trasera mas ancha que el hueco -> hace de TOPE
    # El hueco de la carita es ESCALONADO: estrecho al frente (para el cuello) y
    # avellanado ancho atras (para la pestana). Se mete el ojo por DETRAS: la
    # cabeza+cuello asoman al frente y la pestana entra a presion en el avellanado
    # (CLIC). La pestana no pasa el escalon (TOPE) y, al montar la carita en el
    # cuerpo, el piso del rebaje respalda la pestana -> el ojo NO se puede sacar.
    FLANGE_T = PANEL_T * 0.45                  # grosor de la pestana trasera
    eye_step_z = pocket_floor + FLANGE_T       # escalon (techo del avellanado)
    eye_pos = [(-EYE_DX, FACE_CY + EYE_DY), (EYE_DX, FACE_CY + EYE_DY)]

    black = None
    eye_holes = None
    for (ex, ey) in eye_pos:
        # 1) pieza del ojo (negra): pestana + cuello + cabeza
        flange = cylinder_field(X, Y, Z, ex, ey, EYE_R + EYE_FLANGE,
                                pocket_floor, eye_step_z)
        neck = cylinder_field(X, Y, Z, ex, ey, EYE_R, eye_step_z, face_top)
        head = op_intersect(sphere_field(X, Y, Z, [ex, ey, face_top], EYE_R),
                            (face_top - Z))    # semiesfera z >= face_top
        eye = op_union(op_union(flange, neck), head)
        black = eye if black is None else op_union(black, eye)
        # 2) hueco escalonado en la carita: cuello estrecho + avellanado ancho
        hole_neck = cylinder_field(X, Y, Z, ex, ey, EYE_R + EYE_CLEAR,
                                   eye_step_z, face_top + 1.0)
        hole_bore = cylinder_field(X, Y, Z, ex, ey,
                                   EYE_R + EYE_FLANGE + EYE_FLANGE_CLEAR,
                                   pocket_floor - 1.0, eye_step_z)
        hole = op_union(hole_neck, hole_bore)
        eye_holes = hole if eye_holes is None else op_union(eye_holes, hole)

    # --- Nariz: bolita (semiesfera) crema que sobresale de la cara plana ---
    ny = FACE_CY + NOSE_DY
    nose_cz = face_top + NOSE_PROTRUDE - NOSE_R    # centro de la esfera de la nariz
    nose_bump = sphere_field(X, Y, Z, [0.0, ny, nose_cz], NOSE_R)

    print("Extrayendo mallas...")
    # --- Cuerpo amarillo (1 color): cubo redondeado menos el rebaje ---
    # El rebaje es un poco MAS GRANDE que la carita (FIT_CLEAR por lado) para
    # que la carita entre a presion. rr - FIT_CLEAR agranda el footprint.
    # Cuerpo redondeado pillowy. (RZ_FRONT/RZ_BACK permiten achatar tapas si se
    # quisiera; con ambos = R esto equivale a la caja redondeada isotropica, que
    # ademas usa mucha menos memoria a alta resolucion.)
    if RZ_FRONT == R and RZ_BACK == R:
        body = sdf_round_box(np.stack([X, Y, Z], axis=-1),
                             (W/2 - R, H/2 - R, D/2 - R), R)
    else:
        body = np.where(Z >= 0,
                        sdf_round_box_aniso(X, Y, Z, W/2, H/2, D/2, R, RZ_FRONT),
                        sdf_round_box_aniso(X, Y, Z, W/2, H/2, D/2, R, RZ_BACK))
    # Rebaje ESCALONADO (sistema de encaje de la carita):
    #  - parte PROFUNDA (pocket_floor..face_top): ajustada al panel (FIT_CLEAR por
    #    lado) -> las paredes centran la carita sola, sin juego lateral.
    #  - BOCA en el rebaje (face_top..frente): un poco mas ancha (FACE_OFFSET) ->
    #    deja un marco/reveal uniforme alrededor de la cara hundida, para que el
    #    borde se vea parejo y no quede un "trocito" desigual.
    pocket_deep = op_intersect(rr - FIT_CLEAR, z_slab(Z, pocket_floor, face_top))
    pocket_mouth = op_intersect(rr - (FIT_CLEAR + FACE_OFFSET), (face_top - Z))
    pocket = op_union(pocket_deep, pocket_mouth)
    body = op_subtract(body, pocket)

    # Cavidad INTERNA para el tag NFC, en la CABEZA. Disco de eje Y (tag acostado)
    # centrado en (X=0, Z=NFC_CZ) hacia atras para no chocar con la carita. Es un
    # hueco cerrado (el cubo se ve solido por fuera). Al imprimir DE PIE, abre
    # hacia arriba: en la pausa (cerca del final) se apoya el tag plano y el techo
    # solido de la cabeza lo sella. NFC_CY se mantiene bajo el redondeo superior
    # para que la seccion horizontal sea plena y quepa el disco de 26 mm.
    nfc_radial = np.hypot(X - 0.0, Z - NFC_CZ) - NFC_DIAM / 2.0
    nfc_y0 = NFC_CY - 0.5 * NFC_CAV_H    # piso de la cavidad (donde se apoya el tag)
    nfc_y1 = NFC_CY + 0.5 * NFC_CAV_H    # techo de la cavidad (abre hacia arriba)
    nfc_yslab = np.abs(Y - NFC_CY) - 0.5 * NFC_CAV_H
    nfc = op_intersect(nfc_radial, nfc_yslab)
    body = op_subtract(body, nfc)

    # Orificio para cuerdita: atraviesa la esquina superior IZQUIERDA-TRASERA
    # (la "espalda" de Bloki, no el lado de la cara). Ademas, al imprimir con la
    # cara hacia arriba, esta esquina queda abajo -> mejor acabado (sin estrias).
    Cc = np.array([-(W / 2 - R), H / 2 - R, -(D / 2 - R)])  # esquina -X,+Y,-Z
    nvec = np.array([-1.0, 1.0, -1.0]) / np.sqrt(3)         # diagonal hacia la punta
    A = Cc + KR_A * nvec                                    # eje cerca de la punta
    u = np.array([1.0, 1.0, 0.0]) / np.sqrt(2)              # direccion del orificio
    kr = cylinder_axis_field(X, Y, Z, A, u, KR_R)
    kr = op_intersect(kr, sphere_field(X, Y, Z, Cc, R + 3))  # confinar a la esquina
    body = op_subtract(body, kr)

    m_body = mesh_from_field(body, origin, spacing, "cuerpo")
    del body, pocket, nfc, kr

    # --- Carita crema (1 color): placa PLANA con nariz y HUECOS para los ojos ---
    panel = op_intersect(rr, z_slab(Z, pocket_floor, face_top))  # placa plana
    panel = op_union(panel, nose_bump)              # anade la naricita crema
    panel = op_subtract(panel, eye_holes)           # huecos donde encajan los ojos
    m_face = mesh_from_field(panel, origin, spacing, "cara")
    del panel, nose_bump, eye_holes

    # --- Ojos (negro, 1 color): 2 piezas que encajan a presion en la carita ---
    m_black = mesh_from_field(black, origin, spacing, "ojos")
    del black

    # ---- DISENO EN 3 PIEZAS, CADA UNA DE 1 SOLO COLOR ----
    # Ningun print cambia de color -> CERO purga, maxima eficiencia. Se imprime
    # cada STL con su filamento y se ensambla a presion (sin pegamento):
    #   1) cuerpo_amarillo.stl  (amarillo)  - lleva el NFC sellado (pausa)
    #   2) cara_crema.stl       (crema)     - encaja en el rebaje del cuerpo
    #   3) ojos_negro.stl       (negro, x2) - encajan en los huecos de la carita
    m_body.export("cuerpo_amarillo.stl")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    print("\nSTLs (cada uno 1 color): cuerpo_amarillo, cara_crema, ojos_negro")

    # Escena a color para previsualizar / compartir (todo ensamblado)
    m_body.visual.face_colors = COL_BODY
    m_face.visual.face_colors = COL_FACE
    m_black.visual.face_colors = COL_BLACK
    trimesh.Scene([m_body, m_face, m_black]).export("cubo_personaje.glb")
    print("Color: cubo_personaje.glb")

    b = (m_body + m_face + m_black).bounds
    dims = b[1] - b[0]
    print(f"\nDimensiones totales (mm): {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f}")


if __name__ == "__main__":
    main()
