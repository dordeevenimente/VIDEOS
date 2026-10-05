import numpy as np, cv2, sys
from PIL import Image
# inner-frame interior of panel 2 (x0,x1,ybottom) measured from each mockup
BOX={1:(512,963,704),2:(507,983,731),3:(517,975,685),4:(526,967,711),5:(513,978,701),6:(509,983,731)}
# row where the search for the illustration top starts (below the subtitle)
START={5:345,6:350}
ONLY=[int(a) for a in sys.argv[1:]] or list(BOX)
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel('EDSR_x4.pb'); sr.setModel('edsr',4)
for i in ONLY:
    x0,x1,yb=BOX[i]; s0=START.get(i,380)
    a=np.asarray(Image.open(f'../images/{i}.webp').convert('RGB')).astype(np.float32)
    lum=a.mean(2)
    reg=lum[s0:yb, x0:x1]
    dark=(reg<215).sum(1)
    # first row of a run of 6 rows that all have content
    top=next(r for r in range(len(dark)-6) if all(dark[r:r+6]>3))+s0
    y0=top-6
    crop=a[y0:yb, x0:x1].astype(np.uint8)
    print(i,'crop',x0,y0,x1,yb,crop.shape)
    up=sr.upsample(cv2.cvtColor(crop,cv2.COLOR_RGB2BGR))
    up=cv2.cvtColor(up,cv2.COLOR_BGR2RGB)
    Image.fromarray(up).save(f'illus_{i}_up.png')  # -> assets/invitacion/ilustracion_{i}.png
