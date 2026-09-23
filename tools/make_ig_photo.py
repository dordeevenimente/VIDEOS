# -*- coding: utf-8 -*-
"""DOR · IG feed carousel, 1080x1350, photographic set.
Each slide pairs its message with a matching live-event photo (cleaned sources from
tools/clean_bg.py): warm, natural colour, a soft dark band behind the type, gentle
vignette - no film effects. Type and logo come from make_ig_fresh (Inter, DOR bold)."""
from PIL import Image
import numpy as np, os
import make_ig_fresh as T

CLEAN = os.environ.get("IG_CLEAN", "build/ig_clean")
OUT = os.environ.get("IG_OUT", "out/ig_dor_photo")
W2, H2, SS = T.W2, T.H2, T.SS

# message -> photo: 1 crowd + stage, 2 friends hugging, 3 hands up singing,
# 4 comedy audience laughing, 5 empty stage waiting for the artist, 6 friends together
PHOTO = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}
# (zoom, x anchor, y anchor) - keeps props clear of the type
FRAMING = {4: (1.48, 0.0, 0.42), 5: (1.45, 0.30, 0.0)}
TEXT_CY = {1: 660, 2: 640, 3: 660, 4: 640, 5: 620, 6: 640}

def reframe(img, i):
    z, ax, ay = FRAMING.get(i, (1.0, .5, .5))
    k = max(W2 / img.width, H2 / img.height) * z
    big = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    x0, y0 = round((big.width - W2) * ax), round((big.height - H2) * ay)
    return big.crop((x0, y0, x0 + W2, y0 + H2))

def grade(img, cy):
    a = np.asarray(img).astype(np.float32) / 255
    # warm, natural: mild S-curve, a touch of warmth, slightly richer colour
    a = np.clip(a, 0, 1); a = a + (a - a ** 2) * (a - .5) * .6
    lum = a @ np.array([.299, .587, .114], np.float32)
    a = lum[..., None] + (a - lum[..., None]) * .86
    a = a * np.array([1.0, .99, .96], np.float32)
    YY, XX = T.YY, T.XX
    # soft dark band behind the type + gentle vignette
    band = np.exp(-(((YY - cy * SS) / (H2 * .17)) ** 2)) * np.exp(-(((XX - W2 / 2) / (W2 * .55)) ** 2))
    a = a * (1 - band[..., None] * .45)
    d = np.sqrt(((XX - W2 / 2) / (W2 * .72)) ** 2 + ((YY - H2 / 2) / (H2 * .72)) ** 2)
    a = a * (1 - np.clip(d - .6, 0, 1)[..., None] * .6)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

os.makedirs(OUT, exist_ok=True)
for i, (titles, lines, footer) in T.POSTS.items():
    src = Image.open(f"{CLEAN}/{PHOTO[i]}.png").convert("RGB")
    img = grade(reframe(src, i), TEXT_CY[i])
    sh, tx = T.typeset(titles, lines, footer, TEXT_CY[i])
    img.alpha_composite(sh); img.alpha_composite(tx); T.logo(img)
    img.convert("RGB").resize((T.W, T.H), Image.LANCZOS).save(f"{OUT}/dor_ig_photo_{i}_1080x1350.jpg", quality=95, subsampling=0)
    print("ok", i)
