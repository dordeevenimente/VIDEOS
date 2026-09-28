import numpy as np
from PIL import Image, ImageFilter
W,H=1080,1350
rng=np.random.default_rng(24)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
hz=930.0
def fbm(o=5,b=2):
    out=np.zeros((H,W),np.float32);amp=1;t=0
    for i in range(o):
        n=b*2**i;g=rng.random((int(n*H/W)+2,n+2)).astype(np.float32)
        out+=amp*np.asarray(Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255;t+=amp;amp*=.5
    return out/t
t=np.clip(yy/hz,0,1)
# filmic dusk: deep plum-black -> wine -> terracotta -> amber haze at horizon
stops=np.array([[0.035,0.02,0.03],[0.09,0.03,0.04],[0.30,0.07,0.05],[0.72,0.25,0.10],[0.95,0.52,0.24]])
pos=np.array([0,0.38,0.66,0.90,1.0])
sky=np.stack([np.interp(t**1.1,pos,stops[:,c]) for c in range(3)],-1)
# thin cloud bands (soft, horizontal)
cl=fbm(6,2); cl=np.asarray(Image.fromarray((cl*255).astype(np.uint8)).resize((W//6,H),Image.BILINEAR).resize((W,H),Image.BICUBIC),np.float32)/255
band=np.clip((cl-0.52)*4,0,1)*np.exp(-((yy-760)/140)**2)
sky=sky*(1-0.45*band[...,None])+band[...,None]*np.array([0.35,0.09,0.05])*0.4
# low sun, soft edge, partly veiled by haze
cx,cy,R=540,905,150
d=np.sqrt((xx-cx)**2+(yy-cy)**2)
disc=np.clip((R-d)/10+0.5,0,1)*(yy<hz)
sun=np.array([1.0,0.60,0.30])
img=sky*(1-disc[...,None]*0.92)+sun*disc[...,None]*0.92
img=img*(1-0.5*band[...,None]*disc[...,None])
glow=np.exp(-np.clip(d-R,0,None)/110.0)*0.55+np.exp(-np.clip(d-R,0,None)/380.0)*0.35
img+=glow[...,None]*np.array([0.75,0.24,0.07])*(yy<hz+4)[...,None]
# anamorphic horizontal flare through the sun
fl=np.exp(-((yy-cy)/5)**2)*np.exp(-((xx-cx)/520)**2)
img+=fl[...,None]*np.array([0.9,0.35,0.12])*0.5
# sea
depth=np.clip((yy-hz)/(H-hz),0,1)
sea=np.array([0.10,0.035,0.03])*(1-depth[...,None])**1.5+0.008
w=fbm(5,3); ws=np.asarray(Image.fromarray((w*255).astype(np.uint8)).resize((W//30,H),Image.BILINEAR).resize((W,H),Image.BICUBIC),np.float32)/255
path=np.exp(-((xx-cx)/(R*(0.9+1.6*depth)))**2)
glit=np.clip((ws-0.45)*3.5,0,1)*(0.6+0.4*np.sin(yy*1.3+w*9))
refl=path*glit*(1-depth)**1.3
seaimg=sea+refl[...,None]*np.array([1.0,0.48,0.20])*0.9
img=np.where((yy>=hz)[...,None],seaimg,img)
# halation + lifted blacks
bl=np.asarray(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18)),np.float32)/255
img=img*0.92+bl*np.array([0.45,0.25,0.18])
img=img*0.96+0.012
# bottom fade + vignette
f=np.clip((yy/H-0.72)/0.14,0,1); img*=(1-0.7*f)[...,None]
dx=(xx-W/2)/W; dy=(yy-H*0.55)/H
img*=np.clip(1-0.9*(dx**2*1.5+dy**2*0.9),0.3,1)[...,None]
img+=rng.normal(0,0.032,(H,W,1)).astype(np.float32)*(0.55+img.mean(-1,keepdims=True))
Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).save('bg_sunset.png')
