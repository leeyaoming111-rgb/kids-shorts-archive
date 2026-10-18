# shared renderer infrastructure (from the engine toolkit)
import sys, json, math, pickle, subprocess, time
import numpy as np, moderngl, skia
import timeline as T
from meshes import ground_h

W, H, FPS = T.W, T.H, T.FPS
D = pickle.load(open("out/meshes.pkl", "rb"))
if sys.platform == "darwin":
    ctx = moderngl.create_standalone_context(require=330)      # native macOS: Apple GPU via OpenGL 4.1 on Metal
else:
    ctx = moderngl.create_standalone_context(backend="egl")
print("GPU:", ctx.info["GL_RENDERER"], flush=True)
ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

# ---------------- shaders ----------------
VS = """
#version 330
in vec3 in_pos; in vec3 in_nrm; in vec3 in_col; in float in_ao;
uniform mat4 M; uniform mat4 VP; uniform mat3 NM; uniform mat4 LVP;
out vec3 v_wp; out vec3 v_n; out vec3 v_col; out float v_ao; out vec3 v_lp; out vec4 v_ls;
void main(){
  vec4 wp = M * vec4(in_pos, 1.0);
  v_wp = wp.xyz; v_n = normalize(NM * in_nrm); v_col = in_col; v_ao = in_ao; v_lp = in_pos;
  v_ls = LVP * wp;
  gl_Position = VP * wp;
}"""
FS = """
#version 330
in vec3 v_wp; in vec3 v_n; in vec3 v_col; in float v_ao; in vec3 v_lp; in vec4 v_ls;
uniform vec3 tint; uniform float tintMix; uniform int mat; uniform float bump; uniform float seed;
uniform vec3 camPos; uniform sampler2DShadow shadowMap; uniform vec4 contact[8]; uniform int nContact;
uniform float fade; uniform float keyI;
out vec4 frag;
vec3 hash3(vec3 p){ p = vec3(dot(p,vec3(127.1,311.7,74.7)), dot(p,vec3(269.5,183.3,246.1)), dot(p,vec3(113.5,271.9,124.6)));
  return fract(sin(p)*43758.5453); }
float vnoise(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  float n000=hash3(i).x, n100=hash3(i+vec3(1,0,0)).x, n010=hash3(i+vec3(0,1,0)).x, n110=hash3(i+vec3(1,1,0)).x;
  float n001=hash3(i+vec3(0,0,1)).x, n101=hash3(i+vec3(1,0,1)).x, n011=hash3(i+vec3(0,1,1)).x, n111=hash3(i+vec3(1,1,1)).x;
  return mix(mix(mix(n000,n100,f.x),mix(n010,n110,f.x),f.y), mix(mix(n001,n101,f.x),mix(n011,n111,f.x),f.y), f.z); }
float thumbs(vec3 p){
  vec3 i=floor(p), f=fract(p); float h=0.0;
  for(int x=-1;x<=1;x++) for(int y=-1;y<=1;y++) for(int z=-1;z<=1;z++){
    vec3 g=vec3(x,y,z); vec3 o=hash3(i+g+seed); vec3 r=g+o-f; float d=length(r);
    float sel = step(0.62, o.z);
    float rad = 0.42 + 0.18*fract(o.x*9.1);
    float dim = smoothstep(rad, 0.0, d);
    float ridge = 0.5 + 0.5*sin(d*55.0 + o.y*6.0);
    h = min(h, -sel*dim*dim*(0.75 + 0.25*ridge));
  }
  return h;
}
float shadowAt(vec4 ls){
  vec3 p = ls.xyz/ls.w*0.5+0.5;
  if(p.x<0.0||p.x>1.0||p.y<0.0||p.y>1.0) return 1.0;
  float s=0.0; float r=1.6/2048.0;
  for(int i=-2;i<=2;i++) for(int j=-2;j<=2;j++){
    s += texture(shadowMap, vec3(p.xy+vec2(i,j)*r*1.2, p.z-0.0012));
  }
  return s/25.0;
}
vec3 srgb2lin(vec3 c){ return pow(c, vec3(2.2)); }
void main(){
  vec3 n = normalize(v_n);
  if(!gl_FrontFacing) n = -n;
  vec3 base = mix(v_col, tint, tintMix);
  if(tintMix < 0.0) base = v_col * tint;
  base = srgb2lin(base);
  vec3 V = normalize(camPos - v_wp);
  if(mat == 3){ frag = vec4(pow(base*1.15, vec3(1.0/2.2)), 1.0); return; }
  // ---- bump: thumbprints & lumps (clay) or fuzz (moss) ----
  float h = 0.0;
  if(mat == 0 || mat == 4){
    h = thumbs(v_lp*9.0) * 0.6 + (vnoise(v_lp*22.0)-0.5)*0.35 + (vnoise(v_lp*5.0)-0.5)*0.5;
  } else if(mat == 1){
    h = vnoise(v_wp*38.0)*0.7 + vnoise(v_wp*90.0)*0.5 + vnoise(v_wp*7.0)*0.8;
    base *= 0.72 + 0.5*vnoise(v_wp*55.0);
    base = mix(base, base*vec3(0.62,0.78,0.55), smoothstep(0.45,0.8,vnoise(v_wp*2.6)));
    base = mix(base, base*vec3(1.25,1.2,0.95), smoothstep(0.7,0.9,vnoise(v_wp*14.0))*0.6);
  }
  if(bump > 0.0){
    vec3 dpdx=dFdx(v_wp), dpdy=dFdy(v_wp);
    float dhx=dFdx(h), dhy=dFdy(h);
    vec3 r1=cross(dpdy,n), r2=cross(n,dpdx); float det=dot(dpdx,r1);
    vec3 grad = sign(det)*(dhx*r1 + dhy*r2);
    n = normalize(abs(det)*n - grad*bump*0.012);
  }
  vec3 L = normalize(vec3(-0.55, 0.85, 0.5));
  float sh = shadowAt(v_ls);
  float ndl = dot(n, L);
  float wrap = clamp((ndl + 0.35)/1.35, 0.0, 1.0);
  float ao = v_ao;
  if(mat == 1){
    for(int i=0;i<nContact;i++){
      vec2 d = (v_wp.xz - contact[i].xy)/contact[i].z;
      ao *= 1.0 - 0.55*exp(-dot(d,d)*1.6)*contact[i].w;
    }
  }
  vec3 keyc = vec3(1.0, 0.93, 0.82)*2.3*keyI;
  vec3 skyc = vec3(0.55, 0.68, 0.95)*0.85*(0.75+0.25*keyI);
  vec3 gndc = vec3(0.45, 0.58, 0.32)*0.45;
  vec3 hemi = mix(gndc, skyc, 0.5 + 0.5*n.y);
  vec3 F = normalize(vec3(0.7, 0.35, 0.6));
  float fill = clamp(dot(n, F), 0.0, 1.0)*0.25;
  vec3 diff = keyc * wrap * mix(0.25, 1.0, sh) + hemi*ao + vec3(0.75,0.8,1.0)*fill*ao;
  // subsurface-ish warm terminator
  diff += vec3(0.35, 0.12, 0.06) * smoothstep(0.35, 0.0, abs(ndl)) * 0.35 * sh;
  vec3 col = base * diff * mix(0.75, 1.0, ao);
  vec3 Hh = normalize(L + V);
  float specp = (mat == 2) ? 90.0 : 18.0;
  float specs = (mat == 2) ? 1.6 : (mat == 1 ? 0.0 : 0.10);
  col += keyc * specs * pow(max(dot(n, Hh), 0.0), specp) * sh;
  float fres = pow(1.0 - max(dot(n, V), 0.0), 3.0);
  col += skyc * fres * (mat == 1 ? 0.08 : 0.28) * ao;
  // aerial perspective
  float dist = length(v_wp - camPos);
  vec3 fogc = srgb2lin(vec3(0.86, 0.90, 0.96));
  col = mix(col, fogc*1.0, clamp((dist - 16.0)/30.0, 0.0, 0.55));
  // tone map
  col = col / (1.0 + col*0.28);
  col = pow(col*1.08, vec3(1.0/2.2));
  frag = vec4(mix(col, vec3(1.0), 0.0), fade);
}"""
SHADOW_VS = """
#version 330
in vec3 in_pos; uniform mat4 M; uniform mat4 LVP;
void main(){ gl_Position = LVP * M * vec4(in_pos, 1.0); }"""
SHADOW_FS = """#version 330
void main(){}"""
SKY_VS = """#version 330
in vec2 in_vert; out vec2 uv; void main(){ uv = in_vert*0.5+0.5; gl_Position = vec4(in_vert, 0.9999, 1.0); }"""
SKY_FS = """#version 330
in vec2 uv; out vec4 frag; uniform float time; uniform vec3 cTop; uniform vec3 cMid; uniform vec3 cHor;
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
float vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec3 top = cTop, mid = cMid, hor = cHor;
  float y = uv.y * 0.75 + 0.15;
  vec3 c = mix(hor, mid, smoothstep(0.35, 0.6, y));
  c = mix(c, top, smoothstep(0.6, 1.0, y));
  float n = vn(uv*vec2(60.0, 110.0))*0.5 + vn(uv*vec2(14.0,26.0))*0.5;
  c *= 0.97 + 0.05*n;
  frag = vec4(c, 1.0);
}"""
prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
sprog = ctx.program(vertex_shader=SHADOW_VS, fragment_shader=SHADOW_FS)
skyprog = ctx.program(vertex_shader=SKY_VS, fragment_shader=SKY_FS)
sky_vao = ctx.vertex_array(skyprog, [(ctx.buffer(np.array([-1, -1, 3, -1, -1, 3], "f4")), "2f", "in_vert")])

class Mesh:
    def __init__(self, m):
        self.name = m.get("name")
        data = np.concatenate([m["v"], m["n"], m["c"], m["ao"][:, None]], 1).astype("f4")
        self.vbo = ctx.buffer(data.tobytes()); self.ibo = ctx.buffer(m["f"].astype("u4").tobytes())
        self.vao = ctx.vertex_array(prog, [(self.vbo, "3f 3f 3f 1f", "in_pos", "in_nrm", "in_col", "in_ao")], self.ibo)
        self.svao = ctx.vertex_array(sprog, [(self.vbo, "3f 36x", "in_pos")], self.ibo)

# ---------------- math ----------------
def trans(x, y, z): m = np.eye(4); m[:3, 3] = (x, y, z); return m
def scale(sx, sy=None, sz=None):
    sy = sx if sy is None else sy; sz = sx if sz is None else sz
    return np.diag([sx, sy, sz, 1.0])
def roty(a): c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c; return m
def rotz(a): c, s = math.cos(a), math.sin(a); m = np.eye(4); m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c; return m
def rotx(a): c, s = math.cos(a), math.sin(a); m = np.eye(4); m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c; return m
def align_up(nrm, amt=1.0):
    up = np.array([0, 1.0, 0]); n = up * (1 - amt) + np.asarray(nrm) * amt; n /= np.linalg.norm(n)
    v = np.cross(up, n); s = np.linalg.norm(v); c = np.dot(up, n)
    if s < 1e-6: return np.eye(4)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2); m = np.eye(4); m[:3, :3] = R; return m
def perspective(fovy, aspect, n, f):
    t = 1 / math.tan(math.radians(fovy) / 2); m = np.zeros((4, 4))
    m[0, 0] = t / aspect; m[1, 1] = t; m[2, 2] = (f + n) / (n - f); m[2, 3] = 2 * f * n / (n - f); m[3, 2] = -1; return m
def ortho(l, r, b, t, n, f):
    m = np.eye(4); m[0, 0] = 2 / (r - l); m[1, 1] = 2 / (t - b); m[2, 2] = -2 / (f - n)
    m[0, 3] = -(r + l) / (r - l); m[1, 3] = -(t + b) / (t - b); m[2, 3] = -(f + n) / (f - n); return m
def look_at(eye, tgt, up=(0, 1, 0)):
    eye, tgt, up = map(np.asarray, (eye, tgt, up)); f = tgt - eye; f = f / np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4); m[0, :3], m[1, :3], m[2, :3] = s, u, -f; m[:3, 3] = -m[:3, :3] @ eye; return m
def gl(m): return tuple(np.asarray(m, "f4").T.ravel())
def nmat(m):
    a = np.linalg.inv(m[:3, :3]).T; return tuple(np.asarray(a, "f4").T.ravel())
def ground_n(x, z):
    e = 0.02
    dx = (ground_h(x + e, z) - ground_h(x - e, z)) / (2 * e); dz = (ground_h(x, z + e) - ground_h(x, z - e)) / (2 * e)
    n = np.array([-dx, 1, -dz]); return n / np.linalg.norm(n)
def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def clamp01(u): return min(max(u, 0.0), 1.0)

