import numpy as np, subprocess, imageio_ffmpeg, sys
from PIL import Image, ImageFilter
W,H=1080,1920; FPS=30
BPM=126.048; BEAT=60/BPM; BAR=4*BEAT
A0=2.198; DUR=13*BAR                       # 13 bars from 2.198 s (drop at +3.81 s)
DROP=6.007-A0
NF=int(round(DUR*FPS))
rng=np.random.default_rng(2410)
# ---------- static part of the thermal field (same recipe as the poster) ----------
S=1.08; RW,RH=1080*S,1350*S
def fbm(oct=5,base=3):
    out=np.zeros((H,W),np.float32); amp=1; tot=0
    for o in range(oct):
        n=base*2**o
        g=rng.random((int(n*H/W)+2,n+2)).astype(np.float32)
        out+=amp*np.asarray(Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255; tot+=amp; amp*=0.5
    return out/tot
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
cx,cy=540,828
dx=(xx-cx)/RW; dy=(yy-cy)/RH*1.05
d=np.sqrt(dx**2+dy**2)
n1=fbm(5,2); n2=fbm(4,3)
f=d+0.10*(n1-0.5)+0.035*np.sin(xx/W*9+n2*4)
heat=np.clip((np.exp(-((d-0.29)/0.17)**2)+0.18*np.exp(-(d/0.8)**2))*(0.75+0.5*n1),0,1.2)
stops=np.array([[0.02,0.005,0.005],[0.18,0.02,0.015],[0.55,0.06,0.02],[1.0,0.27,0.04],[1.0,0.56,0.20]])
xs=np.linspace(0,1,len(stops)); h=np.clip(heat,0,1)
base=np.stack([np.interp(h**1.3,xs,stops[:,c]) for c in range(3)],-1)*0.38
lc=np.stack([np.interp(np.clip(h*1.1,0,1),xs,stops[:,c]) for c in range(3)],-1)*(0.25+1.1*h[...,None]**1.2)
cm=np.array([1,0.88,0.8],np.float32)
v=np.clip(1-0.9*((dx*1.2)**2+(((yy-cy)/RH)*0.9)**2)*1.6,0.15,1)
m=v*(1-0.6*np.clip((yy-1200)/234,0,1))*(1-0.5*np.clip((300-yy)/300,0,1))
base=(base*cm*m[...,None]).astype(np.float32); lc=(lc*cm*m[...,None]).astype(np.float32)
fN=(f*40).astype(np.float32)
grain=[rng.normal(0,0.028,(H,W,1)).astype(np.float32) for _ in range(6)]
del yy,xx,dx,dy,d,n1,n2,f,heat,h,v,m
# ---------- audio-driven kick envelope ----------
low=np.load('lowenv.npy'); hopt=512/44100
def kick(ta):
    i=int(ta/hopt); seg=low[max(i-2,0):i+1]
    return float(np.clip((seg.max()-0.45)/0.55,0,1)) if len(seg) else 0.0
# ---------- foreground layers ----------
def load(k):
    a=np.asarray(Image.open(f'layer_{k}.png').convert('RGBA'),np.float32)/255
    bb=Image.open(f'layer_{k}.png').getchannel('A').getbbox()
    x0,y0,x1,y1=bb; y0=max(y0-24,0); y1=min(y1+4,H)
    c=a[y0:y1,x0:x1]; return dict(rgb=c[...,:3]*c[...,3:],a=c[...,3:],box=(x0,y0,x1,y1))
L={k:load(k) for k in ['photo','warm','j2','label','n1','n2','n3','venue','date','l1','l2','l3']}
photo_full=Image.open('layer_photo.png').convert('RGBA')
def ease(x): x=min(max(x,0),1); return 1-(1-x)**3
T={'warm':(0.45,0.9),'j2':(DROP,0.55),'label':(DROP+BEAT,0.55),'n1':(DROP+BAR/2,0.6),'n2':(DROP+BAR,0.6),'n3':(DROP+1.5*BAR,0.6),
   'venue':(DROP+2*BAR,0.7),'date':(DROP+2*BAR+BEAT,0.7),'l1':(DROP+2*BAR+2*BEAT,0.6),'l2':(DROP+2*BAR+3*BEAT,0.6),'l3':(DROP+3*BAR,0.6)}
def over(img,lay,alpha,dy=0):
    if alpha<=0: return
    x0,y0,x1,y1=lay['box']; y0+=dy; y1+=dy
    reg=img[y0:y1,x0:x1]; a=lay['a']*alpha
    img[y0:y1,x0:x1]=reg*(1-a)+lay['rgb']*alpha
# ---------- encoder ----------
ff=imageio_ffmpeg.get_ffmpeg_exe()
out=sys.argv[1] if len(sys.argv)>1 else 'out.mp4'
cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
     '-ss',f'{A0:.3f}','-t',f'{DUR:.3f}','-i','track.wav',
     '-map','0:v','-map','1:a','-af',f'afade=t=in:d=0.05,afade=t=out:st={DUR-1.6:.3f}:d=1.6',
     '-c:v','libx264','-preset','slow','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-movflags','+faststart',
     '-c:a','aac','-b:a','320k','-ar','48000','-shortest',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
flash=0.0
for fi in range(NF):
    t=fi/FPS; ta=A0+t
    # background: rings drift outward one spacing per bar, pulse on the kick
    ph=(t/BAR)%1.0
    lp=np.abs(((fN-ph)%1.0)-0.5)*2
    line=np.clip(1-lp/0.055,0,1)**1.5
    k=kick(ta) if t>=DROP-0.05 else 0.0
    if abs(t-DROP)<0.5/FPS: flash=1.0
    flash*=0.9
    fade=ease(t/2.6)
    gb=fade*(1+0.25*k+0.6*flash); gl=fade*(1+0.55*k+1.2*flash)
    img=base*gb+line[...,None]*lc*gl
    sm=Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).resize((W//4,H//4),Image.BILINEAR).filter(ImageFilter.GaussianBlur(3.5)).resize((W,H),Image.BILINEAR)
    img=img+np.asarray(sm,np.float32)/255*0.45
    img+=grain[fi%6]*(0.5+img.mean(-1,keepdims=True))
    img=np.clip(img,0,1)
    # photo: fade in with a slow settle (1.05 -> 1.0)
    pa=ease((t-0.9)/2.6)
    if pa>0:
        sc=1.05-0.05*ease((t-0.9)/3.6)
        if sc>1.0005:
            x0,y0,x1,y1=L['photo']['box']
            nw,nh=int(W*sc),int(H*sc)
            big=photo_full.resize((nw,nh),Image.BILINEAR)
            ox,oy=(nw-W)//2,int((nh-H)*0.42)
            c=np.asarray(big.crop((ox,oy,ox+W,oy+H)),np.float32)/255
            a=c[...,3:]*pa; img=img*(1-a)+c[...,:3]*c[...,3:]*pa
        else: over(img,L['photo'],pa)
    for kname,(t0,du) in T.items():
        e=ease((t-t0)/du)
        if e>0: over(img,L[kname],e,int(round(18*(1-e))))
    # gentle push-in over the whole clip
    z=1.0+0.03*(t/DUR)
    fr=Image.fromarray((img*255+0.5).astype(np.uint8))
    if z>1.0005:
        nw,nh=int(W*z),int(H*z); fr=fr.resize((nw,nh),Image.BICUBIC); ox,oy=(nw-W)//2,(nh-H)//2; fr=fr.crop((ox,oy,ox+W,oy+H))
    p.stdin.write(fr.tobytes())
    if fi%60==0: print(fi,NF,flush=True)
p.stdin.close(); p.wait(); print('done',out)
