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

import numpy as np
from skimage import measure
import trimesh

# ----------------------------------------------------------------------------
# PARAMETROS (en milimetros)
# ----------------------------------------------------------------------------
# Cuerpo (cubo redondeado)
W = 60.0     # ancho  (X)
H = 56.0     # alto   (Y)
D = 46.0     # fondo  (Z)  -> la cara mira hacia +Z (mas delgado)
R = 13.0     # redondeo de esquinas/aristas

# Panel de la cara (crema), al ras de la cara frontal (embutido en un rebaje)
FACE_W = 38.0     # ancho del panel (mas ancho -> mas rectangular)
FACE_H = 24.0     # alto del panel  (mas bajo  -> menos cuadrado)
FACE_R = 6.0      # redondeo de las esquinas del panel
FACE_CY = 2.0     # desplazamiento vertical del centro del panel (+ = arriba)
PANEL_T = 1.8     # grosor del panel = profundidad del rebaje (queda al ras)

# Ojos y nariz (negros) EN RELIEVE (sobresalen de la cara)
RELIEF = 1.2      # cuanto sobresalen respecto a la cara frontal
EMBED = 1.0       # cuanto se hunden dentro del panel crema (para que peguen)

EYE_DX = 9.5      # separacion horizontal de los ojos
EYE_DY = 2.5      # altura de los ojos respecto al centro del panel
EYE_R = 1.7       # radio del ojo (50% mas pequenos)

# Nariz: bultito EN RELIEVE del MISMO color crema de la cara, muy pequena
NOSE_DY = -4.0    # altura de la nariz respecto al centro del panel
NOSE_R = 0.7      # radio de la nariz (muy pequena)
NOSE_RELIEF = 0.5 # cuanto sobresale la nariz (relieve suave)

# Cavidad INTERNA para el tag NFC, cerca de la base (-Y).
# El cubo queda SOLIDO por fuera (sin orificio): el tag se sella dentro durante
# la impresion (pausa -> se coloca el tag -> se reanuda). Queda imperceptible,
# bloqueado y no removible.
NFC_DIAM = 26.0   # diametro de la cavidad (tag de 25 mm + holgura)
NFC_SKIN = 1.2    # grosor de material solido entre la cavidad y la base
NFC_CAV_H = 1.6   # alto de la cavidad interna (grosor del tag + holgura)

# Orificio para cuerdita (llavero) que atraviesa una esquina superior
KR_R = 1.75       # radio del orificio (~3.5 mm) -> pasa una cuerdita
KR_A = 9.5        # cercania a la punta de la esquina (dist. desde el centro de la esquina)

# Resolucion de la grilla (mm/voxel). Mas pequeno = mas detalle y mas lento.
VOXEL = 0.45

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

    black_back = front_z - EMBED      # los ojos/nariz se hunden hasta aca
    black_front = front_z + RELIEF    # y sobresalen hasta aca

    # --- Solido negro: SOLO los ojos, en relieve ---
    eye_l = cylinder_field(X, Y, Z, -EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    eye_r = cylinder_field(X, Y, Z,  EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    black = op_union(eye_l, eye_r)

    # --- Nariz: bultito crema (mismo color de la cara), muy pequeno ---
    nose_bump = cylinder_field(X, Y, Z, 0.0, FACE_CY + NOSE_DY, NOSE_R,
                               pocket_floor, front_z + NOSE_RELIEF)

    print("Extrayendo mallas...")
    # --- Cuerpo amarillo: cubo redondeado menos el rebaje del panel ---
    body = sdf_round_box(np.stack([X, Y, Z], axis=-1), (W/2 - R, H/2 - R, D/2 - R), R)
    pocket = op_intersect(rr, (pocket_floor - Z))   # footprint del panel, z>pocket_floor
    body = op_subtract(body, pocket)

    # Cavidad INTERNA para el tag NFC, cerca de la base (-Y).
    # Es un hueco cerrado (no toca ninguna cara) -> el cubo se ve solido por
    # fuera. El tag se sella dentro durante la impresion.
    nfc_radial = np.hypot(X, Z) - NFC_DIAM / 2.0
    nfc_y0 = -H / 2 + NFC_SKIN            # techo de la piel solida hacia la base
    nfc_y1 = nfc_y0 + NFC_CAV_H           # techo de la cavidad
    nfc_yc = 0.5 * (nfc_y0 + nfc_y1)
    nfc_yslab = np.abs(Y - nfc_yc) - 0.5 * NFC_CAV_H
    nfc = op_intersect(nfc_radial, nfc_yslab)
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

    # --- Panel crema: loza que rellena el rebaje, + nariz, - huecos de ojos ---
    panel = op_intersect(rr, z_slab(Z, pocket_floor, front_z))
    panel = op_union(panel, nose_bump)              # anade la naricita crema
    panel = op_subtract(panel, black)               # deja el hueco para los ojos
    m_face = mesh_from_field(panel, origin, spacing, "cara")
    del panel, nose_bump

    # --- Negro: los ojos en relieve ---
    m_black = mesh_from_field(black, origin, spacing, "ojos")
    del black

    # Exportar STLs (una pieza por color, registradas)
    m_body.export("cuerpo_amarillo.stl")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    print("\nSTLs: cuerpo_amarillo.stl, cara_crema.stl, ojos_negro.stl")

    # Escena a color para previsualizar / compartir
    m_body.visual.face_colors = COL_BODY
    m_face.visual.face_colors = COL_FACE
    m_black.visual.face_colors = COL_BLACK
    scene = trimesh.Scene([m_body, m_face, m_black])
    scene.export("cubo_personaje.glb")
    print("Color: cubo_personaje.glb")
    try:
        scene.export("cubo_personaje.3mf")
        print("Color: cubo_personaje.3mf")
    except Exception as e:
        print(f"(3mf no exportado: {e})")

    b = (m_body + m_face + m_black).bounds
    dims = b[1] - b[0]
    print(f"\nDimensiones totales (mm): {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f}")


if __name__ == "__main__":
    main()
