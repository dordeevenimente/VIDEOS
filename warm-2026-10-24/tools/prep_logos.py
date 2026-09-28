"""Official logos -> transparent PNGs. Shapes, proportions and colours are kept as supplied.

- WARM: used as supplied when it is already a transparent PNG (only trimmed). If a flat version on
  white is given, alpha is recovered from the paper and the colour stays the logo's own red.
- Bribón del Puerto: only the white lettering ("BRIBÓN / del puerto") is used, as requested;
  the emblem and the patterned background are left out.

- Under The Sun: white lettering lifted out of its brown box (the source is only 150 px, so it is
  upscaled 4x and re-thresholded for clean edges).

env: WARM_SRC, BRIBON_SRC, UTS_SRC, OUT_DIR
"""
import os

import numpy as np
from PIL import Image

OUT = os.environ.get("OUT_DIR", "assets")


def crop_alpha(rgba, thr=8, pad=4):
    a = rgba[..., 3]
    ys, xs = np.where(a > thr)
    y0, y1 = max(0, ys.min() - pad), min(a.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(a.shape[1], xs.max() + pad + 1)
    return rgba[y0:y1, x0:x1]


def warm(src):
    src_im = Image.open(src)
    if src_im.mode == "RGBA" and np.asarray(src_im)[..., 3].min() == 0:
        # already transparent: use it exactly as supplied, only trimmed
        out = crop_alpha(np.asarray(src_im))
        Image.fromarray(out).save(os.path.join(OUT, "warm_logo.png"))
        return np.median(out[out[..., 3] > 250][:, :3], axis=0), out.shape
    im = np.asarray(src_im.convert("RGB"), np.float32)
    # solid logo red = median of strongly red pixels
    red = im[(im[..., 0] > 150) & (im[..., 1] < 60)]
    colour = np.median(red, axis=0)
    # coverage from the green channel: paper white (measured on the border) -> colour[1]
    g = im[..., 1]
    paper = np.median(np.concatenate([g[:8].ravel(), g[-8:].ravel(), g[:, :8].ravel(), g[:, -8:].ravel()]))
    a = np.clip((paper - 3.0 - g) / (paper - 3.0 - colour[1]), 0, 1)
    rgba = np.zeros(im.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = colour.astype(np.uint8)
    rgba[..., 3] = (a * 255).astype(np.uint8)
    out = crop_alpha(rgba)
    Image.fromarray(out).save(os.path.join(OUT, "warm_logo.png"))
    return colour, out.shape


def bribon(src):
    im = np.asarray(Image.open(src).convert("RGB"), np.float32)
    h = im.shape[0]
    lo = im.min(axis=2)
    # white lettering: bright and neutral (the emblem is red, the dots orange)
    a = np.clip((lo - 110.0) / (215.0 - 110.0), 0, 1)
    a[: int(h * 0.33)] = 0  # emblem sits above the lettering
    rgba = np.zeros(im.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (a * 255).astype(np.uint8)
    out = crop_alpha(rgba, thr=40)
    Image.fromarray(out).save(os.path.join(OUT, "bribon_lettering.png"))
    return out.shape


def under_the_sun(src, scale=4):
    from scipy import ndimage
    im = Image.open(src).convert("RGB")
    rgb = np.asarray(im, np.float32)
    dark = rgb.max(axis=2) < 120
    box = ndimage.binary_fill_holes(ndimage.binary_closing(dark, iterations=3))
    box = ndimage.binary_erosion(box, iterations=2)  # stay off the box edge
    lum = rgb.mean(axis=2)
    a = np.clip((lum - 120.0) / (220.0 - 120.0), 0, 1) * box
    big = Image.fromarray((a * 255).astype(np.uint8)).resize(
        (im.width * scale, im.height * scale), Image.LANCZOS)
    b = np.asarray(big, np.float32) / 255.0
    b = np.clip((b - 0.35) / 0.3, 0, 1)  # crisp edge after upscaling
    rgba = np.zeros(b.shape + (4,), np.uint8)
    rgba[..., :3] = 255
    rgba[..., 3] = (b * 255).astype(np.uint8)
    out = crop_alpha(rgba, thr=40)
    Image.fromarray(out).save(os.path.join(OUT, "under_the_sun_lettering.png"))
    return out.shape


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("warm", warm(os.environ["WARM_SRC"]))
    print("bribon", bribon(os.environ["BRIBON_SRC"]))
    print("under the sun", under_the_sun(os.environ["UTS_SRC"]))
