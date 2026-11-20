"""Meisterwerk-Stilprobe: Blender-Frames (12 fps, interpoliert) + 2D-Overlays Bemassung und Laser-Gravur."""
import subprocess, math, numpy as np, cv2, glob, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 24
# Frames: neue Gluehen-Frames ersetzen die alten
src = {os.path.basename(p): p for p in glob.glob("mw/f_*.png")}
for p in glob.glob("mw2/f_*.png"): src[os.path.basename(p)] = p
os.makedirs("mw_all", exist_ok=True)
for k, p in src.items():
    d = "mw_all/" + k
    if os.path.islink(d): os.remove(d)
    os.symlink(os.path.abspath(p), d)
subprocess.run("ffmpeg -y -loglevel error -pattern_type glob -framerate 12 -i 'mw_all/f_*.png' -vf \"minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,scale=1920:1080:flags=lanczos\" -pix_fmt rgb24 -f rawvideo /tmp/mw.raw", shell=True, check=True)
raw = np.memmap("/tmp/mw.raw", np.uint8, "r").reshape(-1, H, W, 3)
FT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 46)
FG = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", 64)
ORANGE = (255, 110, 20)
def eo(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3

def glut(fr, t):
    """Gluehen kraeftiger: pfirsichfarbene Bereiche des Rings Richtung Glut-Orange ziehen."""
    if t < 8.4: return fr
    f = fr.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    m = np.clip((r - b - 18) / 50, 0, 1) * min(1, (t - 8.4) / 1.0)
    m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
    hot = np.stack([np.clip(r * 1.05, 0, 255), g * 0.55, b * 0.15], -1)
    out = f * (1 - m) + hot * m
    bloom = cv2.GaussianBlur((hot * m), (0, 0), 25) * 0.6
    return np.clip(out + bloom, 0, 255).astype(np.uint8)

def overlay(fr, t):
    fr = glut(fr, t)
    im = Image.fromarray(fr).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # Bemassung: Masslinie zeichnet sich ueber den Ring (0.4-2.6 s)
    if 0.4 < t < 2.8:
        u = eo((t - 0.4) / 0.7); a = int(255 * min(1, (2.8 - t) / 0.3))
        x0, x1, y = 650, 1270, 175
        xm = x0 + (x1 - x0) * u
        d.line([(x0, y), (xm, y)], fill=(40, 40, 46, a), width=5)
        for x in (x0, x1 if u > 0.98 else None):
            if x: d.line([(x, y - 22), (x, y + 22)], fill=(40, 40, 46, a), width=5)
        if u > 0.95:
            d.rounded_rectangle([870, 95, 1050, 155], 8, fill=(245, 243, 238, a)); d.text((960, 125), "Ø 52 mm", font=FT, fill=(30, 30, 34, a), anchor="mm")
    # Laser-Gravur: Text brennt sich Zeichen fuer Zeichen ein, Funken an der Spitze (8.6-11.3 s)
    if t > 8.6:
        txt = "GEHÄRTET · 840 °C"; u = min(1, (t - 8.6) / 1.4); n = int(len(txt) * u)
        x, y = 960, 1010
        tw = d.textlength(txt, font=FG); x0 = x - tw / 2
        glow = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        gd.text((x0, y), txt[:n], font=FG, fill=ORANGE + (255,), anchor="lm")
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
        d.text((x0, y), txt[:n], font=FG, fill=(255, 210, 160, 255), anchor="lm")
        if u < 1:
            tip = x0 + d.textlength(txt[:n], font=FG); r = np.random.default_rng(int(t * 100))
            for _ in range(14):
                a_ = r.uniform(-2.8, -0.3); L = r.uniform(10, 60)
                d.line([(tip, y), (tip + L * math.cos(a_), y + L * math.sin(a_))], fill=(255, 200, 90, 230), width=3)
    im.alpha_composite(ov); return np.array(im.convert("RGB"))

out = "stilprobe_meisterwerk.mp4"
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", out], stdin=subprocess.PIPE)
for i in range(len(raw)):
    p.stdin.write(overlay(np.array(raw[i]), i / FPS).tobytes())
p.stdin.close(); p.wait(); print("ok", len(raw) / FPS)
