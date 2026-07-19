#!/usr/bin/env python3
"""Construye la guia de impresion del Bloki en HTML (para exportar a PDF)."""
import base64
from pathlib import Path


def img64(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


hero = img64("hero.png")
diagrama = img64("diagrama_nfc.png")
preview = img64("preview.png")

HTML = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 16mm 14mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
         color: #222; font-size: 11pt; line-height: 1.5; margin: 0; }}
  h1 {{ font-size: 25pt; margin: 0 0 2px; color: #1a1a1a; }}
  h2 {{ font-size: 15pt; margin: 22px 0 8px; color: #a8850f;
        border-bottom: 2px solid #f2cd28; padding-bottom: 4px; }}
  .sub {{ color: #666; font-size: 11pt; margin: 0 0 10px; }}
  .hero {{ text-align:center; }}
  .hero img {{ width: 62%; }}
  table {{ border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 10.5pt; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 9px; text-align: left; vertical-align: top; }}
  th {{ background: #fdf6d6; }}
  .box {{ background:#fffbe9; border:1px solid #f2cd28; border-radius:8px; padding:10px 14px; margin:8px 0; }}
  .step {{ margin: 5px 0; }}
  .num {{ display:inline-block; width:22px; height:22px; background:#f2cd28; color:#111;
          border-radius:50%; text-align:center; font-weight:700; line-height:22px; margin-right:6px; }}
  code {{ background:#f4f4f4; padding:1px 5px; border-radius:4px; font-size:10pt; }}
  .imgfull {{ width:100%; margin:8px 0; border:1px solid #eee; border-radius:6px; }}
  .cols {{ display:flex; gap:16px; }}
  .cols > div {{ flex:1; }}
  .pb {{ page-break-before: always; }}
  ul {{ margin: 6px 0; padding-left: 20px; }}
  li {{ margin: 3px 0; }}
  .tag {{ color:#d12; font-weight:700; }}
</style></head><body>

<h1>Bloki — Guía de impresión del prototipo</h1>
<p class="sub">Cubo 3D con carita + tag NFC embebido (oculto) y orificio para llavero.</p>
<div class="hero"><img src="{hero}"></div>

<h2>1. Qué vamos a imprimir</h2>
<p>Un cubito redondeado (“Bloki”) de <b>60 × 56 × 47 mm</b>. Lleva un <b>tag NFC de 25 mm
escondido y sellado por dentro</b> (no se ve ni se puede sacar) y un <b>orificio en una
esquina superior</b> para colgarlo con una cuerdita.</p>

<h2>2. Materiales necesarios</h2>
<table>
<tr><th>Material</th><th>Detalle</th></tr>
<tr><td>Filamento amarillo (PLA)</td><td>Cuerpo del cubo. Es el color principal.</td></tr>
<tr><td>Filamento crema/blanco hueso (PLA)</td><td>Panel de la carita. <i>Opcional si se imprime en un solo color.</i></td></tr>
<tr><td>Filamento negro (PLA)</td><td>Los dos ojitos. <i>Opcional si se imprime en un solo color.</i></td></tr>
<tr><td class="tag">Tag NFC Ø 25 mm</td><td>Tipo moneda/sticker, delgado (≈1 mm). Es el que se embebe dentro.</td></tr>
<tr><td>Cuerdita / cordón fino</td><td>Para el llavero (pasa por el orificio de Ø 3.5 mm).</td></tr>
</table>

<h2>3. Archivos incluidos</h2>
<table>
<tr><th>Archivo</th><th>Para qué</th></tr>
<tr><td><code>cuerpo_amarillo.stl</code></td><td>El cubo (amarillo). <b>Lleva dentro la cavidad del NFC.</b></td></tr>
<tr><td><code>cara_crema.stl</code></td><td>Panel de la carita + naricita (crema).</td></tr>
<tr><td><code>ojos_negro.stl</code></td><td>Los dos ojos (negro, en relieve).</td></tr>
<tr><td><code>cubo_personaje.3mf</code></td><td>Proyecto a color ya armado (las 3 piezas juntas y con colores).</td></tr>
<tr><td><code>cubo_personaje.glb</code></td><td>Para ver el modelo en 3D en cualquier visor.</td></tr>
</table>

<h2>4. Configuración de impresión (punto de partida)</h2>
<table>
<tr><th>Parámetro</th><th>Valor</th></tr>
<tr><td>Material</td><td>PLA</td></tr>
<tr><td>Altura de capa</td><td>0.2 mm (0.12–0.16 mm si se quiere más fino)</td></tr>
<tr><td>Relleno (infill)</td><td>10–15 %</td></tr>
<tr><td>Perímetros / paredes</td><td>3</td></tr>
<tr><td>Soportes</td><td><b>No</b></td></tr>
<tr><td>Adherencia</td><td><i>Brim</i> opcional</td></tr>
<tr><td>Orientación</td><td><b>De pie sobre la base</b> (ver punto 6, importante para el NFC)</td></tr>
</table>

<h2 class="pb">5. Cómo imprimir a color</h2>
<div class="cols">
  <div class="box"><b>Opción A — Impresora multicolor (Bambu AMS, Prusa MMU)</b>
  <ul>
   <li>Abrir <code>cubo_personaje.3mf</code> (ya trae las 3 piezas y colores), o importar los 3 STL juntos como “un solo objeto”.</li>
   <li>Asignar: amarillo al cuerpo, crema a la cara, negro a los ojos.</li>
  </ul></div>
  <div class="box"><b>Opción B — Un solo color (más simple para el 1er prototipo)</b>
  <ul>
   <li>Imprimir solo <code>cuerpo_amarillo.stl</code> para validar forma + NFC.</li>
   <li>La carita se puede pintar después, o imprimir a color en la siguiente versión.</li>
  </ul></div>
</div>
<p style="color:#666"><i>Para un primer prototipo, la Opción B es la más rápida para verificar que todo
calce (tamaño, NFC, llavero). El color se puede pulir después.</i></p>

<h2>6. Lo importante: embeber el tag NFC durante la impresión</h2>
<p>El cubo es <b>sólido por fuera, sin ningún agujero</b>. El tag se mete <b>durante la
impresión</b>, haciendo una <b>pausa</b>. Es una función estándar de todos los programas
de impresión (slicers).</p>
<img class="imgfull" src="{diagrama}">
<div class="box">
  <div class="step"><span class="num">1</span> Imprimir el cuerpo <b>de pie sobre la base</b>.</div>
  <div class="step"><span class="num">2</span> En el slicer, agregar una <b>PAUSA a ~2.6 mm de altura</b>
     (la cavidad va de 1.2 a 2.8 mm desde la base):
     <ul>
       <li><b>Bambu Studio / Orca:</b> rebanar → en la barra de capas de la derecha, clic derecho en la capa de ~2.6 mm → <b>“Add pause”</b>.</li>
       <li><b>PrusaSlicer:</b> en la barra vertical de capas, ícono <b>“+” naranja → “Add pause”</b> a ~2.6 mm.</li>
       <li><b>Cura:</b> <b>Extensions → Post Processing → Modify G-Code → “Pause at height”</b> = 2.6 mm.</li>
     </ul>
  </div>
  <div class="step"><span class="num">3</span> Cuando la impresora se detenga, <b>colocar el tag NFC</b> en el hueco
     redondo (con una pinza; una gotita de pegamento si se quiere fijar).</div>
  <div class="step"><span class="num">4</span> Presionar <b>Reanudar</b>. La impresión cierra el techo encima →
     el tag queda <b>encapsulado: no se ve y no se puede sacar</b>.</div>
</div>
<p>El PLA no bloquea la señal NFC, así que el teléfono lo lee igual a través del plástico.</p>

<h2 class="pb">7. Vistas de referencia</h2>
<img class="imgfull" src="{preview}">
<p style="color:#666"><i>Izquierda: la carita. Centro: la base es totalmente lisa (el tag es imperceptible).
Derecha: corte que muestra el tag sellado dentro.</i></p>

<h2>8. Consejos y posibles problemas</h2>
<ul>
  <li><b>Altura de la pausa:</b> si tu tag es más grueso, conviene hacer una prueba con un tag de sacrificio para afinar la altura exacta.</li>
  <li><b>El tag no debe sobresalir</b> del nivel de impresión al reanudar; si sobresale, la boquilla lo golpea. Debe quedar dentro del hueco.</li>
  <li><b>Rapidez en la pausa:</b> colocar el tag y reanudar sin demorar mucho, para que la capa no se enfríe y siga pegando bien.</li>
  <li><b>Llavero:</b> el orificio es de Ø 3.5 mm; entra una cuerdita/cordón fino.</li>
  <li><b>Sin soportes</b> en la orientación de pie sobre la base.</li>
</ul>

<div class="box"><b>¿Dudas o ajustes?</b> Si el tag que consigues mide distinto (diámetro o grosor),
avísame y ajusto la cavidad a esa medida exacta antes de imprimir. También puedo dar los
clics precisos según el modelo de impresora.</div>

</body></html>"""

Path("guia_bloki.html").write_text(HTML, encoding="utf-8")
print("Guardado guia_bloki.html")
