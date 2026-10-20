"""CATCAPE × LA FÁBRICA PREMIUM — 19.12.2026. Meta Feed poster, 1080×1350 (4:5).

Logos are the supplied white-on-black files: only the black ground is made transparent
(alpha = brightness), scaled uniformly, never redrawn or recoloured.
All essential content stays inside a centred safe area (x 80–1000, y 70–1250).

env: SRC (assets/source), FONT_DIR (barlow-condensed-latin-800, montserrat-latin-300/500/600 woff),
     OUT (png path)
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
SRC, FONT_DIR = os.environ["SRC"], os.environ["FONT_DIR"]

WHITE = (244, 240, 234)
SOFT = (214, 206, 198)
RED = (212, 44, 32)

# exact copy — do not modify
ORGS = "CATCAPE × LA FÁBRICA PREMIUM"  # carried by the two logos and the ×
DATE = "19 DICIEMBRE 2026"
TAGLINE = "NOS VAMOS DE FIESTA EN HORARIO ESCOLAR."
INFO = "MÚSICA ELECTRÓNICA · DESDE LAS 16:00 H"
SOON = "PRÓXIMAMENTE, TODA LA INFORMACIÓN."

FONTS = {"cond": "barlow-condensed-latin-800-normal.woff",
         "light": "montserrat-latin-300-normal.woff",
         "medium": "montserrat-latin-500-normal.woff",
         "semi": "montserrat-latin-600-normal.woff"}


def font(face, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[face]), size)


def background():
    """The supplied 3D render, cropped to 4:5 around the form; the type zone is deepened."""
    im = Image.open(os.path.join(SRC, "background_3d.jpg")).convert("RGB")
    cw = im.width
    ch = round(cw * H / W)
    top = 190
    im = im.crop((0, top, cw, top + ch)).resize((W, H), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    a *= 1 - 0.45 * np.clip((y - 0.68) / 0.22, 0, 1)  # quieter behind the date block
    a += np.random.default_rng(4).normal(0, 3.0, (H, W, 1)).astype(np.float32)  # fine grain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def venue_photo(width):
    """The supplied venue photo: phone/map interface cropped away, pixels untouched."""
    im = Image.open(os.path.join(SRC, "venue_streetview_screenshot.jpg")).convert("RGB")
    im = im.crop((190, 545, 924, 1050))
    h = round(im.height * width / im.width)
    return im.resize((width, h), Image.LANCZOS)


def logo(name, box, width):
    im = Image.open(os.path.join(SRC, name)).convert("L").crop(box)
    h = round(im.height * width / im.width)
    a = im.resize((width, h), Image.LANCZOS)
    out = Image.new("RGBA", a.size, WHITE + (0,))
    out.putalpha(a)
    return out


def text(draw, s, face, size, cy, fill=WHITE, tracking=0.0, cx=W / 2):
    f = font(face, size)
    track = tracking * size
    xs = [f.getlength(s[:i]) + i * track for i in range(len(s) + 1)]
    width = xs[-1] - track
    hb = f.getbbox("H")
    y = cy - (hb[1] + hb[3]) / 2
    x0 = cx - width / 2
    for i, c in enumerate(s):
        draw.text((x0 + xs[i], y), c, font=f, fill=fill)
    return width


def fit(s, face, max_w, start):
    size = start
    while font(face, size).getlength(s) > max_w:
        size -= 2
    return size


def main():
    canvas = background()

    # soft dark halo behind the logo block so the white marks sit cleanly on the render
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse((250, 40, 830, 640), fill=120)
    halo = halo.filter(ImageFilter.GaussianBlur(80))
    canvas = Image.composite(Image.new("RGBA", (W, H), (2, 2, 30, 255)), canvas, halo)

    cat = logo("catcape_logo_source.jpg", (74, 500, 822, 1262), 360)
    canvas.alpha_composite(cat, ((W - cat.width) // 2, 72))
    d = ImageDraw.Draw(canvas)
    text(d, "×", "light", 40, 474, fill=SOFT)
    fab = logo("lafabrica_logo_source.jpg", (232, 717, 668, 942), 210)
    canvas.alpha_composite(fab, ((W - fab.width) // 2, 500))

    # venue photo as a framed print with a soft shadow
    ph = venue_photo(410)
    px, py = (W - ph.width) // 2, 636
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rectangle((px - 6, py + 10, px + ph.width + 6, py + ph.height + 18), fill=170)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.composite(Image.new("RGBA", (W, H), (0, 0, 12, 255)), canvas, shadow)
    d = ImageDraw.Draw(canvas)
    d.rectangle((px - 5, py - 5, px + ph.width + 4, py + ph.height + 4), fill=WHITE)
    canvas.paste(ph, (px, py))

    d = ImageDraw.Draw(canvas)
    ds = fit(DATE, "cond", 900, 170)
    text(d, DATE, "cond", ds, 1016)
    text(d, TAGLINE, "semi", fit(TAGLINE, "semi", 860, 32), 1104)
    text(d, INFO, "medium", 22, 1148, fill=SOFT, tracking=0.14)
    d.rectangle((W / 2 - 30, 1188, W / 2 + 30, 1190), fill=RED)
    text(d, SOON, "medium", 19, 1226, fill=SOFT, tracking=0.2)

    canvas.convert("RGB").save(os.environ["OUT"], quality=95)


if __name__ == "__main__":
    main()
