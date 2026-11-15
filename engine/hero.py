import bpy, math, sys
exec(open('scenes2.py').read().split("anchors = {}")[0].replace("SCENE, OUT = sys.argv[1], sys.argv[2]","SCENE, OUT = 'x', '/tmp'"))
tgt = empty("t")
b = ball((0, 0, 0), 1.0, seg=96)
def card(loc, rot, size, col, strength):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc, rotation=rot)
    m = bpy.data.materials.new("c"); m.use_nodes = True; nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"]); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = col; e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
    o = bpy.context.object; o.data.materials.append(m); o.visible_camera = False
card((0, 0, -2.5), (0, 0, 0), 40, (0.95, 0.93, 0.9, 1), 0.9)
card((0, 9, 0), (math.pi / 2, 0, 0), 40, (0.45, 0.44, 0.42, 1), 0.6)
card((-6, 0, 2), (0, math.pi / 2, 0), 6, (0.03, 0.03, 0.04, 1), 1)
card((5, -1, 0.5), (0, math.pi / 2, 0.4), 4, (1, 0.3, 0.05, 1), 4)
card((0, -3, 8), (0, 0, 0), 8, (1, 1, 1, 1), 4)
cam = camera(70, tgt); cam.location = (-2.0, -7.0, 1.2)
studio(tgt)
sc.render.resolution_x, sc.render.resolution_y = 1280, 1280; sc.cycles.samples = 24
sc.render.filepath = "/home/claude/meisterwerk/pilot/hero_ball.png"
bpy.ops.render.render(write_still=True)
