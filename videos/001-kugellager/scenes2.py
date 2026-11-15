"""Meisterwerk – Blender scenes for the main part (ball bearing video).
usage: python3 scenes2.py <scene> <outdir> [fs fe]
"""
import bpy, bmesh, math, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

SCENE, OUT = sys.argv[1], sys.argv[2]
FS = int(sys.argv[3]) if len(sys.argv) > 3 else None
FE = int(sys.argv[4]) if len(sys.argv) > 4 else None

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
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7


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


anchors = {}
tgt = empty("t")
END = 96

if SCENE == "muehle":  # Fischer principle / Entgraten: balls between two discs, top disc glass
    linear()
    base = cyl(3.2, 0.5, (0, 0, -0.55), m=DARKSTEEL, v=128)
    top = cyl(3.2, 0.4, (0, 0, 0.5), m=GLASS, v=128)
    grooves = []
    for r in (1.4, 2.0, 2.6):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.04, location=(0, 0, -0.3))
        g = bpy.context.object; g.data.materials.append(ORG); grooves.append(g)
    balls = []
    rot = empty("rot"); base.parent = rot
    for r, n in ((1.4, 10), (2.0, 14), (2.6, 18)):
        carrier = empty("c")
        for i in range(n):
            a = 2 * math.pi * i / n
            b = ball((r * math.cos(a), r * math.sin(a), 0), 0.26, seg=32); b.parent = carrier
            b.rotation_euler = (0, 0, 0); key(b, 1, "rotation_euler")
            b.rotation_euler = (math.radians(900), math.radians(360 * 1.3), 0); key(b, END, "rotation_euler")
        carrier.rotation_euler = (0, 0, 0); key(carrier, 1, "rotation_euler")
        carrier.rotation_euler = (0, 0, math.radians(70 * 1.4 / r)); key(carrier, END, "rotation_euler")
    rot.rotation_euler = (0, 0, 0); key(rot, 1, "rotation_euler")
    rot.rotation_euler = (0, 0, math.radians(140)); key(rot, END, "rotation_euler")
    bez()
    cam = camera(40, tgt)
    cam.location = (0, -9.5, 6.5); key(cam, 1); cam.location = (2.5, -7.5, 4.2); key(cam, END)
    studio(tgt)

elif SCENE == "schneiden":  # wire fed and cut into slugs
    END = 72
    rod = cyl(0.3, 8, (-4.2, 0, 0), rot=(0, math.pi / 2, 0), m=STEEL, v=48)
    guide = box((1.2, 1.4, 1.4), (-0.5, 0, 0), m=DARKSTEEL, bevel=0.08)
    blade = box((0.18, 1.2, 1.0), (0.12, 0, 1.6), m=ORG, bevel=0.03)
    slugs = []
    for k, (f_cut) in enumerate((22, 50)):
        s = cyl(0.3, 0.55, (0.38, 0, 0), rot=(0, math.pi / 2, 0), m=STEEL, v=48)
        vis(s, [(1, False), (f_cut, True)])
        s.location = (0.38, 0, 0); key(s, f_cut)
        s.location = (1.0 + 0.2 * k, -0.3 * k, -2.2); key(s, f_cut + 14)
        slugs.append(s)
    # rod feeds one slug length, gets cut (snap back = slug separated)
    for f, x in ((1, -4.2), (16, -3.65), (21, -3.65), (22, -4.2), (44, -3.65), (49, -3.65), (50, -4.2), (END, -4.2)):
        rod.location = (x, 0, 0); key(rod, f)
    for f in (22, 50):
        blade.location = (0.12, 0, 1.6); key(blade, f - 6)
        blade.location = (0.12, 0, 0.1); key(blade, f)
        blade.location = (0.12, 0, 1.6); key(blade, f + 8)
    cam = camera(45, tgt); tgt.location = (0.2, 0, -0.4)
    cam.location = (3.5, -7.5, 2.8); key(cam, 1); cam.location = (2.2, -6.0, 2.0); key(cam, END)
    studio(tgt)

elif SCENE == "stauchen":  # cold heading: two dies slam, ball with flash appears
    slug = cyl(0.42, 0.9, (0, 0, 0), rot=(0, math.pi / 2, 0), m=STEEL, v=48)
    dl = cyl(0.9, 1.6, (-3.0, 0, 0), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=64)
    dr = cyl(0.9, 1.6, (3.0, 0, 0), rot=(0, math.pi / 2, 0), m=DARKSTEEL, v=64)
    # orange rings marking the dies
    for x in (-2.15, 2.15):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.92, minor_radius=0.05, location=(x, 0, 0), rotation=(0, math.pi / 2, 0))
        t = bpy.context.object; t.data.materials.append(ORG); t.parent = dl if x < 0 else dr
        t.matrix_parent_inverse = (dl if x < 0 else dr).matrix_world.inverted()
    b = ball((0, 0, 0), 0.55, m=STEEL)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.56, minor_radius=0.045, location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    flash = bpy.context.object; flash.data.materials.append(STEEL); bpy.ops.object.shade_smooth()
    IMP = 34
    vis(slug, [(1, True), (IMP, False)]); vis(b, [(1, False), (IMP, True)]); vis(flash, [(1, False), (IMP, True)])
    for d, s in ((dl, -1), (dr, 1)):
        d.location = (s * 3.0, 0, 0); key(d, 1); key(d, IMP - 10)
        d.location = (s * 1.25, 0, 0); key(d, IMP)
        key(d, IMP + 6)
        d.location = (s * 4.2, 0, 0); key(d, IMP + 26)
    b.rotation_euler = (0, 0, 0); key(b, IMP, "rotation_euler"); key(flash, IMP, "rotation_euler")
    b.rotation_euler = (0, math.radians(20), math.radians(50)); key(b, END, "rotation_euler")
    flash.rotation_euler = (0, math.pi / 2 + math.radians(20), math.radians(50)); key(flash, END, "rotation_euler")
    flash.rotation_euler = (0, math.pi / 2, 0); key(flash, IMP, "rotation_euler")
    cam = camera(50, tgt)
    cam.location = (0, -9, 2.2); key(cam, 1); key(cam, IMP + 6); cam.location = (0.6, -5.2, 1.2); key(cam, END)
    studio(tgt)
    anchors["impact_frame"] = IMP

elif SCENE == "ofen":  # heat + quench: balls and a ring glow, then sink into oil
    HOT = mat("hot", (0.3, 0.3, 0.32, 1), 1.0, 0.3, emit=(1.0, 0.22, 0.02, 1))
    tray = empty("tray")
    objs = []
    o = outer_ring(m=HOT); o.location = (-1.6, 0, 0.75 * 0 + 0.0); o.scale = (0.7, 0.7, 0.7); o.parent = tray; objs.append(o)
    for i in range(5):
        bb = ball((1.3 + (i % 3) * 0.75, -0.4 + (i // 3) * 0.8, 0), 0.32, m=HOT); bb.parent = tray
    plate = box((5.6, 2.6, 0.12), (0, 0, -0.42), m=DARKSTEEL, bevel=0.02); plate.parent = tray
    oil = box((7.5, 4.5, 2.5), (0, 0, -2.7), m=mat("oil", (0.05, 0.035, 0.02, 1), 0.0, 0.08), bevel=0)
    b = HOT.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Strength"].default_value = 0; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=1)
    b.inputs["Emission Strength"].default_value = 2.2; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=40)
    b.inputs["Emission Strength"].keyframe_insert("default_value", frame=56)
    b.inputs["Emission Strength"].default_value = 0; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=72)
    tray.location = (0, 0, 0); key(tray, 1); key(tray, 48); tray.location = (0, 0, -2.0); key(tray, 64); key(tray, END)
    cam = camera(42, tgt); tgt.location = (0, 0, -0.6)
    cam.location = (-1.5, -9, 4.0); key(cam, 1); cam.location = (1.0, -8, 2.6); key(cam, END)
    studio(tgt, 0.8)

elif SCENE == "drehen":  # turning: ring blank on lathe, tool cuts, chip curls off
    TURN = mat("turn", (0.5, 0.48, 0.46, 1), 0.9, 0.7)
    blank = lathe("blank", ring_profile(PITCH + 0.18, 2.3, 0.95, R_BALL, True, groove=False), TURN)
    blank.rotation_euler = (math.pi / 2, 0, 0)
    linear(); key(blank, 1, "rotation_euler")
    blank.rotation_euler = (math.pi / 2, 0, math.radians(720)); key(blank, END, "rotation_euler"); bez()
    rb = TURN.node_tree.nodes["Principled BSDF"].inputs["Roughness"]
    rb.default_value = 0.7; rb.keyframe_insert("default_value", frame=20); rb.default_value = 0.25; rb.keyframe_insert("default_value", frame=80)
    tool = box((0.25, 0.25, 1.4), (2.3, 0, 2.2), m=ORG, bevel=0.03)
    tool.location = (0.4, 0, 3.6); key(tool, 1); tool.location = (0.4, 0, 2.42); key(tool, 18); key(tool, 82); tool.location = (0.4, 0, 3.6); key(tool, END)
    # chip: helix curve with bevel, growing
    cd = bpy.data.curves.new("chip", "CURVE"); cd.dimensions = "3D"; sp = cd.splines.new("POLY")
    pts = []
    for i in range(160):
        t = i / 159; a = t * 6 * math.pi; r = 0.18 + 0.12 * t
        pts.append((0.4 + r * math.cos(a) + t * 0.6, -0.1 - t * 1.8, 2.45 + r * math.sin(a) + t * 1.2))
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    cd.bevel_depth = 0.035; cd.bevel_resolution = 2
    chip = bpy.data.objects.new("chip", cd); sc.collection.objects.link(chip); chip.data.materials.append(mat("chipm", (0.55, 0.45, 0.35, 1), 1.0, 0.3))
    cd.bevel_factor_end = 0; cd.keyframe_insert("bevel_factor_end", frame=18)
    cd.bevel_factor_end = 1; cd.keyframe_insert("bevel_factor_end", frame=82)
    cam = camera(45, tgt); tgt.location = (0.2, 0, 0.9)
    cam.location = (3.5, -14, 4.5); key(cam, 1); cam.location = (2.2, -12, 3.6); key(cam, END)
    studio(tgt)

elif SCENE == "schleifen":  # raceway grinding: wheel inside ring, sparks added in comp
    o = outer_ring(); o.rotation_euler = (math.pi / 2, 0, 0)
    linear(); key(o, 1, "rotation_euler"); o.rotation_euler = (math.pi / 2, 0, math.radians(540)); key(o, END, "rotation_euler")
    wheel = cyl(0.55, 0.5, (PITCH + 0.18 - 0.55 - 0.02 - 0.0, 0, 0), rot=(math.pi / 2, 0, 0), m=WHEEL, v=64)
    wheel.location = (0.95, 0, 0)
    shaft = cyl(0.12, 3.5, (0.95, -1.8, 0), rot=(math.pi / 2, 0, 0), m=DARKSTEEL, v=32)
    key(wheel, 1, "rotation_euler"); wheel.rotation_euler = (math.pi / 2, 0, math.radians(-2400)); key(wheel, END, "rotation_euler"); bez()
    cam = camera(45, tgt)
    cam.location = (-3.5, -12.5, 4.0); key(cam, 1); cam.location = (-2.2, -10.5, 3.0); key(cam, END)
    studio(tgt)
    sc.frame_set(48); p = world_to_camera_view(sc, cam, Vector((1.5, -0.2, 0))); anchors["spark"] = [p.x, 1 - p.y]

elif SCENE == "honen":  # mirror finish: roughness goes from matte to mirror
    END = 72
    HM = mat("hon", (0.8, 0.8, 0.82, 1), 1.0, 0.55)
    o = lathe("outer", ring_profile(PITCH + 0.18, 2.15, 0.75, R_BALL, True), HM)
    o.rotation_mode = "ZXY"; o.rotation_euler = (math.radians(18), 0, 0)
    linear(); key(o, 1, "rotation_euler"); o.rotation_euler = (math.radians(18), 0, math.radians(120)); key(o, END, "rotation_euler"); bez()
    rb = HM.node_tree.nodes["Principled BSDF"].inputs["Roughness"]
    rb.default_value = 0.55; rb.keyframe_insert("default_value", frame=8); rb.default_value = 0.03; rb.keyframe_insert("default_value", frame=60)
    # stripes to reflect
    for x in (-3, 0, 3):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, 2, 5), rotation=(0.5, 0, 0)); pl = bpy.context.object; pl.scale = (0.4, 6, 1)
        em = bpy.data.materials.new("em"); em.use_nodes = True; nt = em.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs[1].default_value = 6; nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
        pl.data.materials.append(em); pl.visible_camera = False
    cam = camera(45, tgt); tgt.location = (0, 0, 0)
    cam.location = (0, -11, 5.5); key(cam, 1); cam.location = (0, -9.0, 4.2); key(cam, END)
    studio(tgt, 0.7)

elif SCENE == "kaefig":  # stamping: punch hits sheet, cage half pops out
    sheet = box((6, 4, 0.06), (0, 0, -0.6), m=mat("sheet", (0.75, 0.75, 0.77, 1), 1.0, 0.3), bevel=0)
    punch = cyl(1.9, 1.2, (0, 0, 3.5), m=DARKSTEEL, v=96)
    die_ring = lathe("diering", ring_profile(1.95, 2.6, 0.5, 0.1, True, groove=False), DARKSTEEL); die_ring.location = (0, 0, -0.9)
    ch = cage_half(9); ch.location = (0, 0, -0.55)
    IMP = 30
    vis(ch, [(1, False), (IMP, True)])
    punch.location = (0, 0, 3.5); key(punch, 1); key(punch, IMP - 10); punch.location = (0, 0, -0.0); key(punch, IMP); key(punch, IMP + 4)
    punch.location = (0, 0, 4.5); key(punch, IMP + 20)
    ch.location = (0, 0, -0.55); key(ch, IMP + 6); ch.location = (0, -0.5, 1.4); key(ch, IMP + 36)
    ch.rotation_euler = (0, 0, 0); key(ch, IMP + 6, "rotation_euler"); ch.rotation_euler = (math.radians(-50), 0, math.radians(40)); key(ch, END, "rotation_euler")
    cam = camera(42, tgt); tgt.location = (0, 0, 0.2)
    cam.location = (0, -8.5, 4.2); key(cam, 1); cam.location = (0.8, -6.8, 3.2); key(cam, END)
    studio(tgt)
    anchors["impact_frame"] = IMP

elif SCENE == "montage":  # eccentric ball filling (Conrad method)
    END = 192
    root = empty("root"); root.rotation_euler = (math.radians(90), 0, 0)
    o = outer_ring(); o.parent = root
    i_r = inner_ring(); i_r.parent = root
    N = 7; E = 0.55
    i_r.location = (-E, 0, 0); key(i_r, 1); key(i_r, 96); i_r.location = (0, 0, 0); key(i_r, 128)
    final = [2 * math.pi * k / N for k in range(N)]
    packed = [math.radians(-69 + k * 23) for k in range(N)]
    balls = []
    for k in range(N):
        b = ball((0, 0, 0), R_BALL); b.parent = root; balls.append(b)
        a = packed[k]; target = Vector((PITCH * math.cos(a), PITCH * math.sin(a), 0))
        f0 = 10 + k * 9
        b.location = target + Vector((0, 4.0, -1.0)); key(b, 1); key(b, f0)  # from above
        b.location = target; key(b, f0 + 10); key(b, 96)
        # spread to final angle (choose nearest equivalent)
        fa = final[(k + 4) % N]
        while fa - a > math.pi: fa -= 2 * math.pi
        while a - fa > math.pi: fa += 2 * math.pi
        b.location = Vector((PITCH * math.cos(fa), PITCH * math.sin(fa), 0)); key(b, 128)
    # cage halves (front/back)
    shift = math.radians(-69 + 4 * 23) - final[(4 + 4) % N]
    c1 = cage_half(N); c1.parent = root; c2 = cage_half(N); c2.parent = root; c2.scale = (1, 1, -1)
    for c, s in ((c1, -1), (c2, 1)):
        c.rotation_euler = (0, 0, 0)
        vis(c, [(1, False), (130, True)])
        c.location = (0, 0, s * 5.0); key(c, 1); key(c, 132); c.location = (0, 0, 0); key(c, 152)
    seal = lathe("seal", [(PITCH - 0.3, -0.03), (PITCH + 0.45, -0.03), (PITCH + 0.45, 0.03), (PITCH - 0.3, 0.03)], RUBBER)
    seal.parent = root; vis(seal, [(1, False), (158, True)]); seal.location = (0, 0, 3.0); key(seal, 1); key(seal, 160); seal.location = (0, 0, 0.42); key(seal, 178)
    root.rotation_mode = "XYZ"
    cam = camera(40, tgt)
    cam.location = (2.2, -9.5, 3.4); key(cam, 1); cam.location = (0.6, -8.5, 2.4); key(cam, 128); cam.location = (3.5, -7.5, 3.0); key(cam, END)
    studio(tgt)

elif SCENE == "draht":  # still: coil of wire + slugs
    END = 1
    cd = bpy.data.curves.new("coil", "CURVE"); cd.dimensions = "3D"; sp = cd.splines.new("POLY")
    pts = []
    for i in range(1200):
        t = i / 1199; a = t * 2 * math.pi * 14; r = 2.2 + 0.0 * t
        pts.append((r * math.cos(a), r * math.sin(a), -1.2 + t * 2.4))
    pts += [(2.2 + 0.5 * k, -0.2 * k, 1.2) for k in range(1, 7)]
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    cd.bevel_depth = 0.09; cd.bevel_resolution = 3
    coil = bpy.data.objects.new("coil", cd); sc.collection.objects.link(coil); coil.data.materials.append(STEEL)
    coil.rotation_euler = (math.radians(60), 0, 0)
    cam = camera(42, tgt); cam.location = (2.5, -9, 4.5)
    studio(tgt)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080; sc.cycles.samples = 16

sc.frame_start, sc.frame_end = 1, END
if FS:
    sc.frame_start, sc.frame_end = FS, FE
json.dump(anchors, open(f"{OUT}/anchors.json", "w"))
sc.render.filepath = f"{OUT}/f_"
sc.render.image_settings.file_format = "PNG"
bpy.ops.render.render(animation=True)
