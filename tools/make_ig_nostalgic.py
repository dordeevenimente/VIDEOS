# -*- coding: utf-8 -*-
"""DOR · IG feed carousel, 1080x1350, nostalgic treatment.
Grade: matte blacks, amber/sepia split-tone, halation, vignette, film grain, dust.
Type: Fraunces (soft, wonky) for titles + Cormorant Garamond Italic for lines.
Every text block is centred on both axes of the canvas."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os

W, H = 1080, 1350
SS = 2
FONTS = os.environ.get("FONT_DIR", "assets/fonts")
CLEAN = os.environ.get("IG_CLEAN", "build/ig_clean")
OUT = os.environ.get("IG_OUT", "out/ig_dor")
LOGO = "assets/dor_logo.png"
CREAM = (246, 234, 212)
os.makedirs(OUT, exist_ok=True)

POSTS = {
    1: (["DOR DE CE?"],
        ["De muzică? De oameni?", "De o seară ca acasă?"]),
    2: (["DOR DE O SEARĂ", "CA ACASĂ?"],
        ["De muzica noastră. De energia noastră.",
         "De oamenii cu care simți", "că ești între ai tăi."]),
    3: (["DOR DE MUZICA", "NOASTRĂ?"],
        ["De piesele pe care le știi", "de la primul vers."]),
    4: (["DOR DE RÂS?"],
        ["Poate că uneori nu ne e dor doar", "de muzică. Ci și de momentele",
         "care ne aduc împreună."]),
}

def title_font(size):
    f = ImageFont.truetype(f"{FONTS}/Fraunces.ttf", size)
    f.set_variation_by_axes([144, 560, 100, 1])      # opsz, wght, SOFT, WONK
    return f

def body_font(size):
    f = ImageFont.truetype(f"{FONTS}/CormorantGaramond-Italic.ttf", size)
    f.set_variation_by_axes([600])
    return f

rng = np.random.default_rng(7)

# ---------------------------------------------------------------- grade
# per-visual reframing: (zoom, x anchor 0..1, y anchor 0..1) - keeps props clear of the type
FRAMING = {4: (1.32, 0.0, 0.55)}

def reframe(img, i):
    z, ax, ay = FRAMING.get(i, (1.0, 0.5, 0.5))
    k = max(W / img.width, H / img.height) * z
    big = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    x0 = round((big.width - W) * ax); y0 = round((big.height - H) * ay)
    return big.crop((x0, y0, x0 + W, y0 + H))

def grade(img):
    a = np.asarray(img).astype(np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    # gentle desaturation
    a = a * 0.72 + lum[..., None] * 0.28
    # halation: glow of the highlights, pushed to red-amber
    hi = np.clip((lum - 0.62) / 0.38, 0, 1)
    glow = Image.fromarray((hi * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(22))
    g = np.asarray(glow).astype(np.float32)[..., None] / 255.0
    a = a + g * np.array([0.30, 0.13, 0.04], np.float32)
    # split tone: shadows warm brown, highlights honey
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    sh = (1 - lum)[..., None] ** 2
    a = a + sh * np.array([0.045, 0.020, -0.010], np.float32)
    a = a + (lum[..., None] ** 2) * np.array([0.03, 0.015, -0.03], np.float32)
    # matte: lifted blacks, rolled-off whites (faded print)
    a = 0.075 + a * 0.86
    a = a * np.array([1.0, 0.965, 0.90], np.float32) + np.array([0.012, 0.006, 0.0], np.float32)
    # vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = a * (1 - np.clip(r - 0.55, 0, 1)[..., None] * 0.75)
    # centre veil so type reads on every image
    rc = np.sqrt(((xx - W / 2) / (W * 0.46)) ** 2 + ((yy - H / 2) / (H * 0.24)) ** 2)
    veil = np.clip(1 - rc, 0, 1) ** 1.4
    a = a * (1 - veil[..., None] * 0.62) + veil[..., None] * np.array([0.05, 0.03, 0.02]) * 0.62
    return np.clip(a, 0, 1)

def light_leak(a, side):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = (W * 1.05, H * 0.08) if side else (-W * 0.05, H * 0.92)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (W * 0.55)
    leak = np.clip(1 - d, 0, 1) ** 2 * 0.38
    col = np.array([1.0, 0.45, 0.18], np.float32)
    return 1 - (1 - a) * (1 - leak[..., None] * col)          # screen

def film(a):
    # grain: luminance-weighted, slightly clumped
    n = rng.normal(0, 1, (H // 2 + 1, W // 2 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((W, H), Image.BICUBIC))
    n = n * 0.55 + rng.normal(0, 1, (H, W)).astype(np.float32) * 0.45
    lum = a.mean(axis=2)
    amp = 0.055 * (1 - np.abs(lum - 0.45) * 0.9)
    a = a + (n * amp)[..., None]
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    # dust + hairlines
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(38):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        s = rng.uniform(0.6, 2.2)
        c = (250, 238, 215, int(rng.uniform(40, 120))) if rng.random() < .6 else (10, 6, 4, int(rng.uniform(60, 140)))
        d.ellipse([x - s, y - s, x + s, y + s], fill=c)
    for _ in range(3):
        x = rng.uniform(60, W - 60); y0 = rng.uniform(0, H * .6)
        d.line([(x, y0), (x + rng.uniform(-6, 6), y0 + rng.uniform(120, 420))],
               fill=(245, 232, 210, 34), width=1)
    return img

# ---------------------------------------------------------------- type
def tw(d, s, f, tr): return d.textlength(s, font=f) + tr * (len(s) - 1)

def put(d, s, f, tr, y, fill):
    x = (W * SS - tw(d, s, f, tr)) / 2
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr

def typeset(titles, lines):
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    maxw = 900 * SS
    size = 150 * SS
    tf = title_font(size)
    while max(tw(d, t, tf, size * .02) for t in titles) > maxw:
        size -= 2; tf = title_font(size)
    ttr = size * .02
    t_lh = int(size * 0.98)
    bs = 56 * SS
    bf = body_font(bs)
    while max(tw(d, s, bf, 0) for s in lines) > 860 * SS:
        bs -= 2; bf = body_font(bs)
    b_lh = int(bs * 1.22)
    cap = tf.getbbox("H")          # (x0, top, x1, bottom) of a cap
    cap_top, cap_h = cap[1], cap[3] - cap[1]
    gap1, orn, gap2 = 46 * SS, 14 * SS, 40 * SS
    title_h = t_lh * (len(titles) - 1) + cap_h
    xb = bf.getbbox("x")
    body_h = b_lh * (len(lines) - 1) + (bf.getbbox("dg")[3] - bf.getbbox("dl")[1])
    total = title_h + gap1 + orn + gap2 + body_h
    y = (H * SS - total) / 2
    for t in titles:
        put(d, t, tf, ttr, y - cap_top, CREAM + (255,)); y += t_lh
    y = y - t_lh + cap_h + gap1
    # ornament: rule · diamond · rule
    cx, cy = W * SS / 2, y + orn / 2
    c = CREAM + (200,)
    d.line([(cx - 92 * SS, cy), (cx - 20 * SS, cy)], fill=c, width=2 * SS)
    d.line([(cx + 20 * SS, cy), (cx + 92 * SS, cy)], fill=c, width=2 * SS)
    r = 7 * SS
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=c)
    y += orn + gap2
    top = bf.getbbox("dl")[1]
    for s in lines:
        put(d, s, bf, 0, y - top, CREAM + (238,)); y += b_lh
    L = L.resize((W, H), Image.LANCZOS)
    sh = L.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new("RGBA", (W, H), (20, 10, 4, 0)); shadow.putalpha(sh.point(lambda v: int(v * .55)))
    glow = L.filter(ImageFilter.GaussianBlur(3)); glow.putalpha(glow.split()[3].point(lambda v: int(v * .25)))
    return shadow, glow, L

def frame_and_logo(img):
    d = ImageDraw.Draw(img, "RGBA")
    m = 34
    d.rectangle([m, m, W - m - 1, H - m - 1], outline=CREAM + (70,), width=2)
    logo = Image.open(LOGO).convert("RGBA")
    lw = 112; lh = round(lw * logo.height / logo.width)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    r, g, b, al = logo.split()
    tinted = Image.new("RGBA", logo.size, CREAM + (0,)); tinted.putalpha(al.point(lambda v: int(v * .85)))
    img.alpha_composite(tinted, ((W - lw) // 2, H - 34 - 40 - lh))
    return img

for i, (titles, lines) in POSTS.items():
    a = grade(reframe(Image.open(f"{CLEAN}/{i}.png").convert("RGB"), i))
    a = light_leak(a, i % 2 == 1)
    img = film(a).convert("RGBA")
    shadow, glow, text = typeset(titles, lines)
    for layer in (shadow, glow, text):
        img.alpha_composite(layer)
    img = frame_and_logo(img).convert("RGB")
    # a touch of grain over the type too, so it sits in the print
    n = rng.normal(0, 5, (H, W, 1))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.float32) + n, 0, 255).astype(np.uint8))
    img.save(f"{OUT}/dor_ig_{i}_1080x1350.jpg", quality=95, subsampling=0)
print("done")
