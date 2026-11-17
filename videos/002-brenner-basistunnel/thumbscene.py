"""Dark dramatic thumbnail renders for 002. usage: python3 thumbscene.py <head|berg|break> <out.png>"""
import sys
which, OUTP = sys.argv[1], sys.argv[2]
src = open(__file__.replace("thumbscene.py", "scenes.py")).read()
src = src.split('if SCENE == "tbm":')[0]
sys.argv = ["x", "x", "/tmp"]
exec(src)
sc.render.film_transparent = False
w.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.010, 0.014, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1
def light(loc, e, s, col, t=None):
    d = bpy.data.lights.new("a", "AREA"); d.energy = e; d.size = s; d.color = col
    o = bpy.data.objects.new("a", d); sc.collection.objects.link(o); o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = t or tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
HOT = mat("hot", (0.25, 0.08, 0.02, 1), 0.6, 0.35, emit=(1.0, 0.2, 0.0, 1))
HOT.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.4
DROCK = rockmat("drock", (0.03, 0.025, 0.02, 1), (0.12, 0.10, 0.09, 1), 2.0)
if which == "head":  # cutterhead bursting out of dark rock, hot rim, backlight
    root, head = tbm(gantries=1); root.rotation_euler = (0, 0, math.radians(180)); root.location = (0.3, 0, 0)
    head.rotation_euler = (math.radians(15), 0, 0)
    ring = lathe("rim", [(1.02, -0.3), (2.6, -0.3), (2.6, 0.3), (1.02, 0.3)], DROCK); ring.rotation_euler = (0, math.pi / 2, 0); ring.location = (0.1, 0, 0)
    glow = lathe("glow", [(1.0, -0.05), (1.12, -0.05), (1.12, 0.05), (1.0, 0.05)], HOT); glow.rotation_euler = (0, math.pi / 2, 0); glow.location = (-0.15, 0, 0)
    for i in range(50):
        a = random.uniform(0, 2 * math.pi); r = random.uniform(1.1, 2.0)
        rock_chunk((random.uniform(-1.5, -0.2), r * math.cos(a), r * math.sin(a)), random.uniform(0.05, 0.16), DROCK)
    light((-5, -5, 4), 700, 4, (0.6, 0.7, 1.0)); light((-1, 4, 3), 500, 3, (1, 0.35, 0.05)); light((-4, 2, -2), 250, 3, (1, 0.4, 0.1))
    tgt.location = (0, 1.6, 0.3); cam = camera(30, tgt); cam.location = (-7.0, -3.0, 1.3)
elif which == "berg":  # dark mountain block, glowing tunnel line
    exec(open(__file__.replace("thumbscene.py", "scenes.py")).read().split('elif SCENE == "berg":')[1].split('elif SCENE == "sprengen":')[0].replace("\n    ", "\n").replace("studio(tgt, 1.0)", ""), globals())
    sc.frame_set(END)
    light((-8, -12, 14), 600, 10, (0.6, 0.7, 1.0)); light((10, 6, 6), 1500, 8, (1, 0.4, 0.1))
    cam.animation_data_clear(); cam.location = (-1, -21, 1.6); tgt.location = (0, 0, 0.2)
elif which == "break":
    CONC.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.055, 1)  # TBM breaking through, light burst behind
    exec(open(__file__.replace("thumbscene.py", "scenes.py")).read().split('elif SCENE == "durchschlag":')[1].split('elif SCENE == "ueberbruch":')[0].replace("\n    ", "\n").replace("studio(tgt, 0.7)", ""), globals())
    sc.frame_set(70)
    light((-4, -5, 3), 500, 4, (0.6, 0.7, 1.0)); light((4, 0, 0), 4000, 3, (1, 0.45, 0.1))
sc.render.resolution_x, sc.render.resolution_y = 1280, 720; sc.cycles.samples = 32
sc.render.filepath = OUTP
bpy.ops.render.render(write_still=True)
