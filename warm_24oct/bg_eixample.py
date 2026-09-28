import numpy as np
from PIL import Image, ImageFilter
W,H=1080,1350
rng=np.random.default_rng(1859)  # Pla Cerdà
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
# oblique aerial view: horizon above the frame
yh=-520.0; F=900.0
z=F/(yy-yh)                        # depth factor (bigger = farther)
gx=(xx-W/2)*z*2.6; gy=z*3600.0     # ground coords
th=np.deg2rad(44.0)                # Eixample grid is rotated ~45°
u= gx*np.cos(th)-gy*np.sin(th)
v= gx*np.sin(th)+gy*np.cos(th)
P=113.0                            # block pitch (113 m in Cerdà's plan)
bu=(u%P)-P/2; bv=(v%P)-P/2
a=P/2-10.0                         # half block (street = 20)
c=a*1.62                           # chamfered corners -> octagon
sd=np.maximum(np.maximum(np.abs(bu)-a,np.abs(bv)-a),(np.abs(bu)+np.abs(bv)-c)/np.sqrt(2))
street=np.clip(sd/4.0+0.5,0,1)     # 1 on streets / plazas
# street centre glow
cu=np.abs(np.abs(bu)-P/2); cv=np.abs(np.abs(bv)-P/2)
dc=np.minimum(cu,cv)
core=np.exp(-(dc/4.5)**2)
# lamps: periodic points along streets
lamp=np.exp(-((((u+7)%18.8)-9.4)**2+(cv*1.0)**2)/5)*0+0
lu=np.exp(-(cv/3.0)**2)*np.exp(-((((u)%14.1)-7.05)/1.6)**2)
lv=np.exp(-(cu/3.0)**2)*np.exp(-((((v)%14.1)-7.05)/1.6)**2)
lamps=np.clip(lu+lv,0,1)
# intersections (chamfered plazas) brighter
inter=np.exp(-((cu**2+cv**2)/(2*14**2)))
# Avinguda Diagonal: a wide avenue crossing the grid
dd=np.abs(gx*np.cos(np.deg2rad(-20))+ (gy-3600*0.95)*np.sin(np.deg2rad(-20)))
diag=np.exp(-(dd/18)**2); diag_core=np.exp(-(dd/5)**2)
# rooftop windows: sparse warm dots inside blocks
blk=1-street
win=(rng.random((H,W))>0.9975).astype(np.float32)
win=np.asarray(Image.fromarray((win*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)),np.float32)/255*blk
# taillight streaks on some streets (red) and headlights (warm white)
row=np.floor(v/P).astype(int); col=np.floor(u/P).astype(int)
def h(n,k): return ((np.sin(n*12.9898+k*78.233)*43758.5453)%1.0).astype(np.float32)

sel_r=(h(row,5)>0.62)&(cv<5); sel_c=(h(col,6)>0.66)&(cu<5)
tail=(sel_r*np.exp(-(((u*0.37+row*13)%60)-30)**2/60)).astype(np.float32)
head=(sel_c*np.exp(-(((v*0.41+col*17)%70)-35)**2/80)).astype(np.float32)
row_f=0.25+1.0*h(row,1)**1.6; col_f=0.25+1.0*h(col,2)**1.6
blk_f=h(row*31+col,3)
# fog / haze with fbm
def fbm(o=5,b=2):
    out=np.zeros((H,W),np.float32);amp=1;t=0
    for i in range(o):
        n=b*2**i;g=rng.random((int(n*H/W)+2,n+2)).astype(np.float32)
        out+=amp*np.asarray(Image.fromarray((g*255).astype(np.uint8)).resize((W,H),Image.BICUBIC),np.float32)/255;t+=amp;amp*=.5
    return out/t
fog=fbm()
sod=np.array([1.0,0.42,0.08]); amber=np.array([1.0,0.70,0.36]); red=np.array([1.0,0.10,0.06]); warmw=np.array([1.0,0.86,0.62])
sf=np.where(cu<cv,col_f,row_f)
lum=((street*0.06+core*0.30)*sf)[...,None]*sod + (inter*0.35)[...,None]*amber + (lamps*0.75*sf)[...,None]*amber \
   + (diag*0.35+diag_core*0.6)[...,None]*sod + (win*0.8*(blk_f>0.4))[...,None]*amber + (tail*0.9)[...,None]*red + (head*0.8)[...,None]*warmw
# distance fade (far = hazier, dimmer); near = crisper
far=np.clip((z-z.min())/(z.max()-z.min()),0,1)
lum*= (1.0-0.55*far)[...,None]
lum*= (0.45+0.9*fog**1.5)[...,None]
# bloom
img=np.clip(lum,0,1.5)
b1=np.asarray(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)),np.float32)/255
b2=np.asarray(Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28)),np.float32)/255
img=img*0.85+b1*0.6+b2*1.0
# sky glow at top (city light pollution), deep night elsewhere
sky=np.exp(-(yy/260)**2)[...,None]*np.array([0.55,0.14,0.04])*(0.6+0.6*fog[...,None])
img=img+sky
# vignette + bottom fade for text
dx=(xx-W/2)/W; dy=(yy-H*0.42)/H
img*=np.clip(1-1.1*(dx**2*1.3+dy**2),0.2,1)[...,None]
t=np.clip((yy/H-0.66)/0.16,0,1); img*=(1-0.82*t)[...,None]
img[...,2]*=0.85
img+=rng.normal(0,0.025,(H,W,1)).astype(np.float32)*(0.45+img.mean(-1,keepdims=True))
Image.fromarray((np.clip(img,0,1)**1.05*255).astype(np.uint8)).save('bg_eixample.png')
