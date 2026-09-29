import numpy as np, subprocess, imageio_ffmpeg, sys
from PIL import Image, ImageFilter
src,out=sys.argv[1],sys.argv[2]
STORY=len(sys.argv)>3 and sys.argv[3]=='story'
W,H=(1080,1920) if STORY else (1080,1350)
PRE='ovS_' if STORY else 'ov_'
ff=imageio_ffmpeg.get_ffmpeg_exe()
rd=imageio_ffmpeg.read_frames(src); meta=next(rd)
FPS=meta['fps']; D=meta['duration']; sw,sh=meta['size']
NF=int(D*FPS)
def lay(k):
    a=np.asarray(Image.open(f'{PRE}{k}.png').convert('RGBA'),np.float32)/255
    x0,y0,x1,y1=Image.open(f'{PRE}{k}.png').getchannel('A').getbbox(); y0=max(y0-24,0); y1=min(y1+4,H)
    c=a[y0:y1,x0:x1]; return dict(rgb=c[...,:3]*c[...,3:],a=c[...,3:],box=(x0,y0,x1,y1))
L={k:lay(k) for k in ['warm','s1','s3','s4','end']}
def ease(x): x=min(max(x,0),1); return 1-(1-x)**3
def over(img,l,al,dy=0):
    if al<=0: return
    x0,y0,x1,y1=l['box']; y0+=dy; y1+=dy
    img[y0:y1,x0:x1]=img[y0:y1,x0:x1]*(1-l['a']*al)+l['rgb']*al
ENDT=D-7.5; T0=1.2; order=['s1','s3','s4']
if (ENDT-T0)/3>8: order=order*2          # long clips: run the three cards twice
SP=(ENDT-T0)/len(order)
scenes=[(k,T0+i*SP) for i,k in enumerate(order)]
yy=np.linspace(0,1,H)[:,None,None].astype(np.float32)
grad=1-0.5*np.exp(-((yy-0.5)/0.2)**2)               # soft band behind the centred text
gtop=1-0.35*np.clip(((0.2 if STORY else 0.16)-yy)/0.16,0,1)             # soft top for the WARM logo
base_mask=(grad*gtop).astype(np.float32)
up=sw<700
cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',src,
     '-map','0:v','-map','1:a?','-af',f'afade=t=out:st={D-0.9:.3f}:d=0.9',
     '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',
     '-c:a','aac','-b:a','256k','-shortest',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
for fi,fr in enumerate(rd):
    t=fi/FPS
    im=Image.frombytes('RGB',(sw,sh),fr)
    if sw/sh > W/H+1e-3:
        cw=int(sh*W/H); x0=(sw-cw)//2; im=im.crop((x0,0,x0+cw,sh))
    elif sw/sh < W/H-1e-3:
        ch=int(sw*H/W); y0=int((sh-ch)*0.45); im=im.crop((0,y0,sw,y0+ch))
    im=im.resize((W,H),Image.LANCZOS)
    if up: im=im.filter(ImageFilter.UnsharpMask(2.2,60,2))
    img=np.asarray(im,np.float32)/255
    e_end=ease((t-ENDT)/0.9)
    img=img*(base_mask*(1-e_end)+0.34*e_end)
    over(img,L['warm'],ease((t-0.3)/0.8))
    for k,t0 in scenes:
        a=ease((t-t0)/0.6)*(1-ease((t-(t0+SP-0.5))/0.45))
        if a>0: over(img,L[k],a,int(round(16*(1-ease((t-t0)/0.6)))))
    if e_end>0: over(img,L['end'],e_end,int(round(16*(1-e_end))))
    p.stdin.write((np.clip(img,0,1)*255+0.5).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print('done',out,round(D,2),FPS)
