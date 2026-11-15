from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D="/home/claude/meisterwerk/pilot"; F="/usr/share/fonts/opentype/inter/"; OR=(255,92,12); Y=(255,200,40)
W,H=2560,1440; B0,B1=H//2-211,H//2+211; S0,S1=W//2-773,W//2+773
CFG={1:{"L":(0,10,300,380),"R":(800,60,1344,380)},2:{"L":(0,0,330,376),"R":(960,80,1344,376)}}
def hfade(w,h,left,right,fw):
    m=Image.new("L",(w,h),255); d=ImageDraw.Draw(m)
    for i in range(fw):
        v=int(255*i/fw)
        if left: d.line((i,0,i,h),fill=v)
        if right: d.line((w-1-i,0,w-1-i,h),fill=v)
    return m
pv=Image.new("RGB",(1600,1150),(20,20,20))
for k,c in CFG.items():
    src=Image.open(f"{D}/bnai{k}.png").convert("RGB")
    s=max(W/src.width,H/src.height); full=src.resize((int(src.width*s),int(src.height*s)),Image.LANCZOS)
    full=full.crop(((full.width-W)//2,(full.height-H)//2,(full.width-W)//2+W,(full.height-H)//2+H))
    im=ImageEnhance.Brightness(full).enhance(.45).filter(ImageFilter.GaussianBlur(6))
    bh=B1-B0+60
    L=src.crop(c["L"]); L=L.resize((int(L.width*bh/L.height),bh),Image.LANCZOS)
    R=src.crop(c["R"]); R=R.resize((int(R.width*bh/R.height),bh),Image.LANCZOS)
    im.paste(L,(S0-40,B0-30),hfade(L.width,bh,True,True,90))
    im.paste(R,(S1-R.width+40,B0-30),hfade(R.width,bh,True,True,110))
    sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).ellipse((W/2-520,H/2-200,W/2+520,H/2+200),fill=170); sh=sh.filter(ImageFilter.GaussianBlur(70))
    im.paste((0,0,0),(0,0),sh)
    d=ImageDraw.Draw(im)
    d.text((W/2,H/2-45),"MEISTERWERK",font=ImageFont.truetype(F+"InterDisplay-Black.otf",104),fill=(255,255,255),anchor="mm",stroke_width=6,stroke_fill=(0,0,0))
    d.rounded_rectangle((W/2-100,H/2+20,W/2+100,H/2+32),6,fill=OR)
    d.text((W/2,H/2+82),"Wie die Dinge wirklich gebaut werden",font=ImageFont.truetype(F+"Inter-Bold.otf",40),fill=Y,anchor="mm",stroke_width=3,stroke_fill=(0,0,0))
    im.save(f"{D}/Meisterwerk_Banner_KI_{k}_zentral.png")
    y=(k-1)*575
    pv.paste(im.crop((0,B0,W,B1)).resize((1600,264)),(0,y))
    pv.paste(im.crop((S0,B0,S1,B1)).resize((1000,273)),(300,y+280))
pv.save(f"{D}/Banner_zentral_Vorschau.jpg",quality=88)
