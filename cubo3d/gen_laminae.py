#!/usr/bin/env python3
"""Regenera SOLO las dos laminas (cara delgada + ojos) sin tocar el cuerpo."""
import numpy as np
import generar_cubo as G
import generar_crochet as C     # fija los mismos parametros (VOXEL, etc.) al importar

X, Y, Z, origin, spacing = G.build_grid()
X = X.astype(np.float32); Y = Y.astype(np.float32); Z = Z.astype(np.float32)
face, eyes = C.build_laminae(X, Y, Z)
mf = G.mesh_from_field(face, origin, spacing, "cara(lamina delgada)")
mb = G.mesh_from_field(eyes, origin, spacing, "ojos(lamina)")
mf.export("cara_crema.stl"); mb.export("ojos_negro.stl")
G.export_3mf_ams([(mf, "cara_crema", "FAEBCD")], "cara_crema.3mf")
G.export_3mf_ams([(mb, "ojos_negro", "1E1E1E")], "ojos_negro.3mf")
df = mf.bounds[1] - mf.bounds[0]; de = mb.bounds[1] - mb.bounds[0]
print("cara  (mm):", df.round(2), " grosor Z =", round(df[2], 2))
print("ojos  (mm):", de.round(2), " grosor Z =", round(de[2], 2))
