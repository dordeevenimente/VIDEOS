import numpy as np
from PIL import Image, ImageDraw, ImageFilter
W,H=1920,1005; S=2; rng=np.random.default_rng(24)
img=Image.new('RGB',(W*S,H*S),(0,0,0)); d=ImageDraw.Draw(img)
pal=np.array([[70,8,10],[150,20,18],[215,55,25],[250,120,50],[255,190,140],[235,120,120]],np.float32)
def col(u):
    u=np.clip(u,0,1)*(len(pal)-1); i=int(u); f=u-i; j=min(i+1,len(pal)-1)
    return pal[i]*(1-f)+pal[j]*f
def bezier(P,t):
    P=np.array(P,np.float32); n=len(P)-1
    from math import comb
    return sum((comb(n,k)*((1-t)**(n-k))*(t**k))[:,None]*P[k][None,:] for k in range(n+1))
def bundle(P,width,N,twist,phase,bright=1.0,lw=2):
    t=np.linspace(0,1,700)[:,None]
    C=bezier(P,t[:,0]); D=np.gradient(C,axis=0); D/=np.linalg.norm(D,axis=1,keepdims=True)+1e-6
    Nn=np.stack([-D[:,1],D[:,0]],1)
    for k in range(N):
        s=k/(N-1)
        # ribbon twists: width narrows/widens along t like a folded band
        wt=width*(0.55+0.45*np.cos(twist*t[:,0]*np.pi+phase))
        off=(s-0.5)*wt[:,None]
        pts=(C+Nn*off)*S
        shade=0.5+0.5*np.cos(twist*t[:,0]*np.pi+phase+ (s-0.5)*2.2)
        for a in range(0,len(pts)-1,4):
            u=0.15+0.8*shade[a]*(0.6+0.4*np.sin(s*9+k*0.3))
            c=col(u)*bright*(0.75+0.25*rng.random())
            d.line([tuple(pts[a]),tuple(pts[min(a+4,len(pts)-1)])],fill=tuple(int(v) for v in np.clip(c,0,255)),width=lw)
# left C-shaped sweep and right mirrored sweep, keeping the centre clear
bundle([(-250,1250),(250,850),(520,420),(260,-120),(-200,-200)],230,110,2.3,0.3,1.0)
bundle([(2170,-250),(1650,150),(1400,600),(1680,1150),(2150,1200)],230,110,2.3,1.9,1.0)
bundle([(-300,380),(180,300),(380,-60)],90,40,1.5,1.0,0.7)
bundle([(2220,640),(1760,720),(1540,1120)],90,40,1.5,2.4,0.7)
img=img.resize((W,H),Image.LANCZOS)
glow=img.filter(ImageFilter.GaussianBlur(18))
a=np.asarray(img,np.float32)/255; g=np.asarray(glow,np.float32)/255
a=a*0.95+g*0.55
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
base=np.array([0.10,0.02,0.02])*np.clip(1-((xx-W/2)/(W*0.6))**2-((yy-H/2)/(H*0.9))**2,0,1)[...,None]
a=np.maximum(a,base)
# keep centre dark behind artist + text
cen=np.exp(-(((xx-W/2)/(W*0.2))**2+((yy-H*0.5)/(H*0.7))**2))
a*=(1-0.75*cen)[...,None]
a+=rng.normal(0,0.02,(H,W,1)).astype(np.float32)*(0.4+a.mean(-1,keepdims=True))
Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8)).save('bg_ribbons_1920.jpg',quality=95)
