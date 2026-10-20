"""CATCAPE × LA FÁBRICA PREMIUM — 19.12.2026. Meta Feed poster, 1080×1350 (4:5).

Logos are the supplied white-on-black files: only the black ground is made transparent
(alpha = brightness), scaled uniformly, never redrawn or recoloured.
Every element is centre-aligned inside a 120 px safe margin (x 120–960, y 120–1230).

env: SRC (assets/source), FONT_DIR (barlow-condensed-latin-800, montserrat-latin-300/500/600 woff),
     OUT (png path)
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
SRC, FONT_DIR = os.environ["SRC"], os.environ["FONT_DIR"]

WHITE = (242, 237, 228)
SOFT = (200, 196, 186)
RED = (200, 50, 42)
GROUND = (11, 26, 20)  # deep evergreen, almost black

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
    """Flat deep-evergreen ground with a faint vertical falloff and film grain."""
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
    a = np.array(GROUND, np.float32)[None, None, :] * (1.12 - 0.3 * y) * (1 - 0.18 * xx ** 2)
    a = a + np.random.default_rng(4).normal(0, 3.4, (H, W, 1)).astype(np.float32)
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
    d = ImageDraw.Draw(canvas)

    cat = logo("catcape_logo_source.jpg", (74, 500, 822, 1262), 314)
    canvas.alpha_composite(cat, ((W - cat.width) // 2, 120))
    text(d, "×", "light", 38, 472, fill=SOFT)
    fab = logo("lafabrica_logo_source.jpg", (232, 717, 668, 942), 190)
    canvas.alpha_composite(fab, ((W - fab.width) // 2, 496))

    # venue photo as a framed print
    ph = venue_photo(400)
    px, py = (W - ph.width) // 2, 628
    d = ImageDraw.Draw(canvas)
    d.rectangle((px - 6, py - 6, px + ph.width + 5, py + ph.height + 5), fill=WHITE)
    canvas.paste(ph, (px, py))

    d = ImageDraw.Draw(canvas)
    text(d, DATE, "cond", fit(DATE, "cond", 840, 170), 994)
    text(d, TAGLINE, "semi", fit(TAGLINE, "semi", 840, 30), 1090)
    text(d, INFO, "medium", fit(INFO, "medium", 840, 21), 1129, fill=SOFT, tracking=0.12)
    d.rectangle((W / 2 - 28, 1163, W / 2 + 28, 1165), fill=RED)
    text(d, SOON, "medium", 18, 1202, fill=SOFT, tracking=0.2)

    canvas.convert("RGB").save(os.environ["OUT"])


if __name__ == "__main__":
    main()
