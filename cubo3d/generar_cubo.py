#!/usr/bin/env python3
"""
Genera un personaje 3D tipo cubo redondeado (como el de la foto de referencia),
SIN paticas, MULTICOLOR y en 3 piezas registradas (misma posicion) para
impresion 3D a color:

  1. cuerpo_amarillo.stl  -> el cubo (amarillo)
  2. cara_crema.stl       -> el panel de la carita, al ras del cuerpo (crema)
  3. ojos_nariz_negro.stl -> dos ojos + nariz, EN RELIEVE (negro)

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
D = 54.0     # fondo  (Z)  -> la cara mira hacia +Z
R = 13.0     # redondeo de esquinas/aristas

# Panel de la cara (crema), al ras de la cara frontal (embutido en un rebaje)
FACE_W = 32.0     # ancho del panel
FACE_H = 24.0     # alto del panel
FACE_R = 7.0      # redondeo de las esquinas del panel
FACE_CY = 2.0     # desplazamiento vertical del centro del panel (+ = arriba)
PANEL_T = 1.8     # grosor del panel = profundidad del rebaje (queda al ras)

# Ojos y nariz (negros) EN RELIEVE (sobresalen de la cara)
RELIEF = 1.2      # cuanto sobresalen respecto a la cara frontal
EMBED = 1.0       # cuanto se hunden dentro del panel crema (para que peguen)

EYE_DX = 9.5      # separacion horizontal de los ojos
EYE_DY = 3.5      # altura de los ojos respecto al centro del panel
EYE_R = 3.4       # radio del ojo

NOSE_DY = -5.5    # altura de la nariz respecto al centro del panel
NOSE_R = 1.4      # radio de la nariz

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


# ----------------------------------------------------------------------------
# Malla desde un campo SDF
# ----------------------------------------------------------------------------
def mesh_from_field(field, origin, spacing, name):
    verts, faces, _, _ = measure.marching_cubes(field, level=0.0, spacing=spacing)
    verts = verts + np.asarray(origin)
    m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    m.update_faces(m.unique_faces())
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    print(f"  [{name}] caras={len(m.faces):,}  watertight={m.is_watertight}  "
          f"vol={m.volume/1000:.2f} cm3")
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

    # --- Solido negro (ojos + nariz), en relieve ---
    eye_l = cylinder_field(X, Y, Z, -EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    eye_r = cylinder_field(X, Y, Z,  EYE_DX, FACE_CY + EYE_DY, EYE_R, black_back, black_front)
    nose = cylinder_field(X, Y, Z, 0.0, FACE_CY + NOSE_DY, NOSE_R, black_back, black_front)
    black = op_union(op_union(eye_l, eye_r), nose)

    print("Extrayendo mallas...")
    # --- Cuerpo amarillo: cubo redondeado menos el rebaje del panel ---
    body = sdf_round_box(np.stack([X, Y, Z], axis=-1), (W/2 - R, H/2 - R, D/2 - R), R)
    pocket = op_intersect(rr, (pocket_floor - Z))   # footprint del panel, z>pocket_floor
    body = op_subtract(body, pocket)
    m_body = mesh_from_field(body, origin, spacing, "cuerpo")
    del body, pocket

    # --- Panel crema: loza que rellena el rebaje, menos los huecos negros ---
    panel = op_intersect(rr, z_slab(Z, pocket_floor, front_z))
    panel = op_subtract(panel, black)               # deja el hueco para el negro
    m_face = mesh_from_field(panel, origin, spacing, "cara")
    del panel

    # --- Negro: ojos + nariz en relieve ---
    m_black = mesh_from_field(black, origin, spacing, "ojos_nariz")
    del black

    # Exportar STLs (una pieza por color, registradas)
    m_body.export("cuerpo_amarillo.stl")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_nariz_negro.stl")
    print("\nSTLs: cuerpo_amarillo.stl, cara_crema.stl, ojos_nariz_negro.stl")

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
