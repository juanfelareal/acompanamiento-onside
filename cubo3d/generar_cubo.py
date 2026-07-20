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
TARGET_H = 45.0            # altura final del Bloki (mm)
S = TARGET_H / 56.0        # factor de escala proporcional

# Cuerpo (cubo redondeado)
W = 60.0 * S   # ancho  (X)
H = 56.0 * S   # alto   (Y) = TARGET_H
D = 46.0 * S   # fondo  (Z)  -> la cara mira hacia +Z
R = 13.0 * S   # redondeo de esquinas/aristas

# Panel de la cara (crema), embutido en la cara frontal
FACE_W = 41.8 * S
FACE_H = 23.1 * S
FACE_R = 6.6 * S
FACE_CY = 4.5 * S    # desplazamiento vertical del centro del panel (+ = arriba)
PANEL_T = 1.8 * S    # grosor del panel = profundidad del rebaje
FACE_BULGE = 1.5 * S # abombamiento del panel (carita con redondez)

# La carita es una PIEZA APARTE que encaja a presion en el rebaje del cuerpo.
# FIT_CLEAR = holgura (por lado) entre la carita y el rebaje. NO se escala
# (es tolerancia de impresion). Subelo si queda muy apretada, bajalo si floja.
FIT_CLEAR = 0.12

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

# Cavidad INTERNA para el tag NFC, DETRAS de la carita (lado +Z).
# TAMANO REAL (NO se escala): tag de 25 mm de diametro x 1.5 mm de alto.
# Al imprimir con la cara hacia arriba, se abre hacia arriba; en la pausa se
# coloca el tag y la cara lo sella. Queda imperceptible y no removible.
NFC_DIAM = 26.0   # diametro de la cavidad (tag 25 mm + 1 mm holgura)
NFC_SKIN = 1.2    # pared solida que sella el tag (entre cavidad y fondo del panel)
NFC_CAV_H = 1.7   # alto de la cavidad (tag 1.5 mm + 0.2 mm holgura)

# Orificio para cordon (llavero) que atraviesa una esquina superior.
# El radio NO se escala (debe seguir pasando un cordon); la posicion si.
KR_R = 1.5        # radio del orificio (~3 mm) -> pasa una cuerdita fina
KR_A = 9.5 * S    # cercania a la punta de la esquina (escala con la esquina)

# Resolucion de la grilla (mm/voxel). Mas pequeno = superficie mas lisa y mas lento.
VOXEL = 0.30

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
    pad = R + 5.0
    xs = np.arange(-W / 2 - pad, W / 2 + pad + VOXEL, VOXEL)
    ys = np.arange(-H / 2 - pad, H / 2 + pad + VOXEL, VOXEL)
    # dejar espacio al frente para el relieve de ojos/nariz
    zs = np.arange(-D / 2 - pad, D / 2 + RELIEF + pad + VOXEL, VOXEL)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    origin = (xs[0], ys[0], zs[0])
    spacing = (VOXEL, VOXEL, VOXEL)
    return X, Y, Z, origin, spacing


def main():
    print("Construyendo grilla...")
    X, Y, Z, origin, spacing = build_grid()

    front_z = D / 2.0                 # cara frontal (plana) en z = 27
    pocket_floor = front_z - PANEL_T  # fondo del rebaje del panel
    hx = FACE_W / 2 - FACE_R
    hy = FACE_H / 2 - FACE_R
    rr = sdf_round_rect_2d(X, Y - FACE_CY, hx, hy, FACE_R)  # footprint del panel

    # Dome (abombamiento) del panel: superficie esferica de radio grande que
    # hace que el centro de la cara sobresalga FACE_BULGE y los bordes queden
    # casi al ras -> la carita se ve redondeada, no plana.
    dome_R = (FACE_W / 2.0) ** 2 / (2.0 * FACE_BULGE) if FACE_BULGE > 1e-6 else 1e9
    dome_zc = front_z + FACE_BULGE - dome_R
    face_top = front_z + FACE_BULGE   # punto mas alto de la cara

    black_back = front_z - EMBED         # los ojos se hunden hasta aca
    black_front = face_top + RELIEF      # y sobresalen por encima del dome

    # --- Solido negro: SOLO los ojos, en relieve ---
    eye_l = cylinder_field(X, Y, Z, -EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    eye_r = cylinder_field(X, Y, Z,  EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    black = op_union(eye_l, eye_r)

    # --- Nariz: bolita (esferita) crema que sobresale de la cara curva ---
    ny = FACE_CY + NOSE_DY
    r_nose = abs(NOSE_DY)                          # distancia al centro del panel
    dome_z_nose = dome_zc + np.sqrt(dome_R**2 - r_nose**2)  # altura del dome ahi
    nose_cz = dome_z_nose + NOSE_PROTRUDE - NOSE_R # centro de la esfera
    nose_bump = sphere_field(X, Y, Z, [0.0, ny, nose_cz], NOSE_R)

    print("Extrayendo mallas...")
    # --- Cuerpo amarillo (1 color): cubo redondeado menos el rebaje ---
    # El rebaje es un poco MAS GRANDE que la carita (FIT_CLEAR por lado) para
    # que la carita entre a presion. rr - FIT_CLEAR agranda el footprint.
    body = sdf_round_box(np.stack([X, Y, Z], axis=-1), (W/2 - R, H/2 - R, D/2 - R), R)
    pocket = op_intersect(rr - FIT_CLEAR, (pocket_floor - Z))
    body = op_subtract(body, pocket)

    # Cavidad INTERNA para el tag NFC, DETRAS del panel de la cara (lado +Z).
    # Disco de eje Z, centrado tras la carita. Es un hueco cerrado (el cubo se
    # ve solido por fuera). Al imprimir con la cara hacia arriba, se abre hacia
    # arriba y el tag se coloca en la pausa; luego la cara lo sella.
    nfc_radial = np.hypot(X - 0.0, Y - FACE_CY) - NFC_DIAM / 2.0
    nfc_z1 = pocket_floor - NFC_SKIN     # techo de la cavidad (hacia la cara)
    nfc_z0 = nfc_z1 - NFC_CAV_H          # fondo de la cavidad (hacia atras)
    nfc_zc = 0.5 * (nfc_z0 + nfc_z1)
    nfc_zslab = np.abs(Z - nfc_zc) - 0.5 * NFC_CAV_H
    nfc = op_intersect(nfc_radial, nfc_zslab)
    body = op_subtract(body, nfc)

    # Orificio para cuerdita: atraviesa la esquina superior frontal-derecha.
    # Cilindro diagonal cerca de la punta, confinado a la esquina para que
    # entre y salga limpio por la superficie redondeada (sin canales largos).
    Cc = np.array([W / 2 - R, H / 2 - R, D / 2 - R])   # centro de la esquina
    nvec = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)      # diagonal hacia la punta
    A = Cc + KR_A * nvec                               # eje cerca de la punta
    u = np.array([1.0, -1.0, 0.0]) / np.sqrt(2)        # direccion del orificio
    kr = cylinder_axis_field(X, Y, Z, A, u, KR_R)
    kr = op_intersect(kr, sphere_field(X, Y, Z, Cc, R + 3))  # confinar a la esquina
    body = op_subtract(body, kr)

    m_body = mesh_from_field(body, origin, spacing, "cuerpo")
    del body, pocket, nfc, kr

    # --- Panel crema: rellena el rebaje y se abomba arriba (dome), + nariz, - ojos ---
    panel = op_intersect(rr, (pocket_floor - Z))    # footprint + por encima del piso
    dome = sphere_field(X, Y, Z, [0.0, FACE_CY, dome_zc], dome_R)
    panel = op_intersect(panel, dome)               # tapa abombada (redondez)
    panel = op_union(panel, nose_bump)              # anade la naricita crema
    panel = op_subtract(panel, black)               # deja el hueco para los ojos
    m_face = mesh_from_field(panel, origin, spacing, "cara")
    del panel, nose_bump, dome

    # --- Negro: los ojos en relieve ---
    m_black = mesh_from_field(black, origin, spacing, "ojos")
    del black

    # Exportar STLs (registradas)
    m_body.export("cuerpo_amarillo.stl")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    print("\nSTLs: cuerpo_amarillo.stl, cara_crema.stl, ojos_negro.stl")

    # ---- DISENO EN 2 PIEZAS (impresion eficiente) ----
    # 1) CUERPO: 1 solo color (amarillo) -> 0 cambios de color, sin torre de
    #    purga. Lleva el NFC sellado dentro. Se imprime desde su STL.
    # 2) CARITA: pieza aparte (crema + ojos negros) que encaja a presion en el
    #    rebaje del cuerpo. Solo esta pieza (pequena) usa el AMS.
    export_3mf_ams([
        (m_face, "Crema (cara)", "FAEBCD"),
        (m_black, "Negro (ojos)", "1E1E1E"),
    ], "Bloki_carita_AMS.3mf")
    print("AMS: Bloki_carita_AMS.3mf (carita: crema + ojos)")

    # Escena a color para previsualizar / compartir (cuerpo + carita encajada)
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
