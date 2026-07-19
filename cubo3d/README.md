# Personaje Cubo 3D 🟨

Personaje 3D tipo **cubo redondeado** con carita (panel hundido + dos ojos + naricita),
inspirado en la foto de referencia — **sin las paticas**. Listo para imprimir.

![Vista previa](preview.png)

## Archivos

| Archivo | Descripción |
|---|---|
| `cubo_personaje.stl` | **Malla lista para imprimir** (watertight / cerrada) |
| `generar_cubo.py` | Script que genera el STL (paramétrico) |
| `preview.py` | Genera la imagen de vista previa |
| `preview.png` | Render de la vista frontal y 3/4 |

## Especificaciones del modelo

- **Dimensiones:** 60 × 56 × 54 mm (ancho × alto × fondo)
- **Volumen sólido:** ~158 cm³ (se imprime con relleno, no macizo)
- **Malla cerrada (watertight):** sí → apta para *slicing* directo
- La cara mira hacia el frente; la base es plana-redondeada y **no necesita soportes**.

## Cómo imprimirlo

1. Abre `cubo_personaje.stl` en tu *slicer* (Cura, PrusaSlicer, Bambu Studio, etc.).
2. Orientación: déjalo **de pie apoyado en su base** (como en la vista previa). La carita
   queda vertical, así que la impresión no requiere soportes.
3. Ajustes recomendados (punto de partida):
   - **Altura de capa:** 0.2 mm (0.12–0.16 mm si quieres la superficie más lisa)
   - **Relleno:** 10–15 %
   - **Paredes/perímetros:** 3
   - **Soportes:** no
   - **Balsa/brim:** *brim* opcional para mejor adherencia
   - **Material:** PLA amarillo para clavar el look de la foto 😄
4. Los ojos y la nariz son **hoyuelos hundidos**; después de imprimir los puedes pintar
   de negro con un marcador o pintura acrílica para resaltarlos.

## Personalizarlo

Todos los parámetros están arriba en `generar_cubo.py` (en milímetros). Puedes cambiar:

- `W`, `H`, `D` → tamaño del cubo
- `R` → qué tan redondeadas son las esquinas (más grande = más "blandito")
- `FACE_W`, `FACE_H`, `FACE_RECESS` → tamaño y profundidad del panel de la cara
- `EYE_DX`, `EYE_DY`, `EYE_R`, `EYE_DEPTH` → posición/tamaño/profundidad de los ojos
- `NOSE_*` → la naricita
- `VOXEL` → resolución de la malla (más pequeño = más detalle, más lento)

Luego vuelve a generar:

```bash
pip install numpy scikit-image trimesh   # dependencias
python3 generar_cubo.py                  # genera cubo_personaje.stl
python3 preview.py                       # (opcional) regenera preview.png
```

## Cómo está hecho

El modelo se construye con una **función de distancia con signo (SDF)**: se define el
cuerpo como un cubo redondeado y se le *restan* (booleano) el panel de la cara y las
esferas de los ojos y la nariz. Luego se extrae la superficie con **marching cubes**,
lo que produce una malla suave y cerrada, ideal para impresión 3D.
