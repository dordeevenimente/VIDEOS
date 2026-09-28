import numpy as np
from PIL import Image, ImageFilter
W,H=1080,1350
rng=np.random.default_rng(2410)
def fbm(oct=5,base=3):
    out=np.zeros((H,W),np.float32); amp=1; tot=0
    for o in range(oct):
        n=base*2**o
        g=rng.random((int(n*H/W)+2,n+2)).astype(np.float32)
        im=Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BICUBIC)
        out+=amp*np.asarray(im,np.float32)/255; tot+=amp; amp*=0.5
    return out/tot
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
cx,cy=540,600
dx=(xx-cx)/W; dy=(yy-cy)/H*1.05
d=np.sqrt(dx**2+dy**2)
n1=fbm(5,2); n2=fbm(4,3)
f=d+0.10*(n1-0.5)+0.035*np.sin(xx/W*9+n2*4)   # warped distance = isotherms
# heat: hot ring close to subject, cooling outward
heat=np.exp(-((d-0.29)/0.17)**2)*1.0+0.18*np.exp(-(d/0.8)**2)
heat*=0.75+0.5*n1
heat=np.clip(heat,0,1.2)
# palette: black -> oxblood -> red -> orange -> amber
stops=np.array([[0.02,0.005,0.005],[0.18,0.02,0.015],[0.55,0.06,0.02],[1.0,0.27,0.04],[1.0,0.56,0.20]])
xs=np.linspace(0,1,len(stops))
h=np.clip(heat,0,1)
base=np.stack([np.interp(h**1.3,xs,stops[:,c]) for c in range(3)],-1)*0.38
# contour lines
N=40
ph=np.abs(((f*N)%1.0)-0.5)*2          # 0 at line
w=0.055
line=np.clip(1-ph/w,0,1)**1.5
lc=np.stack([np.interp(np.clip(h*1.1,0,1),xs,stops[:,c]) for c in range(3)],-1)
img=base+line[...,None]*lc*(0.25+1.1*h[...,None]**1.2)
img[...,1]*=0.88; img[...,2]*=0.8
# soft bloom
bl=np.asarray(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)),np.float32)/255
img=img+bl*0.45
# vignette + bottom fall-off for info block
v=np.clip(1-0.9*((dx*1.2)**2+(((yy-cy)/H)*0.9)**2)*1.6,0.15,1)
img*=v[...,None]
t=np.clip((yy/H-0.70)/0.16,0,1); img*=(1-0.55*t)[...,None]
# grain
img+=rng.normal(0,0.028,(H,W,1)).astype(np.float32)*(0.5+img.mean(-1,keepdims=True))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save('bg_thermal.png')
