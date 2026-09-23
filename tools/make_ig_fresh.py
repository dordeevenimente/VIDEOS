# -*- coding: utf-8 -*-
"""DOR · IG feed carousel, 1080x1350, fresh / premium set.
Backgrounds are drawn entirely in code: a rich colour field per slide (soft mesh
gradient + very fine noise) and one signature motif (disco sphere, two rings,
waveform, spotlight + mic, VIP pass, gold confetti).
Type: Inter only - "DOR" ExtraBold, the rest ExtraLight; uppercase tracked lines."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, os

W, H = 1080, 1350
SS = 2
W2, H2 = W * SS, H * SS
FONTS = os.environ.get("FONT_DIR", "assets/fonts")
OUT = os.environ.get("IG_OUT", "out/ig_dor_fresh")
LOGO = "assets/dor_logo.png"
CREAM = (255, 248, 238)
GOLD = (227, 189, 110)
rng = np.random.default_rng(11)

L, B = 200, 800
POSTS = {
    1: ([[("DOR", B), (" DE CE?", L)]],
        ["De muzică? De oameni?", "De o seară ca acasă?"], None),
    2: ([[("DOR", B), (" DE O SEARĂ", L)], [("CA ACASĂ?", L)]],
        ["De muzica noastră. De energia noastră.",
         "De oamenii cu care simți", "că ești între ai tăi."], None),
    3: ([[("DOR", B), (" DE MUZICA", L)], [("NOASTRĂ?", L)]],
        ["De piesele pe care le știi", "de la primul vers."], None),
    4: ([[("DOR", B), (" DE RÂS?", L)]],
        ["Poate că uneori nu ne e dor doar", "de muzică. Ci și de momentele",
         "care ne aduc împreună."], None),
    5: ([[("ȚIE DE CE", L)], [("ARTIST ȚI-E ", L), ("DOR", B), ("?", L)]],
        ["Scrie-ne în comentarii.", "Poate îl aducem mai aproape."], None),
    6: ([[("DOR", B), (" E PENTRU NOI.", L)], [("ȘI DESPRE NOI.", L)]],
        ["Muzică. Oameni. Seri împreună. În Spania."], "Follow @dor.evenimente"),
}
# optical centre (y, canvas px) of each text block - motifs live below it
TEXT_CY = {1: 560, 2: 520, 3: 520, 4: 520, 5: 520, 6: 540}

_cache = {}
def inter(size, weight):
    k = (size, weight)
    if k not in _cache:
        f = ImageFont.truetype(f"{FONTS}/Inter.ttf", size)
        f.set_variation_by_axes([32, weight])
        _cache[k] = f
    return _cache[k]

def hexc(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255

YY, XX = np.mgrid[0:H2, 0:W2].astype(np.float32)

# ---------------------------------------------------------------- backgrounds
def field(base, blobs):
    """base colour + soft radial blobs [(cx, cy, r, colour, strength)] in canvas px."""
    a = np.ones((H2, W2, 3), np.float32) * hexc(base)
    for cx, cy, r, col, s in blobs:
        d = np.sqrt((XX - cx * SS) ** 2 + (YY - cy * SS) ** 2) / (r * SS)
        w = (np.clip(1 - d, 0, 1) ** 2 * s)[..., None]
        a = a * (1 - w) + hexc(col) * w
    return a

def finish(a):
    # gentle vignette + very fine noise (clean, not film grain)
    d = np.sqrt(((XX - W2 / 2) / (W2 * .75)) ** 2 + ((YY - H2 / 2) / (H2 * .75)) ** 2)
    a = a * (1 - np.clip(d - .55, 0, 1)[..., None] * .55)
    a = a + rng.normal(0, .010, (H2, W2, 1)).astype(np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

def glow_layer(size, fn, blur):
    L_ = Image.new("RGBA", size, (0, 0, 0, 0)); fn(ImageDraw.Draw(L_))
    return L_.filter(ImageFilter.GaussianBlur(blur))

def add(img, layer):
    """additive (screen-ish) blend of an RGBA glow layer"""
    a = np.asarray(img).astype(np.float32) / 255
    l = np.asarray(layer).astype(np.float32) / 255
    rgb = 1 - (1 - a[..., :3]) * (1 - l[..., :3] * l[..., 3:4])
    return Image.fromarray((np.dstack([rgb, a[..., 3:]]) * 255).astype(np.uint8))

def P(*v): return [x * SS for x in v]

# 1 - disco sphere -------------------------------------------------------------
def bg1():
    img = finish(field("#0a1430", [(540, 250, 820, "#1d2f6e", .9), (540, 1060, 420, "#2a3f8a", .55)]))
    cx, cy, R = 540 * SS, 1015 * SS, 170 * SS
    # halo + floor shadow
    img = add(img, glow_layer(img.size, lambda d: d.ellipse([cx - R * 1.6, cy - R * 1.6, cx + R * 1.6, cy + R * 1.6], fill=(120, 150, 255, 90)), 90))
    sh = glow_layer(img.size, lambda d: d.ellipse([cx - R * .9, cy + R * 1.18, cx + R * .9, cy + R * 1.34], fill=(0, 0, 0, 170)), 30)
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(12, 18, 44, 255))    # dark grout between the mirrors
    light = np.array([-.45, -.65, .62]); light /= np.linalg.norm(light)
    n_lat = 22
    sparks = []
    for i in range(n_lat):
        t0, t1 = -math.pi / 2 + math.pi * i / n_lat, -math.pi / 2 + math.pi * (i + 1) / n_lat
        tm = (t0 + t1) / 2
        n_lon = max(6, int(round(2 * n_lat * math.cos(tm))))
        for j in range(n_lon):
            p0, p1 = 2 * math.pi * j / n_lon, 2 * math.pi * (j + 1) / n_lon
            pm = (p0 + p1) / 2
            nz = math.cos(tm) * math.cos(pm)
            if nz <= 0.02: continue
            def pt(t, p):
                return (cx + R * math.cos(t) * math.sin(p), cy + R * math.sin(t))
            g = .08 * (t1 - t0)
            quad = [pt(t0 + g, p0 + g), pt(t0 + g, p1 - g), pt(t1 - g, p1 - g), pt(t1 - g, p0 + g)]
            n = np.array([math.cos(tm) * math.sin(pm), math.sin(tm), nz])
            diff = max(0, n @ light)
            env = rng.random()                                  # each mirror reflects something different
            v = .08 + .50 * diff + (.35 if env > .82 else .12 * env)
            spec = (2 * (n @ light) * n - light)[2]
            if spec > .95 or rng.random() < .012:
                v = 1.25; sparks.append(pt(tm, pm))
            v = min(1.2, v) * (.45 + .55 * nz)
            dark, lite = np.array([22, 32, 72]), np.array([236, 242, 255])
            tint = np.array([150, 185, 255]) if env < .18 else lite
            c = np.clip(dark + (tint - dark) * v, 0, 255).astype(int)
            d.polygon(quad, fill=tuple(c) + (255,))
    # sparkles on the sphere + reflected specks on the backdrop
    sp = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sp)
    for x, y in sparks[:9]:
        r = rng.uniform(16, 34) * SS
        ds.polygon([(x - r, y), (x, y - 2 * SS), (x + r, y), (x, y + 2 * SS)], fill=(255, 255, 255, 235))
        ds.polygon([(x, y - r), (x + 2 * SS, y), (x, y + r), (x - 2 * SS, y)], fill=(255, 255, 255, 235))
        ds.ellipse([x - 4 * SS, y - 4 * SS, x + 4 * SS, y + 4 * SS], fill=(255, 255, 255, 255))
    for _ in range(70):
        ang = rng.uniform(0, 2 * math.pi); dist = rng.uniform(260, 900) * SS
        x = cx + math.cos(ang) * dist; y = cy + math.sin(ang) * dist * .75
        if 330 * SS < y < 800 * SS and 150 * SS < x < 930 * SS: continue    # keep the type zone calm
        l = rng.uniform(4, 14) * SS; a = int(rng.uniform(90, 200))
        ds.line([x - l * math.cos(ang), y - l * math.sin(ang), x + l * math.cos(ang), y + l * math.sin(ang)],
                fill=(220, 232, 255, a), width=int(rng.uniform(2, 4)) * SS)
    img = add(img, sp.filter(ImageFilter.GaussianBlur(4)))
    img.alpha_composite(sp)
    return img

# 2 - two rings (togetherness) -------------------------------------------------
def bg2():
    img = finish(field("#360912", [(300, 200, 700, "#6d1427", .8), (760, 1150, 650, "#8c2b24", .55)]))
    cy, R, off = 1045, 165, 105
    c1, c2 = (540 - off, cy), (540 + off, cy)
    # warm lens glow where the rings meet
    lens = Image.new("L", img.size, 0)
    m1 = Image.new("L", img.size, 0); ImageDraw.Draw(m1).ellipse(P(c1[0] - R, cy - R, c1[0] + R, cy + R), fill=255)
    m2 = Image.new("L", img.size, 0); ImageDraw.Draw(m2).ellipse(P(c2[0] - R, cy - R, c2[0] + R, cy + R), fill=255)
    lens = Image.fromarray(np.minimum(np.asarray(m1), np.asarray(m2)))
    gl = Image.new("RGBA", img.size, GOLD + (0,)); gl.putalpha(lens.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .75)))
    img = add(img, gl)
    img = add(img, glow_layer(img.size, lambda d: d.ellipse(P(540 - 120, cy - 150, 540 + 120, cy + 150), fill=GOLD + (120,)), 80))
    d = ImageDraw.Draw(img)
    for (x, y) in (c1, c2):
        for k, a in ((0, 255), (38, 70), (76, 30)):     # ring + two faint echoes
            r = R + k
            d.ellipse(P(x - r, y - r, x + r, y + r), outline=GOLD + (a,), width=int(2.2 * SS) if k == 0 else SS)
    return img

# 3 - waveform ----------------------------------------------------------------
def bg3():
    img = finish(field("#6f2812", [(250, 180, 760, "#c8672f", .85), (900, 1250, 600, "#4d1a0a", .6)]))
    cy = 1060; n = 64; x0, x1 = 110, 970
    step = (x1 - x0) / (n - 1)
    xs = np.arange(n)
    env = np.exp(-((xs - n / 2) / (n * .30)) ** 2)
    wave = (.55 + .45 * np.sin(xs * .55) * np.cos(xs * .21 + 1)) * env
    wave = np.clip(wave + rng.uniform(-.08, .08, n) * env, .04, 1)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, v in enumerate(wave):
        x = x0 + i * step; h = 12 + v * 250
        t = abs(i - n / 2) / (n / 2)
        col = tuple(int(CREAM[k] * (1 - t) + GOLD[k] * t) for k in range(3))
        d.rounded_rectangle(P(x - 3.2, cy - h / 2, x + 3.2, cy + h / 2), radius=3.2 * SS, fill=col + (245,))
    img = add(img, lay.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(lay)
    return img

# 4 - spotlight + mic -----------------------------------------------------------
def bg4():
    img = finish(field("#082a1f", [(540, 150, 700, "#1c5a44", .7), (540, 1150, 500, "#0f4633", .6)]))
    fy = 1150
    # cone
    cone = Image.new("L", img.size, 0)
    ImageDraw.Draw(cone).polygon(P(470, -40, 610, -40, 820, fy, 260, fy), fill=255)
    ramp = np.clip((YY / (fy * SS)), 0, 1) ** 1.3
    ca = (np.asarray(cone.filter(ImageFilter.GaussianBlur(40))).astype(np.float32) / 255) * (.10 + .20 * ramp)
    lay = np.zeros((H2, W2, 4), np.float32); lay[..., :3] = [.85, 1, .92]; lay[..., 3] = ca
    img = add(img, Image.fromarray((lay * 255).astype(np.uint8)))
    # floor pool
    img = add(img, glow_layer(img.size, lambda d: d.ellipse(P(250, fy - 60, 830, fy + 60), fill=(230, 255, 240, 200)), 26))
    img = add(img, glow_layer(img.size, lambda d: d.ellipse(P(360, fy - 32, 720, fy + 32), fill=(255, 255, 255, 170)), 10))
    # mic: weighted base, chrome stand, chrome capsule head with grille and a gold band
    d = ImageDraw.Draw(img)
    d.ellipse(P(480, fy - 14, 600, fy + 10), fill=(14, 18, 16, 255))
    d.ellipse(P(484, fy - 16, 596, fy + 2), fill=(52, 60, 56, 255))
    def chrome(w, h):
        x = np.linspace(0, 1, w)[None, :]
        v = .18 + .75 * np.exp(-((x - .30) / .10) ** 2) + .35 * np.exp(-((x - .78) / .07) ** 2)
        v = np.repeat(v, h, 0)
        rgb = np.dstack([v * 205, v * 225, v * 215]).clip(0, 255)
        return Image.fromarray(np.dstack([rgb, np.full((h, w), 255)]).astype(np.uint8))
    stand = chrome(12 * SS, (fy - 900) * SS)
    img.alpha_composite(stand, (534 * SS, 900 * SS))
    hw, hh = 84 * SS, 170 * SS
    head = Image.new("RGBA", (hw + 40 * SS, hh + 90 * SS), (0, 0, 0, 0))
    m = Image.new("L", (hw, hh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, hw - 1, hh - 1], radius=hw // 2, fill=255)
    cap = chrome(hw, hh); cap.putalpha(m)
    dg = ImageDraw.Draw(cap)
    for yy in range(14 * SS, int(hh * .62), 7 * SS):          # grille mesh
        for xx in range(8 * SS + (yy // (7 * SS)) % 2 * 3 * SS, hw - 6 * SS, 7 * SS):
            dg.ellipse([xx, yy, xx + 3 * SS, yy + 3 * SS], fill=(10, 16, 13, 150))
    cap.putalpha(m)
    dg.rectangle([0, int(hh * .66), hw, int(hh * .66) + 5 * SS], fill=GOLD + (255,))
    cap.putalpha(Image.fromarray(np.minimum(np.asarray(cap.split()[3]), np.asarray(m))))
    head.alpha_composite(cap, (20 * SS, 0))
    neck = chrome(22 * SS, 80 * SS); head.alpha_composite(neck, (20 * SS + hw // 2 - 11 * SS, hh - 4 * SS))
    head = head.rotate(-18, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(head, (540 * SS - head.width // 2 + 22 * SS, 900 * SS - head.height + 70 * SS))
    return img

# 5 - VIP pass -----------------------------------------------------------------
def bg5():
    img = finish(field("#101012", [(540, 900, 620, "#2e2717", .75), (540, 120, 700, "#1d1d22", .6)]))
    img = add(img, glow_layer(img.size, lambda d: d.polygon(P(430, -40, 650, -40, 800, 1300, 280, 1300), fill=(255, 225, 160, 30)), 60))
    cw, ch = 300, 400
    card = Image.new("RGBA", ((cw + 80) * SS, (ch + 80) * SS), (0, 0, 0, 0)); dc = ImageDraw.Draw(card)
    o = 40 * SS
    # card body with subtle vertical gradient
    body = Image.new("RGBA", (cw * SS, ch * SS))
    g = np.linspace(.13, .06, ch * SS)[:, None, None] * np.ones((1, cw * SS, 1))
    body = Image.fromarray((np.dstack([g, g, g * 1.05, np.ones_like(g)]) * 255).astype(np.uint8))
    mask = Image.new("L", body.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw * SS - 1, ch * SS - 1], radius=22 * SS, fill=255)
    card.paste(body, (o, o), mask)
    dc.rounded_rectangle([o + 14 * SS, o + 14 * SS, o + (cw - 14) * SS, o + (ch - 14) * SS], radius=14 * SS, outline=GOLD + (255,), width=2 * SS)
    dc.rounded_rectangle([o + (cw / 2 - 34) * SS, o + 30 * SS, o + (cw / 2 + 34) * SS, o + 44 * SS], radius=7 * SS, fill=(5, 5, 6, 255))
    lg = Image.open(LOGO).convert("RGBA"); lw = 96 * SS; lh = round(lw * lg.height / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS); tint = Image.new("RGBA", lg.size, GOLD + (0,)); tint.putalpha(lg.split()[3])
    card.alpha_composite(tint, (o + (cw * SS - lw) // 2, o + 92 * SS))
    def ctext(s, y, size, w, col, tr):
        f = inter(size * SS, w); tw_ = dc.textlength(s, font=f) + tr * SS * (len(s) - 1)
        x = o + (cw * SS - tw_) / 2
        for c in s:
            dc.text((x, o + y * SS), c, font=f, fill=col); x += dc.textlength(c, font=f) + tr * SS
    ctext("VIP · BACKSTAGE", 160, 15, 600, GOLD + (255,), 4)
    dc.line([o + 50 * SS, o + 280 * SS, o + (cw - 50) * SS, o + 280 * SS], fill=CREAM + (200,), width=2 * SS)
    ctext("ARTISTUL TĂU", 296, 13, 500, CREAM + (170,), 4)
    ctext("ALL ACCESS", 340, 13, 700, GOLD + (220,), 5)
    card = card.rotate(-7, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0)); shadow.putalpha(card.split()[3].point(lambda v: int(v * .7)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(26 * SS))
    px, py = 540 * SS - card.width // 2, 1055 * SS - card.height // 2
    img.alpha_composite(shadow, (px + 14 * SS, py + 30 * SS))
    # satin lanyard: a soft curve from the card slot out of the right edge
    d = ImageDraw.Draw(img)
    sx, sy = 548, 880
    pts = [(sx + (1110 - sx) * t + 120 * math.sin(math.pi * t) * 0, sy - 60 * math.sin(math.pi * t * .9) - (sy - 820) * t) for t in np.linspace(0, 1, 60)]
    for wdt, col in ((24, (12, 12, 14, 255)), (10, (46, 44, 42, 255)), (2, (95, 90, 84, 200))):
        d.line([(x * SS, y * SS) for x, y in pts], fill=col, width=wdt * SS, joint="curve")
    img.alpha_composite(card, (px, py))
    return img

# 6 - gold confetti ------------------------------------------------------------
def bg6():
    img = finish(field("#0f2d8f", [(540, 380, 800, "#3462e6", .75), (540, 1400, 700, "#0a1f6a", .6)]))
    img = add(img, glow_layer(img.size, lambda d: d.ellipse(P(140, 250, 940, 850), fill=(120, 160, 255, 70)), 120))
    for depth in (0, 1, 2):                                   # back to front
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        count, scale, blur = ((90, .7, 1.2), (70, 1.0, 0), (14, 2.2, 7))[depth]
        for _ in range(count):
            x, y = rng.uniform(-20, 1100), rng.uniform(-20, 1370)
            if depth < 2 and 330 < y < 900 and 140 < x < 940 and rng.random() < .8: continue
            if depth == 2 and 200 < y < 1000 and 120 < x < 960: continue
            w, h = rng.uniform(12, 24) * scale, rng.uniform(6, 11) * scale
            piece = Image.new("RGBA", (int(w * SS) + 2, int(h * SS) + 2), (0, 0, 0, 0))
            t = rng.uniform(.80, 1.12)
            base = np.array([232, 192, 108]) * t + np.array([30, 30, 30]) * max(0, t - 1) * 3
            c1 = tuple(int(v) for v in np.clip(base, 0, 255)); c2 = tuple(int(v) for v in np.clip(base * .72, 0, 255))
            dp = ImageDraw.Draw(piece)
            dp.rectangle([0, 0, piece.width - 1, piece.height - 1], fill=c1 + (255,))
            dp.rectangle([0, piece.height // 2, piece.width - 1, piece.height - 1], fill=c2 + (255,))
            piece = piece.rotate(rng.uniform(0, 180), resample=Image.BICUBIC, expand=True)
            lay.alpha_composite(piece, (int(x * SS), int(y * SS)))
        if blur: lay = lay.filter(ImageFilter.GaussianBlur(blur * SS))
        img.alpha_composite(lay)
    return img

BGS = {1: bg1, 2: bg2, 3: bg3, 4: bg4, 5: bg5, 6: bg6}

# ---------------------------------------------------------------- type
TTR, BTR = -0.02, 0.09

def tw(d, s, f, tr): return d.textlength(s, font=f) + tr * (len(s) - 1)
def runs_w(d, runs, size):
    return sum(tw(d, t, inter(size, w), size * TTR) + size * TTR for t, w in runs) - size * TTR

def typeset(titles, lines, footer, cy):
    Lr = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); d = ImageDraw.Draw(Lr)
    size = 132 * SS
    while max(runs_w(d, r, size) for r in titles) > 920 * SS: size -= 2
    lead = 1.18 if any(c in "ȚȘ" for r in titles[:-1] for t, _ in r for c in t) else 1.06
    t_lh = int(size * lead)
    bs = 32 * SS; lines = [s.upper() for s in lines]
    while max(tw(d, s, inter(bs, 500), bs * BTR) for s in lines) > 880 * SS: bs -= 1
    bf = inter(bs, 500); b_lh = int(bs * 1.6)
    cap = inter(size, B).getbbox("H"); cap_top, cap_h = cap[1], cap[3] - cap[1]
    bcap = bf.getbbox("H"); bch = bcap[3] - bcap[1]
    ff = inter(int(bs * .9), 400); fcap = ff.getbbox("H")
    gap1, rule_gap, rule_h, f_gap = 62 * SS, 46 * SS, 3 * SS, 40 * SS
    total = t_lh * (len(titles) - 1) + cap_h + gap1 + b_lh * (len(lines) - 1) + bch + rule_gap + rule_h
    if footer: total += f_gap + fcap[3] - fcap[1]
    y = cy * SS - total / 2
    for r in titles:
        x = (W2 - runs_w(d, r, size)) / 2
        for t, w in r:
            f = inter(size, w)
            for ch in t:
                d.text((x, y - cap_top), ch, font=f, fill=CREAM + (255,)); x += d.textlength(ch, font=f) + size * TTR
        y += t_lh
    y = y - t_lh + cap_h + gap1
    for s in lines:
        x = (W2 - tw(d, s, bf, bs * BTR)) / 2
        for ch in s:
            d.text((x, y - bcap[1]), ch, font=bf, fill=CREAM + (240,)); x += d.textlength(ch, font=bf) + bs * BTR
        y += b_lh
    y = y - b_lh + bch + rule_gap
    d.rounded_rectangle([W2 / 2 - 32 * SS, y, W2 / 2 + 32 * SS, y + rule_h], radius=rule_h / 2, fill=GOLD + (255,))
    if footer:
        y += rule_h + f_gap
        d.text(((W2 - d.textlength(footer, font=ff)) / 2, y - fcap[1]), footer, font=ff, fill=CREAM + (225,))
    sh = Image.new("RGBA", Lr.size, (0, 0, 0, 0)); sh.putalpha(Lr.split()[3].point(lambda v: int(v * .35)))
    return sh.filter(ImageFilter.GaussianBlur(14 * SS)), Lr

def logo(img):
    lg = Image.open(LOGO).convert("RGBA"); lw = 104 * SS; lh = round(lw * lg.height / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    img.alpha_composite(lg, ((W2 - lw) // 2, H2 - 58 * SS - lh))

if __name__ == "__main__":
  os.makedirs(OUT, exist_ok=True)
  for i, (titles, lines, footer) in POSTS.items():
    img = BGS[i]()
    sh, tx = typeset(titles, lines, footer, TEXT_CY[i])
    img.alpha_composite(sh); img.alpha_composite(tx); logo(img)
    img.convert("RGB").resize((W, H), Image.LANCZOS).save(f"{OUT}/dor_ig_fresh_{i}_1080x1350.jpg", quality=95, subsampling=0)
    print("ok", i)
