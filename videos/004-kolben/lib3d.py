"""Meisterwerk 004 – Kolben: Blender-Helfer (1 BE = 10 mm). Kolben Ø86 mm."""
import bpy, bmesh, math, mathutils, os, sys
from mathutils import Vector
sc = bpy.context.scene
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global sc; sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = 12; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 4; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 2; sc.cycles.diffuse_bounces = 2
    sc.render.use_persistent_data = True
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.resolution_x, sc.render.resolution_y = 960, 540
    sc.render.fps = 12; sc.render.image_settings.file_format = "PNG"
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.055, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    return sc

def mat(name, col, metal=0.0, rough=0.5, emit=None, estr=0.0, bump=0.0, alpha=1.0, trans=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col if len(col) == 4 else (*col, 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[:3], 1); b.inputs["Emission Strength"].default_value = estr
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED" if hasattr(m, "surface_render_method") else None
    if trans: b.inputs["Transmission Weight"].default_value = trans
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60
        nz.inputs["Detail"].default_value = 8; bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m

def link(ob):
    sc.collection.objects.link(ob); return ob
def setmat(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m); return ob
def smooth(ob, ang=40):
    for p in ob.data.polygons: p.use_smooth = abs(p.normal.z) < 0.97
    try:
        ob.modifiers.new("ws", "WEIGHTED_NORMAL")
    except Exception: pass
    return ob

def lathe(name, prof, segs=96, m=None):
    """prof: Liste (r, z) – offener Linienzug, wird um Z gedreht"""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me))
    if m: setmat(ob, m)
    return ob

def cyl(name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), m=None, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    ob = bpy.context.active_object; ob.name = name
    if m: setmat(ob, m)
    return ob
def box(name, size, loc=(0, 0, 0), m=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); ob = bpy.context.active_object
    ob.name = name; ob.scale = size
    if m: setmat(ob, m)
    return ob
def boolean(ob, cutter, op="DIFFERENCE", apply=True):
    md = ob.modifiers.new("b", "BOOLEAN"); md.object = cutter; md.operation = op; md.solver = "EXACT"
    if apply:
        bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(cutter)
    return ob

R = 4.3  # Kolbenradius
def piston_profile(crown_dish=0.0):
    """Außen von unten (Schaftende) nach oben, dann Krone, dann innen zurück"""
    p = [(R - 0.42, 0.0), (R, 0.08), (R, 3.55)]
    # Ringzone: Ölring-Nut, 2. Nut, 1. Nut
    z = 3.55
    for (z0, z1, dep) in [(3.75, 4.10, 0.38), (4.50, 4.66, 0.34), (5.05, 5.21, 0.34)]:
        p += [(R - 0.02, z0), (R - dep, z0 + 0.01), (R - dep, z1 - 0.01), (R - 0.02, z1)]
    p += [(R - 0.03, 5.85), (R - 0.15, 6.0), (0.0, 6.0)]
    return p
def piston_inner():
    return [(0.0, 4.55), (2.8, 4.45), (3.75, 3.9), (3.86, 0.25), (R - 0.42, 0.0)]

def piston(name="kolben", m=None, pin_axis="X", segs=128, recess=True):
    prof = piston_profile() + list(reversed(piston_inner()))[1:-1] if False else None
    outer = piston_profile(); inner = piston_inner()
    full = outer + list(reversed(inner))  # endet bei (R-0.42,0) -> geschlossen über remove_doubles
    full = full[:-1] + [outer[0]]
    ob = lathe(name, full, segs, m)
    # Bolzenaugen: Zylinder entlang X innen
    for s in (-1, 1):
        bo = cyl("boss", 1.55, 1.6, loc=(s * 2.95, 0, 2.55), rot=(0, math.pi / 2, 0), verts=48)
        boolean(ob, bo, "UNION")
    # Bolzenbohrung
    bore = cyl("bore", 1.1, 10, loc=(0, 0, 2.55), rot=(0, math.pi / 2, 0), verts=64)
    boolean(ob, bore)
    if recess:
        for s in (-1, 1):  # Schaftfenster an den Bolzenseiten (eingezogen)
            c = box("rc", (1.0, 4.6, 2.4), loc=(s * (R + 0.15), 0, 2.2))
            boolean(ob, c)
    smooth(ob)
    return ob

def ring(name, z, h=0.15, r0=R - 0.32, r1=R + 0.005, gap=0.05, m=None):
    prof = [(r0, z), (r1, z), (r1, z + h), (r0, z + h), (r0, z)]
    bm = bmesh.new(); vs = [bm.verts.new((r, 0, zz)) for r, zz in prof]
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    bmesh.ops.spin(bm, geom=bm.verts[:] + bm.edges[:], cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi - gap, steps=96)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.contextual_create(bm, geom=[e for e in bm.edges if e.is_boundary])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = link(bpy.data.objects.new(name, me)); smooth(ob)
    if m: setmat(ob, m)
    return ob

def pin(m=None):
    ob = lathe("bolzen", [(0.62, -3.75), (1.1, -3.75), (1.1, 3.75), (0.62, 3.75), (0.62, -3.75)], 64, m)
    ob.rotation_euler = (0, math.pi / 2, 0); ob.location = (0, 0, 2.55); smooth(ob); return ob

def conrod(m=None, length=14.0):
    """Pleuel: kleines Auge bei z=0 (Bolzen), großes Auge bei z=-length, Achsen entlang X"""
    small = cyl("p_s", 1.6, 1.4, rot=(0, math.pi / 2, 0)); h = cyl("h", 1.12, 3, rot=(0, math.pi / 2, 0)); boolean(small, h)
    big = cyl("p_b", 3.0, 1.6, loc=(0, 0, -length), rot=(0, math.pi / 2, 0)); h = cyl("h", 2.2, 3, loc=(0, 0, -length), rot=(0, math.pi / 2, 0)); boolean(big, h)
    beam = box("p_beam", (1.2, 1.5, length - 3.6), loc=(0, 0, -length / 2 - 0.3))
    for o in (beam, big):
        boolean(small, o, "UNION")
    small.name = "pleuel"; smooth(small)
    if m: setmat(small, m)
    return small

def camera(loc, target, lens=50, name="cam"):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cam = link(bpy.data.objects.new(name, cd))
    cam.location = loc
    tg = target if isinstance(target, bpy.types.Object) else empty("tgt", target)
    c = cam.constraints.new("TRACK_TO"); c.target = tg; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    sc.camera = cam; return cam, tg
def empty(name, loc=(0, 0, 0)):
    e = link(bpy.data.objects.new(name, None)); e.location = loc; return e
def area(name, loc, size, energy, col=(1, 1, 1), rot=None, target=None, shape="RECTANGLE", sy=None):
    ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.color = col; ld.shape = shape; ld.size = size
    if sy: ld.size_y = sy
    ob = link(bpy.data.objects.new(name, ld)); ob.location = loc
    if target is not None:
        c = ob.constraints.new("TRACK_TO"); c.target = target if isinstance(target, bpy.types.Object) else empty(name + "_t", target)
        c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    if rot: ob.rotation_euler = rot
    return ob
def point(name, loc, energy, col=(1, .5, .2), r=0.5):
    ld = bpy.data.lights.new(name, "POINT"); ld.energy = energy; ld.color = col; ld.shadow_soft_size = r
    ob = link(bpy.data.objects.new(name, ld)); ob.location = loc; return ob

def hall(dark=False, floor_col=(0.32, 0.31, 0.30), fz=0.0):
    """Werkhalle: Betonboden, Rückwand mit Fensterband, Träger. dark=True für dramatische Szenen"""
    fl = box("boden", (200, 200, 0.2), loc=(0, 0, fz - 0.1), m=mat("beton", floor_col, 0, 0.75, bump=0.25))
    wall_c = (0.18, 0.18, 0.2) if dark else (0.55, 0.54, 0.52)
    box("wand", (200, 0.4, 60), loc=(0, 45, 30), m=mat("wand", wall_c, 0.2, 0.6, bump=0.15))
    # Fensterband
    win = mat("fenster", (1, 1, 1), emit=(0.9, 0.95, 1.0), estr=(1.5 if dark else 6.0))
    for i in range(-6, 7):
        box(f"fe{i}", (6.0, 0.2, 3.0), loc=(i * 8, 44.7, 22), m=win)
    stl = mat("traeger", (0.08, 0.08, 0.09), 0.8, 0.45)
    for i in range(-4, 5):
        box(f"st{i}", (0.8, 0.8, 40), loc=(i * 16, 43, 20), m=stl)
    box("dach", (200, 0.9, 1.2), loc=(0, 43.5, 30), m=stl)
    return fl

def key(ob, f, path="location"):
    ob.keyframe_insert(path, frame=f)
def kloc(ob, f, loc): ob.location = loc; ob.keyframe_insert("location", frame=f)
def krot(ob, f, rot): ob.rotation_euler = rot; ob.keyframe_insert("rotation_euler", frame=f)
def ksc(ob, f, s): ob.scale = (s, s, s) if isinstance(s, (int, float)) else s; ob.keyframe_insert("scale", frame=f)
def linear(ob):
    if ob.animation_data and ob.animation_data.action:
        try:
            for fc in ob.animation_data.action.fcurves:
                for k in fc.keyframe_points: k.interpolation = "LINEAR"
        except Exception:
            pass
def kval(sock, f, v): sock.default_value = v; sock.keyframe_insert("default_value", frame=f)

def render(out, f0, f1, res=(960, 540), samples=None):
    sc.render.resolution_x, sc.render.resolution_y = res
    if samples: sc.cycles.samples = samples
    os.makedirs(out, exist_ok=True)
    sc.render.filepath = out + "/f_"; sc.frame_start, sc.frame_end = f0, f1
    bpy.ops.render.render(animation=True)
