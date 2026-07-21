#!/usr/bin/env python3
"""Construye una previsualizacion 3D interactiva (rotar con el mouse) como una
pagina HTML autocontenida: un visor WebGL propio (sin librerias externas) con
las 3 mallas embebidas (cuerpo, cara, ojos). Sirve como Artifact."""
import base64
import numpy as np
import trimesh

MESHES = [
    ("cuerpo_conejito.stl", [0.95, 0.80, 0.16], 55000, True),   # amarillo
    ("cara_crema.stl",      [0.98, 0.92, 0.80], 16000, False),  # crema
    ("ojos_negro.stl",      [0.09, 0.09, 0.10], 5000, False),   # negro
]


def simplify(m, target):
    if len(m.faces) <= target:
        return m
    for meth in ("quadric_decimation",):
        try:
            r = m.simplify_quadric_decimation(face_count=target)
            if r is not None and len(r.faces) > 0:
                return r
        except Exception:
            pass
    return m


def pack(m):
    m.merge_vertices()
    V = m.vertices.astype(np.float32)
    F = m.faces.astype(np.uint32)
    N = m.vertex_normals.astype(np.float32)
    return V, N, F


def b64(arr):
    return base64.b64encode(arr.tobytes()).decode()


parts = []
allV = []
for path, color, target, outer_only in MESHES:
    m = trimesh.load(path)
    if outer_only:
        comps = m.split(only_watertight=False)
        if len(comps) > 1:
            m = max(comps, key=lambda c: float(np.prod(c.extents)))
    m = simplify(m, target)
    trimesh.repair.fix_normals(m)
    V, N, F = pack(m)
    allV.append(V)
    parts.append({
        "color": color,
        "pos": b64(V.reshape(-1)),
        "nrm": b64(N.reshape(-1)),
        "idx": b64(F.reshape(-1)),
        "nidx": int(F.size),
    })
    print(f"{path}: {len(V)} verts, {len(F)} faces")

allV = np.concatenate(allV)
center = ((allV.max(0) + allV.min(0)) / 2).tolist()
radius = float(np.linalg.norm(allV.max(0) - allV.min(0)) / 2)

import json
DATA = json.dumps({"parts": parts, "center": center, "radius": radius})

HTML = """<div id="wrap">
  <canvas id="c"></canvas>
  <div id="hud">
    <div class="row"><b>Bloki</b> — arrastra para rotar · rueda para zoom</div>
    <div class="row muted">cuerpo amarillo · carita crema (encaje escalonado) · ojos negros (encajan desde atras, con tope)</div>
    <div class="row"><button id="explode">Ver piezas separadas</button>
      <button id="reset">Reiniciar vista</button></div>
  </div>
</div>
<style>
  #wrap{position:fixed;inset:0;background:linear-gradient(160deg,#eef2f7,#dbe3ee);overflow:hidden}
  :root[data-theme=dark] #wrap, @media (prefers-color-scheme:dark){#wrap{background:linear-gradient(160deg,#1a1f2b,#0e1219)}}
  canvas{width:100%;height:100%;display:block;cursor:grab;touch-action:none}
  canvas:active{cursor:grabbing}
  #hud{position:absolute;left:16px;bottom:16px;font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;
       background:rgba(255,255,255,.82);backdrop-filter:blur(8px);padding:12px 14px;border-radius:12px;
       box-shadow:0 6px 24px rgba(0,0,0,.15);max-width:min(92vw,440px);color:#222}
  @media (prefers-color-scheme:dark){#hud{background:rgba(28,32,42,.82);color:#e8ecf2}}
  .row{margin:2px 0}.muted{color:#667;font-size:12.5px}
  @media (prefers-color-scheme:dark){.muted{color:#9aa5b5}}
  button{font:13px inherit;padding:6px 12px;margin-right:8px;border:0;border-radius:8px;cursor:pointer;
         background:#2d6cdf;color:#fff;font-weight:600}
  button:hover{background:#1f5ad0}
</style>
<script>
const DATA = __DATA__;
const cv = document.getElementById('c');
const gl = cv.getContext('webgl', {antialias:true, alpha:false});
function dec(b64){const s=atob(b64),n=s.length,a=new Uint8Array(n);for(let i=0;i<n;i++)a[i]=s.charCodeAt(i);return a.buffer;}

const vs = `attribute vec3 p;attribute vec3 n;uniform mat4 mvp;uniform mat4 mv;
varying vec3 vn;varying vec3 vp;void main(){vn=mat3(mv)*n;vp=(mv*vec4(p,1.)).xyz;gl_Position=mvp*vec4(p,1.);}`;
const fs = `precision highp float;varying vec3 vn;varying vec3 vp;uniform vec3 col;
void main(){vec3 N=normalize(vn);vec3 L=normalize(vec3(0.4,0.7,0.9));
vec3 V=normalize(-vp);vec3 H=normalize(L+V);
float d=max(dot(N,L),0.);float s=pow(max(dot(N,H),0.),24.)*0.35;
vec3 c=col*(0.32+0.72*d)+vec3(s);gl_FragColor=vec4(pow(c,vec3(0.4545)),1.);}`;
function sh(t,src){const o=gl.createShader(t);gl.shaderSource(o,src);gl.compileShader(o);
  if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))console.error(gl.getShaderInfoLog(o));return o;}
const prog=gl.createProgram();gl.attachShader(prog,sh(gl.VERTEX_SHADER,vs));
gl.attachShader(prog,sh(gl.FRAGMENT_SHADER,fs));gl.linkProgram(prog);gl.useProgram(prog);
const aP=gl.getAttribLocation(prog,'p'),aN=gl.getAttribLocation(prog,'n');
const uMVP=gl.getUniformLocation(prog,'mvp'),uMV=gl.getUniformLocation(prog,'mv'),uCol=gl.getUniformLocation(prog,'col');

const C=DATA.center, RAD=DATA.radius;
const parts=DATA.parts.map(pt=>{
  const pos=new Float32Array(dec(pt.pos)), nrm=new Float32Array(dec(pt.nrm)), idx=new Uint32Array(dec(pt.idx));
  const bp=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,bp);gl.bufferData(gl.ARRAY_BUFFER,pos,gl.STATIC_DRAW);
  const bn=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,bn);gl.bufferData(gl.ARRAY_BUFFER,nrm,gl.STATIC_DRAW);
  const bi=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,bi);gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,idx,gl.STATIC_DRAW);
  return {bp,bn,bi,n:pt.nidx,col:pt.color};
});
const extU=gl.getExtension('OES_element_index_uint');

// --- matrices ---
function mul(a,b){const o=new Float32Array(16);for(let i=0;i<4;i++)for(let j=0;j<4;j++){
  let s=0;for(let k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k];o[i*4+j]=s;}return o;}
function persp(f,ar,n,fa){const t=1/Math.tan(f/2);return new Float32Array([t/ar,0,0,0, 0,t,0,0, 0,0,(fa+n)/(n-fa),-1, 0,0,2*fa*n/(n-fa),0]);}
function trans(x,y,z){return new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,x,y,z,1]);}
function rotX(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1]);}
function rotY(a){const c=Math.cos(a),s=Math.sin(a);return new Float32Array([c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1]);}

let rx=-0.25, ry=0.5, dist=RAD*3.0, exploded=0, target=0;
let drag=false,px=0,py=0;
cv.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;cv.setPointerCapture(e.pointerId);});
cv.addEventListener('pointerup',()=>drag=false);
cv.addEventListener('pointermove',e=>{if(!drag)return;ry+=(e.clientX-px)*0.01;rx+=(e.clientY-py)*0.01;
  rx=Math.max(-1.5,Math.min(1.5,rx));px=e.clientX;py=e.clientY;});
cv.addEventListener('wheel',e=>{e.preventDefault();dist*=Math.exp(e.deltaY*0.001);
  dist=Math.max(RAD*1.6,Math.min(RAD*7,dist));},{passive:false});
document.getElementById('explode').onclick=()=>{target=target?0:1;};
document.getElementById('reset').onclick=()=>{rx=-0.25;ry=0.5;dist=RAD*3.0;target=0;};

function resize(){const dpr=Math.min(devicePixelRatio||1,2);
  cv.width=cv.clientWidth*dpr;cv.height=cv.clientHeight*dpr;gl.viewport(0,0,cv.width,cv.height);}
addEventListener('resize',resize);resize();
gl.enable(gl.DEPTH_TEST);

function frame(){
  exploded += (target-exploded)*0.12;
  gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  const ar=cv.width/cv.height;
  const P=persp(0.9,ar,RAD*0.5,RAD*12);
  const view=mul(trans(0,0,-dist),mul(rotX(rx),rotY(ry)));
  parts.forEach((pt,i)=>{
    // separacion en +Z (hacia el frente): cara y ojos se alejan del cuerpo
    const off = i===0?0 : i===1? exploded*RAD*0.55 : exploded*RAD*1.1;
    const model=mul(trans(0,0,off),trans(-C[0],-C[1],-C[2]));
    const mv=mul(view,model), mvp=mul(P,mv);
    gl.uniformMatrix4fv(uMV,false,mv);gl.uniformMatrix4fv(uMVP,false,mvp);
    gl.uniform3fv(uCol,pt.col);
    gl.bindBuffer(gl.ARRAY_BUFFER,pt.bp);gl.enableVertexAttribArray(aP);gl.vertexAttribPointer(aP,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,pt.bn);gl.enableVertexAttribArray(aN);gl.vertexAttribPointer(aN,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,pt.bi);
    gl.drawElements(gl.TRIANGLES,pt.n,gl.UNSIGNED_INT,0);
  });
  requestAnimationFrame(frame);
}
frame();
</script>"""

HTML = HTML.replace("__DATA__", DATA)
from pathlib import Path
Path("preview_conejito.html").write_text(HTML, encoding="utf-8")
kb = len(HTML.encode()) / 1024
print(f"Guardado preview_conejito.html ({kb:.0f} KB)")
