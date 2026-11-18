"""Yol için kule yerlerini otomatik öner + önizleme. Kullanım: yerlestir.py stage.json out.png"""
import sys, json, numpy as np
from PIL import Image, ImageDraw
cfg=json.load(open(sys.argv[1]))
def spline(P,step=6):
    P=[np.array(p,float) for p in P]; out=[]
    for i in range(len(P)-1):
        p0=P[max(0,i-1)];p1=P[i];p2=P[i+1];p3=P[min(len(P)-1,i+2)]
        for t in np.linspace(0,1,max(4,int(np.linalg.norm(p2-p1)//step)),endpoint=False):
            t2,t3=t*t,t*t*t
            out.append(0.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
    return np.array(out)
R=np.vstack([spline(p) for p in cfg['paths']])
def d(x,y): return np.min(np.hypot(R[:,0]-x,R[:,1]-y))
cast=cfg['castle']; river=cfg.get('river')
fixed=[tuple(p) for p in cfg.get('spots',[])]
if cfg.get('auto'):
    cands=[(x,y) for x in range(120,2140,20) for y in range(140,1180,20)]
    cands=[c for c in cands if 115<=d(*c)<=160 and np.hypot(c[0]-cast[0],c[1]-cast[1])>230 and not (river and river[0]-60<c[0]<river[0]+river[1]+60)]
    # kıvrımlara yakın olanları önceliklendir: yol uzunluğu kapsamı (menzil 300 içinde kalan yol noktası sayısı)
    cov=lambda c: np.sum(np.hypot(R[:,0]-c[0],R[:,1]-c[1])<300)
    cands.sort(key=lambda c:-cov(c))
    for c in cands:
        if len(fixed)>=cfg['auto']: break
        if all(np.hypot(c[0]-f[0],c[1]-f[1])>=185 for f in fixed): fixed.append(c)
mines=[tuple(m) for m in cfg.get('mines',[])]
for p in fixed+mines: print(p, int(d(*p)))
print(json.dumps([list(p) for p in fixed]))
im=Image.new('RGB',(2304,1296),(90,120,60)); dr=ImageDraw.Draw(im)
if river: dr.rectangle([river[0],0,river[0]+river[1],1296],fill=(60,90,140))
for x,y in R: dr.ellipse([x-59,y-59,x+59,y+59],fill=(170,140,100))
for i,p in enumerate(fixed): dr.ellipse([p[0]-60,p[1]-30,p[0]+60,p[1]+30],outline=(255,255,255),width=5); dr.text((p[0]-6,p[1]-8),str(i),fill=(255,255,255))
for p in mines: dr.ellipse([p[0]-60,p[1]-30,p[0]+60,p[1]+30],outline=(255,210,80),width=7)
for h in cfg.get('hills',[]): dr.ellipse([h[0]-h[2],h[1]-h[2]*0.7,h[0]+h[2],h[1]+h[2]*0.7],outline=(200,200,220),width=4)
dr.rectangle([cast[0]-50,cast[1]-80,cast[0]+50,cast[1]],fill=(80,80,90))
im.resize((1152,648)).save(sys.argv[2])
