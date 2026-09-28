"""Composite the WARM 24.10.26 promo: graded plate + typographic system + soundtrack.

env: FONT_DIR (Inter extras/ttf), TRACK (supplied WAV), BG (plate from bg.py),
     ASSETS (warm_logo.png, bribon_lettering.png, just2_logo.png — official logos),
     OUT (mp4 path), FFMPEG (optional), POSTER (optional png of the last frame)

All information sits inside Meta's Reels safe zone (14 % top, 35 % bottom, 6 % sides kept clear).
"""
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from timeline import (AUDIO_IN, BAR, BEAT, BUILD, DROP, DURATION, FPS, FRAMES, H,
                      INFO1, INFO2, INFO3, INTRO, LAYER, NAME2, NAME3, RIFF1, RIFF2,
                      SUCK, W)

# snap every event to a frame so cuts, exposure and type change on the same frame
_q = lambda x: round(x * FPS) / FPS  # noqa: E731
BUILD, SUCK, DROP, NAME2, NAME3, RIFF1, INFO1, INFO2, INFO3, RIFF2, LAYER = map(
    _q, (BUILD, SUCK, DROP, NAME2, NAME3, RIFF1, INFO1, INFO2, INFO3, RIFF2, LAYER))

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FONT_DIR = os.environ["FONT_DIR"]

MINT = np.array([168, 240, 207], np.float32)
SILVER = np.array([206, 208, 210], np.float32)
WHITE = np.array([246, 244, 240], np.float32)
HAZE = np.array([206, 204, 200], np.float32)

SUPPORT = ["SALVI FERNANDEZ", "CORAL", "BITCH"]  # given order, all caps as requested
DATE = "24 OCTOBER 2026"
TIME = "23:00 – 07:00"
TOWN = "AGUADULCE"
ASSETS = os.environ["ASSETS"]

SAFE_TOP, SAFE_BOT = 270, 1250  # Meta Reels: 14 % top / 35 % bottom free of text


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"InterDisplay-{weight}.ttf"), size)


def clamp01(x):
    return max(0.0, min(1.0, x))


class Line:
    """One line of type rendered to a mask, with per-letter column spans for decode."""

    def __init__(self, text, weight, size, cy, tracking=0.0, cx=W / 2, color=MINT, seed=0):
        self.color = color
        f = font(weight, size)
        track = tracking * size
        xs = [f.getlength(text[:i]) + i * track for i in range(len(text) + 1)]
        width = xs[-1] - track
        asc, desc = f.getmetrics()
        pad = int(size * 0.25)
        self.w, self.h = int(width) + 2 * pad, asc + desc + 2 * pad
        img = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(img)
        for i, ch in enumerate(text):
            d.text((pad + xs[i], pad), ch, font=f, fill=255)
        self.mask = np.asarray(img, np.float32) / 255.0
        # soft dark halo for legibility over bright footage
        self.halo = np.asarray(img.filter(ImageFilter.GaussianBlur(size * 0.14)), np.float32) / 255.0
        # visible-cap centre -> placement
        hb = f.getbbox("H")
        top, cap = pad + hb[1], hb[3] - hb[1]
        self.x0 = int(round(cx - self.w / 2))
        self.y0 = int(round(cy - (top + cap / 2)))
        self.spans = [(int(pad + xs[i]), int(pad + xs[i + 1])) for i in range(len(text))]
        rng = random.Random(f"{text}-{seed}")
        self.order = [rng.random() for _ in text]
        self.text = text

    def column_alpha(self, reveal):
        """reveal in [0,1] -> per-column visibility (letters switch on in random order)."""
        col = np.zeros(self.w, np.float32)
        for (a, b), r, ch in zip(self.spans, self.order, self.text):
            if ch != " " and r < reveal:
                col[a:b] = 1.0
        # let the last glyph's overhang through
        if reveal >= 1.0:
            col[:] = 1.0
        return col


def comp(frame, line, alpha, reveal=1.0, color=None):
    if alpha <= 0.003 or reveal <= 0.0:
        return
    col = line.column_alpha(reveal)[None, :] * alpha
    m = line.mask * col
    x0, y0 = line.x0, line.y0
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + line.w), min(H, y0 + line.h)
    if xa >= xb or ya >= yb:
        return
    sl = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
    m = m[sl][..., None]
    c = line.color if color is None else color
    reg = frame[ya:yb, xa:xb]
    reg *= 1 - 0.4 * np.minimum(1, 1.6 * (line.halo * col)[sl][..., None])
    reg += (c - reg) * m


class Marquee:
    """Endless line of large regular type scrolling at constant speed."""

    def __init__(self, phrase, size, cy, speed, direction, seed=0):
        f = font("Regular", size)
        unit = f.getlength(phrase)
        reps = int((W + abs(speed) * DURATION) / unit) + 3
        text = phrase * reps
        asc, desc = f.getmetrics()
        img = Image.new("L", (int(f.getlength(text)) + 8, asc + desc + 20), 0)
        ImageDraw.Draw(img).text((4, 10), text, font=f, fill=255)
        self.mask = np.asarray(img, np.float32) / 255.0
        cap = f.getbbox("H")
        self.y0 = int(round(cy - (10 + cap[1] + (cap[3] - cap[1]) / 2)))
        self.speed, self.dir, self.unit = speed, direction, unit
        self.h = self.mask.shape[0]

    def comp(self, frame, t, alpha):
        if alpha <= 0.003:
            return
        off = (self.speed * t) % self.unit
        x = int(off) if self.dir < 0 else int(self.unit - off)
        m = self.mask[:, x:x + W]
        ya, yb = max(0, self.y0), min(H, self.y0 + self.h)
        m = m[ya - self.y0:yb - self.y0, :, None] * alpha
        # silver -> mint metallic gradient in screen space, drifting slowly
        g = 0.5 + 0.5 * np.sin(np.linspace(0, np.pi * 2, W) + t * 1.3)
        col = SILVER[None, :] * (1 - g[:, None]) + MINT[None, :] * g[:, None]
        reg = frame[ya:yb]
        reg += (col[None, :, :] - reg) * m


class Logo:
    """Official logo sprite: scaled uniformly, colours untouched, faded/flickered only."""

    def __init__(self, name, width, cy, cx=W / 2):
        im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255.0
        self.rgb, self.a = a[..., :3] * 255.0, a[..., 3:]
        self.halo = (np.asarray(im.getchannel("A").filter(ImageFilter.GaussianBlur(h * 0.18)),
                                np.float32) / 255.0)[..., None]
        self.x0, self.y0 = int(round(cx - width / 2)), int(round(cy - h / 2))
        self.w, self.h = width, h

    def comp(self, frame, alpha):
        if alpha <= 0.003:
            return
        reg = frame[self.y0:self.y0 + self.h, self.x0:self.x0 + self.w]
        reg *= 1 - 0.35 * np.minimum(1, 1.6 * self.halo * alpha)
        reg += (self.rgb - reg) * (self.a * alpha)


def fit_size(texts, weight, max_w, start):
    s = start
    while s > 20 and max(font(weight, s).getlength(t) for t in texts) > max_w:
        s -= 2
    return s


def ramp(t, t0, dur):
    return clamp01((t - t0) / dur) if dur > 0 else float(t >= t0)


def flicker(t, t0, frames=(0.35, 1, 0.45, 1, 0.6, 1)):
    k = int(round((t - t0) * FPS))
    return frames[k] if 0 <= k < len(frames) else 1.0


# ---------------------------------------------------------------- layout
SAFE_W = 880
stamp_top = Logo("warm_logo.png", 150, 318)
stamp_bot = Logo("bribon_lettering.png", 170, 1195)

mq_top = Marquee(f"WARM  ·  {DATE}  ·  ", 128, 560, 240, +1)
mq_bot = Marquee(f"BRIBÓN DEL PUERTO  ·  {TOWN}  ·  ", 128, 930, 240, -1)

# lineup: JUST2 alone and large over his own front-view footage, then the full bill
head_big = Logo("just2_logo.png", 640, 1030)
head_small = Logo("just2_logo.png", 440, 460)
ss = fit_size(SUPPORT, "Black", 760, 84)
support = [Line(n, "Black", ss, 620 + k * ss * 1.22, seed=3 + k) for k, n in enumerate(SUPPORT)]
support_t = [NAME3, NAME3 + 2 * BEAT, RIFF1]

info_date = Line(DATE, "Black", 96, 430)
info_time = Line(TIME, "Black", 96, 545)
info_venue = Logo("bribon_lettering.png", 340, 715)
info_town = Line(TOWN, "SemiBold", 40, 855, tracking=0.5, color=WHITE)

# end card — the poster
end_org = Logo("warm_logo.png", 560, 400)
end_head = Logo("just2_logo.png", 440, 600)
es = fit_size(SUPPORT, "Black", 640, 64)
end_support = [Line(n, "Black", es, 730 + k * es * 1.25, seed=11 + k) for k, n in enumerate(SUPPORT)]
end_when = Line(f"{DATE}  ·  {TIME}", "SemiBold", 40, 1000, tracking=0.04, color=WHITE)
end_venue = Logo("bribon_lettering.png", 250, 1108)
end_town = Line(TOWN, "SemiBold", 30, 1212, tracking=0.5, color=WHITE)

DECODE = BEAT  # letters switch on over one beat

rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 3.5, (H, W, 1)).astype(np.float32) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = (1 - 0.16 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2)[..., None]


# soft dark band behind the info block (hazy footage there)
SCRIM = (1 - 0.34 * np.exp(-(((np.arange(H, dtype=np.float32) - 640) / 300) ** 2)))[:, None, None]


def exposure(t):
    if t < INTRO + 0.5:
        return 0.55 + 0.45 * ramp(t, INTRO, 0.5)
    if SUCK <= t < DROP:
        return 0.16 + 0.1 * ramp(t, SUCK, DROP - SUCK)
    if t >= RIFF2:
        return 1.0 - 0.42 * ramp(t, RIFF2, 0.6)  # settle darker under the end card
    return 1.0


def render_frame(bg, i):
    t = i / FPS
    f = bg.astype(np.float32) * exposure(t)

    # haze whiteout into the end card
    if RIFF2 <= t < RIFF2 + 0.7:
        a = 0.88 * np.exp(-(t - RIFF2) / 0.18)
        f += (HAZE - f) * a

    # frame stamps (official logos) — until the end card; venue stamp yields to the big venue line
    s_a = 0.92 * ramp(t, 0.1, 0.4) * (1 - ramp(t, RIFF2, 0.2))
    stamp_top.comp(f, s_a)
    stamp_bot.comp(f, s_a * (1 - ramp(t, INFO3, 0.15)))

    # intro + build marquees
    if t < SUCK:
        a = 0.72 if t < BUILD else 0.95
        if t >= BUILD + BEAT:  # 1/8-note strobe through the riser
            a *= 1.0 if int((t - BUILD) / (BEAT / 2)) % 2 == 0 else 0.5
        a *= ramp(t, INTRO, 0.25)
        mq_top.comp(f, t, a)
        mq_bot.comp(f, t, a)

    # JUST2 alone on the drop (2 bars of his front-view footage)
    if DROP <= t < NAME3:
        head_big.comp(f, ramp(t, DROP, DECODE / 2))

    # full bill: JUST2 on top, support acts decode in, stack flickers on the riff
    if NAME3 <= t < INFO1:
        out = (1 - ramp(t, INFO1 - 0.15, 0.15)) * flicker(t, RIFF1)
        head_small.comp(f, out)
        for ln, t0 in zip(support, support_t):
            comp(f, ln, out, ramp(t, t0, DECODE))

    # date / time / venue — one per bar
    if INFO1 <= t < RIFF2:
        f *= 1 - (1 - SCRIM) * ramp(t, INFO1, 0.1) * (1 - ramp(t, RIFF2 - 0.1, 0.1))
        comp(f, info_date, 1.0, ramp(t, INFO1, DECODE))
        comp(f, info_time, 1.0, ramp(t, INFO2, DECODE))
        info_venue.comp(f, ramp(t, INFO3, DECODE / 2))
        comp(f, info_town, 1.0, ramp(t, INFO3 + BEAT, DECODE))

    # end card — doubles as the poster (last frame)
    if t >= RIFF2:
        end_org.comp(f, ramp(t, RIFF2 + 0.05, DECODE / 2) * flicker(t, LAYER))
        end_head.comp(f, ramp(t, RIFF2 + BEAT, DECODE / 2))
        for k, ln in enumerate(end_support):
            comp(f, ln, 1.0, ramp(t, RIFF2 + 1.5 * BEAT + k * BEAT / 2, DECODE))
        comp(f, end_when, 1.0, ramp(t, RIFF2 + 3 * BEAT, DECODE))
        end_venue.comp(f, ramp(t, RIFF2 + 3.5 * BEAT, DECODE / 2))
        comp(f, end_town, 1.0, ramp(t, RIFF2 + 4 * BEAT, DECODE))

    f *= VIGNETTE
    f += GRAIN[(i // 2) % len(GRAIN)]
    return np.clip(f, 0, 255).astype(np.uint8)


def main():
    bg = subprocess.Popen([FFMPEG, "-v", "error", "-i", os.environ["BG"], "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([
        FFMPEG, "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", os.environ["TRACK"],
        "-filter_complex",
        f"[1:a]atrim=start={AUDIO_IN:.6f}:duration={DURATION:.6f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={DURATION - BEAT:.6f}:d={BEAT:.6f}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M", "-bufsize", "24M", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", os.environ["OUT"]], stdin=subprocess.PIPE)
    size = W * H * 3
    last = None
    for i in range(FRAMES):
        raw = bg.stdout.read(size)
        if len(raw) < size:
            raw = last
        last = raw
        frame = render_frame(np.frombuffer(raw, np.uint8).reshape(H, W, 3), i)
        enc.stdin.write(frame.tobytes())
        if os.environ.get("POSTER") and i == FRAMES - 1:
            Image.fromarray(frame).save(os.environ["POSTER"])
    enc.stdin.close()
    enc.wait()
    bg.stdout.close()
    bg.wait()


if __name__ == "__main__":
    main()
