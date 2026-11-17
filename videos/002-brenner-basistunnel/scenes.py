"""Meisterwerk – Blender scenes for the main part (ball bearing video).
usage: python3 scenes2.py <scene> <outdir> [fs fe]
"""
import bpy, bmesh, math, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

SCENE, OUT = sys.argv[1], sys.argv[2]
FS = int(sys.argv[3]) if len(sys.argv) > 3 else None
FE = int(sys.argv[4]) if len(sys.argv) > 4 else None
STEP = int(sys.argv[5]) if len(sys.argv) > 5 else 1

bpy.ops.wm.read_factory_settings(use_empty=True)
P = bpy.context.preferences.edit
P.keyframe_new_interpolation_type = "BEZIER"; P.keyframe_new_handle_type = "AUTO_CLAMPED"
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 4; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.render.fps = 24; sc.render.film_transparent = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.82, 0.78, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.45


def mat(name, color, metal, rough, alpha=1.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color; b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = emit; b.inputs["Emission Strength"].default_value = 0
    return m

CHROME = mat("chrome", (0.9, 0.9, 0.92, 1), 1.0, 0.06)
STEEL = mat("steel", (0.7, 0.7, 0.72, 1), 1.0, 0.22)
DARKSTEEL = mat("dsteel", (0.35, 0.35, 0.37, 1), 1.0, 0.35)
ROUGH = mat("rough", (0.42, 0.40, 0.38, 1), 0.85, 0.65)
ORG = mat("org", (1.0, 0.27, 0.02, 1), 0.0, 0.35)
RUBBER = mat("rubber", (0.06, 0.06, 0.07, 1), 0.0, 0.55)
GLASS = mat("glass", (0.85, 0.88, 0.9, 1), 0.0, 0.05, alpha=0.18)
WHEEL = mat("wheel", (0.55, 0.53, 0.5, 1), 0.0, 0.95)


def shade(o, m=None, smooth=True, split=35):
    if m: o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = smooth
    if split:
        es = o.modifiers.new("es", "EDGE_SPLIT"); es.split_angle = math.radians(split)
    return o


def lathe(name, profile, m, seg=128):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    n = len(profile)
    for i in range(seg):
        A, B = rings[i], rings[(i + 1) % seg]
        for j in range(n):
            bm.faces.new((A[j], A[(j + 1) % n], B[(j + 1) % n], B[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    return shade(o, m)


def ring_profile(r_in, r_out, h, groove_r, groove_on_inner, k=24, groove=True):
    pts = []
    if groove_on_inner:
        pts += [(r_out, -h / 2), (r_out, h / 2), (r_in, h / 2)]
        if groove:
            for i in range(k + 1):
                t = math.pi / 2 - math.pi * i / k
                pts.append((r_in + groove_r * math.cos(t) * 0.55, groove_r * math.sin(t) * 0.9))
        pts += [(r_in, -h / 2)]
    else:
        pts += [(r_in, -h / 2), (r_out, -h / 2)]
        if groove:
            for i in range(k + 1):
                t = -math.pi / 2 + math.pi * i / k
                pts.append((r_out - groove_r * math.cos(t) * 0.55, groove_r * math.sin(t) * 0.9))
        pts += [(r_out, h / 2), (r_in, h / 2)]
    return pts

R_BALL, PITCH = 0.32, 1.55
def outer_ring(m=STEEL, groove=True): return lathe("outer", ring_profile(PITCH + 0.18, 2.15, 0.75, R_BALL, True, groove=groove), m)
def inner_ring(m=STEEL, groove=True): return lathe("inner", ring_profile(0.95, PITCH - 0.18, 0.75, R_BALL, False, groove=groove), m)


def ball(loc, r=R_BALL, m=CHROME, seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o


def cyl(r, d, loc, rot=(0, 0, 0), m=STEEL, v=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.object; return shade(o, m)


def box(size, loc, m=STEEL, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object; o.scale = size
    o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    return o


def cage_half(n, z=0.0, m=ORG):
    bpy.ops.mesh.primitive_torus_add(major_radius=PITCH, minor_radius=0.05, location=(0, 0, z))
    c = bpy.context.object; c.data.materials.append(m); bpy.ops.object.shade_smooth()
    tabs = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        bpy.ops.mesh.primitive_cube_add(size=1, location=(PITCH * math.cos(a), PITCH * math.sin(a), z * 0.4))
        b = bpy.context.object; b.scale = (0.12, 0.12, 0.36); b.rotation_euler = (0, 0, a); b.data.materials.append(m); tabs.append(b)
    for b in tabs: b.select_set(True)
    c.select_set(True); bpy.context.view_layer.objects.active = c; bpy.ops.object.join()
    return c


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e


def camera(lens, tgt):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return cam


def area(loc, energy, size, tgt, color=(1, 1, 1)):
    d = bpy.data.lights.new("a", "AREA"); d.energy = energy; d.size = size; d.color = color
    o = bpy.data.objects.new("a", d); sc.collection.objects.link(o); o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"


def studio(tgt, k=1.0):
    area((-5, -5, 7), 1300 * k, 6, tgt); area((6, -3, 3), 500 * k, 4, tgt, (1, 0.92, 0.85)); area((0, 6, 5), 900 * k, 5, tgt)


def key(o, f, path="location"): o.keyframe_insert(path, frame=f)


def linear():
    P.keyframe_new_interpolation_type = "LINEAR"
def bez():
    P.keyframe_new_interpolation_type = "BEZIER"


def vis(o, frames_on):
    """frames_on: list of (frame, visible)"""
    for f, v in frames_on:
        o.hide_render = not v; o.keyframe_insert("hide_render", frame=f)
        o.hide_viewport = not v; o.keyframe_insert("hide_viewport", frame=f)



# ================= 002 Brenner-Basistunnel =================
import random
random.seed(5)
HSCALE = 1.0
anchors = {}
tgt = empty("t")
END = 96


def rockmat(name="rock", c1=(0.10, 0.085, 0.07, 1), c2=(0.28, 0.25, 0.22, 1), scale=3.0, rough=0.9):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = c1; cr.color_ramp.elements[1].color = c2
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    bm_ = nt.nodes.new("ShaderNodeBump"); bm_.inputs["Strength"].default_value = 0.6
    nt.links.new(nz.outputs["Fac"], bm_.inputs["Height"]); nt.links.new(bm_.outputs["Normal"], b.inputs["Normal"])
    return m


ROCK = rockmat()
CONC = mat("conc", (0.42, 0.41, 0.39, 1), 0.0, 0.8)
CONC2 = mat("conc2", (0.33, 0.32, 0.30, 1), 0.0, 0.8)
WHITE = mat("white", (0.75, 0.75, 0.76, 1), 0.0, 0.4)
BLACK = mat("black", (0.04, 0.04, 0.05, 1), 0.0, 0.5)
YEL = mat("yel", (1.0, 0.75, 0.05, 1), 0.0, 0.4)


def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = color; e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0]); return m


def arc_seg(name, r_in, r_out, width, a0, a1, m, k=24):
    """ring segment around X axis (tunnel axis = X), angles in radians, x from -w/2..w/2"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); vs = []
    for i in range(k + 1):
        a = a0 + (a1 - a0) * i / k
        ring = []
        for r, x in ((r_in, -width / 2), (r_out, -width / 2), (r_out, width / 2), (r_in, width / 2)):
            ring.append(bm.verts.new((x, r * math.cos(a), r * math.sin(a))))
        vs.append(ring)
    for i in range(k):
        A, B = vs[i], vs[i + 1]
        for j in range(4):
            bm.faces.new((A[j], A[(j + 1) % 4], B[(j + 1) % 4], B[j]))
    bm.faces.new(list(reversed(vs[0]))); bm.faces.new(vs[-1])
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    return shade(o, m, split=40)


def tube_x(r_in, r_out, x0, x1, m, a0=0, a1=2 * math.pi, k=64):
    o = arc_seg("tube", r_in, r_out, x1 - x0, a0, a1, m, k); o.location.x = (x0 + x1) / 2; return o


def rock_chunk(loc, s, m=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=s, location=loc)
    o = bpy.context.object
    for v in o.data.vertices: v.co *= random.uniform(0.7, 1.3)
    o.data.materials.append(m or ROCK); o.rotation_euler = (random.random() * 6, random.random() * 6, random.random() * 6)
    return o


def cutterhead(r=1.0, depth=0.22, n_cut=26):
    root = empty("head")
    h = cyl(r, depth, (0, 0, 0), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=96); h.parent = root
    face = depth / 2 + 0.01
    for k in range(6):  # orange spokes
        a = 2 * math.pi * k / 6
        b = box((0.06, 0.16, r * 0.92), (face + 0.03, 0.46 * r * math.cos(a), 0.46 * r * math.sin(a)), m=ORG, bevel=0.01)
        b.rotation_euler = (a - math.pi / 2, 0, 0); b.parent = root
    for k in range(n_cut):  # disc cutters on a spiral
        rr = 0.12 + (r - 0.2) * k / (n_cut - 1); a = k * 2.4
        c = cyl(0.07, 0.03, (face + 0.05, rr * math.cos(a), rr * math.sin(a)), rot=(0, 0, 0), m=CHROME, v=24)
        c.rotation_euler = (a, 0, 0); c.parent = root
    hub = cyl(0.16, 0.12, (face + 0.05, 0, 0), rot=(0, math.pi / 2, 0), m=ORG, v=32); hub.parent = root
    for k in range(6):  # muck openings
        a = 2 * math.pi * (k + .5) / 6
        o = box((0.03, 0.12, 0.28), (face + 0.005, 0.8 * r * math.cos(a), 0.8 * r * math.sin(a)), m=BLACK, bevel=0)
        o.rotation_euler = (a - math.pi / 2, 0, 0); o.parent = root
    return root


def tbm(r=1.0, gantries=5):
    root = empty("tbm")
    head = cutterhead(r); head.parent = root
    sh = cyl(r * 0.97, 1.6, (-0.9, 0, 0), rot=(0, math.pi / 2, 0), m=STEEL, v=96); sh.parent = root
    st = cyl(r * 0.975, 0.1, (-0.4, 0, 0), rot=(0, math.pi / 2, 0), m=ORG, v=96); st.parent = root
    tail = cyl(r * 0.95, 0.8, (-2.1, 0, 0), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=96); tail.parent = root
    for g in range(gantries):
        x = -3.2 - g * 1.35
        for y in (-0.55, 0.55):
            p = box((1.1, 0.06, 1.2), (x, y, -0.25), m=ORG if g % 2 == 0 else YEL, bevel=0.01); p.parent = root
        deck = box((1.2, 1.2, 0.06), (x, 0, 0.35), m=DARKSTEEL, bevel=0.01); deck.parent = root
        tank = cyl(0.18, 0.9, (x, 0.3, 0.6), rot=(0, math.pi / 2, 0), m=WHITE, v=24); tank.parent = root
        cab = box((0.5, 0.4, 0.35), (x, -0.25, 0.58), m=WHITE, bevel=0.03); cab.parent = root
        for wx in (-0.4, 0.4):
            wh = cyl(0.12, 0.08, (x + wx, 0.55, -0.85), rot=(math.pi / 2, 0, 0), m=BLACK, v=16); wh.parent = root
            wh = cyl(0.12, 0.08, (x + wx, -0.55, -0.85), rot=(math.pi / 2, 0, 0), m=BLACK, v=16); wh.parent = root
    belt = box((gantries * 1.35 + 2.4, 0.22, 0.05), (-2.6 - gantries * 0.65, 0, 0.98), m=BLACK, bevel=0); belt.parent = root
    pipe = cyl(0.12, gantries * 1.35 + 2.6, (-2.6 - gantries * 0.65, -0.5, 0.95), rot=(0, math.pi / 2, 0), m=YEL, v=24); pipe.parent = root
    return root, head


if SCENE == "tbm":  # product shot: whole TBM, head rotating, camera orbit
    END = 144
    root, head = tbm()
    linear(); head.rotation_euler = (0, 0, 0); key(head, 1, "rotation_euler"); head.rotation_euler = (math.radians(360), 0, 0); key(head, END, "rotation_euler"); bez()
    tgt.location = (-3.2, 0, 0)
    cam = camera(34, tgt)
    cam.location = (3.5, -9.0, 2.8); key(cam, 1); cam.location = (0.0, -10.0, 1.6); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "kopf":  # front 3/4 view of the rotating cutterhead
    END = 96
    root, head = tbm(gantries=1)
    linear(); head.rotation_euler = (0, 0, 0); key(head, 1, "rotation_euler"); head.rotation_euler = (math.radians(180), 0, 0); key(head, END, "rotation_euler"); bez()
    tgt.location = (-0.3, 0, 0)
    cam = camera(40, tgt)
    cam.location = (4.6, -2.6, 1.3); key(cam, 1); cam.location = (4.0, -1.6, 0.9); key(cam, END)
    studio(tgt, 0.8)
    area((6, 0, 1), 400, 3, tgt)

elif SCENE == "bohrkopf":  # close: head presses into rock, chips fall
    END = 120
    root, head = tbm(gantries=1)
    wall = box((3.0, 4.5, 4.5), (1.62, 0, 0), m=ROCK, bevel=0)
    # cut the wall in half (cutaway) so we see the head inside it
    wall.scale = (3.0, 2.25, 4.5); wall.location = (1.62, 1.125 + 0.0, 0)
    root.location = (-0.2, 0, 0); key(root, 1); root.location = (0.25, 0, 0); key(root, END)
    linear(); head.rotation_euler = (0, 0, 0); key(head, 1, "rotation_euler"); head.rotation_euler = (math.radians(300), 0, 0); key(head, END, "rotation_euler"); bez()
    for i in range(40):
        f0 = random.randint(1, END - 20)
        y = random.uniform(-0.9, 0.4); z = random.uniform(-0.3, 0.9)
        c = rock_chunk((0.25, y, z), random.uniform(0.03, 0.07))
        vis(c, [(1, False), (f0, True), (f0 + 20, False)])
        c.location = (0.25 + 0.4 * (f0 / END), y, z); key(c, f0)
        c.location = (0.1 + 0.4 * (f0 / END), y - 0.1, -0.95); key(c, f0 + 18)
    tgt.location = (0.0, 0, 0)
    cam = camera(32, tgt)
    cam.location = (-2.5, -6.0, 1.6); key(cam, 1); cam.location = (-1.0, -5.2, 1.0); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "tuebbing":  # ring build: 6 segments placed by erector, previous rings behind
    END = 168
    R0, R1, Wd = 1.0, 1.14, 0.42
    for k in range(8):  # finished rings
        x = -0.45 - k * (Wd + 0.015)
        for s in range(6):
            a0 = math.radians(s * 60 + (k % 2) * 30 + 0.6); a1 = math.radians((s + 1) * 60 + (k % 2) * 30 - 0.6)
            seg = arc_seg("r", R0, R1, Wd, a0, a1, CONC if (s + k) % 2 else CONC2); seg.location.x = x
    arm = empty("arm")
    beam = box((0.12, 0.12, 0.85), (0, 0, -0.45), m=ORG, bevel=0.01); beam.parent = arm
    hubc = cyl(0.2, 0.3, (0, 0, 0), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=32)
    order = [0, 1, 5, 2, 4, 3]  # bottom first, then alternate sides, key last
    angles = [-90, -30, -150, 30, 210, 90]
    for j, s in enumerate(order):
        f0 = 4 + j * 26
        ang = math.radians(angles[j])
        piv = empty("p"); piv.location = (0, 0, 0)
        seg = arc_seg("n", R0, R1, Wd, math.radians(-90 - 29.4), math.radians(-90 + 29.4), ORG if j == 5 else CONC)
        seg.parent = piv
        vis(seg, [(1, False), (f0, True)])
        # starts lowered (on the feeder, closer to the axis) then swings to final angle and moves out
        seg.location = (-1.2, 0, -0.5); key(seg, 1); key(seg, f0)
        seg.location = (0, 0, 0.35); key(seg, f0 + 8)
        seg.location = (0, 0, 0.0); key(seg, f0 + 22)
        piv.rotation_euler = (0, 0, 0); key(piv, 1, "rotation_euler"); key(piv, f0 + 8, "rotation_euler")
        piv.rotation_euler = (ang + math.pi / 2, 0, 0); key(piv, f0 + 20, "rotation_euler")
        arm.rotation_euler = (0, 0, 0) if j == 0 else (math.radians(angles[j - 1]) + math.pi / 2, 0, 0); key(arm, f0 + 8, "rotation_euler")
        arm.rotation_euler = (ang + math.pi / 2, 0, 0); key(arm, f0 + 20, "rotation_euler")
    tgt.location = (-0.6, 0, 0)
    cam = camera(36, tgt)
    cam.location = (3.4, -4.6, 1.9); key(cam, 1); cam.location = (3.9, -3.5, 1.2); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "system":  # two main tubes + exploratory gallery below + cross passages
    END = 192
    GL = mat("gl", (0.55, 0.56, 0.6, 1), 0.0, 0.3, alpha=0.28)
    L0, L1 = -14, 14
    for y in (-1.3, 1.3):
        t_ = tube_x(0.55, 0.62, L0, L1, GL); t_.location.y = y
        ln = cyl(0.05, L1 - L0, (0, y, -0.52), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=8)
    gal = tube_x(0.30, 0.36, L0, L1, mat("galm", (1.0, 0.36, 0.06, 1), 0.0, 0.5)); gal.location = (0, 0, -1.25)
    gal.scale = (0.001, 1, 1); key(gal, 1, "scale"); key(gal, 56, "scale"); gal.scale = (1, 1, 1); key(gal, 90, "scale")
    vis(gal, [(1, False), (56, True)])
    k = 0
    for x in range(L0 + 2, L1 - 1, 3):
        q = cyl(0.22, 2.0, (x, 0, 0), rot=(math.pi / 2, 0, 0), m=YEL, v=24)
        vis(q, [(1, False), (110 + k * 6, True)]); q.scale = (1, 1, 0.01); key(q, 1, "scale"); key(q, 110 + k * 6, "scale"); q.scale = (1, 1, 1); key(q, 118 + k * 6, "scale"); k += 1
    train = box((3.0, 0.5, 0.5), (-12, -1.3, -0.15), m=WHITE, bevel=0.08)
    stripe = box((3.02, 0.52, 0.08), (-12, -1.3, -0.25), m=ORG, bevel=0); stripe.parent = train; stripe.location = (0, 0, -0.1)
    stripe.matrix_parent_inverse = train.matrix_world.inverted() if False else stripe.matrix_parent_inverse
    linear(); train.location = (-16, -1.3, -0.15); key(train, 1); train.location = (16, -1.3, -0.15); key(train, END); bez()
    tgt.location = (0, 0, -0.4)
    cam = camera(30, tgt)
    cam.location = (-7, -12, 8.5); key(cam, 1); cam.location = (4, -11, 6.5); key(cam, END)
    sc.cycles.samples = 12
    studio(tgt, 0.8)

elif SCENE == "berg":  # mountain block cutaway, old line over the pass vs flat base tunnel
    END = 144
    NX, NY = 220, 60; SX, SY = 24.0, 6.0
    def hgt(x, y):
        h = 3.6 * math.exp(-((x - 0.5) ** 2) / 18) + 1.4 * math.exp(-((x + 5) ** 2) / 6) + 1.2 * math.exp(-((x - 6) ** 2) / 5)
        h += 0.25 * math.sin(x * 2.1 + y * 1.7) + 0.18 * math.sin(x * 4.3 - y * 3.1) + 0.12 * math.sin(x * 7.9 + y * 5.3)
        return h
    me = bpy.data.meshes.new("terrain"); bm = bmesh.new(); grid = []
    for i in range(NX + 1):
        row = []
        for j in range(NY + 1):
            x = -SX / 2 + SX * i / NX; y = -SY / 2 + SY * j / NY
            row.append(bm.verts.new((x, y, hgt(x, y))))
        grid.append(row)
    for i in range(NX):
        for j in range(NY):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    # front skirt (y = -SY/2) down to base
    BASE = -2.5
    bot = [bm.verts.new((grid[i][0].co.x, -SY / 2, BASE)) for i in range(NX + 1)]
    for i in range(NX): bm.faces.new((grid[i + 1][0], grid[i][0], bot[i], bot[i + 1]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    terr = bpy.data.objects.new("terr", me); sc.collection.objects.link(terr)
    for p in terr.data.polygons: p.use_smooth = p.index < NX * NY
    m = bpy.data.materials.new("terrm"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.9
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nrm = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], nrm.inputs[0])
    cr = nt.nodes.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.30, 0.38, 0.22, 1); el[1].position = 0.55; el[1].color = (0.42, 0.40, 0.36, 1)
    e3 = el.new(0.8); e3.color = (0.95, 0.95, 0.97, 1)
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs[1].default_value = 0.0; mr.inputs[2].default_value = 4.0
    nt.links.new(sep.outputs[2], mr.inputs[0]); nt.links.new(mr.outputs[0], cr.inputs[0])
    rk = rockmat("frontrock", (0.40, 0.36, 0.32, 1), (0.60, 0.56, 0.50, 1), 1.5)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    # front face (normal.y strongly negative) -> rock color
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(nrm.outputs[1], ab.inputs[0])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = "GREATER_THAN"; lt.inputs[1].default_value = 0.7
    nt.links.new(ab.outputs[0], lt.inputs[0]); nt.links.new(lt.outputs[0], mix.inputs[0])
    nt.links.new(cr.outputs[0], mix.inputs[6]); mix.inputs[7].default_value = (0.45, 0.40, 0.35, 1)
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    terr.data.materials.append(m)
    base = box((SX, SY, 0.4), (0, 0, BASE - 0.2), m=DARKSTEEL, bevel=0.02)
    FY = -SY / 2 - 0.04
    # old mountain line: follows the surface at the front, offset up
    cdo = bpy.data.curves.new("old", "CURVE"); cdo.dimensions = "3D"; spo = cdo.splines.new("POLY"); pts = []
    for i in range(121):
        x = -SX / 2 + SX * i / 120; pts.append((x, FY - 0.02, min(hgt(x, -SY / 2) * 0.62 + 0.25, 3.0)))
    spo.points.add(len(pts) - 1)
    for p, c in zip(spo.points, pts): p.co = (*c, 1)
    cdo.bevel_depth = 0.06; old = bpy.data.objects.new("oldl", cdo); sc.collection.objects.link(old); old.data.materials.append(BLACK)
    # base tunnel: almost flat line low in the block
    cdt = bpy.data.curves.new("bt", "CURVE"); cdt.dimensions = "3D"; spt = cdt.splines.new("POLY"); pts = []
    for i in range(121):
        x = -SX / 2 + SX * i / 120; pts.append((x, FY - 0.04, -1.4 + 0.18 * math.exp(-((x - 0.5) ** 2) / 40)))
    spt.points.add(len(pts) - 1)
    for p, c in zip(spt.points, pts): p.co = (*c, 1)
    cdt.bevel_depth = 0.11
    bt = bpy.data.objects.new("btl", cdt); sc.collection.objects.link(bt); bt.data.materials.append(emit_mat("glow", (1.0, 0.36, 0.05, 1), 3.0))
    cdt.bevel_factor_end = 0.0; cdt.keyframe_insert("bevel_factor_end", frame=30)
    cdt.bevel_factor_end = 1.0; cdt.keyframe_insert("bevel_factor_end", frame=110)
    tgt.location = (0, 0, 0.7)
    cam = camera(36, tgt)
    cam.location = (-3, -33, 6.5); key(cam, 1); cam.location = (2, -31, 4.6); key(cam, END)
    studio(tgt, 1.0)
    sc.frame_set(END)
    for nm, x in (("innsbruck", -SX / 2 + 0.6), ("pass", 0.5), ("franz", SX / 2 - 0.6)):
        p = world_to_camera_view(sc, cam, Vector((x, FY, hgt(x, -SY / 2) * 0.62 + 0.25))); anchors[nm] = [p.x, 1 - p.y]
    p = world_to_camera_view(sc, cam, Vector((0.5, FY, -1.25))); anchors["tunnel"] = [p.x, 1 - p.y]

elif SCENE == "sprengen":  # drill pattern, blast, debris flies
    END = 120
    face = box((0.6, 5, 4), (0.3, 0, 0), m=ROCK, bevel=0)
    sidel = box((3, 0.6, 4), (-1.5, -2.2, 0), m=ROCK, bevel=0); sider = box((3, 0.6, 4), (-1.5, 2.2, 0), m=ROCK, bevel=0)
    floor_ = box((3, 5, 0.3), (-1.5, 0, -1.6), m=CONC2, bevel=0)
    holes = []
    pts = [(0, 0)] + [(0.35 * math.cos(a), 0.35 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]]
    pts += [(0.85 * math.cos(a), 0.85 * math.sin(a)) for a in [k * math.pi / 6 for k in range(12)]]
    pts += [(y, z) for y in (-1.5, -0.75, 0, 0.75, 1.5) for z in (-1.25, 1.25)] + [(y, 0) for y in (-1.5, 1.5)]
    for k, (y, z) in enumerate(pts):
        hcy = cyl(0.045, 0.05, (-0.005, y, z + 0.1), rot=(0, math.pi / 2, 0), m=BLACK, v=12)
        vis(hcy, [(1, False), (4 + k, True), (70, False)])
        wire = cyl(0.012, 0.5, (-0.2, y, z + 0.1), rot=(0, math.pi / 2, 0), m=ORG, v=6)
        vis(wire, [(1, False), (40 + k // 3, True), (70, False)])
    BL = 70
    chunks = []
    for i in range(90):
        y = random.uniform(-1.8, 1.8); z = random.uniform(-1.3, 1.6)
        c = rock_chunk((0.0, y, z), random.uniform(0.06, 0.2))
        vis(c, [(1, False), (BL, True)])
        c.location = (0.05, y, z); key(c, BL)
        vx = random.uniform(-4.5, -1.5); vy = y * random.uniform(0.3, 0.9); vz = random.uniform(0.0, 2.0)
        for f in range(BL + 2, END + 1, 4):
            t_ = (f - BL) / 24.0; zz = z + vz * t_ - 4.9 * t_ * t_
            c.location = (0.05 + vx * t_, y + vy * t_, max(zz, -1.42)); key(c, f)
    face.location = (0.3, 0, 0); key(face, BL); face.location = (0.75, 0, 0); key(face, BL + 2)
    tgt.location = (0.0, 0, 0)
    cam = camera(30, tgt)
    cam.location = (-7.5, -3.0, 1.0); key(cam, 1); key(cam, BL); cam.location = (-8.5, -3.6, 1.4); key(cam, END)
    studio(tgt, 0.8)
    anchors["blast_frame"] = BL

elif SCENE == "zug":  # train passes through cutaway tube
    END = 96
    t_ = tube_x(1.0, 1.12, -12, 12, CONC, a0=math.radians(-160), a1=math.radians(100), k=72)
    bed = box((24, 1.4, 0.15), (0, 0, -0.88), m=CONC2, bevel=0)
    for y in (-0.3, 0.3):
        cyl(0.025, 24, (0, y, -0.78), rot=(0, math.pi / 2, 0), m=CHROME, v=8)
    wire = cyl(0.015, 24, (0, 0, 0.72), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=6)
    tr = empty("train")
    for c in range(5):
        car = box((2.2, 0.62, 0.72), (-c * 2.3, 0, -0.3), m=WHITE, bevel=0.06); car.parent = tr
        stp = box((2.21, 0.63, 0.06), (-c * 2.3, 0, -0.42), m=ORG, bevel=0); stp.parent = tr
        win = box((1.9, 0.635, 0.16), (-c * 2.3, 0, -0.16), m=BLACK, bevel=0.02); win.parent = tr
    nose = box((0.6, 0.6, 0.6), (1.2, 0, -0.35), m=WHITE, bevel=0.25); nose.parent = tr
    linear(); tr.location = (-14, 0, 0); key(tr, 1); tr.location = (26, 0, 0); key(tr, END); bez()
    for x in range(-11, 12, 3):
        l_ = box((0.3, 0.05, 0.05), (x, 0.9, 0.4), m=emit_mat("lamp", (1, 0.85, 0.6, 1), 8), bevel=0)
    tgt.location = (0, 0, -0.2)
    cam = camera(28, tgt)
    cam.location = (1.5, -6.2, 1.0); key(cam, 1); cam.location = (-1.0, -5.8, 0.8); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "durchschlag":  # rock wall breaks open, cutterhead pushes through, light behind
    END = 120
    R = 1.0
    t_ = tube_x(1.0, 1.12, -6, -0.05, CONC, a0=math.radians(-160), a1=math.radians(100), k=72)
    # wall made of many chunks in a grid
    BR = 56
    for iy in range(-6, 7):
        for iz in range(-6, 7):
            y, z = iy * 0.19, iz * 0.19
            if y * y + z * z > 1.02: continue
            c = rock_chunk((0.15, y, z), 0.13)
            c.location = (0.15, y, z); key(c, 1); key(c, BR - 1)
            if y * y + z * z < 0.95:
                d = random.uniform(0.6, 1.4)
                vis(c, [(1, True), (BR + 26, False)])
                for f in range(BR, BR + 26, 3):
                    t2 = (f - BR) / 24
                    c.location = (0.15 - 1.4 * t2 * d, y * (1 + 0.6 * t2), z + 0.8 * t2 - 4.9 * t2 * t2); key(c, f)
    back = box((0.5, 3.0, 3.0), (0.6, 0, 0), m=ROCK, bevel=0)
    ring = lathe("ringcut", [(1.0, -0.25), (2.0, -0.25), (2.0, 0.25), (1.0, 0.25)], ROCK); ring.rotation_euler = (0, math.pi / 2, 0); ring.location = (0.15, 0, 0)
    vis(back, [(1, True), (BR - 2, False)])
    lightp = box((0.1, 2.0, 2.0), (3.5, 0, 0), m=emit_mat("sky", (1, 0.9, 0.75, 1), 12), bevel=0)
    root, head = tbm(gantries=0); root.rotation_euler = (0, 0, math.pi)
    root.location = (2.2, 0, 0); key(root, 1); key(root, BR - 6); root.location = (0.25, 0, 0); key(root, BR + 20); root.location = (-0.3, 0, 0); key(root, END)
    linear(); head.rotation_euler = (0, 0, 0); key(head, 1, "rotation_euler"); head.rotation_euler = (math.radians(240), 0, 0); key(head, END, "rotation_euler"); bez()
    vis(root, [(1, False), (BR - 6, True)])
    tgt.location = (0.0, 0, 0)
    cam = camera(26, tgt)
    cam.location = (-7.5, -2.2, 0.4); key(cam, 1); cam.location = (-6.0, -1.6, 0.25); key(cam, END)
    studio(tgt, 0.7)
    anchors["break_frame"] = BR

elif SCENE == "ueberbruch":  # rocks fall from a cavity onto the TBM shield in a cutaway tunnel
    END = 120
    root, head = tbm(gantries=2); root.location = (0.5, 0, 0)
    tun = tube_x(1.06, 1.6, -6, 1.6, ROCK, a0=math.radians(-160), a1=math.radians(100), k=72)
    for i in range(70):
        f0 = random.randint(10, 80)
        x = random.uniform(-1.6, 0.6); y = random.uniform(-0.5, 0.7)
        c = rock_chunk((x, y, 1.7), random.uniform(0.07, 0.18))
        vis(c, [(1, False), (f0, True)])
        c.location = (x, y, 1.7); key(c, f0)
        zf = math.sqrt(max(0.0, 1.0 - y * y)) + 0.05
        for f in range(f0 + 2, min(END, f0 + 24), 2):
            t2 = (f - f0) / 24; c.location = (x, y + 0.6 * t2 * (1 if y > 0 else -1), max(1.7 - 4.9 * t2 * t2 * 3, zf)); key(c, f)
    tgt.location = (-0.5, 0, 0.4)
    cam = camera(28, tgt)
    cam.location = (-1.5, -8.5, 2.6); key(cam, 1); cam.location = (-0.4, -7.6, 2.0); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "foerderband":  # conveyor carrying rubble out of the mountain
    END = 96
    belt = box((14, 0.6, 0.06), (0, 0, 0), m=BLACK, bevel=0)
    for x in range(-7, 8):
        cyl(0.07, 0.7, (x, 0, -0.08), rot=(math.pi / 2, 0, 0), m=STEEL, v=16)
        box((0.06, 0.06, 1.0), (x, 0.38, -0.55), m=YEL, bevel=0); box((0.06, 0.06, 1.0), (x, -0.38, -0.55), m=YEL, bevel=0)
    tun = tube_x(1.6, 1.75, -8, 8, CONC, a0=math.radians(-165), a1=math.radians(105), k=72); tun.location.z = 0.4
    linear()
    for i in range(70):
        c = rock_chunk((0, 0, 0), random.uniform(0.05, 0.14))
        x0 = random.uniform(-7, 7); y = random.uniform(-0.2, 0.2)
        c.location = (x0, y, 0.1); key(c, 1); c.location = (x0 - 6.0, y, 0.1); key(c, END)
        if x0 - 6 < -7: vis(c, [(1, True), (int(1 + (x0 + 7) / 6 * (END - 1)), False)])
    bez()
    tgt.location = (0, 0, 0)
    cam = camera(30, tgt)
    cam.location = (3.5, -6.5, 2.4); key(cam, 1); cam.location = (1.5, -6.0, 1.8); key(cam, END)
    studio(tgt, 0.8)

sc.frame_start, sc.frame_end = 1, END
sc.frame_step = STEP
if FS:
    sc.frame_start, sc.frame_end = FS, min(FE, END)
import os
os.makedirs(OUT, exist_ok=True)
json.dump(anchors, open(f"{OUT}/anchors.json", "w"))
sc.render.filepath = f"{OUT}/f_"
sc.render.image_settings.file_format = "PNG"
bpy.ops.render.render(animation=True)
