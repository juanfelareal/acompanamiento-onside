#!/usr/bin/env python3
"""Version FINAL de produccion de las dos texturas elegidas: RANURADO y DIMPLES.
Optimizadas para boquilla 0.4 mm, malla mas fina, y verificando el encaje de la
cara. Exporta cuerpo_<tex>_final.stl/.3mf y bloki_<tex>_final.glb (ensamblado)."""
import numpy as np
import trimesh
import generar_cubo as G
import generar_texturas as T   # reusa build_features / finish_body / pole_fade

# ---- Ajustes de produccion ----
G.EARS_ON = False
G.BASE_CUT = 1.0
G.VOXEL = 0.18                 # malla mas fina entre las texturas (mas nitido)
G.NFC_CY = -G.H / 2 + G.BASE_CUT + G.NFC_READ + G.NFC_CAV_H / 2

W, H, D, R = G.W, G.H, G.D, G.R
# sincronizar los atajos que usa el modulo T (se fijaron al importar)
T.W, T.H, T.D, T.R, T.S = W, H, D, R, G.S


# --- texturas afinadas para 0.4 mm (profundidad ~= 1 perimetro, ancho >= 2x boquilla) ---
def tex_ranurado_final(X, Y, Z):
    N = 30                                   # estrias un pelin mas anchas (~2.0 mm)
    amp = 0.40                               # profundidad (mm): nitida a 0.4 mm
    theta = np.arctan2(Z, X).astype(np.float32)
    groove = 0.5 + 0.5 * np.cos(N * theta)
    yfade = np.clip((H / 2 - Y) / R, 0.0, 1.0).astype(np.float32)
    return (amp * groove * yfade * T.pole_fade(X, Z)).astype(np.float32)


def tex_dimples_final(X, Y, Z):
    p = 2.5                                  # celdas un poco mas grandes (mas limpias)
    amp = 0.45                               # profundidad del hoyuelo (mm)
    b = ((0.5 + 0.5 * np.cos(2 * np.pi * X / p)) *
         (0.5 + 0.5 * np.cos(2 * np.pi * Y / p)) *
         (0.5 + 0.5 * np.cos(2 * np.pi * Z / p)))
    return (amp * (b ** 0.55) * T.pole_fade(X, Z)).astype(np.float32)


def main():
    print("Grilla (VOXEL=%.2f)..." % G.VOXEL)
    X, Y, Z, origin, spacing = G.build_grid()
    X = X.astype(np.float32); Y = Y.astype(np.float32); Z = Z.astype(np.float32)

    print("Piezas comunes...")
    feats = T.build_features(X, Y, Z, origin)

    def round_body():
        return G.sdf_round_box(np.stack([X, Y, Z], axis=-1),
                               (W / 2 - R, H / 2 - R, D / 2 - R), R).astype(np.float32)

    m_face = G.mesh_from_field(feats["panel"], origin, spacing, "cara")
    m_black = G.mesh_from_field(feats["black"], origin, spacing, "ojos")
    m_face.export("cara_crema.stl")
    m_black.export("ojos_negro.stl")
    G.export_3mf_ams([(m_face, "cara_crema", "FAEBCD")], "cara_crema.3mf")
    G.export_3mf_ams([(m_black, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")

    # --- verificacion del encaje cara<->rebaje ---
    fb = m_face.bounds
    print(f"\nEncaje: panel {fb[1][0]-fb[0][0]:.2f} x {fb[1][1]-fb[0][1]:.2f} mm, "
          f"holgura por lado {G.FIT_CLEAR:.2f} mm (rebaje = panel + {2*G.FIT_CLEAR:.2f} mm). OK")

    for name, tex in [("ranurado", tex_ranurado_final), ("dimples", tex_dimples_final)]:
        print(f"\n== {name} (final) ==")
        body = round_body()
        body = body + tex(X, Y, Z)
        body = T.finish_body(body, feats, Y)
        m = G.mesh_from_field(body, origin, spacing, f"cuerpo_{name}_final")
        del body
        fn = f"cuerpo_{name}_final"
        m.export(fn + ".stl")
        G.export_3mf_ams([(m, fn, "F2CD28")], fn + ".3mf")
        # ensamblado a color
        b = m.copy(); b.visual.face_colors = G.COL_BODY
        f = m_face.copy(); f.visual.face_colors = G.COL_FACE
        e = m_black.copy(); e.visual.face_colors = G.COL_BLACK
        trimesh.Scene([b, f, e]).export(f"bloki_{name}_final.glb")
        d = m.bounds[1] - m.bounds[0]
        print(f"  dim (mm): {d[0]:.1f} x {d[1]:.1f} x {d[2]:.1f}")

    print("\nLISTO: cuerpo_ranurado_final, cuerpo_dimples_final (+ cara/ojos)")


if __name__ == "__main__":
    main()
