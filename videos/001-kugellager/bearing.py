"""Meisterwerk pilot – Blender scenes for the ball-bearing intro.
usage: python3 bearing.py <scene> <outdir> [fs fe]
scenes: kugel (macro steel ball, 96f) | lager (exploded bearing assembles + spins, 144f) | viele (still: many bearings)
"""
import bpy, bmesh, math, sys
from mathutils import Vector

SCENE, OUT = sys.argv[1], sys.argv[2]
FS = int(sys.argv[3]) if len(sys.argv) > 3 else None
FE = int(sys.argv[4]) if len(sys.argv) > 4 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
P = bpy.context.preferences.edit
P.keyframe_new_interpolation_type = "BEZIER"; P.keyframe_new_handle_type = "AUTO_CLAMPED"
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 8; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 960, 540
sc.render.fps = 24; sc.render.film_transparent = True
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.82, 0.78, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7


def mat(name, color, metal, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color; b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    return m

CHROME = mat("chrome", (0.9, 0.9, 0.92, 1), 1.0, 0.06)
STEEL = mat("steel", (0.7, 0.7, 0.72, 1), 1.0, 0.22)
ORG = mat("org", (1.0, 0.27, 0.02, 1), 0.0, 0.35)


def lathe(name, profile, m, seg=128):
    """profile: list of (r, z) closed loop; revolve around Z."""
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
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    es = o.modifiers.new("es", "EDGE_SPLIT"); es.split_angle = math.radians(35)
    return o


def ring_profile(r_in, r_out, h, groove_r, groove_on_inner, k=24):
    pts = []
    # outer side straight, inner side with groove (or vice versa)
    if groove_on_inner:  # outer ring: groove faces inward at r_in
        pts += [(r_out, -h / 2), (r_out, h / 2), (r_in, h / 2)]
        for i in range(k + 1):
            t = math.pi / 2 - math.pi * i / k
            pts.append((r_in + groove_r * math.cos(t) * 0.55, groove_r * math.sin(t) * 0.9))
        pts += [(r_in, -h / 2)]
    else:  # inner ring: groove faces outward at r_out
        pts += [(r_in, -h / 2), (r_out, -h / 2)]
        for i in range(k + 1):
            t = -math.pi / 2 + math.pi * i / k
            pts.append((r_out - groove_r * math.cos(t) * 0.55, groove_r * math.sin(t) * 0.9))
        pts += [(r_out, h / 2), (r_in, h / 2)]
    # fix winding / ccw not important for render with smooth shading
    return pts


def ball(loc, r, m=CHROME):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=r, location=loc)
    o = bpy.context.object; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o


def area(loc, energy, size, tgt, color=(1, 1, 1)):
    d = bpy.data.lights.new("a", "AREA"); d.energy = energy; d.size = size; d.color = color
    o = bpy.data.objects.new("a", d); sc.collection.objects.link(o); o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"


def camera(lens, tgt):
    cd = bpy.data.cameras.new("cam"); cd.lens = lens
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    return cam


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.location = loc; return e


def bearing(parent=None, loc=(0, 0, 0)):
    """deep groove ball bearing: returns dict of parts (unparented positions relative to loc)."""
    R_ball, n_ball, pitch = 0.32, 9, 1.55
    outer = lathe("outer", ring_profile(pitch + 0.18, 2.15, 0.75, R_ball, True), STEEL)
    inner = lathe("inner", ring_profile(0.95, pitch - 0.18, 0.75, R_ball, False), STEEL)
    balls = []
    for i in range(n_ball):
        a = 2 * math.pi * i / n_ball
        balls.append(ball((pitch * math.cos(a), pitch * math.sin(a), 0), R_ball))
    bpy.ops.mesh.primitive_torus_add(major_radius=pitch, minor_radius=0.05, location=(0, 0, 0.3))
    cage = bpy.context.object; cage.data.materials.append(ORG); bpy.ops.object.shade_smooth()
    cage2_parts = []
    for i in range(n_ball):
        a = 2 * math.pi * (i + 0.5) / n_ball
        bpy.ops.mesh.primitive_cube_add(size=1, location=(pitch * math.cos(a), pitch * math.sin(a), 0.12))
        b = bpy.context.object; b.scale = (0.12, 0.12, 0.38); b.rotation_euler = (0, 0, a); b.data.materials.append(ORG)
        cage2_parts.append(b)
    for b in cage2_parts:
        b.select_set(True)
    cage.select_set(True); bpy.context.view_layer.objects.active = cage; bpy.ops.object.join()
    parts = {"outer": outer, "inner": inner, "cage": cage, **{f"b{i}": b for i, b in enumerate(balls)}}
    root = empty("bearing", loc)
    for o in parts.values():
        o.parent = root
    return root, parts


if SCENE == "kugel":
    tgt = empty("t", (0, 0, 0))
    b = ball((0, 0, 0), 1.0)
    # second, out-of-focus balls behind for depth
    for x, y, z in [(-2.6, 3.5, -0.3), (2.9, 5.0, 0.4), (-0.6, 7.0, 0.9)]:
        ball((x, y, z), 1.0)
    # invisible studio cards so the chrome has something to reflect
    def card(loc, rot, size, col, strength):
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
        m = bpy.data.materials.new("c"); m.use_nodes = True; nt = m.node_tree
        nt.nodes.remove(nt.nodes["Principled BSDF"]); e = nt.nodes.new("ShaderNodeEmission")
        e.inputs[0].default_value = col; e.inputs[1].default_value = strength
        nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
        o = bpy.context.object; o.data.materials.append(m); o.visible_camera = False
    card((0, 0, -2.5), (0, 0, 0), 40, (0.95, 0.93, 0.9, 1), 0.9)
    card((0, 9, 0), (math.pi / 2, 0, 0), 40, (0.5, 0.49, 0.47, 1), 0.6)
    card((-6, 0, 2), (0, math.pi / 2, 0), 6, (0.05, 0.05, 0.06, 1), 1)
    card((0, -3, 8), (0, 0, 0), 8, (1, 1, 1, 1), 4)
    cam = camera(70, tgt)
    cam.data.dof.use_dof = True; cam.data.dof.focus_object = b; cam.data.dof.aperture_fstop = 1.8
    cam.location = (-3.0, -8.5, 1.4); cam.keyframe_insert("location", frame=1)
    cam.location = (2.2, -7.2, 0.7); cam.keyframe_insert("location", frame=72)
    area((-4, -3, 5), 900, 5, tgt); area((5, -2, 1), 400, 6, tgt, (1, 0.6, 0.35)); area((0, 6, 4), 600, 4, tgt)
    # orange accent reflection card
    bpy.ops.mesh.primitive_plane_add(size=3, location=(4, 1, 0), rotation=(0, math.pi / 2, 0.4))
    em = bpy.data.materials.new("em"); em.use_nodes = True
    nt = em.node_tree; nt.nodes.remove(nt.nodes["Principled BSDF"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (1, 0.3, 0.05, 1); e.inputs[1].default_value = 3
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
    card = bpy.context.object; card.data.materials.append(em); card.visible_camera = False
    sc.frame_start, sc.frame_end = 1, 72

elif SCENE == "lager":
    tgt = empty("t", (0, 0, 0))
    root, parts = bearing()
    root.rotation_mode = "ZXY"
    root.rotation_euler = (math.radians(62), 0, 0)
    A0, A1, END = 1, 60, 120
    ex = {"outer": (0, 0, 1.8), "inner": (0, 0, -1.8), "cage": (0, 0, 3.0)}
    for n, o in parts.items():
        base = o.location.copy()
        if n.startswith("b"):
            off = Vector((base.x, base.y, 0)) * 0.9
        else:
            off = Vector(ex[n])
        o.location = base + off; o.keyframe_insert("location", frame=A0); o.keyframe_insert("location", frame=12)
        o.location = base; o.keyframe_insert("location", frame=A1)
    # spin after assembly (inner ring + balls + cage rotate)
    spin = empty("spin"); spin.parent = root
    P.keyframe_new_interpolation_type = "LINEAR"
    root.rotation_euler = (math.radians(62), 0, 0); root.keyframe_insert("rotation_euler", frame=1)
    root.rotation_euler = (math.radians(62), 0, math.radians(140)); root.keyframe_insert("rotation_euler", frame=END)
    P.keyframe_new_interpolation_type = "BEZIER"
    cam = camera(50, tgt)
    cam.location = (0, -15, 2.5); cam.keyframe_insert("location", frame=1)
    cam.location = (0, -11.5, 1.8); cam.keyframe_insert("location", frame=END)
    area((-5, -5, 7), 1300, 6, tgt); area((6, -3, 3), 500, 4, tgt, (1, 0.92, 0.85)); area((0, 6, 5), 900, 5, tgt)
    sc.frame_start, sc.frame_end = 1, END

elif SCENE == "viele":
    tgt = empty("t", (0, 0, 0))
    k = 0
    for gx in range(-4, 5):
        for gy in range(0, 5):
            root, parts = bearing(loc=(gx * 4.8 + (gy % 2) * 2.4, gy * 4.8, 0))
            root.rotation_euler = (0, 0, (gx * 7 + gy * 13) % 40 * 0.05)
            k += 1
    cam = camera(45, tgt)
    tgt.location = (0, 7, 0)
    cam.location = (-3, -9, 10)
    area((-8, -8, 14), 4000, 10, tgt); area((10, 0, 6), 1500, 8, tgt, (1, 0.9, 0.8))
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.cycles.samples = 16
    sc.frame_start, sc.frame_end = 1, 1

if FS:
    sc.frame_start, sc.frame_end = FS, FE
sc.render.filepath = f"{OUT}/f_"
sc.render.image_settings.file_format = "PNG"
bpy.ops.render.render(animation=True)
