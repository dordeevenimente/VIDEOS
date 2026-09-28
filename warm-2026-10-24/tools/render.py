"""Composite the WARM · JUST2 promo (24.10.2026) on the identity of the final poster.

Look: black ground, glowing orange/red contour lines (animated, pulsing on the kick), the artist's
footage graded warm inside a soft central window, white type. Motion keeps the reference reel's
grammar: letters switch on in random order, flicker on accents, cuts on the kick.
All copy comes from the final poster and each item is shown once. Everything sits centred and
inside Meta's Reels safe zone (y 270-1250).

env: FONT_DIR (woff files: barlow-condensed-latin-800, montserrat-latin-300/500/600/700),
     ASSETS (warm_logo.png, just2_logo.png, bribon_lettering.png), TRACK (supplied WAV),
     BG (plate from bg.py), OUT (mp4 path), FFMPEG (optional), POSTER (optional png, last frame)
"""
import os
import random
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

from timeline import (AUDIO_IN, BEAT, BUILD, DROP, DURATION, FPS, FRAMES, H, INFO1, INFO2,
                      INFO3, INTRO, LAYER, NAME2, NAME3, RIFF1, RIFF2, SUCK, W)

# snap every event to a frame so cuts, pulses and type change on the same frame
_q = lambda x: round(x * FPS) / FPS  # noqa: E731
BUILD, SUCK, DROP, NAME2, NAME3, RIFF1, INFO1, INFO2, INFO3, RIFF2, LAYER = map(
    _q, (BUILD, SUCK, DROP, NAME2, NAME3, RIFF1, INFO1, INFO2, INFO3, RIFF2, LAYER))

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FONT_DIR = os.environ["FONT_DIR"]
ASSETS = os.environ["ASSETS"]

WHITE = np.array([246, 244, 240], np.float32)
SOFT = np.array([214, 206, 200], np.float32)
WHITE_RGB = (246, 244, 240)

# ---- copy, exactly as on the final poster
SUBTITLE = "SOLID GROOVES"
SUPPORT = ["SALVI FERNANDEZ", "DANI CORRAL", "LADY SASHA"]
DAY, DATE = "SÁB", "24 OCTUBRE"
HOURS = "23:00H  —  07:00H"
ADDRESS = ["PENÍNSULA DE CONTRADIQUE, 04720", "AGUADULCE (ALMERÍA)"]
BOOKING = "INFO & RESERVAS  ·  679 743 114"

FONTS = {
    "cond": "barlow-condensed-latin-800-normal.woff",
    "light": "montserrat-latin-300-normal.woff",
    "medium": "montserrat-latin-500-normal.woff",
    "semi": "montserrat-latin-600-normal.woff",
    "bold": "montserrat-latin-700-normal.woff",
}


def font(face, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[face]), size)


def clamp01(x):
    return max(0.0, min(1.0, x))


def ramp(t, t0, dur):
    return clamp01((t - t0) / dur) if dur > 0 else float(t >= t0)


def flicker(t, t0, frames=(0.35, 1, 0.45, 1, 0.6, 1)):
    k = int(round((t - t0) * FPS))
    return frames[k] if 0 <= k < len(frames) else 1.0


def text_width(text, face, size, tracking=0.0):
    f = font(face, size)
    return f.getlength(text) + max(0, len(text) - 1) * tracking * size


class Line:
    """One line of type rendered to a mask, with per-letter column spans for the decode."""

    def __init__(self, text, face, size, cy, tracking=0.0, cx=W / 2, color=WHITE, seed=0):
        self.color, self.text = color, text
        f = font(face, size)
        track = tracking * size
        xs = [f.getlength(text[:i]) + i * track for i in range(len(text) + 1)]
        width = xs[-1] - track
        asc, desc = f.getmetrics()
        pad = int(size * 0.3)
        self.w, self.h = int(width) + 2 * pad, asc + desc + 2 * pad
        img = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(img)
        for i, ch in enumerate(text):
            d.text((pad + xs[i], pad), ch, font=f, fill=255)
        self.mask = np.asarray(img, np.float32) / 255.0
        self.halo = np.asarray(img.filter(ImageFilter.GaussianBlur(size * 0.16)), np.float32) / 255.0
        hb = f.getbbox("H")
        self.x0 = int(round(cx - self.w / 2))
        self.y0 = int(round(cy - (pad + hb[1] + (hb[3] - hb[1]) / 2)))
        self.spans = [(int(pad + xs[i]), int(pad + xs[i + 1])) for i in range(len(text))]
        rng = random.Random(f"{text}-{seed}")
        self.order = [rng.random() for _ in text]

    def column_alpha(self, reveal):
        if reveal >= 1.0:
            return np.ones(self.w, np.float32)
        col = np.zeros(self.w, np.float32)
        for (a, b), r, ch in zip(self.spans, self.order, self.text):
            if ch != " " and r < reveal:
                col[a:b] = 1.0
        return col

    def comp(self, frame, alpha, reveal=1.0):
        if alpha <= 0.003 or reveal <= 0.0:
            return
        col = self.column_alpha(reveal)[None, :] * alpha
        x0, y0 = self.x0, self.y0
        xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + self.w), min(H, y0 + self.h)
        sl = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
        reg = frame[ya:yb, xa:xb]
        reg *= 1 - 0.45 * np.minimum(1, 1.6 * (self.halo * col)[sl][..., None])
        reg += (self.color - reg) * (self.mask * col)[sl][..., None]


class Logo:
    """Official logo sprite: scaled uniformly, faded/flickered only."""

    def __init__(self, name, width, cy, cx=W / 2, fill=None):
        im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
        if fill is not None:  # single-colour version of the mark (shape untouched)
            solid = Image.new("RGBA", im.size, tuple(fill) + (255,))
            solid.putalpha(im.getchannel("A"))
            im = solid
        h = round(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255.0
        self.rgb, self.a = a[..., :3] * 255.0, a[..., 3:]
        self.halo = (np.asarray(im.getchannel("A").filter(ImageFilter.GaussianBlur(h * 0.2)),
                                np.float32) / 255.0)[..., None]
        self.x0, self.y0 = int(round(cx - width / 2)), int(round(cy - h / 2))
        self.w, self.h = width, h

    def comp(self, frame, alpha):
        if alpha <= 0.003:
            return
        reg = frame[self.y0:self.y0 + self.h, self.x0:self.x0 + self.w]
        reg *= 1 - 0.4 * np.minimum(1, 1.6 * self.halo * alpha)
        reg += (self.rgb - reg) * (self.a * alpha)


class Rule:
    """Thin horizontal rule (the poster's dashes around SOLID GROOVES)."""

    def __init__(self, cx, cy, length, thickness=2):
        self.x0, self.x1 = int(cx - length / 2), int(cx + length / 2)
        self.y0, self.y1 = int(cy - thickness / 2), int(cy + thickness / 2) + 1

    def comp(self, frame, alpha, color=SOFT):
        if alpha > 0.003:
            reg = frame[self.y0:self.y1, self.x0:self.x1]
            reg += (color - reg) * alpha


def fit_size(texts, face, max_w, start):
    s = start
    while s > 20 and max(text_width(t, face, s) for t in texts) > max_w:
        s -= 2
    return s


# ---------------------------------------------------------------- contour field (poster)
CX, CY, RX, RY = W / 2, 860.0, 560.0, 820.0
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
R = np.sqrt(((xx - CX) / RX) ** 2 + ((yy - CY) / RY) ** 2)


def smooth_noise(seed, cell, sigma):
    g = np.random.default_rng(seed).normal(size=(H // cell + 2, W // cell + 2)).astype(np.float32)
    g = ndimage.gaussian_filter(g, sigma)
    g = ndimage.zoom(g, cell, order=3)[:H, :W]
    return g / (np.abs(g).max() + 1e-6)


N1, N2 = smooth_noise(3, 32, 2.5), smooth_noise(5, 16, 2.0)
RW = R * (1 + 0.14 * N1 + 0.018 * N2)  # warped rings, like the poster's topography


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


ENV = (smoothstep(0.5, 0.85, R) * (1 - smoothstep(1.1, 1.75, R)) * (0.75 + 0.25 * N2))[..., None]
_mix = smoothstep(0.7, 1.35, R)[..., None]
LINE_COL = (np.array([245, 150, 70], np.float32) * (1 - _mix)
            + np.array([196, 40, 16], np.float32) * _mix)
GLOW = (np.exp(-((R - 0.95) / 0.34) ** 2) * (0.6 + 0.4 * N1))[..., None] \
    * np.array([118, 34, 8], np.float32)
PORTAL = (1 - smoothstep(0.62, 1.05, R))[..., None]  # footage window in the middle
RINGS = 14.0


def contour_gain(t):
    """Brightness of the contour field, driven by the music."""
    if t < BUILD:
        return 0.2 + 0.6 * ramp(t, INTRO, 1.2)
    if t < SUCK:  # 1/8-note pulse through the riser
        return 0.85 if int((t - BUILD) / (BEAT / 2)) % 2 == 0 else 0.55
    if t < DROP:
        return 0.12
    since = (t - DROP) % BEAT  # kick on every beat after the drop
    return 0.7 + 0.55 * np.exp(-since / 0.09)


def contours(t):
    phase = RW * RINGS - t * 0.55  # rings drift outward
    f = phase - np.floor(phase)
    d = np.minimum(f, 1 - f)
    line = np.clip(1 - d / 0.07, 0, 1) ** 1.6
    return LINE_COL * (line[..., None] * ENV) + GLOW


# ---------------------------------------------------------------- layout (all centred)
warm = Logo("warm_logo.png", 380, 960, fill=WHITE_RGB)

just2 = Logo("just2_logo.png", 640, 1030)
sub = Line(SUBTITLE, "medium", 30, 1140, tracking=0.45, color=SOFT)
_sw = text_width(SUBTITLE, "medium", 30, 0.45)
sub_rules = [Rule(W / 2 - _sw / 2 - 70, 1140, 90), Rule(W / 2 + _sw / 2 + 70, 1140, 90)]

ns = fit_size(SUPPORT, "cond", 800, 140)
support = [Line(n, "cond", ns, 960 + (k - 1) * ns * 1.02, seed=k) for k, n in enumerate(SUPPORT)]
support_t = [NAME3, NAME3 + 2 * BEAT, RIFF1]

_ds = 100
_gap = text_width(" ", "bold", _ds)
_dw, _tw = text_width(DAY, "light", _ds), text_width(DATE, "bold", _ds)
_x0 = W / 2 - (_dw + _gap + _tw) / 2
day = Line(DAY, "light", _ds, 935, cx=_x0 + _dw / 2)
date = Line(DATE, "bold", _ds, 935, cx=_x0 + _dw + _gap + _tw / 2)
hours = Line(HOURS, "semi", 46, 1060, tracking=0.08)

venue = Logo("bribon_lettering.png", 420, 900)
address = [Line(a, "medium", 30, 1052 + k * 46, tracking=0.08, seed=20 + k)
           for k, a in enumerate(ADDRESS)]
booking = Line(BOOKING, "medium", 27, 1170, tracking=0.1, color=SOFT)

DECODE = BEAT
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]
VIGNETTE = (1 - 0.2 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2)[..., None]


def render_frame(bg, i):
    t = i / FPS
    f = bg.astype(np.float32) * PORTAL  # footage lives in the central window
    f += contours(t) * contour_gain(t)

    # 1 — WARM
    if t < SUCK:
        a = ramp(t, 0.3, 0.6)
        if t >= BUILD + BEAT:
            a *= 1.0 if int((t - BUILD) / (BEAT / 2)) % 2 == 0 else 0.45
        warm.comp(f, a)

    # 2 — JUST2 · SOLID GROOVES, on the drop
    if DROP <= t < NAME3:
        out = 1 - ramp(t, NAME3 - 0.12, 0.12)
        just2.comp(f, ramp(t, DROP, DECODE / 2) * flicker(t, NAME2) * out)
        r = ramp(t, DROP + BEAT, DECODE)
        sub.comp(f, out, r)
        for rl in sub_rules:
            rl.comp(f, 0.8 * r * out)

    # 3 — support acts, one per step, flicker on the riff
    if NAME3 <= t < INFO1:
        out = (1 - ramp(t, INFO1 - 0.15, 0.15)) * flicker(t, RIFF1)
        for ln, t0 in zip(support, support_t):
            ln.comp(f, out, ramp(t, t0, DECODE))

    # 4 — SÁB 24 OCTUBRE, then the hours
    if INFO1 <= t < INFO3:
        out = 1 - ramp(t, INFO3 - 0.15, 0.15)
        day.comp(f, out, ramp(t, INFO1, DECODE))
        date.comp(f, out, ramp(t, INFO1 + BEAT, DECODE))
        hours.comp(f, out, ramp(t, INFO2, DECODE))

    # 5 — Bribón del Puerto, then the address, then bookings (held to the end)
    if t >= INFO3:
        venue.comp(f, ramp(t, INFO3, DECODE / 2) * flicker(t, LAYER))
        for k, ln in enumerate(address):
            ln.comp(f, 1.0, ramp(t, RIFF2 + k * BEAT, DECODE))
        booking.comp(f, 1.0, ramp(t, RIFF2 + 2.5 * BEAT, DECODE))

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
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M", "-bufsize", "24M",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "320k",
        "-ar", "48000", "-movflags", "+faststart", "-shortest", os.environ["OUT"]],
        stdin=subprocess.PIPE)
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
