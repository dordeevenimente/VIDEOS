from PIL import Image
import numpy as np

import os
src = os.environ.get("LOGO_SRC", "assets/dor_logo_source.png")
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32) / 255.0
# logo is light cream mark on black -> luminance becomes alpha, colour forced to the mark's own cream
lum = a.max(axis=2)
# normalise: black bg -> 0, mark -> 1
lo, hi = 0.06, 0.55
alpha = np.clip((lum - lo) / (hi - lo), 0, 1)
# sample the mark colour (brightest pixels) to keep the official cream tone
mask = lum > 0.8
mark = a[mask].mean(axis=0)
print("mark colour:", (mark*255).round())
h, w = alpha.shape
rgba = np.zeros((h, w, 4), dtype=np.uint8)
rgba[..., 0] = round(mark[0]*255); rgba[..., 1] = round(mark[1]*255); rgba[..., 2] = round(mark[2]*255)
rgba[..., 3] = (alpha*255).astype(np.uint8)
out = Image.fromarray(rgba, "RGBA")
bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
print("bbox:", bbox)
out = out.crop(bbox)
print("trimmed:", out.size, "aspect:", round(out.size[0]/out.size[1], 4))
out.save("dor_logo.png")
