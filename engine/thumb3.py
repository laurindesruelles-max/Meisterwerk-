import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D="/home/claude/meisterwerk/pilot"; F="/usr/share/fonts/opentype/inter/"
W,H=1280,720; Y=(255,214,0); WH=(255,255,255); OR=(255,92,12)
def sparks(im, xy, n=160, seed=3):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); r=random.Random(seed)
    for i in range(n):
        a=r.uniform(0,2*math.pi); L=r.uniform(20,260); x=xy[0]+math.cos(a)*r.uniform(30,420); y=xy[1]+math.sin(a)*r.uniform(20,260)
        d.line((x,y,x+math.cos(a)*L*.25,y+math.sin(a)*L*.25+L*.08),fill=(255,r.randint(150,220),60,r.randint(150,255)),width=r.choice([2,3,4]))
    g=ov.filter(ImageFilter.GaussianBlur(5)); im.paste(g,(0,0),g); im.paste(ov,(0,0),ov)
def text(im, lines, cols, x, y, size, rot=0):
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for l,c in zip(lines,cols):
        f=ImageFont.truetype(F+"InterDisplay-Black.otf",size)
        d.text((x,y),l,font=f,fill=c,stroke_width=int(size*.09),stroke_fill=(0,0,0))
        y+=int(size*1.02)
    if rot: lay=lay.rotate(rot,resample=Image.BICUBIC,center=(x,y))
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); sh.paste((0,0,0,170),(0,0),lay.split()[3]); sh=sh.filter(ImageFilter.GaussianBlur(14))
    im.paste(sh,(8,10),sh); im.paste(lay,(0,0),lay)
def arrow(im, p0, p1):
    d=ImageDraw.Draw(im); d.line((p0,p1),fill=(0,0,0),width=30); d.line((p0,p1),fill=OR,width=18)
    a=math.atan2(p1[1]-p0[1],p1[0]-p0[0]); L=55
    pts=[p1,(p1[0]-L*math.cos(a-.5),p1[1]-L*math.sin(a-.5)),(p1[0]-L*math.cos(a+.5),p1[1]-L*math.sin(a+.5))]
    d.polygon(pts,fill=OR,outline=(0,0,0))
def base(name, bright=1.15):
    im=Image.open(f"{D}/th_{name}.png").convert("RGB"); im=ImageEnhance.Contrast(im).enhance(1.15); im=ImageEnhance.Brightness(im).enhance(bright); return im.convert("RGBA")
# 1: press
im=base("press"); sparks(im,(820,360)); text(im,["20 TONNEN"],[WH],60,40,150); text(im,["FÜR 1 KUGEL?!"],[Y],60,560,110); im.convert("RGB").save(f"{D}/Thumbnail_1.jpg",quality=92)
# 2: chrome
im=base("chrome",1.05); text(im,["PERFEKT"],[WH],50,60,150); text(im,["RUND?!"],[Y],50,215,150)
d=ImageDraw.Draw(im); d.ellipse((470,120,830,480),outline=OR,width=10) if False else None
text(im,["0,0001 mm"],[OR],60,560,90); im.convert("RGB").save(f"{D}/Thumbnail_2.jpg",quality=92)
# 3: bearing + bombers angle
im=base("bearing",1.1); text(im,["291 BOMBER"],[WH],50,40,140); text(im,["WEGEN DIESEM","TEIL?!"],[Y,Y],50,470,100); arrow(im,(700,600),(800,500)); im.convert("RGB").save(f"{D}/Thumbnail_3.jpg",quality=92)
o=Image.new("RGB",(1280*3+40,720),"white")
for i in range(3): o.paste(Image.open(f"{D}/Thumbnail_{i+1}.jpg"),(i*1300,0))
o.resize((1980,360)).save(f"{D}/t3/thumbs.jpg")
