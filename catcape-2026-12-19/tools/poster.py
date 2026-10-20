"""CATCAPE × LA FÁBRICA PREMIUM — 19.12.2026. Meta Feed poster, 1080×1350 (4:5).

Logos are the supplied white-on-black files: only the black ground is made transparent
(alpha = brightness), scaled uniformly, never redrawn or recoloured.
All essential content stays inside a centred safe area (x 80–1000, y 100–1250).

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
    im = Image.open(os.path.join(SRC, "background_lights.jpg")).convert("RGB")
    ch = round(im.width * H / W)  # 4:5 crop from the top: keeps the lit sign and the red glow
    im = im.crop((0, 0, im.width, ch)).resize((W, H), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * 0.85  # slightly calmer colour
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    # darker overall, deepest under the type block (lower half)
    shade = 0.6 - 0.46 * np.clip((y - 0.42) / 0.42, 0, 1) ** 1.1
    shade = shade + 0.06 * np.exp(-((y - 0.25) / 0.2) ** 2)
    a = a * shade
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
    a *= 1 - 0.25 * xx ** 2  # soft side vignette
    a += np.random.default_rng(4).normal(0, 4.0, (H, W, 1)).astype(np.float32)  # film grain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


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

    # soft dark halo behind the logo block so the white marks sit cleanly on the photo
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse((170, 70, 910, 860), fill=115)
    halo = halo.filter(ImageFilter.GaussianBlur(90))
    canvas = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), canvas, halo)

    cat = logo("catcape_logo_source.jpg", (74, 500, 822, 1262), 470)
    canvas.alpha_composite(cat, ((W - cat.width) // 2, 104))
    fab = logo("lafabrica_logo_source.jpg", (232, 717, 668, 942), 250)

    d = ImageDraw.Draw(canvas)
    text(d, "×", "light", 46, 640, fill=SOFT)
    canvas.alpha_composite(fab, ((W - fab.width) // 2, 672))

    d = ImageDraw.Draw(canvas)
    ds = fit(DATE, "cond", 900, 190)
    text(d, DATE, "cond", ds, 905)
    text(d, TAGLINE, "semi", fit(TAGLINE, "semi", 880, 34), 1010)
    text(d, INFO, "medium", 24, 1062, fill=SOFT, tracking=0.14)
    d.rectangle((W / 2 - 32, 1178, W / 2 + 32, 1180), fill=RED)
    text(d, SOON, "medium", 20, 1222, fill=SOFT, tracking=0.2)

    canvas.convert("RGB").save(os.environ["OUT"], quality=95)


if __name__ == "__main__":
    main()
