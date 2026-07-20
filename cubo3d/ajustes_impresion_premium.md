# Bloki — Ajustes para un acabado LISO y premium (Bambu A1 Mini)

El escalonado que se ve en las **curvas de arriba** es *stair-stepping*: cada capa
de 0.2 mm forma un escalón donde la superficie se vuelve casi horizontal. Las
paredes rectas salen lisas porque ahí las capas quedan verticales. Esto **se
arregla desde el slicer**, no desde el modelo. Aquí va todo, en orden de impacto.

> El modelo ya se actualizó a malla fina (curvas perfectas, sin facetas).
> Falta configurar bien el slicer. Sigue esta lista completa.

---

## 1. Altura de capa — el cambio #1 (Global / Quality)
- Poner **altura de capa = 0.08 mm** (perfil "0.08 mm Extra Fine" o manual).
- Baja el escalón a la cuarta parte vs 0.2 mm → las curvas casi no muestran capas.
- Cuesta más tiempo (≈2–2.5×), pero es lo que da el look premium. Bloki es
  pequeño, así que aún es rápido.

## 2. Capa adaptativa — el arma secreta para las curvas
- En Bambu Studio, barra de la **derecha** → botón **"Variable Layer Height"**
  (el ícono de capas). Clic en **"Adaptive"**.
- Usa capas finas (0.08) SOLO en las curvas y capas normales en las paredes
  rectas → superficie lisa sin que el tiempo se dispare.
- Si no quieres complicarte: deja 0.08 mm global (punto 1) y listo.

## 3. Planchado / Ironing (Quality → Ironing)
- **Ironing: activado**, tipo **"Topmost surface only"**.
- Flujo de ironing ≈ 10 %, espaciado 0.1 mm.
- Alisa las superficies superiores planas (la cara y cualquier zona plana de
  arriba) → quedan tipo espejo, quita los anillos alrededor de la nariz.

## 4. Enfriamiento y tiempo mínimo de capa (Cooling) — quita las estrías
- **Ventilador de pieza al 100 %** (PLA, pieza pequeña).
- **"Slow down for better layer cooling"** activado, con **tiempo mínimo de
  capa ≈ 8–10 s**.
- Por qué: arriba, en la punta redondeada, la sección se hace muy pequeña; si
  la capa se imprime muy rápido/caliente, no alcanza a enfriar y salen estrías.
  Forzar 8–10 s por capa la deja enfriar → curva limpia.

## 5. Paredes y velocidad (Strength + Speed)
- **Perímetros / paredes = 3** (o 4). Más pared = superficie más firme y pareja.
- **Velocidad de pared exterior ≈ 30–50 mm/s** (bájala). Lento = menos vibración
  = menos "fantasmas"/ondas en la superficie.
- **Capas superiores/inferiores ≥ 5**.

## 6. Costura en la espalda (Quality → Seam)
- **Seam: "Aligned"**.
- Usa **"Seam painting"** y pinta la línea de costura en la **parte trasera**
  (la espalda, donde está el orificio del llavero), para que no se vea al frente.

## 7. Calibración del filamento (una sola vez)
- **Calibrar Flow Dynamics / Pressure Advance** para tu filamento (menú de
  calibración de Bambu). Esquinas más nítidas, sin abombamientos.
- **Calibrar Flow Rate** → paredes parejas, sin sobre/sub-extrusión.

## 8. Temperatura y filamento
- **Boquilla en el rango bajo del PLA (200–205 °C)** → detalle más nítido, menos
  hilos/oozing.
- **Filamento SECO.** El PLA con humedad sale rugoso/con pelusa (parte del
  aspecto mate rugoso de la foto puede ser esto). Secar 4–6 h a ~45–50 °C si
  tienes secador, o usarlo recién abierto.

## 9. Orientación (OBLIGATORIA por el NFC)
- **Cara hacia ARRIBA**, apoyado sobre la **parte trasera plana** (la espalda).
- Esto es necesario para poder meter el tag en la pausa. No lo cambies.
- Sin soportes.

## 10. Recordatorio: pausa para el tag NFC
- La cavidad del tag va **detrás de la cara**. Añade una **PAUSA** a la altura
  de la cavidad (Bambu: clic derecho en la capa → "Add Pause"), coloca el tag y
  reanuda. El techo lo sella → queda oculto y no removible.
- (La altura exacta de la pausa la da el diagrama `diagrama_nfc.png`.)

---

## Resumen exprés (si solo haces 4 cosas)
1. **Altura de capa 0.08 mm** (o adaptativa).
2. **Ironing** en superficies superiores.
3. **Tiempo mínimo de capa 8–10 s + ventilador 100 %** (quita estrías arriba).
4. **Pared exterior lenta (30–50 mm/s) + 3 paredes.**

Con esto las curvas de arriba pasan de "escalón visible" a "liso premium".
Si quieres el 10/10 absoluto: un lijado suave 400→800 y listo (opcional).
