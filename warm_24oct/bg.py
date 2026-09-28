import numpy as np, imageio_ffmpeg as iff, glob
from PIL import Image, ImageFilter
src=glob.glob('/root/.claude/uploads/5fa91e00-88e2-5875-b923-03b6ccfc5702/9154*.mp4')[0]
r=iff.read_frames(src); meta=next(r); W,H=meta['size']
frames=[np.frombuffer(f,np.uint8).reshape(H,W,3).astype(np.float32)/255 for i,f in enumerate(r) if i%6==0][:80]
rng=np.random.default_rng(24)
acc=np.zeros((H,W,3),np.float32)
# long exposure with a slow downward drag + slight sway: lighten blend
for k,f in enumerate(frames[:22]):
    dy=int(k*11); dx=int(18*np.sin(k/5))
    s=np.roll(np.roll(f,dy,0),dx,1)
    acc=np.maximum(acc, s*0.85) + s*0.02
acc=np.clip(acc,0,None)
img=acc[285:285+1350]
lum=(img[...,0]*.35+img[...,1]*.5+img[...,2]*.15)
lum=np.clip(lum/np.percentile(lum,99.3),0,1)
# vertical smear
L=Image.fromarray((lum*255).astype(np.uint8)).filter(ImageFilter.BoxBlur(1))
L=np.asarray(L.resize((1080,1350//18),Image.BILINEAR).resize((1080,1350),Image.BICUBIC)).astype(np.float32)/255*0.6+lum*0.4
# warm gradient map
stops=np.array([[0,0,0],[0.10,0.01,0.01],[0.42,0.03,0.02],[0.86,0.14,0.04],[1.0,0.45,0.08],[1.0,0.80,0.45]])
xs=np.linspace(0,1,len(stops))
L=np.clip((L-0.38)/0.62,0,1)
g=np.stack([np.interp(L**1.6,xs,stops[:,c]) for c in range(3)],-1)
# heat concentration: bright core top-right, cooling toward bottom
yy,xx=np.mgrid[0:1350,0:1080]/np.array([1350,1080])[:,None,None]
heat=np.exp(-(((xx-0.6)/0.36)**2+((yy-0.2)/0.3)**2))
g=g*(0.06+1.1*heat[...,None])
# cold residue bottom-left from original colors (cyan) -> dawn
cold=img*np.array([0.15,0.55,0.75])*np.clip((yy-0.55)/0.45,0,1)[...,None]*np.clip(1-xx*1.3,0,1)[...,None]*0.55
cl=(cold.mean(-1,keepdims=True)>0.12)
#g=g+cold*cl
# horizontal glitch slices with RGB split
for _ in range(3):
    y0=int(rng.integers(180,700)); h=int(rng.integers(2,9)); sh=int(rng.integers(-90,90))
    band=g[y0:y0+h].copy()
    g[y0:y0+h,:,0]=np.roll(band[...,0],sh+6,1); g[y0:y0+h,:,1]=np.roll(band[...,1],sh,1); g[y0:y0+h,:,2]=np.roll(band[...,2],sh-6,1)
# vignette + grain
v=1-0.55*(((xx-0.5)*1.4)**2+((yy-0.45)*1.1)**2)
g=g*np.clip(v,0.2,1)[...,None]
g=g+rng.normal(0,0.035,(1350,1080,1)).astype(np.float32)*(0.4+g.mean(-1,keepdims=True))
Image.fromarray((np.clip(g,0,1)**0.95*255).astype(np.uint8)).save('bg_heat.png')
