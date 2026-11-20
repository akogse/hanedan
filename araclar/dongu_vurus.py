"""Vuruşa hizalı döngü: tempo (onset otokorelasyonu) bulunur, döngü uzunluğu tam ölçü katı seçilir,
son kısım başa eşit güçlü çapraz geçişle bağlanır. kullanım: dongu_vurus.py girdi cikti [bpm_tahmini]"""
import sys, subprocess, numpy as np
SR = 44100
src, dst = sys.argv[1], sys.argv[2]
bpm0 = float(sys.argv[3]) if len(sys.argv) > 3 else None
x = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32).reshape(-1,2).copy()
L = len(x); m = x.mean(1)
H = 256
e = np.sqrt(np.convolve(m**2, np.ones(1024)/1024, 'same'))[::H]
o = np.maximum(np.diff(np.log(e+1e-6), prepend=0), 0)   # onset zarfı
o = o - o.mean()
fr = SR / H
ac = np.correlate(o, o, 'full')[len(o)-1:]
lo, hi = int(fr*60/150), int(fr*60/80)
if bpm0: lo, hi = int(fr*60/(bpm0*1.06)), int(fr*60/(bpm0*0.94))
k = lo + np.argmax(ac[lo:hi])
# alt örnek hassasiyeti: parabolik
y0,y1,y2 = ac[k-1],ac[k],ac[k+1]; kk = k + 0.5*(y0-y2)/(y0-2*y1+y2)
# uzun gecikmede inceltme: 16 vuruş sonrası tepeyi ara
T = kk/fr
for n in (16, 32):
    c = int(round(n*T*fr)); w = int(0.06*fr)
    seg = ac[c-w:c+w+1]; c2 = c-w+np.argmax(seg); T = (c2/fr)/n
bpm = 60/T
bar = 4*T
X = bar  # bir ölçü çapraz geçiş
best=None
W = int(6*fr)
for nb in range(int((L/SR - X)/bar), int((L/SR - X)/bar) - 6, -1):
    P = nb*bar
    if P + X > L/SR: continue
    a = o[:W]; b = o[int(P*fr):int(P*fr)+W]
    if len(b) < W: continue
    c = float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
    if best is None or c > best[0]: best=(c,P,nb)
c,P,nb = best
Ps = int(round(P*SR)); Xs = int(round(X*SR))
t = np.linspace(0, np.pi/2, Xs)[:,None]
bas = x[:Xs]*np.sin(t) + x[Ps:Ps+Xs]*np.cos(t)
out = np.concatenate([bas, x[Xs:Ps]])
print(f'{src.split("/")[-1][:30]}: {bpm:.2f} BPM, ölçü {bar:.3f}s, döngü {nb} ölçü = {P:.2f}s, benzerlik {c:.2f}')
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-af','loudnorm=I=-16.3:TP=-1.5','-b:a','160k',dst],input=out.astype(np.float32).tobytes(),check=True)
