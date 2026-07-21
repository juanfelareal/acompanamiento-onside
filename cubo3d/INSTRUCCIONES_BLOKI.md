# Bloki — Instrucciones completas de impresión

Cubito 3D con carita + **tag NFC oculto** (sellado dentro, no se ve ni se saca) +
orificio para llavero + **logo BLOKI grabado en la espalda**. Se imprime **de pie
(mirando al frente)** en 3 piezas de 1 color cada una, que encajan a presión.

> **El logo va grabado en el mismo color** (viene en el `cuerpo_amarillo.stl`).
> No hay que hacer nada extra: **no es un cambio de color**, así que no agrega
> tiempo ni purga. Sale al imprimir el cuerpo.

**Impresora de referencia:** Bambu Lab A1 Mini (sirve cualquier FDM).

---

## 1. Archivos

| Archivo | Qué es |
|---|---|
| `cuerpo_amarillo.stl` | El cuerpo. **Lleva dentro la cavidad del tag NFC.** |
| `cara_crema.stl` | El panel de la carita + la naricita. |
| `ojos_negro.stl` | Los 2 ojos (encajan desde atrás de la carita). |
| `cubo_personaje.glb` | Modelo a color para ver en 3D (arrástralo a un visor). |
| `diagrama_nfc.png` | Dónde va el tag y a qué altura hacer la pausa. |

**Colores:** son sugerencia (cuerpo amarillo, cara crema, ojos negros). Puedes
usar los colores que quieras; cada pieza es de 1 solo color, así que **no hay
cambios de color ni desperdicio**.

**Dimensiones del cuerpo:** 37 × 32.5 × 31 mm (ancho × alto × fondo). Tamaño
mínimo manteniendo las proporciones (limitado por el tag NFC de 25 mm).

---

## 2. Materiales

- Filamento PLA (los colores que elijas para cuerpo / cara / ojos).
- **1 tag NFC de Ø 25 mm** (tipo moneda/sticker, ~1–1.5 mm de grosor).
- Cuerdita/cordón fino para el llavero (pasa por un orificio de ~2 mm).
- Pinza para colocar el tag en la pausa.

---

## 3. Orientación de impresión (IMPORTANTE)

- **Cuerpo y carita: DE PIE, con la cara mirando al frente** (parados sobre su
  base plana). Así la cara y el frente se imprimen como pared vertical y salen
  **lisos** (sin el escalonado de las curvas).
- Los **ojos**: apoyados sobre su pestaña plana (la cúpula hacia arriba).
- **Sin soportes.** La base es plana, así que se para y se pega bien a la cama.

---

## 4. Configuración para un acabado LISO y premium

Estos ajustes son los que hacen que las curvas no muestren las capas:

| Ajuste | Valor | Por qué |
|---|---|---|
| **Altura de capa** | **0.08 mm** (o capa adaptativa) | Lo #1: reduce el escalonado a la cuarta parte. |
| **Planchado / Ironing** | Activado, superficies superiores | Alisa las zonas planas de arriba. |
| **Tiempo mínimo de capa** | **8–10 s** + ventilador 100 % | Quita las estrías de las partes pequeñas de arriba. |
| **Pared exterior** | Velocidad 30–50 mm/s | Menos vibración = superficie más pareja. |
| **Perímetros / paredes** | 3 (o 4) | Superficie más firme. |
| **Costura (Seam)** | "Aligned" + pintarla atrás | Que no se vea al frente. |
| **Temperatura** | PLA 200–205 °C | Detalle nítido, menos hilos. |
| **Filamento** | Seco | El PLA húmedo sale rugoso. |
| **Relleno** | 10–15 % | Suficiente. |

> Calibrar **Flow Dynamics / Pressure Advance** del filamento (una vez) mejora
> mucho las esquinas. (Detalle ampliado en `ajustes_impresion_premium.md`.)

---

## 5. El tag NFC — PAUSA para embeberlo

El tag va **acostado ~2 mm sobre la base**, oculto dentro del cuerpo. Se coloca
durante la impresión, con una pausa. **Ver `diagrama_nfc.png`.**

1. Empieza a imprimir el **cuerpo** (de pie).
2. Programa una **PAUSA a los 3.7 mm de altura** (la capa justo antes de que se
   cierre el hueco):
   - **Bambu Studio / Orca:** rebana → en la barra de capas de la derecha, clic
     derecho en la capa de ~3.7 mm → **"Add Pause"**.
   - (A 0.08 mm de capa, eso es alrededor de la **capa 46**; a 0.2 mm, la ~18.)
3. Cuando se detenga, **apoya el tag NFC plano** en el hueco redondo (con pinza).
   Queda descansando sobre el piso que está a 2 mm.
4. Pulsa **Reanudar**. La impresora cierra el cuerpo encima → el tag queda
   **sellado: no se ve y no se puede sacar.**

**Cómo se lee:** acercando el teléfono a la **parte de abajo** (la base) de
Bloki. Como el tag queda a ~2 mm de la base, lee al instante. El PLA no bloquea
la señal NFC.

> **Prueba recomendada:** antes de sellar en serie, haz una prueba con un tag de
> sacrificio para confirmar que ese tag específico lee bien y que la altura de la
> pausa calza (si tu tag es más grueso, sube la pausa 1–2 décimas).

---

## 6. Ensamble (sin pegamento)

1. **Ojos en la carita:** mete cada ojo **desde atrás** del panel. La cabeza y el
   cuello asoman por el frente; la **pestaña trasera hace tope y clic**. No se
   salen.
2. **Carita en el cuerpo:** presiona el panel en el rebaje del frente. Entra
   ajustado y se centra solo; queda un marco parejo alrededor. Al montarla, el
   cuerpo respalda las pestañas de los ojos → quedan trabados de forma definitiva.
3. **Llavero:** pasa la cuerdita por el orificio de la esquina superior trasera.

---

## 7. Resumen exprés

1. Imprimir **de pie**, sin soportes.
2. Capa **0.08 mm** + planchado + ventilador/tiempo mínimo de capa.
3. **Pausa a 3.7 mm** → colocar tag → reanudar.
4. Ensamblar: ojos desde atrás (clic) → carita a presión → cordón.
5. Leer el NFC por **debajo**.

¿Dudas o el tag mide distinto? Avísame y ajusto la cavidad/pausa a esa medida.
