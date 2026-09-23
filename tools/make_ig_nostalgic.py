# -*- coding: utf-8 -*-
"""DOR · IG feed carousel, 1080x1350, nostalgic treatment.
Grade: matte blacks, amber/sepia split-tone, halation, vignette, film grain, dust.
Type: Inter only - titles mix Light and ExtraBold, lines in uppercase Medium with tracking.
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
GOLD = (201, 160, 72)
os.makedirs(OUT, exist_ok=True)

# titles: one list of (text, weight) runs per line - "DOR DE" light, the object of the longing bold
L, B = 250, 800
POSTS = {
    1: ([[("DOR DE ", L), ("CE?", B)]],
        ["De muzică? De oameni?", "De o seară ca acasă?"]),
    2: ([[("DOR DE ", L), ("O SEARĂ", B)], [("CA ACASĂ?", B)]],
        ["De muzica noastră. De energia noastră.",
         "De oamenii cu care simți", "că ești între ai tăi."]),
    3: ([[("DOR DE ", L), ("MUZICA", B)], [("NOASTRĂ?", B)]],
        ["De piesele pe care le știi", "de la primul vers."]),
    4: ([[("DOR DE ", L), ("RÂS?", B)]],
        ["Poate că uneori nu ne e dor doar", "de muzică. Ci și de momentele",
         "care ne aduc împreună."]),
}

_cache = {}
def inter(size, weight):
    k = (size, weight)
    if k not in _cache:
        f = ImageFont.truetype(f"{FONTS}/Inter.ttf", size)
        f.set_variation_by_axes([32, weight])       # opsz (display), wght
        _cache[k] = f
    return _cache[k]

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
TTR = -0.01      # title tracking (em)
BTR = 0.06       # body tracking (em), uppercase

def tw(d, s, f, tr): return d.textlength(s, font=f) + tr * (len(s) - 1)

def runs_w(d, runs, size):
    return sum(tw(d, t, inter(size, w), size * TTR) + size * TTR for t, w in runs) - size * TTR

def put_runs(d, runs, size, y, fill):
    x = (W * SS - runs_w(d, runs, size)) / 2
    for t, w in runs:
        f = inter(size, w)
        for ch in t:
            d.text((x, y), ch, font=f, fill=fill)
            x += d.textlength(ch, font=f) + size * TTR

def typeset(titles, lines):
    Lr = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(Lr)
    size = 132 * SS
    while max(runs_w(d, r, size) for r in titles) > 900 * SS:
        size -= 2
    t_lh = int(size * 1.04)
    bs = 34 * SS
    lines = [s.upper() for s in lines]
    while max(tw(d, s, inter(bs, 500), bs * BTR) for s in lines) > 860 * SS:
        bs -= 1
    bf = inter(bs, 500)
    b_lh = int(bs * 1.55)
    cap = inter(size, B).getbbox("H")
    cap_top, cap_h = cap[1], cap[3] - cap[1]
    bcap = bf.getbbox("H")
    gap1, orn, gap2 = 58 * SS, 0, 0
    title_h = t_lh * (len(titles) - 1) + cap_h
    body_h = b_lh * (len(lines) - 1) + (bcap[3] - bcap[1])
    rule_gap, rule_h = 46 * SS, 3 * SS
    total = title_h + gap1 + body_h + rule_gap + rule_h
    y = (H * SS - total) / 2
    for r in titles:
        put_runs(d, r, size, y - cap_top, CREAM + (255,)); y += t_lh
    y = y - t_lh + cap_h + gap1
    for s in lines:
        f = bf; x = (W * SS - tw(d, s, f, bs * BTR)) / 2
        for ch in s:
            d.text((x, y - bcap[1]), ch, font=f, fill=CREAM + (240,))
            x += d.textlength(ch, font=f) + bs * BTR
        y += b_lh
    y = y - b_lh + (bcap[3] - bcap[1]) + rule_gap
    cx = W * SS / 2
    d.rectangle([cx - 40 * SS, y, cx + 40 * SS, y + rule_h], fill=GOLD + (235,))
    Lr = Lr.resize((W, H), Image.LANCZOS)
    sh = Lr.split()[3].filter(ImageFilter.GaussianBlur(10))
    shadow = Image.new("RGBA", (W, H), (20, 10, 4, 0)); shadow.putalpha(sh.point(lambda v: int(v * .55)))
    glow = Lr.filter(ImageFilter.GaussianBlur(3)); glow.putalpha(glow.split()[3].point(lambda v: int(v * .18)))
    return shadow, glow, Lr

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
