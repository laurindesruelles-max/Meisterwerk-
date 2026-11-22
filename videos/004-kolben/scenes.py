"""Meisterwerk 004 – alle 3D-Szenen. Aufruf: python3 scenes.py <szene> <variante> <outdir> <frames> [still]"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector
import lib3d as L
SCN, VAR, OUT, N = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
STILL = len(sys.argv) > 5 and sys.argv[5] == "still"
sc = L.reset()
rnd = random.Random(4)
pi = math.pi

# ---------- Materialien ----------
ALU = L.mat("alu", (0.80, 0.80, 0.82), 1.0, 0.26, bump=0.03)
ALU_ROH = L.mat("alu_roh", (0.62, 0.62, 0.63), 0.9, 0.55, bump=0.25)
STAHL = L.mat("stahl", (0.56, 0.57, 0.6), 1.0, 0.2)
STAHL_D = L.mat("stahl_d", (0.18, 0.18, 0.2), 1.0, 0.35)
GUSS = L.mat("guss", (0.12, 0.12, 0.13), 0.7, 0.7, bump=0.4)
GLAS = L.mat("glas", (0.75, 0.85, 1.0), 0.0, 0.05, alpha=0.12)
ORANGE = (1.0, 0.16, 0.01)
def glowmat(name, base=(0.8, 0.8, 0.82), metal=1.0, rough=0.3, col=ORANGE):
    return L.mat(name, base, metal, rough, emit=col, estr=0.0)
def estr(m): return m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
def ecol(m): return m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
def bcol(m): return m.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
def alpha(m): return m.node_tree.nodes["Principled BSDF"].inputs["Alpha"]

# ---------- Bühne ----------
def dark_stage(floor=True, key=1.0, warm=False):
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.008, 0.008, 0.01, 1)
    if floor:
        L.box("boden", (300, 300, 0.2), loc=(0, 0, -0.1), m=L.mat("boden_d", (0.02, 0.02, 0.022), 0.6, 0.25))
def light_stage():
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.6, 0.62, 1)
    sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    # Hohlkehle
    bm = bmesh.new(); pts = []
    for i in range(13):
        a = i / 12 * pi / 2; pts.append((0, 40 - 12 * math.sin(a) if False else 30 + 12 * (1 - math.cos(a)) * 0 + 0, 0))
    me = bpy.data.meshes.new("cyc")
    prof = [(0, -80, 0), (0, 25, 0)] + [(0, 25 + 12 * math.sin(i / 12 * pi / 2), 12 - 12 * math.cos(i / 12 * pi / 2)) for i in range(1, 13)] + [(0, 37, 70)]
    vs = []
    for x in (-150, 150):
        vs.append([bm.verts.new((x, y, z)) for _, y, z in prof])
    for j in range(len(prof) - 1):
        bm.faces.new((vs[0][j], vs[1][j], vs[1][j + 1], vs[0][j + 1]))
    bm.to_mesh(me); bm.free(); ob = L.link(bpy.data.objects.new("cyc", me))
    L.setmat(ob, L.mat("cycm", (0.62, 0.61, 0.6), 0, 0.8)); L.smooth(ob)
def lights_dark(t=(0, 0, 3), k=1.0, rimcol=(1, .8, .6)):
    L.area("key", (14, -12, 16), 10, 2200 * k, target=t)
    L.area("rim", (-16, 12, 12), 6, 2600 * k, col=rimcol, target=t)
    L.area("rim2", (16, 14, 8), 5, 1500 * k, col=(.6, .75, 1), target=t)
def lights_light(t=(0, 0, 3), k=1.0):
    L.area("key", (12, -14, 18), 16, 3000 * k, target=t)
    L.area("fill", (-16, -10, 8), 14, 900 * k, target=t)
    L.area("rim", (-6, 16, 14), 8, 1500 * k, col=(1, .9, .8), target=t)
def cam(loc, tgt, lens=50, dof=None):
    c, tg = L.camera(loc, tgt, lens)
    if dof:
        c.data.dof.use_dof = True; c.data.dof.focus_object = tg; c.data.dof.aperture_fstop = dof
    return c, tg
def K(ob, f, loc=None, rot=None, s=None):
    if loc is not None: ob.location = loc; ob.keyframe_insert("location", frame=f)
    if rot is not None: ob.rotation_euler = rot; ob.keyframe_insert("rotation_euler", frame=f)
    if s is not None: ob.scale = (s, s, s) if isinstance(s, (int, float)) else s; ob.keyframe_insert("scale", frame=f)
def KV(sock, f, v): sock.default_value = v; sock.keyframe_insert("default_value", frame=f)
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lerpv(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))
def frames(fn):
    for f in range(1, N + 1):
        fn(f, (f - 1) / max(N - 1, 1))
def all_linear():
    for ob in list(bpy.data.objects) + list(bpy.data.materials):
        ad = getattr(ob, "animation_data", None) or (ob.node_tree.animation_data if hasattr(ob, "node_tree") and ob.node_tree else None)
        for a in [getattr(ob, "animation_data", None), ob.node_tree.animation_data if hasattr(ob, "node_tree") and ob.node_tree else None]:
            if a and a.action:
                try:
                    for fc in a.action.fcurves:
                        for k in fc.keyframe_points: k.interpolation = "LINEAR"
                except Exception:
                    try:
                        for lay in a.action.layers:
                            for st in lay.strips:
                                for cb in st.channelbags:
                                    for fc in cb.fcurves:
                                        for k in fc.keyframe_points: k.interpolation = "LINEAR"
                    except Exception: pass

# ---------- Bauteile ----------
def kolben_set(m=ALU, rings=True, pin=True, boss_m=None, name="kolben"):
    k = L.piston(name, m)
    parts = [k]
    if rings:
        for i, z in enumerate([5.07, 4.52, 3.78]):
            r = L.ring(f"ring{i}", z, h=0.13 if i < 2 else 0.30, m=STAHL_D if i == 0 else STAHL); r.parent = k; parts.append(r)
    if pin:
        p = L.pin(STAHL); p.parent = k; parts.append(p)
    return k, parts
def ghost_cyl(z0, z1, r=4.38):
    c = L.lathe("zyl", [(r, z0), (r, z1)], 96, GLAS)
    rimm = L.mat("rim", (1, 1, 1), emit=(1, .45, .1), estr=3)
    for z in (z0, z1):
        t = L.lathe("rimr", [(r - 0.03, z), (r + 0.06, z), (r + 0.06, z + 0.06), (r - 0.03, z + 0.06), (r - 0.03, z)], 96, rimm)
    return c
def kurbeltrieb(r=4.3, Lc=14.5):
    """liefert Funktion set(f, theta)"""
    zc = -Lc - r
    k, parts = kolben_set()
    pl = L.conrod(STAHL_D, Lc)
    cr = L.empty("kurbel", (0, 0, zc))
    web = L.box("wange", (1.0, 3.2, r * 2 + 3), loc=(1.3, 0, r / 2), m=STAHL)
    web2 = L.box("wange2", (1.0, 3.2, r * 2 + 3), loc=(-1.3, 0, r / 2), m=STAHL)
    cp = L.cyl("hubzapfen", 2.15, 3.6, loc=(0, 0, r), rot=(0, pi / 2, 0), m=STAHL)
    mj = L.cyl("welle", 2.4, 12, loc=(0, 0, 0), rot=(0, pi / 2, 0), m=STAHL)
    for o in (web, web2, cp, mj): o.parent = cr
    def set_(f, th):
        yp = r * math.cos(th) + math.sqrt(Lc ** 2 - (r * math.sin(th)) ** 2)
        pz = zc + yp
        K(k, f, loc=(0, 0, pz - 2.55))
        a = math.asin(r * math.sin(th) / Lc)
        K(pl, f, loc=(0, 0, pz), rot=(a, 0, 0))
        K(cr, f, rot=(-th, 0, 0))
        return pz
    return set_, k, pl, cr, zc

# ======================= SZENEN =======================
def s_motor():
    dark_stage(floor=False)
    set_, k, pl, cr, zc = kurbeltrieb()
    ghost_cyl(-11.6, 4.0)
    fl = L.mat("flamme", (0, 0, 0), emit=(1, .2, .02), estr=0)
    flame = L.lathe("flame", [(0, 3.5), (4.2, 3.5), (4.2, 3.8), (3.0, 4.2), (0, 4.4)], 64, fl); flame.hide_render = False
    pt = L.point("blitz", (0, 0, 5.5), 0, col=(1, .55, .2), r=2)
    lights_dark(t=(0, 0, -4))
    v = VAR
    revs = {"slow": 0.5, "wide": 0.35, "tacho": 2.0, "side": 1.0, "otut": 1.0, "fast": 6.0, "speed": 1.0, "zuend": 0.5,
            "zuend2": 0.5, "laeuft": 4.0, "laeuft2": 6.0, "finale": 5.0}.get(v, 1)
    th0 = {"zuend": -0.25, "zuend2": -0.2, "slow": pi}.get(v, 0)
    camd = {"slow": ((16, -26, 4), (5, -18, 2), (0, 0, -3), 40),
            "wide": ((-24, -30, 6), (24, -30, 4), (0, 0, -8), 35),
            "tacho": ((10, -30, -8), (14, -26, -6), (0, 0, -9), 35),
            "side": ((40, 0, -9), (38, -4, -9), (0, 0, -10), 40),
            "otut": ((30, -16, -3), (26, -14, -4), (0, 0, -5), 45),
            "fast": ((6, -20, 6), (4, -16, 4), (0, 0, -2), 40),
            "speed": ((22, -12, -2), (20, -16, -3), (0, 0, -4), 45),
            "zuend": ((10, -16, 8), (8, -13, 6), (0, 0, 1), 40),
            "zuend2": ((-10, -14, 10), (-6, -13, 8), (0, 0, 2), 40),
            "laeuft": ((-18, -24, 0), (-12, -27, 2), (0, 0, -6), 38),
            "laeuft2": ((18, -10, -22), (20, -16, -16), (0, 0, -16), 40),
            "finale": ((0, -40, -2), (0, -24, 0), (0, 0, -5), 40)}[v]
    c, tg = cam(camd[0], camd[2], camd[3])
    if v == "fast": sc.render.use_motion_blur = True
    def fn(f, u):
        th = th0 + 2 * pi * revs * u
        if v in ("slow",): th = th0 + 2 * pi * revs * ease(u)
        set_(f, th)
        K(c, f, loc=lerpv(camd[0], camd[1], ease(u)))
        if v in ("zuend", "zuend2"):
            e = max(0, 1 - abs(u - 0.18) / 0.12) if u < 0.3 else max(0, (0.6 - u) * 1.2)
            KV(estr(fl), f, 4 * e); pt.data.energy = 6000 * e; pt.data.keyframe_insert("energy", frame=f)
            K(flame, f, loc=(0, 0, k.location.z - 3.45 + 0.0), s=(1, 1, 0.6 + 2.0 * min(1, u / 0.2)))
        else:
            K(flame, f, s=0.001)
    frames(fn)

def s_messuhr():
    v = VAR
    heiss = v == "heiss"
    (dark_stage() if v != "kalt" else light_stage())
    m = glowmat("alu_g") if heiss else ALU
    k, parts = kolben_set(m, rings=True)
    tt = L.cyl("teller", 5.2, 0.6, loc=(0, 0, -0.3), m=STAHL_D)
    k.parent = None
    # Messuhr
    body = L.cyl("uhr", 2.4, 0.9, loc=(0, -9.2, 2.2), rot=(pi / 2, 0, 0), m=STAHL)
    face = L.cyl("zifferblatt", 2.15, 0.1, loc=(0, -9.68, 2.2), rot=(pi / 2, 0, 0), m=L.mat("ziff", (0.95, 0.95, 0.93), 0, 0.4))
    for i in range(40):
        a = i / 40 * 2 * pi; ln = 0.35 if i % 5 == 0 else 0.18
        L.box(f"tick{i}", (0.05, 0.02, ln), loc=(1.85 * math.sin(a), -9.75, 2.2 + 1.85 * math.cos(a)), rot=(0, a, 0), m=STAHL_D)
    ndl = L.empty("zeiger_p", (0, -9.8, 2.2))
    nd = L.box("zeiger", (0.07, 0.03, 1.7), loc=(0, 0, 0.75), m=L.mat("zeigm", (0.9, 0.12, 0.05), 0, 0.4)); nd.parent = ndl
    stem = L.cyl("taster", 0.18, 4.6, loc=(0, -6.6, 2.2), rot=(pi / 2, 0, 0), m=STAHL)
    arm = L.box("stativ", (0.6, 0.6, 9), loc=(0, -9.2, -2.3), m=STAHL_D)
    (lights_dark if v != "kalt" else lights_light)(t=(0, -4, 2.5))
    if heiss:
        L.point("glut", (0, 0, 9), 800, col=(1, .4, .1), r=3)
    camd = {"kalt": ((14, -24, 10), (9, -22, 8), (0, -5, 2.5), 45),
            "makro": ((2.4, -19, 4.0), (1.0, -16.5, 3.0), (0, -9.7, 2.2), 60),
            "kalt2": ((-6, -17, 5), (-3, -15.5, 4), (0, -9.7, 2.2), 55),
            "heiss": ((-12, -22, 9), (-7, -20, 7), (0, -6, 2.5), 45)}[v]
    c, tg = cam(camd[0], camd[2], camd[3], dof=4 if v in ("makro", "kalt2") else None)
    turns = {"kalt": 1.5, "makro": 1.2, "kalt2": 1.0, "heiss": 1.2}[v]
    def fn(f, u):
        a = 2 * pi * turns * u
        K(k, f, rot=(0, 0, a)); K(tt, f, rot=(0, 0, a))
        amp = 0 if heiss else 0.9
        K(ndl, f, rot=(0, amp * math.cos(2 * a), 0))
        K(c, f, loc=lerpv(camd[0], camd[1], ease(u)))
        if heiss: KV(estr(m), f, 0.6 + 0.3 * u)
    frames(fn)

def s_band():
    light_stage() if VAR == "pile" else dark_stage()
    proto, parts = kolben_set(ALU, rings=False, pin=False)
    belt = L.box("band", (200, 7, 0.6), loc=(0, 0, -0.3), m=L.mat("gurt", (0.05, 0.05, 0.05), 0, 0.6, bump=0.3))
    for s_ in (-1, 1): L.box("schiene", (200, 0.5, 1.2), loc=(0, s_ * 3.8, 0), m=STAHL)
    obs = []
    rows = 3 if VAR == "zeitraffer" else 1
    for i in range(70 if VAR == "pile" else 22):
        o = proto.copy(); sc.collection.objects.link(o); obs.append(o)
    proto.hide_render = True; proto.location = (0, 0, -50)
    (lights_dark if VAR != "pile" else lights_light)(t=(0, 0, 2), k=1.6)
    L.area("top", (0, -6, 20), 30, 2500, target=(0, 0, 0))
    if VAR == "zeitraffer":
        c, tg = cam((-34, -30, 22), (4, 0, 2), 40, dof=3.2)
        for b in range(1, 3):
            for s_ in (-1, 1): pass
        def fn(f, u):
            for i, o in enumerate(obs):
                x = -110 + ((i * 10.0 + u * 140) % 220)
                K(o, f, loc=(x, 0, 0), rot=(0, 0, i * 0.7))
            K(c, f, loc=lerpv((-34, -30, 22), (-28, -26, 18), ease(u)))
    else:  # Stapel wächst im Zeitraffer
        for o in obs: o.scale = (0.5, 0.5, 0.5)
        c, tg = cam((22, -40, 22), (0, 8, 6), 35)
        pos = []
        for layer in range(5):
            for ix in range(-3, 4):
                for iy in range(0, 2):
                    pos.append((ix * 4.6 + (layer % 2) * 2.3, 8 + iy * 4.6, layer * 3.1 + 0.3))
        def fn(f, u):
            for i, o in enumerate(obs):
                if i >= len(pos): K(o, f, loc=(0, 0, -50)); continue
                t0 = i / len(pos) * 0.85; p = ease((u - t0) / 0.08)
                start = (-60 + 0, 0, 0)
                loc = lerpv((-60, 0, 0), pos[i], p) if p < 1 else pos[i]
                if p > 0 and p < 1: loc = (loc[0], loc[1], loc[2] + 6 * math.sin(p * pi))
                K(o, f, loc=loc if p > 0 else (-60, 0, -50))
            K(c, f, loc=lerpv((22, -40, 22), (16, -36, 18), ease(u)))
    frames(fn)

def s_gewicht():
    dark_stage()
    k, parts = kolben_set(ALU)
    k.location = (0, 0, 24)
    pl = L.conrod(STAHL_D, 14.5); pl.location = (0, 0, 26.55)
    L.box("traverse", (24, 3, 1.2), loc=(0, 0, 30.8), m=STAHL_D)
    for s_ in (-1, 1): L.box("saeule", (1.2, 3, 31), loc=(s_ * 11.4, 0, 15.5), m=STAHL_D)
    L.cyl("halter", 0.9, 1.0, loc=(0, 0, 30.2), m=STAHL)
    blk = L.box("block", (8, 6, 6), loc=(0, 0, 0), m=L.mat("block", (0.22, 0.22, 0.24), 1, 0.45, bump=0.2))
    hook = L.cyl("kette", 0.25, 10, loc=(0, 0, 8), m=STAHL); hook.parent = blk
    lights_dark(t=(0, 0, 10))
    c, tg = cam((22, -64, 18), (0, 0, 17), 35)
    def fn(f, u):
        p = ease((u - 0.25) / 0.25)
        z = lerp(42, 4.0, p)
        jolt = 0
        if u > 0.5: jolt = 0.6 * math.exp(-(u - 0.5) * 30) * math.sin((u - 0.5) * 120)
        K(blk, f, loc=(0, 0, z + jolt if u < 0.5 else 4.0 + jolt))
        K(pl, f, loc=(0, 0, 26.55 + jolt * 0.15))
        K(c, f, loc=lerpv((22, -64, 18), (17, -58, 17), ease(u)))
    blk.location = (0, 0, 42)
    frames(fn)

def s_glut():
    dark_stage()
    m = glowmat("alu_g")
    k, parts = kolben_set(m)
    fl = L.mat("flamme2", (0, 0, 0), emit=(1, .3, .05), estr=0)
    flame = L.lathe("flame", [(0, 6.05), (4.3, 6.05), (4.3, 6.6), (0, 8.4)], 64, fl)
    lights_dark(t=(0, 0, 4), k=0.7)
    pt = L.point("glow", (0, 0, 10), 0, col=(1, .45, .1), r=3)
    if VAR == "flamme":
        c, tg = cam((10, -14, 12), (0, 0, 6), 40)
        def fn(f, u):
            KV(estr(fl), f, 6 * (0.6 + 0.4 * math.sin(u * 9) ** 2)); K(flame, f, s=(1, 1, 0.8 + 0.3 * math.sin(u * 7)))
            KV(estr(m), f, 0.3 + 0.7 * u); pt.data.energy = 3000; pt.data.keyframe_insert("energy", frame=f)
            K(c, f, loc=lerpv((10, -14, 12), (6, -12, 10), ease(u)))
    else:
        flame.hide_render = True
        c, tg = cam((-12, -12, 13), (0, 0, 5.5), 45)
        def fn(f, u):
            KV(estr(m), f, 1.1 * ease(u / 0.7)); KV(bcol(m), f, (lerp(.8, .25, u), lerp(.8, .2, u), lerp(.82, .2, u), 1)); pt.data.energy = 1500 * u; pt.data.keyframe_insert("energy", frame=f)
            K(k, f, rot=(0, 0, 0.6 * u))
            K(c, f, loc=lerpv((-12, -12, 13), (-8, -10, 11), ease(u)))
    frames(fn)

def ingot(name, m, loc=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for vv in bm.verts:
        vv.co.x *= 12; vv.co.y *= 4.4 if vv.co.z > 0 else 5.4; vv.co.z *= 2.4
        if vv.co.z > 0: vv.co.x *= 0.9
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = L.link(bpy.data.objects.new(name, me)); L.setmat(ob, m); ob.location = loc
    bv = ob.modifiers.new("bv", "BEVEL"); bv.width = 0.25; bv.segments = 3
    return ob

def s_barren():
    dark_stage()
    b = ingot("barren", L.mat("alu_b", (0.82, 0.82, 0.84), 1, 0.32, bump=0.08), (0, 0, 1.2))
    lights_dark(t=(0, 0, 1), k=0.6)
    sweep = L.area("sweep", (-30, -10, 10), 4, 4000, target=(0, 0, 1))
    c, tg = cam((0, -24, 9), (0, 0, 1), 50)
    def fn(f, u):
        K(b, f, rot=(0, 0, -0.5 + 0.9 * u))
        K(sweep, f, loc=(lerp(-30, 30, u), -10, 10))
        K(c, f, loc=lerpv((0, -24, 9), (0, -18, 7), ease(u)))
    frames(fn)

def s_alt():
    light_stage()
    lights_light(t=(0, 0, 6))
    gm = L.mat("grauguss", (0.09, 0.09, 0.1), 0.5, 0.85, bump=0.6)
    beam = L.empty("balken", (0, 0, 14))
    bb = L.box("bb", (34, 1.2, 0.8), loc=(0, 0, 14), m=STAHL); bb.parent = beam; bb.location = (0, 0, 0)
    L.box("saeule", (1.2, 1.2, 14), loc=(0, 0, 7), m=STAHL_D); L.cyl("fuss", 4, 0.6, loc=(0, 0, 0.3), m=STAHL_D)
    pans = []
    for s_ in (-1, 1):
        pe = L.empty(f"pan{s_}", (s_ * 15, 0, 14)); pe.parent = beam; pe.location = (s_ * 15, 0, 0)
        pan = L.cyl("schale", 5, 0.4, loc=(0, 0, -8), m=STAHL); pan.parent = pe
        for a in range(3):
            ch = L.cyl("seil", 0.06, 8.6, loc=(4 * math.cos(a * 2.1), 4 * math.sin(a * 2.1), -4), m=STAHL_D); ch.parent = pe
        pans.append(pe)
    ki, _ = kolben_set(gm, rings=False, pin=False, name="eisen"); ki.parent = pans[0]; ki.location = (0, 0, -7.8)
    ka, _ = kolben_set(ALU, rings=False, pin=False, name="aluk"); ka.parent = pans[1]; ka.location = (0, 0, -7.8)
    if VAR == "waage":
        c, tg = cam((10, -48, 14), (0, 0, 8), 40)
        ka.hide_render = True
        def fn(f, u):
            a = 0.18 * ease(u / 0.5)
            K(beam, f, rot=(0, -a if True else a, 0))
            for p in pans: K(p, f, rot=(0, a, 0))
            K(c, f, loc=lerpv((10, -48, 14), (6, -44, 12), ease(u)))
    else:
        c, tg = cam((-6, -46, 12), (0, 0, 8), 40)
        def fn(f, u):
            p = ease((u - 0.2) / 0.5)
            a = 0.18 * (1 - p) - 0.08 * p
            K(beam, f, rot=(0, -a, 0))
            for pp in pans: K(pp, f, rot=(0, a, 0))
            K(ki, f, loc=(0, -lerp(0, 30, ease((u - 0.1) / 0.3)), -7.8))
            K(ka, f, s=max(0.001, ease((u - 0.15) / 0.3)))
            K(c, f, loc=lerpv((-6, -46, 12), (-2, -42, 11), ease(u)))
    frames(fn)

def s_brief():
    dark_stage(floor=False)
    desk = L.box("tisch", (40, 24, 1.5), loc=(0, 0, -0.75), m=L.mat("holz", (0.22, 0.11, 0.05), 0, 0.45, bump=0.15))
    for i in range(4):
        L.box(f"papier{i}", (8.5, 11, 0.04), loc=(-6 + i * 0.4, 2 - i * 0.3, 0.02 + i * 0.04), rot=(0, 0, 0.1 * i - 0.15),
              m=L.mat(f"pap{i}", (0.85, 0.8, 0.68), 0, 0.8))
    pw = L.cyl("briefbeschwerer", 2.6, 2.2, loc=(-5, 1.5, 1.3), m=L.mat("alu_alt", (0.78, 0.78, 0.8), 1, 0.35, bump=0.1))
    bv = pw.modifiers.new("bv", "BEVEL"); bv.width = 0.3; bv.segments = 4
    L.cyl("tintenfass", 1.4, 2.4, loc=(7, 5, 1.2), m=L.mat("glas2", (0.1, 0.12, 0.2), 0, 0.1))
    L.cyl("feder", 0.1, 9, loc=(4, -3, 0.2), rot=(0, pi / 2, 0.4), m=L.mat("feder_m", (0.05, 0.03, 0.02), 0, 0.4))
    L.area("lampe", (-4, -6, 14), 5, 1200, col=(1, .8, .55), target=(-4, 1, 0))
    L.area("rim", (-14, 14, 8), 6, 800, col=(.7, .8, 1), target=(-4, 1, 0))
    c, tg = cam((-1, -15, 7), (-5, 1.5, 1), 55, dof=2.0)
    def fn(f, u):
        K(c, f, loc=lerpv((-1, -15, 7), (-3, -10, 4.5), ease(u)))
    frames(fn)

def s_werkstatt():
    L.hall(dark=False)
    bench = L.box("werkbank", (16, 6, 0.6), loc=(0, 0, 6), m=L.mat("holz2", (0.3, 0.18, 0.09), 0, 0.6, bump=0.2))
    for x in (-7, 7):
        for y in (-2.5, 2.5): L.box("bein", (0.6, 0.6, 6), loc=(x, y, 3), m=STAHL_D)
    L.box("schraubstock", (2, 3, 2), loc=(-5, 0, 7.3), m=L.mat("blau", (0.1, 0.2, 0.4), 0.5, 0.5))
    k, _ = kolben_set(ALU_ROH, rings=False, pin=False); k.scale = (0.4, 0.4, 0.4); k.location = (2, 0, 6.3)
    for i in range(5): L.cyl(f"werkz{i}", 0.15, 3, loc=(-1 + i * 0.6, 1.5, 6.4), rot=(pi / 2, 0, 0.3), m=STAHL)
    L.area("fenster", (6, 30, 14), 30, 6000, col=(.85, .9, 1), target=(0, 0, 6))
    L.area("lampe", (0, -6, 16), 4, 1200, col=(1, .8, .55), target=(0, 0, 6))
    camd = ((-12, -16, 11), (0, 0, 6.6)) if VAR == "a" else ((10, -14, 9), (2, 0, 6.6))
    c, tg = cam(camd[0], camd[1], 40, dof=3)

def crucible():
    cr = L.lathe("tiegel", [(0, 0), (5.2, 0), (6.2, 8), (5.6, 8.2), (4.6, 0.6), (0, 0.6)], 64, L.mat("tiegel_m", (0.12, 0.1, 0.09), 0.2, 0.8, bump=0.3))
    melt_m = L.mat("schmelze", (0.3, .1, .02), 0, 0.2, emit=(1, .22, .02), estr=3)
    tc = melt_m.node_tree.nodes.new("ShaderNodeTexCoord"); nz = melt_m.node_tree.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3
    mr = melt_m.node_tree.nodes.new("ShaderNodeMapRange"); mr.inputs[3].default_value = 1.2; mr.inputs[4].default_value = 4.5
    melt_m.node_tree.links.new(tc.outputs["Object"], nz.inputs["Vector"]); melt_m.node_tree.links.new(nz.outputs["Fac"], mr.inputs[0])
    melt_m.node_tree.links.new(mr.outputs[0], melt_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"])
    melt = L.cyl("melt", 5.85, 0.2, loc=(0, 0, 7.2), m=melt_m)
    return cr, melt, nz

def s_schmelze():
    dark_stage()
    cr, melt, nz = crucible()
    L.point("glut", (0, 0, 10), 4000, col=(1, .45, .12), r=4)
    lights_dark(t=(0, 0, 6), k=0.4)
    if VAR == "si":
        c, tg = cam((8, -14, 18), (0, 0, 7), 40)
        sim = L.mat("silizium", (0.25, 0.27, 0.32), 0.9, 0.25)
        chunks = []
        for i in range(9):
            bpy.ops.mesh.primitive_ico_sphere_add(radius=0.7 + rnd.random() * 0.4, subdivisions=1)
            o = bpy.context.active_object; L.setmat(o, sim); chunks.append(o)
        def fn(f, u):
            for i, o in enumerate(chunks):
                t0 = 0.1 + i * 0.07; p = (u - t0) / 0.18
                x, y = 3 * math.cos(i * 2.3), 3 * math.sin(i * 2.3)
                z = 22 - 15 * min(1, max(0, p)) ** 2 if p < 1 else 7.2 - 1.6 * min(1, (p - 1) * 2)
                K(o, f, loc=(x, y, z if p > 0 else 30), rot=(u * 5 + i, u * 3, i))
            nz.inputs["W"].default_value = u * 2; nz.inputs["W"].keyframe_insert("default_value", frame=f) if hasattr(nz.inputs["W"], "keyframe_insert") else None
            K(c, f, loc=lerpv((8, -14, 18), (5, -12, 16), ease(u)))
        nz.noise_dimensions = "4D"
    else:
        c, tg = cam((-14, -22, 16), (0, 0, 7), 35)
        bars = [ingot(f"b{i}", L.mat(f"alu_b{i}", (0.8, 0.8, 0.82), 1, 0.35), (0, 0, 30)) for i in range(3)]
        for b in bars: b.scale = (0.3, 0.4, 0.4)
        nz.noise_dimensions = "4D"
        def fn(f, u):
            for i, b in enumerate(bars):
                p = (u - 0.1 - i * 0.22) / 0.25
                z = lerp(24, 6.5, ease(p)) if p < 1.2 else 6.5 - (p - 1.2) * 1.5
                K(b, f, loc=(lerp(-6, 0, ease(p)) + i - 1, 0, max(z, 4.5)), rot=(0, 0.5 * (1 - ease(p)), i))
            nz.inputs["W"].default_value = u * 2; nz.inputs["W"].keyframe_insert("default_value", frame=f)
            K(c, f, loc=lerpv((-14, -22, 16), (-10, -18, 13), ease(u)))
    frames(fn)

def s_dehnung():
    dark_stage()
    ms = glowmat("stahl_g", (0.45, 0.46, 0.5), 1, 0.3); ma = glowmat("alu_g2", (0.82, 0.82, 0.84), 1, 0.28)
    def rod(name, y, m):
        bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.active_object; o.name = name
        o.data.transform(__import__("mathutils").Matrix.Diagonal((14, 1.2, 1.2, 1)) @ __import__("mathutils").Matrix.Translation((0.5, 0, 0)))
        o.location = (-7, y, 3); L.setmat(o, m); return o
    st = rod("stab_s", -2.5, ms); al = rod("stab_a", 2.5, ma)
    L.box("anschlag", (1, 9, 6), loc=(-7.6, 0, 3), m=STAHL_D)
    for x in (-3, 1, 5):
        bz = L.mat(f"brenner{x}", (0, 0, 0), emit=(.25, .45, 1), estr=3)
        for y in (-2.5, 2.5): L.lathe("flamme", [(0, 0.2), (0.3, 0.3), (0.08, 1.4), (0, 1.5)], 24, bz).location = (x, y, 0.6)
    lights_dark(t=(0, 0, 3), k=0.7)
    c, tg = cam((2, -22, 14), (1, 0, 3), 45) if VAR == "a" else cam((14, -18, 10), (4, 0, 3), 50)
    def fn(f, u):
        p = ease((u - 0.15) / 0.6)
        K(st, f, s=(1 + 0.07 * p, 1, 1)); K(al, f, s=(1 + 0.13 * p, 1, 1))
        KV(estr(ms), f, 0.3 * p); KV(estr(ma), f, 0.3 * p)
    frames(fn)

def kokille_parts():
    km = L.mat("kokille", (0.3, 0.31, 0.33), 1, 0.4, bump=0.15)
    base = L.box("grundplatte", (18, 14, 1.2), loc=(0, 0, 0.6), m=km)
    halves = []
    for s_ in (-1, 1):
        h = L.box(f"halb{s_}", (6, 12, 9), loc=(s_ * 3.0, 0, 5.7), m=km)
        cut = L.cyl("cav", 4.5, 9.5, loc=(0, 0, 5.9)); L.boolean(h, cut); halves.append(h)
    core = L.lathe("kern", [(0, 0), (3.5, 0), (3.2, 5), (0, 5.2)], 48, km); core.location = (0, 0, 1.2)
    return base, halves, core

def s_kokille():
    L.hall(dark=True); 
    base, halves, core = kokille_parts()
    L.point("glut", (0, 0, 20), 500, col=(1, .6, .3), r=4)
    L.area("key", (14, -16, 22), 10, 2500, target=(0, 0, 5)); L.area("rim", (-14, 12, 14), 6, 1800, col=(1, .7, .5), target=(0, 0, 5))
    c, tg = cam((18, -24, 20), (0, 0, 5), 38, dof=4)
    if VAR == "zu":
        def fn(f, u):
            for i, (h, s_) in enumerate(zip(halves, (-1, 1))):
                p = ease((u - 0.15 - i * 0.12) / 0.35)
                K(h, f, loc=(s_ * lerp(14, 3.0, p), 0, 5.7))
            K(core, f, loc=(0, 0, lerp(-6, 1.2, ease((u - 0.05) / 0.3))))
            K(c, f, loc=lerpv((18, -24, 20), (14, -22, 18), ease(u)))
    else:
        for h, s_ in zip(halves, (-1, 1)): h.location.x = s_ * 3.0
        ringm = L.mat("salz", (0.95, 0.95, 0.93), 0, 0.85, bump=0.4) if VAR == "salz" else L.mat("ni", (0.2, 0.2, 0.21), 0.8, 0.5, bump=0.2)
        z0 = 8.3 if VAR == "salz" else 9.2
        rg = L.lathe("ring", [(3.4, 0), (4.1, 0), (4.1, 0.7), (3.4, 0.7), (3.4, 0)], 64, ringm)
        if VAR == "ring":
            sr = L.lathe("salzring", [(3.4, 0), (4.1, 0), (4.1, 0.7), (3.4, 0.7), (3.4, 0)], 64, L.mat("salz2", (0.95, 0.95, 0.93), 0, 0.85)); sr.location = (0, 0, 8.3)
        grip = L.empty("greifer", (0, 0, 20))
        L.box("gr_arm", (0.8, 0.8, 10), loc=(0, 0, 5.5), m=STAHL_D).parent = grip
        for s_ in (-1, 1):
            fg = L.box("finger", (0.4, 1, 2.2), loc=(s_ * 4.3, 0, 0.6), m=STAHL); fg.parent = grip
        L.box("gr_quer", (9.4, 1, 0.6), loc=(0, 0, 1.6), m=STAHL).parent = grip
        c2, _ = c, tg
        def fn(f, u):
            p = ease(u / 0.55); q = ease((u - 0.65) / 0.3)
            K(grip, f, loc=(0, 0, lerp(22, z0, p) + 14 * q))
            K(rg, f, loc=(0, 0, lerp(22, z0, p) - 0.4))
            K(c, f, loc=lerpv((12, -20, 22), (8, -16, 19), ease(u)))
    frames(fn)

def s_alfin():
    dark_stage()
    cr, melt, nz = crucible(); nz.noise_dimensions = "4D"
    L.point("glut", (0, 0, 11), 3500, col=(1, .45, .12), r=4)
    lights_dark(t=(0, 0, 8), k=0.5)
    rm = L.mat("ni_r", (0.15, 0.15, 0.16), 0.8, 0.6, bump=0.2)
    rg = L.lathe("ring", [(3.4, 0), (4.1, 0), (4.1, 0.9), (3.4, 0.9), (3.4, 0)], 64, rm)
    hk = L.cyl("haken", 0.15, 12, loc=(0, 0, 6), m=STAHL)
    c, tg = cam((10, -17, 17), (0, 0, 9), 40)
    def fn(f, u):
        dip = math.sin(min(1, max(0, (u - 0.1) / 0.75)) * pi)
        z = lerp(16, 6.2, dip)
        K(rg, f, loc=(0, 0, z)); K(hk, f, loc=(0, 0, z + 6.4))
        m_ = min(1, max(0, (u - 0.45) / 0.1))
        KV(bcol(rm), f, (lerp(0.15, 0.85, m_), lerp(0.15, 0.85, m_), lerp(0.16, 0.88, m_), 1))
        nz.inputs["W"].default_value = u * 2; nz.inputs["W"].keyframe_insert("default_value", frame=f)
        K(c, f, loc=lerpv((10, -17, 17), (7, -14, 14), ease(u)))
    frames(fn)

def s_guss():
    L.hall(dark=True)
    km = L.mat("kokille2", (0.3, 0.31, 0.33), 1, 0.4, bump=0.15)
    for x in (-5.5, 5.5):
        L.box("form", (9, 10, 9), loc=(x, 0, 4.5), m=km)
        sp = L.cyl("einguss", 1.4, 0.2, loc=(x, 0.6, 9.05), m=L.mat("glut_e", (0, 0, 0), emit=(1, .25, .03), estr=0))
    ladles, streams = [], []
    gm = L.mat("strahl", (0.3, .1, .02), 0, 0.2, emit=(1, .25, .03), estr=6)
    for x in (-5.5, 5.5):
        ld = L.empty("pfanne", (x, -1.2, 13.5))
        cup = L.lathe("pfanne_m", [(0, 0), (2.4, 0), (2.9, 3.6), (2.6, 3.7), (2.1, 0.4), (0, 0.4)], 48, L.mat("pf", (0.15, 0.12, 0.1), 0.3, 0.7))
        cup.parent = ld; cup.location = (0, -2.9, -1.5)
        L.cyl("stiel", 0.25, 9, loc=(0, -8, 0.5), rot=(pi / 2, 0, 0), m=STAHL_D).parent = ld
        ladles.append(ld)
        s_ = L.cyl("strahl", 0.45, 1, loc=(x, 0.6, 11.3), m=gm); streams.append(s_)
    pt = L.point("glut", (0, -2, 11), 0, col=(1, .45, .12), r=3)
    L.area("key", (16, -18, 22), 8, 1200, target=(0, 0, 8))
    teaser = VAR == "teaser"
    c, tg = cam((22, -20, 14), (0, 0, 10), 40, dof=3) if not teaser else cam((-6, -14, 11), (0, 0, 10), 55, dof=2)
    def fn(f, u):
        tilt = ease(u / 0.22) * 1.0 * (1 - 0.6 * ease((u - 0.88) / 0.12))
        for ld in ladles: K(ld, f, rot=(tilt, 0, 0))
        pour = ease((u - 0.18) / 0.08) * (1 - ease((u - 0.88) / 0.1))
        for s_, x in zip(streams, (-5.5, 5.5)):
            K(s_, f, s=(1 + 0.1 * math.sin(u * 60), 1 + 0.1 * math.cos(u * 50), max(0.001, 4.4 * pour)))
        pt.data.energy = 4000 * pour + 300; pt.data.keyframe_insert("energy", frame=f)
        for m in bpy.data.materials:
            if m.name.startswith("glut_e"): KV(estr(m), f, 4 * ease((u - 0.3) / 0.4))
    frames(fn)

def s_entformen():
    L.hall(dark=True)
    km = L.mat("kokille3", (0.3, 0.31, 0.33), 1, 0.4, bump=0.15)
    gm = glowmat("roh_g", (0.6, 0.6, 0.62), 0.9, 0.5)
    pis = []
    for x in (-5.5, 5.5):
        k, _ = kolben_set(gm, rings=False, pin=False, name=f"roh{x}"); k.location = (x, 0, 1); pis.append(k)
        L.cyl("speiser", 1.4, 3, loc=(0, 0, 7.5), m=gm).parent = k
    top = L.box("formh", (24, 12, 10), loc=(0, 0, 5), m=km)
    L.box("platte", (26, 16, 1), loc=(0, 0, 0.5), m=km)
    L.point("glut", (0, 0, 6), 800, col=(1, .45, .12), r=3)
    L.area("key", (14, -20, 22), 8, 2200, target=(0, 0, 5)); L.area("rim", (-14, 12, 14), 6, 1500, col=(1, .7, .5), target=(0, 0, 5))
    c, tg = cam((10, -32, 18), (0, 0, 5), 38, dof=4)
    def fn(f, u):
        p = ease((u - 0.05) / 0.35)
        K(top, f, loc=(0, 0, 5 + 22 * p))
        q = ease((u - 0.5) / 0.35)
        for k, s_ in zip(pis, (-1, 1)): K(k, f, loc=(s_ * (5.5 + 5 * q), 0, 1 + 3 * q))
        KV(estr(gm), f, 1.0 * (1 - 0.5 * u))
        K(c, f, loc=lerpv((10, -32, 18), (6, -28, 15), ease(u)))
    frames(fn)

def s_spuelen():
    L.hall(dark=True)
    km = L.mat("roh_glas", (0.7, 0.7, 0.72), 0.9, 0.45, alpha=0.35)
    k, _ = kolben_set(km, rings=False, pin=False)
    salt = L.mat("salz3", (0.95, 0.95, 0.93), 0, 0.8, emit=(1, 1, 1), estr=0.2)
    ch = L.lathe("salzkanal", [(3.0, 4.6), (3.7, 4.6), (3.7, 5.3), (3.0, 5.3), (3.0, 4.6)], 64, salt)
    noz = L.cyl("duese", 0.5, 4, loc=(9, 0, 4.9), rot=(0, pi / 2, 0), m=STAHL)
    wm = L.mat("wasser", (0.7, 0.85, 1), 0, 0.05, emit=(0.6, 0.8, 1), estr=2)
    jet = L.cyl("strahl", 0.18, 1, loc=(6, 0, 4.9), rot=(0, pi / 2, 0), m=wm)
    grains = []
    for i in range(30):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.12, subdivisions=1); g = bpy.context.active_object; L.setmat(g, salt); grains.append(g)
    L.area("key", (12, -14, 18), 8, 2200, target=(0, 0, 4)); L.area("rim", (-12, 12, 10), 6, 1600, col=(.6, .8, 1), target=(0, 0, 4))
    c, tg = cam((6, -18, 11), (0, 0, 4.5), 42)
    def fn(f, u):
        K(jet, f, s=(1, 1, 5.0 * ease(u / 0.1)))
        K(ch, f, s=(1, 1, max(0.001, 1 - ease((u - 0.2) / 0.6))))
        K(k, f, rot=(0, 0, u * 1.2))
        for i, g in enumerate(grains):
            t0 = 0.15 + (i / 30) * 0.6; a = (u - t0)
            if a < 0: K(g, f, loc=(0, 0, -20)); continue
            ang = i * 2.4
            K(g, f, loc=(-4 * math.cos(ang) - a * 20, 4 * math.sin(ang), 4.9 - 25 * a * a))
        K(c, f, loc=lerpv((6, -18, 11), (3, -16, 9), ease(u)))
    frames(fn)

def s_kanal():
    dark_stage()
    gm = L.mat("geist", (0.75, 0.78, 0.82), 0.5, 0.3, alpha=0.18)
    k, _ = kolben_set(gm, rings=False, pin=False)
    om = L.mat("oel", (1, .6, .1), 0, 0.2, emit=(1, .55, .1), estr=0)
    ch = L.lathe("kanal", [(3.0, 4.6), (3.7, 4.6), (3.7, 5.3), (3.0, 5.3), (3.0, 4.6)], 64, om)
    rm = L.mat("ringtr", (0.15, 0.15, 0.16), 0.8, 0.5, emit=ORANGE, estr=0)
    rt = L.lathe("ringtraeger", [(3.6, 4.95), (4.31, 4.95), (4.31, 5.35), (3.6, 5.35), (3.6, 4.95)], 64, rm)
    cm = L.mat("krone", (0.8, 0.8, 0.82), 0.5, 0.3, emit=(1, .35, .05), estr=0)
    crown = L.cyl("krone", 4.2, 0.12, loc=(0, 0, 5.95), m=cm)
    lights_dark(t=(0, 0, 4), k=0.6)
    c, tg = cam((12, -15, 13), (0, 0, 4.5), 42)
    def fn(f, u):
        K(k, f, rot=(0, 0, 0.8 * u)); K(ch, f, rot=(0, 0, 0.8 * u))
        if VAR == "oel":
            KV(estr(om), f, 2.5 * ease(u / 0.2))
            hot = 1 - ease((u - 0.3) / 0.5)
            KV(ecol(cm), f, (lerp(0.2, 1, hot), lerp(0.5, 0.35, hot), lerp(1, 0.05, hot), 1)); KV(estr(cm), f, 3)
        else:
            KV(estr(om), f, 0.6); KV(estr(rm), f, 1.6 * ease((u - 0.2) / 0.3)); KV(estr(cm), f, 0)
        K(c, f, loc=lerpv((12, -15, 13), (8, -12, 10), ease(u)) if VAR == "oel" else lerpv((-12, -12, 9), (-8, -9, 7), ease(u)))
    frames(fn)

def lathe_machine(dark=False):
    L.hall(dark=True, fz=-8.5)
    bed = L.box("bett", (40, 8, 3), loc=(0, 0, -7), m=L.mat("masch", (0.16, 0.2, 0.22), 0.4, 0.5))
    head = L.box("spindelkasten", (8, 10, 12), loc=(-16, 0, 0), m=L.mat("masch2", (0.2, 0.24, 0.26), 0.4, 0.5))
    spin = L.empty("spindel", (-12, 0, 0))
    chuck = L.cyl("futter", 4.5, 2.4, loc=(1.2, 0, 0), rot=(0, pi / 2, 0), m=STAHL); chuck.parent = spin
    for i in range(3):
        a = i * 2 * pi / 3
        j = L.box("backe", (2.2, 1.2, 1.6), loc=(2.8, 3.6 * math.cos(a), 3.6 * math.sin(a)), m=STAHL_D); j.parent = spin
    return spin
def s_drehbank():
    v = VAR
    if v == "bohren":
        dark_stage()
        k, _ = kolben_set(ALU, rings=False, pin=False); k.location = (0, 0, 0)
        L.box("vorrichtung", (12, 12, 2), loc=(0, 0, -1), m=STAHL_D)
        bar = L.cyl("bohrstange", 0.95, 14, loc=(16, 0, 2.55), rot=(0, pi / 2, 0), m=STAHL)
        ins = L.box("schneide", (0.6, 0.4, 0.4), loc=(9.3, 0, 3.5), m=L.mat("gold", (0.9, 0.7, 0.3), 1, 0.3)); ins.parent = bar
        lights_dark(t=(0, 0, 3))
        c, tg = cam((14, -14, 8), (2, 0, 2.5), 42)
        def fn(f, u):
            K(bar, f, loc=(lerp(18, 6, ease(u / 0.8)), 0, 2.55), rot=(u * 40, pi / 2, 0))
            K(c, f, loc=lerpv((14, -14, 8), (11, -12, 6.5), ease(u)))
        frames(fn); return
    spin = lathe_machine(dark=v == "teaser")
    mrough = ALU_ROH if v in ("roh", "teaser", "nuten") else ALU
    k, _ = kolben_set(mrough, rings=False, pin=False)
    k.parent = spin; k.location = (2.6, 0, 0); k.rotation_euler = (0, pi / 2, 0)
    post = L.empty("support", (6, -6, 0))
    L.box("halter", (2, 3, 2), loc=(0, -2, 0), m=STAHL_D).parent = post
    tool = L.box("meissel", (0.5, 3, 0.5), loc=(0, 0, 0), m=L.mat("hm", (0.85, 0.65, 0.3), 1, 0.3)); tool.parent = post
    chips = []
    for i in range(16):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.05); ch = bpy.context.active_object; L.setmat(ch, ALU); chips.append(ch)
    if v == "teaser":
        L.area("spot", (-5, -10, 8), 1.0, 600, col=(1, .8, .6), target=(-7, -4.4, 0))
        sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    else:
        L.area("key", (-2, -16, 14), 10, 2600, target=(-6, 0, 0)); L.area("rim", (-10, 14, 10), 6, 1500, col=(1, .8, .6), target=(-6, 0, 0))
    camd = {"roh": ((16, -30, 8), (10, -26, 6), (-8, 0, 0), 35), "teaser": ((0, -17, 3), (-1, -16, 2.5), (-7, -4, 0), 50),
            "nuten": ((4, -21, 7), (2, -19, 6), (-5.5, -3, 0), 45), "schaft": ((-2, -26, 12), (2, -24, 10), (-8, 0, 0), 35),
            "oszi": ((-1, -16, 4.5), (-2, -15, 4), (-7.5, -4.3, 0), 50)}[v]
    c, tg = cam(camd[0], camd[2], camd[3], dof=3 if v in ("oszi", "nuten") else None)
    revs = {"roh": 0.3, "teaser": 6, "nuten": 8, "schaft": 10, "oszi": 2.0}[v]
    def fn(f, u):
        th = 2 * pi * revs * u
        K(spin, f, rot=(th, 0, 0))
        R = 4.3
        if v == "roh":
            K(spin, f, rot=(0, 0, 0)); K(post, f, loc=(-6, -14, 0))
        elif v == "nuten":
            g = min(2, int(u * 3)); gu = (u * 3) % 1
            zs = [-4.25, -4.8, -5.47]  # x-Position der Nuten (Kolben liegt in x)
            dep = math.sin(min(1, gu / 0.8) * pi) * 0.4
            K(post, f, loc=(zs[g] - 0.0, -(R + 1.5) + dep * 1.0, 0))
        elif v == "schaft":
            K(post, f, loc=(lerp(-6.0, -9.0, u), -(R + 1.5), 0))
        elif v == "oszi":
            K(post, f, loc=(-7.5, -(R + 1.5) + 0.35 * math.cos(2 * th), 0))
        else:
            K(post, f, loc=(lerp(-6, -9, u), -(R + 1.5) + 0.25 * math.cos(2 * th), 0))
        for i, ch in enumerate(chips):
            a = (u * 6 + i / 16) % 1
            if v in ("roh",): K(ch, f, loc=(0, 0, -40)); continue
            K(ch, f, loc=(post.location.x + a * 2, -(R + 0.6) - a * 4, -a * 5 + 3 * a * (1 - a)), rot=(a * 20, i, a * 9))
        K(c, f, loc=lerpv(camd[0], camd[1], ease(u)))
    frames(fn)

def s_ofen():
    L.hall(dark=True)
    gm = glowmat("ofen_k", (0.7, 0.7, 0.72), 0.9, 0.4)
    rack = L.empty("gestell", (0, 0, 6))
    L.box("rost", (18, 10, 0.4), loc=(0, 0, -0.2), m=STAHL_D).parent = rack
    proto, _ = kolben_set(gm, rings=False, pin=False); proto.scale = (0.55, 0.55, 0.55)
    ps = [proto]
    for i in range(5):
        o = proto.copy(); sc.collection.objects.link(o); ps.append(o)
    for i, o in enumerate(ps): o.parent = rack; o.location = ((i % 3 - 1) * 5.5, (i // 3 - 0.5) * 5, 0)
    if VAR == "a":
        ofm = L.mat("ofen", (0.15, 0.13, 0.12), 0.2, 0.8)
        for s_ in (-1, 1): L.box("wand", (1.5, 14, 14), loc=(s_ * 11, 0, 7), m=ofm)
        L.box("decke", (23.5, 14, 1.5), loc=(0, 0, 14.5), m=ofm); L.box("rueck", (23.5, 1.5, 14), loc=(0, 7.5, 7), m=ofm)
        hm = L.mat("heiz", (0, 0, 0), emit=(1, .2, .02), estr=4)
        for z in (3, 7, 11): L.cyl("heizstab", 0.25, 20, loc=(0, 6.4, z), rot=(0, pi / 2, 0), m=hm)
        L.point("ofenlicht", (0, 2, 10), 3000, col=(1, .4, .1), r=5)
        c, tg = cam((6, -26, 9), (0, 0, 6.5), 38)
        def fn(f, u):
            KV(estr(gm), f, 0.2 + 0.9 * ease(u / 0.8)); KV(bcol(gm), f, (lerp(.7, .3, u), lerp(.7, .25, u), lerp(.72, .25, u), 1)); K(c, f, loc=lerpv((6, -26, 9), (3, -20, 8), ease(u)))
    else:
        wm = L.mat("wasser2", (0.05, 0.12, 0.16), 0, 0.05, alpha=0.75)
        L.box("becken", (24, 14, 0.2), loc=(0, 0, 3), m=wm)
        L.box("beckenrand", (25, 15, 3), loc=(0, 0, 1.4), m=STAHL_D)
        L.area("key", (14, -16, 20), 8, 1500, target=(0, 0, 4))
        c, tg = cam((10, -24, 12), (0, 0, 4), 38)
        def fn(f, u):
            p = ease((u - 0.05) / 0.25)
            K(rack, f, loc=(0, 0, lerp(12, 1.0, p)))
            KV(estr(gm), f, 1.1 * (1 - ease((u - 0.25) / 0.45)))
            K(c, f, loc=lerpv((10, -24, 12), (8, -22, 10), ease(u)))
    frames(fn)

def s_profil():
    light_stage()
    k, _ = kolben_set(ALU)
    lights_light(t=(0, 0, 3))
    camd = {"geist": ((0, -40, 3), (0, -36, 3.2), 80), "konus": ((-3, -38, 4.5), (0, -34, 4.2), 85), "fass": ((4, -38, 2), (0, -35, 2.6), 85)}[VAR]
    c, tg = cam(camd[0], (0, 0, 3), camd[2])
    def fn(f, u):
        K(k, f, rot=(0, 0, 0.5 * u - 0.25)); K(c, f, loc=lerpv(camd[0], camd[1], ease(u)))
    frames(fn)

def shaped_piston(mode):
    """Kolben mit Formschlüssel: oval (übertrieben) bzw. konisch -> rund/gerade"""
    gm = glowmat("form_g", (0.8, 0.8, 0.82), 1, 0.28)
    k = L.piston("kolbenform", gm, recess=False)
    sk0 = k.shape_key_add(name="Basis"); sk1 = k.shape_key_add(name="kalt")
    for i, vv in enumerate(k.data.vertices):
        co = vv.co.copy()
        if mode == "oval": co.x *= 0.93
        else:
            t = max(0, (co.z - 2.0) / 4.0); co.x *= 1 - 0.07 * t; co.y *= 1 - 0.07 * t
        sk1.data[i].co = co
    return k, sk1, gm
def s_oval3d():
    dark_stage()
    k, sk, gm = shaped_piston("oval")
    lights_dark(t=(0, 0, 6), k=0.8)
    ghost_cyl(-0.5, 6.4, r=4.6)
    c, tg = cam((0, -13, 32), (0, 0, 5), 50)
    def fn(f, u):
        if VAR == "draufsicht":
            sk.value = 1; sk.keyframe_insert("value", frame=f); K(k, f, rot=(0, 0, 0.15 * math.sin(u * pi)))
        else:
            p = ease((u - 0.2) / 0.55); sk.value = 1 - p; sk.keyframe_insert("value", frame=f)
            KV(estr(gm), f, 1.0 * ease((u - 0.1) / 0.4))
    frames(fn)
def s_konus3d():
    dark_stage()
    k, sk, gm = shaped_piston("konus")
    lights_dark(t=(0, 0, 3), k=0.8)
    c, tg = cam((0, -40, 3.2), (0, 0, 3.2), 80)
    def fn(f, u):
        p = ease((u - 0.2) / 0.55); sk.value = 1 - p; sk.keyframe_insert("value", frame=f)
        KV(estr(gm), f, 1.0 * ease((u - 0.1) / 0.4))
        K(c, f, loc=lerpv((0, -40, 3.2), (0, -37, 3.4), ease(u)))
    frames(fn)

def s_spalt():
    dark_stage(floor=False)
    k, _ = kolben_set(ALU)
    wall = L.lathe("wand", [(4.42, -4), (12.0, -4), (12.0, 6.05), (4.42, 6.05), (4.42, -4)], 192, L.mat("zylw", (0.3, 0.3, 0.33), 1, 0.3, bump=0.05))
    L.smooth(wall)
    L.point("unten", (0, 0, -2), 20000, col=(1, .55, .2), r=1)
    L.area("key", (8, -10, 20), 8, 4000, target=(4.3, 0, 6))
    c, tg = cam((6, -9, 18), (4.33, -0.5, 6), 50, dof=3)
    def fn(f, u):
        K(c, f, loc=lerpv((6, -9, 18), (4.9, -2.2, 9.5), ease(u)))
    frames(fn)

def s_fresser():
    dark_stage(floor=False)
    gm = glowmat("fress_g", (0.8, 0.8, 0.82), 1, 0.3, col=(1, .22, .02))
    k, parts = kolben_set(gm)
    # Riefen: Streifen-Textur über Maske
    nt = gm.node_tree; b = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Z" if hasattr(wv, "bands_direction") else wv.bands_direction
    wv.inputs["Scale"].default_value = 6; wv.inputs["Distortion"].default_value = 8
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "FLOAT"; mix.inputs[2].default_value = 0.25
    nt.links.new(wv.outputs["Fac"], mix.inputs[3]); nt.links.new(mix.outputs[0], b.inputs["Roughness"])
    ghost_cyl(-1, 9)
    pt = L.point("glut", (0, -6, 6), 0, col=(1, .4, .1), r=3)
    lights_dark(t=(0, 0, 4))
    c, tg = cam((17, -26, 12), (0, 0, 4), 45)
    def fn(f, u):
        stop = 0.78
        sp = (1 - ease((u - 0.55) / (stop - 0.55))) if u < stop else 0
        ph = 2 * pi * 3.5 * (u if u < stop else stop) - (2 * pi * 3.5 * 0.0)
        z = 2.0 * math.sin(ph * (1 if u < 0.55 else 1)) * (1 if u < stop else 0) if u < stop else 2.0 * math.sin(2 * pi * 3.5 * stop)
        heat = ease(u / 0.7)
        sc_ = 1 + 0.012 * heat
        K(k, f, loc=(0, 0, z), s=(sc_, sc_, 1))
        KV(estr(gm), f, 0.9 * heat); KV(mix.inputs[0], f, ease((u - 0.5) / 0.3))
        pt.data.energy = 1500 * heat; pt.data.keyframe_insert("energy", frame=f)
        K(c, f, loc=lerpv((17, -26, 12), (13, -21, 9), ease(u)))
    frames(fn)

def s_unten():
    light_stage() if VAR == "dreh" else dark_stage()
    bm_ = glowmat("boss_g", (0.8, 0.8, 0.82), 1, 0.26) if VAR == "augen" else ALU
    # Bolzenaugen als eigenes Material: Kolben normal, Augen-Zylinder getrennt hinzufügen
    k = L.piston("kolben", ALU)
    eyes = []
    if VAR == "augen":
        for s_ in (-1, 1):
            e = L.cyl("auge", 1.6, 1.62, loc=(s_ * 2.95, 0, 2.55), rot=(0, pi / 2, 0), m=bm_, verts=48)
            h = L.cyl("h", 1.1, 3, loc=(s_ * 2.95, 0, 2.55), rot=(0, pi / 2, 0)); L.boolean(e, h); eyes.append(e)
    piv = L.empty("piv", (0, 0, 6)); k.parent = piv; k.location = (0, 0, -3)
    for e in eyes: e.parent = piv; e.location.z -= 6 - 3
    (lights_light if VAR == "dreh" else lights_dark)(t=(0, 0, 6))
    if VAR == "augen": L.point("aug", (0, -3, 2), 300, col=(1, .4, .1), r=1)
    c, tg = cam((10, -20, 15) if VAR == "dreh" else (5, -11, 15), (0, 0, 5), 45)
    def fn(f, u):
        if VAR == "dreh": K(piv, f, rot=(-pi * 0.8 * ease(u / 0.8), 0, 0.6 * u))
        else:
            K(piv, f, rot=(-pi * 0.8, 0, 0.4 * u)); KV(estr(bm_), f, 1.5 * ease((u - 0.25) / 0.35))
        K(c, f, loc=lerpv(c.location[:], c.location[:], 0))
    frames(fn)

def s_siebdruck():
    dark_stage()
    gm = L.mat("alu_s", (0.8, 0.8, 0.82), 1, 0.28)
    nt = gm.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = -6; mr.inputs[2].default_value = -5.9
    nt.links.new(sep.outputs[0], mr.inputs[0])
    zr = nt.nodes.new("ShaderNodeMapRange"); zr.inputs[1].default_value = 3.2; zr.inputs[2].default_value = 3.1
    nt.links.new(sep.outputs[2], zr.inputs[0])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; nt.links.new(mr.outputs[0], mul.inputs[0]); nt.links.new(zr.outputs[0], mul.inputs[1])
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = "RGBA"; mc.inputs[6].default_value = (0.8, 0.8, 0.82, 1); mc.inputs[7].default_value = (0.08, 0.08, 0.09, 1)
    nt.links.new(mul.outputs[0], mc.inputs[0]); nt.links.new(mc.outputs[2], b.inputs["Base Color"])
    mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "FLOAT"; mm.inputs[2].default_value = 1; mm.inputs[3].default_value = 0.2
    nt.links.new(mul.outputs[0], mm.inputs[0]); nt.links.new(mm.outputs[0], b.inputs["Metallic"])
    k = L.piston("kolben", gm, recess=True)
    k.rotation_euler = (0, 0, pi / 2)
    rak = L.empty("rakel", (-7, -6.2, 1.6))
    L.box("rakel_m", (0.3, 1.0, 4), loc=(0, 0, 0), rot=(0, 0, 0), m=L.mat("gummi", (0.6, 0.35, 0.05), 0, 0.6)).parent = rak
    L.box("sieb", (14, 0.05, 6), loc=(0, -4.6, 1.8), m=L.mat("siebm", (0.5, 0.5, 0.55), 0.3, 0.5, alpha=0.12))
    for zz in (-1.2, 4.8): L.box("rahmen", (14.4, 0.4, 0.4), loc=(0, -4.6, zz), m=STAHL_D)
    lights_dark(t=(0, -2, 2), k=0.5 if VAR == "teaser" else 1.0)
    c, tg = cam((5, -18, 6), (0, -3, 2), 45, dof=3 if VAR == "teaser" else None)
    def fn(f, u):
        if VAR == "teaser":
            K(rak, f, loc=(-7, -6.2, lerp(6, 1.6, ease(u / 0.8)))); KV(mr.inputs[1], f, -9); KV(mr.inputs[2], f, -8.9)
        else:
            x = lerp(-6, 6, ease((u - 0.1) / 0.7))
            K(rak, f, loc=(x, -6.2, 1.6)); KV(mr.inputs[1], f, x); KV(mr.inputs[2], f, x + 0.1)
        K(c, f, loc=lerpv((5, -18, 6), (3, -15, 5), ease(u)))
    # Maske läuft in Objekt-X: Kolben um 90° gedreht -> Objekt-X zeigt Richtung Welt-Y
    frames(fn)

def s_messen():
    dark_stage()
    L.box("granit", (30, 20, 3), loc=(0, 0, -1.5), m=L.mat("granit", (0.05, 0.05, 0.055), 0.1, 0.3, bump=0.2))
    k, _ = kolben_set(ALU)
    br = L.empty("portal", (0, 0, 0))
    for s_ in (-1, 1): L.box("p_saeule", (1.4, 2, 16), loc=(s_ * 12, 0, 8), m=L.mat("weiss", (0.8, 0.8, 0.8), 0, 0.4)).parent = br
    L.box("p_quer", (26, 2, 1.6), loc=(0, 0, 16), m=L.mat("weiss2", (0.8, 0.8, 0.8), 0, 0.4)).parent = br
    pr = L.empty("taster", (0, 0, 10))
    L.cyl("t_schaft", 0.6, 6, loc=(0, 0, 3), m=STAHL_D).parent = pr
    L.cyl("t_nadel", 0.12, 3, loc=(0, 0, -1.2), m=STAHL).parent = pr
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, -2.8)); rb = bpy.context.active_object; L.setmat(rb, L.mat("rubin", (0.8, 0.05, 0.05), 0, 0.1)); rb.parent = pr
    lights_dark(t=(0, 0, 4))
    c, tg = cam((8, -26, 9), (0, 0, 4), 40)
    pts = [(4.6, 0, 1.5 + 2.8), (0, -4.6, 2 + 2.8), (-4.6, 0, 1 + 2.8), (0, 4.6, 2.5 + 2.8), (2.0, 0, 6.3 + 2.8)]
    def fn(f, u):
        seg = min(len(pts) - 1, int(u * len(pts))); su = (u * len(pts)) % 1
        p = pts[seg]; away = (p[0] * 1.4, p[1] * 1.4, p[2] + 2)
        q = math.sin(min(1, su) * pi)
        loc = lerpv(away, p, q)
        K(pr, f, loc=loc); K(br, f, loc=(0, loc[1], 0))
        K(k, f, rot=(0, 0, 0.3 * u))
        K(c, f, loc=lerpv((8, -26, 9), (5, -23, 8), ease(u)))
    frames(fn)

def s_explode():
    light_stage()
    k = L.piston("kolben", ALU)
    rings = [L.ring(f"ring{i}", z, h=0.13 if i < 2 else 0.30, m=STAHL_D if i == 0 else STAHL) for i, z in enumerate([5.07, 4.52, 3.78])]
    p = L.pin(STAHL)
    clips = []
    for s_ in (-1, 1):
        cl = L.lathe("clip", [(0.85, -0.05), (1.05, -0.05), (1.05, 0.05), (0.85, 0.05), (0.85, -0.05)], 32, STAHL_D)
        cl.rotation_euler = (0, pi / 2, 0); cl.location = (s_ * 3.85, 0, 2.55); clips.append((cl, s_))
    pl = L.conrod(STAHL_D, 14.5); pl.location = (0, 0, 2.55)
    lights_light(t=(0, 0, 2))
    c, tg = cam((22, -30, 14), (0, 0, 0), 38)
    home = {o: tuple(o.location) for o in rings + [p, pl] + [c_ for c_, _ in clips]}
    out = {rings[0]: (0, 0, 9), rings[1]: (0, 0, 6.5), rings[2]: (0, 0, 4)}
    out[p] = (11, 0, 2.55); out[pl] = (0, 0, -9)
    for cl, s_ in clips: out[cl] = (s_ * 17, 0, 2.55)
    def fn(f, u):
        if VAR == "auf": e = ease((u - 0.15) / 0.5)
        else: e = 1 - ease((u - 0.1) / 0.55)
        for o, h in home.items():
            K(o, f, loc=lerpv(h, out[o], e))
        K(k, f, rot=(0, 0, 0.5 * u))
        K(c, f, loc=lerpv((22, -30, 14), (16, -26, 10), ease(u)))
    frames(fn)

def s_erde():
    dark_stage(floor=False)
    em = bpy.data.materials.new("erde"); em.use_nodes = True; nt = em.node_tree; b = nt.nodes["Principled BSDF"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 6
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.52; cr.color_ramp.elements[0].color = (0.04, 0.07, 0.12, 1)
    cr.color_ramp.elements[1].position = 0.54; cr.color_ramp.elements[1].color = (0.42, 0.4, 0.36, 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6
    bpy.ops.mesh.primitive_uv_sphere_add(radius=6, segments=96, ring_count=48); g = bpy.context.active_object; L.setmat(g, em); L.smooth(g)
    # Linie als Kurve (Spirale 1,25 Umläufe)
    cu = bpy.data.curves.new("linie", "CURVE"); cu.dimensions = "3D"; sp = cu.splines.new("POLY"); n = 300
    sp.points.add(n - 1)
    for i in range(n):
        a = i / (n - 1) * 2 * pi * 1.27; lat = 0.25 * math.sin(a * 0.8)
        sp.points[i].co = (6.12 * math.cos(a) * math.cos(lat), 6.12 * math.sin(a) * math.cos(lat), 6.12 * math.sin(lat), 1)
    cu.bevel_depth = 0.07; ln = L.link(bpy.data.objects.new("linie", cu))
    lm = L.mat("linie_m", (1, .4, .1), emit=(1, .38, .05), estr=12); ln.data.materials.append(lm)
    stand = L.lathe("staender", [(0, -9), (3, -9), (3, -8.6), (0.4, -8.2), (0.4, -6)], 48, STAHL)
    L.area("key", (14, -14, 10), 10, 2600, target=(0, 0, 0)); L.area("rim", (-14, 10, 6), 8, 2000, col=(.6, .75, 1), target=(0, 0, 0))
    c, tg = cam((0, -36, 8), (0, 0, 0), 50)
    def fn(f, u):
        cu.bevel_factor_end = ease(u / 0.85); cu.keyframe_insert("bevel_factor_end", frame=f)
        K(g, f, rot=(0.3, 0, -0.8 * u)); K(ln, f, rot=(0.3, 0, -0.8 * u))
        K(c, f, loc=lerpv((0, -38, 9), (0, -32, 7), ease(u)))
    frames(fn)

def s_stahl():
    dark_stage()
    sm = L.mat("stahlk", (0.62, 0.63, 0.66), 1, 0.24, bump=0.02)
    k = L.piston("stahlkolben", sm); k.scale = (1, 1, 1.15)
    for i, z in enumerate([5.07, 4.52, 3.78]):
        r = L.ring(f"ring{i}", z, h=0.13 if i < 2 else 0.3, m=STAHL_D); r.parent = k
    lights_dark(t=(0, 0, 3.5), k=1.5)
    L.area("front", (0, -20, 6), 12, 1200, target=(0, 0, 3))
    sweep = L.area("sweep", (-20, -10, 8), 3, 3000, target=(0, 0, 3))
    c, tg = cam((0, -22, 7), (0, 0, 3.4), 45)
    def fn(f, u):
        K(k, f, rot=(0, 0, 1.4 * u)); K(sweep, f, loc=(lerp(-20, 20, u), -10, 8)); K(c, f, loc=lerpv((0, -22, 7), (0, -17, 5.5), ease(u)))
    frames(fn)

def s_bg():
    if VAR == "hell":
        light_stage(); k, _ = kolben_set(ALU); lights_light(t=(0, 0, 3)); c, tg = cam((14, -24, 10), (0, 0, 3), 45, dof=1.2)
    else:
        L.hall(dark=True); k, _ = kolben_set(ALU); lights_dark(t=(0, 0, 3)); c, tg = cam((-12, -22, 8), (0, 0, 3), 45, dof=1.0)

def s_thumb():
    dark_stage()
    hot = glowmat("hot", (0.22, 0.2, 0.2), 1, 0.3, col=(1, .09, .0))
    nt = hot.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 3.0; mr.inputs[2].default_value = 6.0; mr.inputs[3].default_value = 0; mr.inputs[4].default_value = 0.9
    nt.links.new(sep.outputs[2], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs["Emission Strength"])
    k, _ = kolben_set(hot if VAR != "b" else ALU)
    L.area("rim", (-12, 10, 10), 6, 3500, col=(1, .45, .15), target=(0, 0, 3)); L.area("rim2", (12, 10, 6), 5, 2500, col=(.5, .65, 1), target=(0, 0, 3))
    L.area("key", (8, -14, 14), 6, 900, target=(0, 0, 3))
    if VAR == "a":
        k.rotation_euler = (0.15, 0, 0.5); c, tg = cam((10, -19, 10), (-3.4, 0, 3.6), 50)
    elif VAR == "b":
        L.point("glut", (0, 0, 9), 1200, col=(1, .4, .1), r=2)
        ring = L.lathe("kreis", [(4.75, 6.3), (4.95, 6.3), (4.95, 6.4), (4.75, 6.4), (4.75, 6.3)], 128, L.mat("kreis", (0, 0, 0), emit=(1, .3, .05), estr=6))
        k.scale = (0.9, 1.0, 1.0); c, tg = cam((2, -14, 22), (-4.5, 0, 4.0), 50)
    else:
        ghost_cyl(-2, 8.5); fl = L.mat("fl", (0, 0, 0), emit=(1, .18, .02), estr=2)
        L.lathe("flame", [(0, 6.05), (4.3, 6.05), (4.3, 6.6), (2.5, 7.6), (0, 8.0)], 64, fl)
        L.point("glut", (0, 0, 8), 1500, col=(1, .35, .08), r=2); c, tg = cam((8, -26, 8), (-4.5, 0, 4.0), 50)
    sc.render.resolution_percentage = 100

S = {"thumb": s_thumb, "motor": s_motor, "messuhr": s_messuhr, "band": s_band, "gewicht": s_gewicht, "glut": s_glut, "barren": s_barren, "alt": s_alt,
     "brief": s_brief, "werkstatt": s_werkstatt, "schmelze": s_schmelze, "dehnung": s_dehnung, "kokille": s_kokille, "alfin": s_alfin,
     "guss": s_guss, "entformen": s_entformen, "spuelen": s_spuelen, "kanal": s_kanal, "drehbank": s_drehbank, "ofen": s_ofen,
     "profil": s_profil, "oval3d": s_oval3d, "konus3d": s_konus3d, "spalt": s_spalt, "fresser": s_fresser, "unten": s_unten,
     "siebdruck": s_siebdruck, "messen": s_messen, "explode": s_explode, "erde": s_erde, "stahl": s_stahl, "bg": s_bg}
S[SCN]()
all_linear()
sc.frame_start, sc.frame_end = 1, N
sc.render.resolution_x, sc.render.resolution_y = (1280, 720) if SCN == "thumb" else (1920, 1080) if STILL else (960, 540)
if STILL: sc.cycles.samples = 48
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.06
if not STILL: sc.cycles.samples = int(os.environ.get("MW_SAMPLES", "5"))
sc.cycles.max_bounces = 3; sc.cycles.glossy_bounces = 2; sc.cycles.diffuse_bounces = 1; sc.cycles.transparent_max_bounces = 4
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
try: sc.cycles.denoising_prefilter = "FAST"
except Exception: pass
sc.render.motion_blur_shutter = 0.5
os.makedirs(OUT, exist_ok=True)
sc.render.filepath = OUT + "/f_"
if len(sys.argv) > 6:
    f = int(sys.argv[6]); sc.frame_set(f); sc.render.filepath = OUT + f"/test_{f:04d}.png"; bpy.ops.render.render(write_still=True)
else:
    if os.environ.get("MW_RANGE"):
        a_, b_ = os.environ["MW_RANGE"].split("-"); sc.frame_start, sc.frame_end = int(a_), int(b_)
    bpy.ops.render.render(animation=True)
