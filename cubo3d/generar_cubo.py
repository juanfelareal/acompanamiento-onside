#!/usr/bin/env python3
"""
Genera un personaje 3D tipo cubo redondeado (como el de la foto de referencia)
con carita tallada (panel hundido + dos ojos + naricita) y SIN paticas.

Metodo: campo de distancia con signo (SDF) evaluado en una grilla 3D y
extraccion de la malla con marching cubes. Produce una superficie suave,
cerrada (watertight) y lista para impresion 3D.

Salida:
  - cubo_personaje.stl  (malla para imprimir)

Uso:
  python3 generar_cubo.py
"""

import numpy as np
from skimage import measure
import trimesh

# ----------------------------------------------------------------------------
# PARAMETROS DEL PERSONAJE (en milimetros)
# ----------------------------------------------------------------------------
# Cuerpo (cubo redondeado)
W = 60.0     # ancho  (eje X)
H = 56.0     # alto   (eje Y)
D = 54.0     # fondo  (eje Z)
R = 13.0     # radio de redondeo de esquinas/aristas (cuanto mas grande, mas "blandito")

# Panel de la cara: la cara es PLANA (al ras), como en la foto. El panel se
# marca solo con un grabado muy superficial de su contorno, que sirve de guia
# para pintarlo de otro color (crema). NO es un hundido.
FACE_W = 40.0            # ancho del panel
FACE_H = 27.0            # alto del panel
FACE_R = 8.0             # redondeo de las esquinas del panel
FACE_CY = 3.0            # desplazamiento vertical del centro del panel (+ = arriba)
FACE_OUTLINE_DEPTH = 0.7 # profundidad del grabado del contorno (mm)
FACE_OUTLINE_WIDTH = 1.4 # ancho de la linea grabada del contorno (mm)

# Ojos (discos grabados muy superficiales, al ras, para pintar de negro)
EYE_DX = 9.5       # separacion horizontal desde el centro
EYE_DY = 3.5       # altura de los ojos respecto al centro del panel
EYE_R = 3.4        # radio del ojo
EYE_DEPTH = 1.0    # profundidad del grabado

# Nariz (disco grabado pequenito)
NOSE_DY = -5.5     # altura de la nariz respecto al centro del panel
NOSE_R = 1.5       # radio
NOSE_DEPTH = 0.7   # profundidad

# Resolucion de la grilla (mm por voxel). Mas pequeno = mas detalle y mas lento.
VOXEL = 0.5

OUT_STL = "cubo_personaje.stl"

# ----------------------------------------------------------------------------
# Funciones de distancia (SDF)
# ----------------------------------------------------------------------------
def sdf_round_box(p, half, r):
    """SDF de una caja redondeada. p:(...,3), half:(3,) semiejes del nucleo, r:radio."""
    q = np.abs(p) - np.asarray(half)
    q_pos = np.maximum(q, 0.0)
    outside = np.linalg.norm(q_pos, axis=-1)
    inside = np.minimum(np.max(q, axis=-1), 0.0)
    return outside + inside - r


def sdf_sphere(p, center, r):
    return np.linalg.norm(p - np.asarray(center), axis=-1) - r


def sdf_round_rect_2d(px, py, hx, hy, r):
    """SDF 2D de un rectangulo redondeado en el plano XY."""
    qx = np.abs(px) - hx
    qy = np.abs(py) - hy
    outside = np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0))
    inside = np.minimum(np.maximum(qx, qy), 0.0)
    return outside + inside - r


def op_subtract(a, b):
    """Resta booleana: a menos b."""
    return np.maximum(a, -b)


def carve_disc(d, X, Y, Z, cx, cy, r, depth, front_z):
    """Talla un disco de fondo plano (grabado superficial) desde la cara frontal."""
    radial = np.hypot(X - cx, Y - cy) - r
    slab = (front_z - depth) - Z            # negativo donde z > front_z - depth
    disc = np.maximum(radial, slab)         # solido del disco cerca del frente
    return op_subtract(d, disc)


# ----------------------------------------------------------------------------
# Construccion del campo
# ----------------------------------------------------------------------------
def build_field():
    pad = R + 4.0
    xs = np.arange(-W / 2 - pad, W / 2 + pad + VOXEL, VOXEL)
    ys = np.arange(-H / 2 - pad, H / 2 + pad + VOXEL, VOXEL)
    zs = np.arange(-D / 2 - pad, D / 2 + pad + VOXEL, VOXEL)

    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    P = np.stack([X, Y, Z], axis=-1)

    # Cuerpo: cubo redondeado (la cara frontal queda PLANA / al ras)
    body_half = (W / 2 - R, H / 2 - R, D / 2 - R)
    d = sdf_round_box(P, body_half, R)

    front_z = D / 2  # cara frontal nominal (plana)

    # Contorno del panel: linea grabada muy superficial (guia para pintar).
    # Se graba solo el borde del rectangulo redondeado, no todo el interior,
    # asi la cara sigue plana como en la foto.
    d2 = sdf_round_rect_2d(X, Y - FACE_CY,
                           FACE_W / 2 - FACE_R, FACE_H / 2 - FACE_R, FACE_R)
    border = np.abs(d2) - FACE_OUTLINE_WIDTH / 2.0   # negativo sobre la linea
    slab = (front_z - FACE_OUTLINE_DEPTH) - Z        # negativo cerca del frente
    groove = np.maximum(border, slab)
    d = op_subtract(d, groove)

    # Ojos: discos grabados superficiales (al ras), para pintar de negro
    d = carve_disc(d, X, Y, Z, -EYE_DX, FACE_CY + EYE_DY, EYE_R, EYE_DEPTH, front_z)
    d = carve_disc(d, X, Y, Z,  EYE_DX, FACE_CY + EYE_DY, EYE_R, EYE_DEPTH, front_z)

    # Nariz: disco grabado pequenito
    d = carve_disc(d, X, Y, Z, 0.0, FACE_CY + NOSE_DY, NOSE_R, NOSE_DEPTH, front_z)

    return d, (xs, ys, zs)


def main():
    print("Construyendo campo SDF...")
    field, (xs, ys, zs) = build_field()
    print(f"  Grilla: {field.shape}  ({field.size:,} voxeles)")

    print("Extrayendo malla con marching cubes...")
    spacing = (xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0])
    verts, faces, normals, _ = measure.marching_cubes(field, level=0.0, spacing=spacing)
    # Reubicar al origen real de la grilla
    verts += np.array([xs[0], ys[0], zs[0]])

    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    mesh.update_faces(mesh.unique_faces())
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh)

    # Orientar para impresion: dejar el modelo apoyado en su base (cara -Y hacia abajo -> Z)
    # Rotamos -90 en X para que la "espalda"/base plana quede abajo.
    print("Estadisticas del modelo:")
    print(f"  Vertices: {len(mesh.vertices):,}")
    print(f"  Caras:    {len(mesh.faces):,}")
    print(f"  Watertight (cerrado): {mesh.is_watertight}")
    print(f"  Volumen: {mesh.volume/1000:.1f} cm3")
    b = mesh.bounds
    dims = b[1] - b[0]
    print(f"  Dimensiones (mm): {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f}")

    mesh.export(OUT_STL)
    print(f"\nGuardado: {OUT_STL}")


if __name__ == "__main__":
    main()
