# Bloki (versión LANA) — Instrucciones de impresión

Cubito con textura de **tejido/lana** (chevron), carita de 2 láminas, **logo BLOKI**
grabado en la espalda y **tag NFC oculto** que se lee por la base. Se imprime
**de pie** (cara al frente), en piezas de 1 color cada una que encajan a presión.

**Impresora de referencia:** Bambu Lab A1 Mini (sirve cualquier FDM).
**Tamaño del cuerpo:** 36 × 32 × 30 mm.

---

## 1. Archivos (cada uno 1 color)

| Archivo | Qué es | Color sugerido |
|---|---|---|
| `cuerpo_crochet.3mf` | El cuerpo tejido. **Lleva dentro la cavidad del tag NFC** y el logo. | Amarillo |
| `cara_crema.3mf` | **Lámina de la cara** (placa con nariz + 2 huecos para los ojos). | Crema |
| `ojos_negro.3mf` | **Lámina de los ojos** (placa con los 2 ojos que asoman por los huecos). | Negro |
| `diagrama_nfc.png` | Dónde va el tag y a qué altura hacer la pausa. | — |

> Los `.stl` van incluidos por si tu hermano usa otro programa distinto a Bambu.

---

## 2. Materiales

- Filamento **PLA mate** (realza el tejido) en los colores que elijas.
- **1 tag NFC de Ø 25 mm** (tipo moneda/sticker, ~1–1.5 mm de grosor).
- Pinza para colocar el tag en la pausa.

---

## 3. Orientación (IMPORTANTE)

- **Cuerpo y cara: DE PIE, cara mirando al frente** (parados sobre la base plana).
- **Ojos:** la lámina apoyada plana (los ojos hacia arriba).
- **Sin soportes** (la base es plana).

---

## 4. Ajustes para que el tejido salga nítido

| Ajuste | Valor | Por qué |
|---|---|---|
| **Altura de capa** | **0.12 mm o menos** | El punto es fino (~1.4 mm); con capa gruesa se pierde. |
| **Pared exterior** | Velocidad **30–40 mm/s** | El tejido vive en la pared; lento = más nítido. |
| **Fuzzy Skin** | **APAGADO** | La textura ya va esculpida en el modelo. |
| **Compensación "pata de elefante"** | **~0.15 mm** | Para que la base no se abombe. |
| **Perímetros / paredes** | 3 | Superficie firme. |
| **Relleno** | 10–15 % | Suficiente. |
| **Temp / filamento** | PLA 200–205 °C, seco | Detalle nítido. |

---

## 5. El tag NFC — PAUSA para embeberlo

El tag va **acostado**, oculto dentro del cuerpo, cerca de la base. **Ver `diagrama_nfc.png`.**

1. Empieza a imprimir el **cuerpo** (de pie).
2. Programa una **PAUSA a los 6.5 mm de altura**:
   - **Bambu Studio / Orca:** rebana → en la barra de capas (derecha), clic
     derecho en la capa de ~6.5 mm → **"Add Pause"**.
   - (A 0.12 mm de capa eso es ~la **capa 54**; a 0.2 mm, la ~32.)
3. Cuando se detenga, **apoya el tag NFC plano** en el hueco redondo (con pinza).
4. Pulsa **Reanudar**. El cuerpo se cierra encima → el tag queda **sellado**
   (no se ve ni se saca).

**Cómo se lee:** acercando el teléfono a la **base** de Bloki (el tag queda a
~5 mm). El PLA no bloquea la señal NFC.

> **Prueba antes de producir en serie:** con un tag de sacrificio confirma que
> ese tag lee bien y que la altura de la pausa calza (si tu tag es más grueso,
> sube la pausa 1–2 décimas).

---

## 6. Ensamble (sin pegamento)

Ahora la carita son **2 láminas que se apilan**:

1. **Arma el sándwich de la cara:** pon la **lámina de ojos (negra)** atrás y la
   **lámina de la cara (crema)** encima → los ojos **asoman por los huecos**.
2. **Mete el sándwich** en el rebaje del frente del cuerpo, a presión. Entra
   ajustado y se centra solo.
3. Listo. (El logo BLOKI ya viene grabado en la espalda.)

---

## 7. Resumen exprés

1. Imprimir **de pie**, sin soportes, sin Fuzzy Skin.
2. Capa **0.12 mm**, pared exterior lenta, pata de elefante ~0.15 mm.
3. **Pausa a 6.5 mm** → colocar tag → reanudar.
4. Ensamblar: ojos (atrás) + cara (adelante) → sándwich a presión en el cuerpo.
5. Leer el NFC por **debajo**.

¿El tag mide distinto o quieres otra altura de pausa? Avísame y ajusto la cavidad.
