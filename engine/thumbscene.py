import bpy, math, sys
which = sys.argv[-1]
exec(open('scenes2.py').read().split("anchors = {}")[0].replace("SCENE, OUT = sys.argv[1], sys.argv[2]","SCENE, OUT = 'x', '/tmp'").replace("FS = int(sys.argv[3]) if len(sys.argv) > 3 else None","FS=None").replace("FE = int(sys.argv[4]) if len(sys.argv) > 4 else None","FE=None"))
sc.render.film_transparent = False
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.012, 0.016, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1
tgt = empty("t")
floor = box((40, 40, .2), (0, 0, -1.25), m=mat("fl", (0.05, 0.05, 0.055, 1), 0.9, 0.35), bevel=0)
def light(loc, e, s, col): 
    d = bpy.data.lights.new("a", "AREA"); d.energy = e; d.size = s; d.color = col
    o = bpy.data.objects.new("a", d); sc.collection.objects.link(o); o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
if which == "press":
    HOT = mat("hot", (0.25, 0.08, 0.02, 1), 0.6, 0.35, emit=(1.0, 0.16, 0.0, 1))
    HOT.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.1
    b = ball((0, 0, 0), 0.75, m=HOT, seg=96)
    for s in (-1, 1):
        d = cyl(1.3, 3.2, (s * 2.4, 0, 0), rot=(0, math.pi / 2, 0), m=mat("die", (0.18, 0.18, 0.2, 1), 1.0, 0.3), v=96)
    light((-4, -6, 6), 1500, 5, (0.7, 0.8, 1.0)); light((4, 4, 3), 2500, 4, (1, 0.5, 0.2)); light((0, -3, -0.5), 300, 2, (1, .4, .1))
    tgt.location = (-1.2, 0, -0.2); cam = camera(50, tgt); cam.location = (1.5, -11.5, 2.6)
elif which == "chrome":
    b = ball((0, 0, 0), 1.0, m=CHROME, seg=96); tgt.location = (-1.3, 0, 0.1)
    light((-3, -4, 5), 2500, 3, (1, 1, 1)); light((5, 2, 1), 3000, 4, (1, 0.35, 0.05)); light((0, -6, 0), 600, 6, (1, 1, 1)); light((-5, 3, 1), 800, 4, (0.5, 0.6, 1))
    cam = camera(60, tgt); cam.location = (-1.0, -8.0, 1.2)
elif which == "bearing":
    root = empty("r"); root.rotation_euler = (math.radians(70), 0, math.radians(15))
    o = outer_ring(); o.parent = root; i_ = inner_ring(); i_.parent = root
    for k in range(9):
        a = 2 * math.pi * k / 9; bb = ball((PITCH * math.cos(a), PITCH * math.sin(a), 0)); bb.parent = root
    c = cage_half(9); c.parent = root
    light((-4, -6, 6), 1500, 5, (0.8, 0.85, 1)); light((5, 3, 2), 3000, 4, (1, 0.35, 0.05)); light((-5, 4, 2), 1200, 4, (1, 0.35, 0.05))
    tgt.location = (-2.0, 0, 0.3); cam = camera(45, tgt); cam.location = (0.5, -12.5, 3.0)
sc.render.resolution_x, sc.render.resolution_y = 1280, 720; sc.cycles.samples = 32
sc.render.filepath = f"/home/claude/meisterwerk/pilot/th_{which}.png"
bpy.ops.render.render(write_still=True)
