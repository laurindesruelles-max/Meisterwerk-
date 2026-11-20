"""Stilprobe Meisterwerk: Explosionsansicht + Gluehen eines Kugellagers. usage: python3 mw_explode.py OUT [fs fe]"""
import sys, math
SRC = "/home/claude/repos/Meisterwerk-/videos/001-kugellager/scenes2.py"
head = open(SRC).read().split("anchors = {}")[0]
OUT = sys.argv[1]; fs = sys.argv[2:4]
sys.argv = ["scenes2.py", "x", OUT] + fs
exec(head)
sc.render.film_transparent = False
w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.78, 0.75, 1)
tgt = empty("t")
GLOW = mat("glow", (0.7, 0.7, 0.72, 1), 1.0, 0.25, emit=(1.0, 0.18, 0.01, 1))
o = outer_ring(GLOW); i = inner_ring(); cu = cage_half(8, 0.33); cd = cage_half(8, -0.33)
balls = [ball((PITCH * math.cos(2 * math.pi * k / 8), PITCH * math.sin(2 * math.pi * k / 8), 0)) for k in range(8)]
root = empty("root")
for ob in [o, i, cu, cd] + balls: ob.parent = root
root.rotation_euler = (math.radians(58), 0, 0)
# Boden
box((30, 30, 0.2), (0, 0, -3.2), ROUGH, 0)
studio(tgt, 1.1)
cam = camera(50, tgt); cam.location = (0, -12, 4.5)
sc.frame_start, sc.frame_end = 1, 276
def kf(ob, f, loc): ob.location = loc; key(ob, f)
for ob in [o, i, cu, cd] + balls: kf(ob, 1, tuple(ob.location)); kf(ob, 24, tuple(ob.location))
# auseinander (24-84), halten, zusammen (150-198)
E_ = {o: (0, 0, 2.6), i: (0, 0, -2.6), cu: (0, 0, 1.3), cd: (0, 0, -1.3)}
for ob, d in E_.items(): kf(ob, 84, d); kf(ob, 150, d); kf(ob, 198, (0, 0, 0))
for k, b in enumerate(balls):
    a = 2 * math.pi * k / 8; p0 = tuple(b.location); p1 = (2.6 * math.cos(a), 2.6 * math.sin(a), 0)
    kf(b, 84 + k * 2, p1); kf(b, 150, p1); kf(b, 198 - k * 2, p0)
# Kamera: langsamer Orbit, am Ende naeher ran
cam.location = (0, -17, 6.5); key(cam, 1); cam.location = (6, -15, 7.5); key(cam, 150); cam.location = (3.5, -11, 4.8); key(cam, 276)
# Gluehen des Aussenrings (204-276)
bs = GLOW.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
bs.default_value = 0; bs.keyframe_insert("default_value", frame=204)
bs.default_value = 2.2; bs.keyframe_insert("default_value", frame=250); bs.keyframe_insert("default_value", frame=276)
sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.frame_step = 2
sc.render.filepath = OUT + "/f_"
if len(fs) == 2:
    sc.frame_start, sc.frame_end = int(fs[0]), int(fs[1])
bpy.ops.render.render(animation=True)
