"""3D claymation renderer: moderngl (headless EGL) + skia overlays, piped to ffmpeg.
python3 render.py            -> out/dino_count.mp4
python3 render.py x 3 10 20  -> stills at those seconds (out/still_XX.png)"""
import sys, json, math, pickle, subprocess, time
import numpy as np, moderngl, skia
import timeline as T
from meshes import hill_height

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
uniform float fade;
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
  vec3 keyc = vec3(1.0, 0.93, 0.82)*2.3;
  vec3 skyc = vec3(0.55, 0.68, 0.95)*0.85;
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
in vec2 uv; out vec4 frag; uniform float time;
float h(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
float vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  return mix(mix(h(i),h(i+vec2(1,0)),f.x), mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x), f.y); }
void main(){
  vec3 top = vec3(0.56, 0.78, 0.95), mid = vec3(0.74, 0.87, 0.98), hor = vec3(0.99, 0.91, 0.82);
  float y = uv.y;
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
    dx = (hill_height(x + e, z) - hill_height(x - e, z)) / (2 * e); dz = (hill_height(x, z + e) - hill_height(x, z - e)) / (2 * e)
    n = np.array([-dx, 1, -dz]); return n / np.linalg.norm(n)
def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def clamp01(u): return min(max(u, 0.0), 1.0)

# ---------------- scene setup ----------------
dmesh = []
for d in D["dinos"]:
    parts = {k: Mesh(p["mesh"]) for k, p in d["parts"].items() if "mesh" in p}
    dmesh.append(parts)
EYE_W, EYE_P = Mesh(D["eye_w"]), Mesh(D["eye_p"])
DIG = {k: (Mesh(f), Mesh(b)) for k, (f, b) in D["digits"].items()}
SC = {k: Mesh(m) for k, m in D["scene"].items()}

# arrival order = list order. slots: (x, z, final yaw, side)
SLOTS = [(-1.55, -1.1, -1.0, -4.9, -1.1), (0.0, -1.15, -1.5, 0.0, -5.2), (1.55, -1.1, -2.15, 4.9, -1.1),
         (-0.85, 1.5, -1.05, -4.3, 1.5), (0.85, 1.5, -2.1, 4.3, 1.5)]
CAM_EYE0 = np.array([0.0, 2.7, 11.2]); CAM_TGT = np.array([0.0, 2.05, 0.0])
rng = np.random.default_rng(11)
FLOWERS = []
pastel = [(1.0, .72, .82), (1.0, .85, .6), (.78, .72, 1.0), (.7, .86, 1.0), (1.0, 1.0, 1.0), (1.0, .78, .7)]
while len(FLOWERS) < 34:
    x, z = rng.uniform(-4.5, 4.5), rng.uniform(-3.5, 3.4)
    if any((x - s[0]) ** 2 + (z - s[1]) ** 2 < 0.75 for s in SLOTS): continue
    if abs(z - 1.5) < 0.4 and abs(x) > 0.5: continue        # keep walk lanes clear
    if abs(z + 1.1) < 0.4: continue
    if abs(x) < 0.5 and z < -1.0: continue
    FLOWERS.append((x, z, rng.uniform(0, 6.28), pastel[len(FLOWERS) % len(pastel)], rng.uniform(0.9, 1.4)))
ROCKS = [(-3.3, 2.2, 0.8), (3.4, 2.4, 0.7), (-2.6, -1.8, 0.6), (2.8, -1.4, 0.9), (-1.9, 5.6, 1.1), (2.1, 6.0, 1.3)]
for k, (x, z, s) in enumerate([(-1.6, 4.6, 2.4), (-2.3, 5.2, 2.0), (-1.0, 5.9, 2.2), (1.4, 4.9, 2.3), (2.4, 5.4, 2.6),
                               (0.9, 6.2, 2.0), (-2.6, 3.6, 1.8), (2.7, 3.9, 1.9), (-0.4, 6.6, 2.4), (1.8, 6.7, 2.1)]):
    FLOWERS.append((x, z, k * 1.3, pastel[(k + 2) % len(pastel)], s))
CONF = [(rng.uniform(-3.2, 3.2), rng.uniform(5.0, 9.5), rng.uniform(-1.5, 2.5), rng.uniform(0, 6.28), rng.uniform(2, 5),
         pastel[i % len(pastel)], rng.uniform(1.2, 2.0)) for i in range(150)]

# ---------------- animation ----------------
FOOT = [0, 1, 2, 2.5, 3]
POPS_BY_DINO = {i: [p for p in T.POPS if p[1] == i] for i in range(5)}
def jump_curve(beat, b, dur=0.5, hgt=0.25):
    u = (beat - b) / dur
    if u < -0.15 or u > 1.4: return 0.0, 0.0
    if u < 0: return 0.0, -0.08 * math.sin(math.pi * (u + 0.15) / 0.15)        # anticipation squash
    if u <= 1: return hgt * math.sin(math.pi * u), 0.06 * math.sin(math.pi * u)  # stretch in air
    v = (u - 1) / 0.4; return 0.0, -0.14 * math.exp(-v * 4) * math.cos(v * 8)     # landing squash

def dino_state(i, tsec):
    beat = tsec / T.BEAT
    sx, sz, fyaw, x0, z0 = SLOTS[i]
    b0 = T.arrival_start(i + 1)
    lb = beat - b0
    st = dict(vis=True, x=sx, z=sz, yaw=fyaw, y=0.0, sq=0.0, legs=[(0.0, 0.0)] * 4, head=(0.0, 0.0), tail=0.0, roll=0.0)
    if lb < -0.6: st["vis"] = False; return st
    t_ = tsec
    st["tail"] = 0.25 * math.sin(2 * math.pi * t_ / 1.3 + i)
    st["head"] = (0.04 * math.sin(2 * math.pi * t_ / 2.1 + i * 1.7), 0.05 * math.sin(2 * math.pi * t_ / 2.9 + i))
    st["sq"] = 0.015 * math.sin(2 * math.pi * t_ / 1.7 + i)
    if lb < 3.6:                                   # ---- stomping walk-in ----
        walk_yaw = math.atan2(-(sz - z0), sx - x0)
        # progress keyed to footfalls
        k = 0
        while k < len(FOOT) - 1 and lb >= FOOT[k + 1]: k += 1
        nfoot = len(FOOT)
        if lb < 0:
            prog_ = 0.0; u = 0.0; k = -1
        elif lb >= FOOT[-1]:
            prog_ = 1.0; u = 1.0
        else:
            u = (lb - FOOT[k]) / (FOOT[k + 1] - FOOT[k])
            prog_ = (k + ease(u)) / (nfoot - 1)
        if lb < 0: prog_ = -0.1 * (1 + lb / 0.6) * 0
        st["x"] = x0 + (sx - x0) * prog_; st["z"] = z0 + (sz - z0) * prog_
        big = k in (0, 1) or k == -1
        if 0 <= lb < FOOT[-1]:
            hop = (0.22 if big else 0.1) * math.sin(math.pi * u)
            st["y"] = hop
            pair = k % 2
            lift = math.sin(math.pi * u) * (0.2 if big else 0.12)
            sw = 0.5 * math.sin(math.pi * u) if big else 0.3 * math.sin(math.pi * u)
            legs = []
            for li in range(4):
                on = (li in (0, 3)) if pair == 0 else (li in (1, 2))
                legs.append((lift if on else 0.0, sw if on else 0.0))
            st["legs"] = legs
            st["sq"] += 0.05 * math.sin(math.pi * u)
        # landing squash on every footfall
        for f in FOOT:
            dtb = lb - f
            if 0 <= dtb < 0.8:
                amp = 0.16 if f in (0, 1) else (0.09 if f < 3 else 0.12)
                st["sq"] -= amp * math.exp(-dtb * 6) * math.cos(dtb * 9)
        turn = ease((lb - 3.0) / 0.6)
        dy = (fyaw - walk_yaw + math.pi) % (2 * math.pi) - math.pi
        st["yaw"] = walk_yaw + dy * turn
        if lb < 0: st["legs"] = [(0.0, 0.0)] * 4
    # ---- count / countdown hops ----
    for (pb, di, m, bigp) in POPS_BY_DINO[i]:
        if pb == b0 + 3: continue
        hgt = 0.45 if pb >= 68 else 0.24
        y, s = jump_curve(beat, pb, 0.55 if pb >= 68 else 0.45, hgt)
        st["y"] += y; st["sq"] += s
    # ---- dance: chorus 2 + "count back down" ----
    if 56 <= beat < 68:
        amp = 1.0 if beat < 64 else 0.6
        ph = math.pi * (beat - 56)
        st["yaw"] += amp * 0.35 * math.sin(ph / 2)
        st["roll"] = amp * 0.10 * math.sin(ph / 2 + 0.3)
        st["y"] += amp * 0.12 * abs(math.sin(ph))
        st["sq"] += amp * 0.06 * (abs(math.sin(ph)) - 0.5)
        lift = amp * 0.12 * max(0, math.sin(ph))
        alt = int(beat - 56) % 2
        st["legs"] = [(lift if (li % 2) == alt else 0.0, 0.2 * lift) for li in range(4)]
        st["head"] = (0.06 * math.sin(ph), amp * 0.22 * math.sin(ph / 2 + 1.0))
        st["tail"] = amp * 0.6 * math.sin(ph)
    if 56 <= beat < 58 or 76 <= beat < 78:        # big stomps
        for f in (56, 57, 76, 77):
            dtb = beat - f
            if 0 <= dtb < 0.8: st["sq"] -= 0.15 * math.exp(-dtb * 6) * math.cos(dtb * 9)
            if -0.5 <= dtb < 0: st["y"] += 0.15 * math.sin(math.pi * (dtb + 0.5) / 0.5)
    # ---- hooray jump + spin ----
    if 73.7 <= beat < 76:
        y, s = jump_curve(beat, 74 + 0.05 * i, 0.9, 0.75)
        st["y"] += y; st["sq"] += s
        u = clamp01((beat - 74 - 0.05 * i) / 0.9)
        st["yaw"] += 2 * math.pi * ease(u) * (1 if i % 2 else -1)
    # ---- goodbye wave ----
    if beat >= 78:
        ph = math.pi * (beat - 78)
        damp = 1.0 if beat < 82 else max(0.0, 1 - (beat - 82) / 4)
        st["head"] = (0.05 * math.sin(ph) * damp, 0.25 * math.sin(ph * 0.5) * damp)
        st["tail"] = 0.7 * math.sin(ph) * damp
        st["roll"] = 0.08 * math.sin(ph * 0.5) * damp
    return st

def blink(i, tsec):
    period = 3.1 + 0.37 * i; ph = (tsec + i * 0.9) % period
    return 1.0 - 0.92 * math.exp(-((ph - 0.1) / 0.06) ** 2)

# ---------------- camera & light ----------------
PROJ = perspective(44.0, W / H, 0.4, 80.0)
LDIR = np.array([-0.55, 0.85, 0.5]); LDIR /= np.linalg.norm(LDIR)
LVIEW = look_at(LDIR * 20 + np.array([0, 0, -0.5]), np.array([0, 0, -0.5]), (0, 1, 0))
LVP = ortho(-9, 9, -9, 9, 1, 45) @ LVIEW

shadow_tex = ctx.depth_texture((2048, 2048)); shadow_tex.compare_func = "<="
shadow_tex.repeat_x = shadow_tex.repeat_y = False
shadow_fbo = ctx.framebuffer(depth_attachment=shadow_tex)
SS = 4
msaa_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4, samples=SS)],
                           depth_attachment=ctx.depth_renderbuffer((W, H), samples=SS))
res_fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((W, H), 4)])

def build_draws(tsec):
    """returns list of (mesh, M, uniforms dict, casts_shadow)"""
    beat = tsec / T.BEAT
    draws = []
    U = lambda **k: k
    # ground + scenery
    draws.append((SC["ground"], np.eye(4), U(mat=1, bump=0.9), False))
    for (x, z, s) in ROCKS:
        draws.append((SC["rock"], trans(x, hill_height(x, z) - 0.04, z) @ roty(x * 3) @ scale(s), U(mat=0, bump=1.0), True))
    stomp_wobble = 0.0
    for (b, s_, who) in T.STOMPS:
        dtb = beat - b
        if 0 <= dtb < 2.5: stomp_wobble += s_ * math.exp(-dtb * 2.2) * math.sin(dtb * 12)
    for fi, (x, z, r, c, s) in enumerate(FLOWERS):
        y = hill_height(x, z)
        wob = 0.06 * math.sin(tsec * 1.6 + fi) + 0.25 * stomp_wobble
        M = trans(x, y - 0.01, z) @ roty(r) @ rotz(wob) @ scale(s, s * (1 - 0.15 * stomp_wobble * math.sin(fi)), s)
        draws.append((SC["flower"], M, U(mat=0, bump=0.0, tint=c, tintMix=-1.0), False))
    for (x, z, s) in [(-4.3, -2.2, 1.25), (4.4, -3.4, 1.4), (-6.5, -7.5, 1.6), (6.8, -8.5, 1.8), (2.5, -9.5, 1.3)]:
        draws.append((SC["tree"], trans(x, hill_height(x, z) - 0.05, z) @ roty(x) @ scale(s), U(mat=0, bump=0.8), True))
    # distant hills, volcano, smoke, clouds, sun
    for (x, y, z, sx, sy, sz, c) in [(-9, -1.2, -20, 9, 5.4, 4, (.62, .82, .66)), (8, -1.4, -22, 10, 6.0, 4, (.58, .78, .7)),
                                     (0, -2.4, -26, 14, 7.0, 5, (.66, .8, .78))]:
        draws.append((SC["ball"], trans(x, y, z) @ scale(sx, sy, sz), U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    vx, vz = -2.9, -14.0
    draws.append((SC["volcano"], trans(vx, -0.6, vz) @ scale(1.9), U(mat=0, bump=0.6), False))
    for k in range(3):
        u = ((tsec * 0.12 + k / 3) % 1.0)
        s = 0.5 + 1.1 * u
        draws.append((SC["smoke"], trans(vx + 0.6 * u + 0.12 * math.sin(tsec + k), -0.6 + 3.3 * 1.9 + 0.3 + u * 3.2, vz) @ scale(s * (1 - u ** 3)),
                      U(mat=0, bump=0.3), False))
    for k, (x, y, z) in enumerate([(-3.2, 10.2, -18), (3.8, 12.4, -20), (-0.5, 14.6, -24)]):
        draws.append((SC["cloud"], trans(x + 0.07 * tsec * (1 if k % 2 else -1), y + 0.15 * math.sin(tsec * 0.5 + k), z) @ scale(1.25 + 0.2 * k),
                      U(mat=0, bump=0.4), False))
    draws.append((SC["sun"], trans(4.6, 15.2, -24) @ rotz(tsec * 0.15) @ scale(1.3), U(mat=0, bump=0.4), False))

    # dinosaurs
    contacts = []
    for i, d in enumerate(D["dinos"]):
        st = dino_state(i, tsec)
        if not st["vis"]: continue
        gy = hill_height(st["x"], st["z"])
        tilt = align_up(ground_n(st["x"], st["z"]), 0.6)
        sq = st["sq"]
        Mroot = trans(st["x"], gy - 0.015 + st["y"], st["z"]) @ tilt @ roty(st["yaw"]) @ rotx(st["roll"]) @ scale(1 - sq * 0.5, 1 + sq, 1 - sq * 0.5)
        parts = d["parts"]; pm = dmesh[i]
        contacts.append((st["x"], st["z"], 0.9 if d["kind"] != "ankylo" else 1.05, max(0.0, 1 - st["y"] * 1.6)))
        unif = U(mat=0, bump=1.0, seed=float(i * 7.3))
        draws.append((pm["body"], Mroot, unif, True))
        for li in range(d["legs"]):
            pv = parts[f"leg{li}"]["pivot"]
            lift, sw = st["legs"][li] if li < len(st["legs"]) else (0, 0)
            Ml = Mroot @ trans(0, lift, 0) @ trans(*pv) @ rotz(-sw * 0.5) @ trans(*(-np.array(pv)))
            draws.append((pm[f"leg{li}"], Ml, unif, True))
        hp = parts["head"]["pivot"]
        pitch, rollh = st["head"]
        Mh = Mroot @ trans(*hp) @ rotz(pitch) @ rotx(rollh) @ trans(*(-np.array(hp)))
        draws.append((pm["head"], Mh, unif, True))
        tp = parts["tail"]["pivot"]
        Mt = Mroot @ trans(*tp) @ roty(st["tail"] * 0.5) @ trans(*(-np.array(tp)))
        draws.append((pm["tail"], Mt, unif, True))
        er = parts["eyes"]["r"]; bl = blink(i, tsec)
        for c in parts["eyes"]["centers"]:
            Me = Mh @ trans(*c) @ scale(er * 0.75, er * bl, er)
            draws.append((EYE_W, Me, U(mat=2, bump=0.0), False))
            if bl > 0.3:
                pc = np.array(c) + np.array([er * 0.62, -er * 0.05, -np.sign(c[2]) * er * 0.08])
                draws.append((EYE_P, Mh @ trans(*pc) @ scale(er * 0.45, er * 0.6 * bl, er * 0.55), U(mat=2, bump=0.0), False))
                hc = pc + np.array([er * 0.4, er * 0.25, er * 0.15])
                draws.append((EYE_W, Mh @ trans(*hc) @ scale(er * 0.14 * bl), U(mat=3, bump=0.0), False))

    # dust puffs on stomps
    for (b, s_, who) in T.STOMPS:
        dts = tsec - T.t(b)
        if not (0 <= dts < 0.5): continue
        whos = range(5) if who == 99 else ([who] if who >= 0 else [])
        for i in whos:
            st = dino_state(i, T.t(b))
            if not st["vis"]: continue
            for k in range(7):
                a = k * 2 * math.pi / 7 + i
                r = 0.45 + 0.6 * dts * 2
                x, z = st["x"] + r * math.cos(a), st["z"] + r * 0.7 * math.sin(a)
                sz_ = 0.09 * s_ * (1 - dts / 0.5) ** 1.5 * (1.2 + 0.4 * math.sin(k * 3.1))
                if sz_ <= 0.005: continue
                draws.append((SC["ball"], trans(x, hill_height(x, z) + 0.05 + dts * 0.5, z) @ scale(sz_),
                              U(mat=0, bump=0.0, tint=(0.93, 0.86, 0.74), tintMix=1.0), False))

    # numbers
    camdir = None
    for (b, di, m, bigp) in T.POPS:
        lb = beat - b
        if lb < 0: continue
        arrival_big = bigp and b < 68
        if arrival_big:
            end = 0.92
        elif bigp:
            end = 74.0 - b if m == 1 else 0.92
        else:
            seg_end = T.arrival_start(int(b - T.ARRIVE0) // 8 + 1) + 8 - 0.25
            end = seg_end - b
        if lb > end + 0.25: continue
        u = lb * T.BEAT
        s = 1 - math.exp(-u * 9) * math.cos(u * 18)
        if lb > end: s *= max(0.0, 1 - (lb - end) / 0.25) ** 2
        size = 1.3 if bigp else 0.62
        st = dino_state(di, tsec)
        d = D["dinos"][di]
        gy = hill_height(st["x"], st["z"])
        y = gy + d["head_top"] + 0.35 + size * 0.55 + 0.06 * math.sin(tsec * 3 + di) + st["y"] * 0.6
        x, z = st["x"], st["z"] + 0.15
        if bigp and arrival_big:
            y += 0.15
        if bigp and not arrival_big:          # countdown: one big number at a time, centre sky
            if m != 1: end = 0.92
            x, z, y = 0.0, 0.5, 4.95 + 0.08 * math.sin(tsec * 3)
            size = 1.7
        yawc = math.atan2(CAM_EYE0[0] - x, CAM_EYE0[2] - z)
        M = trans(x, y, z) @ roty(yawc) @ rotz(0.12 * math.sin(tsec * 2.4 + m)) @ scale(size * max(s, 0.001))
        f, bk = DIG[str(m)]
        draws.append((bk, M, U(mat=4, bump=0.25, tint=(1.0, 1.0, 1.0), tintMix=1.0, seed=3.0), False))
        draws.append((f, M, U(mat=4, bump=0.35, tint=tuple(d["numcol"]), tintMix=1.0, seed=5.0), False))

    # confetti
    if beat >= 73.9:
        dtc = tsec - T.t(73.9)
        for (x, y0, z, r0, spin, c, sp) in CONF:
            y = y0 - sp * dtc
            gy = hill_height(x, z)
            if y < gy + 0.03: y = gy + 0.03
            M = trans(x + 0.25 * math.sin(dtc * 2 + r0), y, z) @ roty(r0 + dtc * spin) @ rotx(r0 * 0.7 + dtc * spin * 0.6 * (1 if y > gy + 0.05 else 0)) @ scale(0.075)
            draws.append((SC["disc"], M, U(mat=0, bump=0.0, tint=c, tintMix=1.0), False))
    return draws, contacts

def render_frame(tsec):
    draws, contacts = build_draws(tsec)
    push = 1 - 0.035 * ease(tsec / T.DURATION)
    eye = CAM_TGT + (CAM_EYE0 - CAM_TGT) * push
    VPm = PROJ @ look_at(eye, CAM_TGT)
    # shadow pass
    shadow_fbo.use(); shadow_fbo.clear(depth=1.0)
    sprog["LVP"].value = gl(LVP)
    ctx.disable(moderngl.CULL_FACE)
    for (mesh, M, u, cast) in draws:
        if cast:
            sprog["M"].value = gl(M); mesh.svao.render()
    ctx.enable(moderngl.CULL_FACE)
    # colour pass
    msaa_fbo.use(); msaa_fbo.clear(0, 0, 0, 1, depth=1.0)
    ctx.disable(moderngl.DEPTH_TEST)
    sky_vao.render()
    ctx.enable(moderngl.DEPTH_TEST)
    shadow_tex.use(0)
    prog["shadowMap"].value = 0
    prog["VP"].value = gl(VPm); prog["LVP"].value = gl(LVP); prog["camPos"].value = tuple(eye)
    cvals = [(c[0], c[1], c[2], c[3]) for c in contacts] + [(0, 0, 1, 0)] * (8 - len(contacts))
    prog["contact"].value = cvals[:8]; prog["nContact"].value = len(contacts)
    prog["fade"].value = 1.0
    for (mesh, M, u, cast) in draws:
        prog["M"].value = gl(M); prog["NM"].value = nmat(M)
        prog["mat"].value = u.get("mat", 0); prog["bump"].value = u.get("bump", 1.0)
        prog["tint"].value = tuple(u.get("tint", (1, 1, 1))); prog["tintMix"].value = u.get("tintMix", 0.0)
        prog["seed"].value = u.get("seed", 0.0)
        ctx.disable(moderngl.CULL_FACE) if mesh is SC["ground"] else ctx.enable(moderngl.CULL_FACE)
        mesh.vao.render()
    ctx.copy_framebuffer(res_fbo, msaa_fbo)
    img = np.frombuffer(res_fbo.read(components=4), np.uint8).reshape(H, W, 4)[::-1].copy()
    img[..., 3] = 255
    return img

# ---------------- 2D overlay (captions, title, vignette, grain) ----------------
WORDS = json.load(open("out/word_times.json"))
LINES = {}
for w in WORDS: LINES.setdefault(w["line"], []).append(w)
LINE_LIST = sorted(LINES.values(), key=lambda ws: ws[0]["t0"])
tf = skia.Typeface.MakeFromFile("assets/Fredoka.ttf")
try:
    arg = skia.FontArguments(); arg.setVariationDesignPosition(skia.FontArguments.VariationPosition(skia.FontArguments.VariationPosition.Coordinates([skia.FontArguments.VariationPosition.Coordinate(0x77676874, 650)])))
    tf = tf.makeClone(arg)
except Exception as e:
    print("font var fail", e)
FONT = skia.Font(tf, 76); TFONT = skia.Font(tf, 150)
grain = (np.random.default_rng(1).integers(0, 255, (H, W), dtype=np.uint8))
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.22 * np.clip((((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.25, 0, 1)).astype(np.float32)

def current_line(tsec):
    for li, ws in enumerate(LINE_LIST):
        start = ws[0]["t0"] - 0.3
        nxt = LINE_LIST[li + 1][0]["t0"] - 0.3 if li + 1 < len(LINE_LIST) else 1e9
        end = min(ws[-1]["t1"] + 0.45, nxt)
        if start <= tsec < end: return ws, start, end
    return None, 0, 0

def wrap_words(ws):
    lines, cur, wsum = [], [], 0
    space = FONT.measureText(" ")
    for w in ws:
        wl = FONT.measureText(w["w"])
        if cur and wsum + space + wl > 960:
            lines.append(cur); cur, wsum = [], 0
        wsum += (space if cur else 0) + wl; cur.append((w, wl))
    if cur: lines.append(cur)
    return lines

def overlay(img, tsec):
    surf = skia.Surface(img)          # RGBA uint8 view
    cv = surf.getCanvas()
    stroke = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=16, Color=skia.Color(74, 43, 69),
                        StrokeJoin=skia.Paint.kRound_Join)
    fill_w = skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255))
    fill_y = skia.Paint(AntiAlias=True, Color=skia.Color(255, 214, 64))
    # title during intro
    if tsec < 3.9:
        a = clamp01(tsec / 0.3) * clamp01((3.9 - tsec) / 0.35)
        title = "Dino Count!"
        cols = [(246, 120, 170), (250, 190, 60), (110, 175, 235), (255, 150, 90), (160, 130, 230)]
        tw = TFONT.measureText(title); x = (W - tw) / 2; y0 = 640 - 12 * math.sin(tsec * 4)
        for k, chh in enumerate(title):
            cw = TFONT.measureText(chh)
            bob = 10 * math.sin(tsec * 6 + k * 0.7)
            st_ = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=22, Color=skia.Color(74, 43, 69, int(255 * a)), StrokeJoin=skia.Paint.kRound_Join)
            r, g, b = cols[k % 5]
            fp = skia.Paint(AntiAlias=True, Color=skia.Color(r, g, b, int(255 * a)))
            cv.drawString(chh, x, y0 + bob, TFONT, st_); cv.drawString(chh, x, y0 + bob, TFONT, fp)
            x += cw
    ws, start, end = current_line(tsec)
    if ws:
        a = clamp01((tsec - start) / 0.15) * clamp01((end - tsec) / 0.15)
        stroke.setAlphaf(a); fill_w.setAlphaf(a); fill_y.setAlphaf(a)
        rows = wrap_words(ws)
        y = 1520 if len(rows) == 1 else 1480
        space = FONT.measureText(" ")
        for row in rows:
            tw = sum(wl for _, wl in row) + space * (len(row) - 1); x = (W - tw) / 2
            for (w, wl) in row:
                on = w["t0"] - 0.03 <= tsec < max(w["t1"], w["t0"] + 0.25)
                yb = y - (6 if on else 0)
                cv.drawString(w["w"], x, yb, FONT, stroke)
                cv.drawString(w["w"], x, yb, FONT, fill_y if on else fill_w)
                x += wl + space
            y += 92
    out = img[..., :3].astype(np.float32) * vig[..., None]
    out += (grain[..., None].astype(np.float32) - 127) * (9 / 255.0)
    return np.clip(out, 0, 255).astype(np.uint8)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "x":
        for s in sys.argv[2:]:
            t0 = time.time(); fr = overlay(render_frame(float(s)), float(s))
            skia.Image.fromarray(np.dstack([fr, np.full(fr.shape[:2], 255, np.uint8)])).save(f"out/still_{float(s):05.2f}.png")
            print(s, round(time.time() - t0, 2), "s")
        sys.exit()
    nfr = int(T.DURATION * FPS)
    if len(sys.argv) > 1 and sys.argv[1] == "seg":
        f0, f1, outp, audio = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], []
    else:                                     # full render with audio: python3 render.py [out.mp4] [max_frames]
        outp = sys.argv[1] if len(sys.argv) > 1 else "out/dino_count.mp4"
        f0, f1 = 0, int(sys.argv[2]) if len(sys.argv) > 2 else nfr
        audio = ["-i", "out/audio.wav", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + \
          audio[:2] + ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"] + audio[2:] + [outp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fi in range(f0, min(f1, nfr)):
        tsec = fi / FPS
        p.stdin.write(overlay(render_frame(tsec), tsec).tobytes())
        if fi % 90 == 0: print(f"frame {fi}/{min(f1, nfr)}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close(); p.wait()
    n = min(f1, nfr) - f0
    print(f"done: {n} frames in {time.time() - t0:.0f}s ({(time.time() - t0) / max(n, 1):.2f} s/frame) -> {outp}", flush=True)
