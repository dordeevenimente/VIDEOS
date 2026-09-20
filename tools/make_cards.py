# -*- coding: utf-8 -*-
"""Builds the typographic layers for the DOR / BOGDAN DLP reel.
One family only: Inter Display. Hierarchy comes from weight, size and tracking.
No decorative effects on type - only a near-invisible soft shadow for legibility.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, os

W, H = 1080, 1920
SS = 2                      # supersampling factor for crisp type
FONTDIR = os.environ.get("INTER_DIR", "inter/extras/ttf")
CREAM = (248, 245, 241)

SAFE_W = 840                # max text width  (x 120 .. 960, clear of the IG action rail)
ANCHOR_Y = 1300             # optical centre of every text block

def font(weight, size):
    return ImageFont.truetype(f"{FONTDIR}/InterDisplay-{weight}.ttf", size)

def text_w(f, s, tracking=0):
    d = ImageDraw.Draw(Image.new("L", (10, 10)))
    w = d.textlength(s, font=f)
    return w + tracking * (len(s) - 1)

def fit_size(weight, s, target_w, tracking=0, cap=400):
    lo, hi = 10, cap
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w(font(weight, mid), s, tracking * mid / 100.0 if tracking else 0) <= target_w:
            lo = mid
        else:
            hi = mid - 1
    return lo

def draw_line(layer, s, weight, size, tracking_px, y_top, alpha):
    """Draws one centred line on the supersampled layer, returns its height."""
    f = font(weight, size)
    d = ImageDraw.Draw(layer)
    total = text_w(f, s, tracking_px)
    x = (W * SS - total) / 2.0
    col = CREAM + (int(255 * alpha),)
    if tracking_px:
        for ch in s:
            d.text((x, y_top), ch, font=f, fill=col)
            x += d.textlength(ch, font=f) + tracking_px
    else:
        d.text((x, y_top), s, font=f, fill=col)
    a, b, c, e = f.getbbox("Hg")
    return e - b

def build(blocks, out_path, shadow=0.42):
    """blocks: list of dicts {text, weight, size, tracking, alpha, gap_before}"""
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    # measure total height first
    heights, ascents = [], []
    for b in blocks:
        f = font(b["weight"], b["size"])
        asc, desc = f.getmetrics()
        heights.append(b.get("line_h", int(b["size"] * 1.02)))
    total_h = sum(heights) + sum(b.get("gap_before", 0) for b in blocks[1:])
    y = ANCHOR_Y * SS - total_h / 2.0
    for i, b in enumerate(blocks):
        if i:
            y += b.get("gap_before", 0)
        f = font(b["weight"], b["size"])
        d = ImageDraw.Draw(layer)
        # position by cap-height so optical spacing is even
        bbox = f.getbbox("H")
        draw_line(layer, b["text"], b["weight"], b["size"],
                  b.get("tracking", 0), y - bbox[1], b.get("alpha", 1.0))
        y += heights[i]

    # soft, barely-there separation from the footage (no plate, no glow)
    a = layer.getchannel("A")
    halo = a.filter(ImageFilter.GaussianBlur(radius=26 * SS / 2))
    halo = halo.point(lambda v: int(min(255, v * 1.35) * shadow))
    shade = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    shade.putalpha(halo)
    out = Image.alpha_composite(shade, layer)
    out = out.resize((W, H), Image.LANCZOS)
    out.save(out_path)
    return out_path

# ---------------------------------------------------------------- copy deck
hook_size   = fit_size("Black", "ȚI-A FOST DOR?", SAFE_W * SS, cap=260 * SS)
name_size   = fit_size("Black", "BOGDAN DLP",     SAFE_W * SS, cap=260 * SS)
date_size   = fit_size("Black", "9 OCTUBRE · 22:00", 790 * SS, cap=260 * SS)
venue_size  = fit_size("Bold",  "BRIBÓN DEL PUERTO", 720 * SS, cap=260 * SS)
phone_size  = fit_size("Black", "679 743 114",       620 * SS, cap=260 * SS)
print("sizes /1x:", {k: round(v / SS) for k, v in dict(
    hook=hook_size, name=name_size, date=date_size, venue=venue_size, phone=phone_size).items()})

cards = {}
cards["hook"] = build([
    dict(text="ȚI-A FOST DOR?", weight="Black", size=hook_size, line_h=int(hook_size * 1.0)),
], "card_hook.png")

cards["artist"] = build([
    dict(text="LIVE CU FORMAȚIA", weight="SemiBold", size=32 * SS, tracking=11 * SS,
         alpha=0.94, line_h=int(32 * SS * 1.0)),
    dict(text="BOGDAN DLP", weight="Black", size=name_size, gap_before=int(26 * SS),
         line_h=int(name_size * 1.0)),
], "card_artist.png", shadow=0.46)

cards["date"] = build([
    dict(text="9 OCTUBRE · 22:00", weight="Black", size=date_size, line_h=int(date_size * 1.0)),
], "card_date.png")

cards["venue"] = build([
    dict(text="BRIBÓN DEL PUERTO", weight="Bold", size=venue_size, line_h=int(venue_size * 1.0)),
    dict(text="AGUADULCE, ALMERÍA", weight="SemiBold", size=39 * SS, tracking=7 * SS,
         alpha=0.94, gap_before=int(26 * SS), line_h=int(38 * SS * 1.0)),
], "card_venue.png")

cards["cta"] = build([
    dict(text="INFORMACIÓN Y RESERVAS", weight="SemiBold", size=32 * SS, tracking=10 * SS,
         alpha=0.94, line_h=int(32 * SS * 1.0)),
    dict(text="679 743 114", weight="Black", size=phone_size, gap_before=int(26 * SS),
         line_h=int(phone_size * 1.0)),
], "card_cta.png")

# ---------------------------------------------------------------- DOR logo
logo = Image.open("dor_logo.png")
LOGO_H = 41                                    # small, discreet
LOGO_W = round(LOGO_H * logo.width / logo.height)   # original proportions kept
logo_s = logo.resize((LOGO_W, LOGO_H), Image.LANCZOS)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
layer.alpha_composite(logo_s, ((W - LOGO_W) // 2, 250))
a = layer.getchannel("A")
halo = a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(min(255, v * 1.3) * 0.38))
shade = Image.new("RGBA", layer.size, (0, 0, 0, 0)); shade.putalpha(halo)
Image.alpha_composite(shade, layer).save("card_logo.png")
print("logo placed:", LOGO_W, "x", LOGO_H, "aspect kept:",
      round(LOGO_W / LOGO_H, 4), "vs", round(logo.width / logo.height, 4))
print("cards:", sorted(cards))
