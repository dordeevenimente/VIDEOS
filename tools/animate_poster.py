import subprocess, sys
import numpy as np, cv2

SRC = sys.argv[1]; MASK = sys.argv[2]; OUT = sys.argv[3]
FPS, DUR = 30, 10.0
N = int(FPS * DUR)

img = cv2.imread(SRC).astype(np.float32) / 255.0
H, W = img.shape[:2]

# ---- foreground mask: artist + all white text/logos ----
person = cv2.imread(MASK, 0).astype(np.float32) / 255.0
mn = img.min(axis=2); mx = img.max(axis=2)
text = ((mn > 0.62) & (mx - mn < 0.18)).astype(np.uint8)
text[:, :] *= 1
text = cv2.dilate(text, np.ones((7, 7), np.uint8)).astype(np.float32)
fg = np.maximum(person, text)
fg = cv2.GaussianBlur(fg, (0, 0), 1.5)
fg = np.clip(fg * 1.15, 0, 1)
fgb = (fg > 0.05).astype(np.uint8)

# clean background plate (only revealed by small parallax offsets)
plate8 = cv2.inpaint((img * 255).astype(np.uint8), cv2.dilate(fgb, np.ones((25, 25), np.uint8)), 9, cv2.INPAINT_TELEA)
plate = plate8.astype(np.float32) / 255.0

# motion weight: zero at the subject/text, ramps up away from them
dist = cv2.distanceTransform(1 - fgb, cv2.DIST_L2, 5)
wmot = np.clip(dist / 140.0, 0, 1)
wmot = wmot * wmot * (3 - 2 * wmot)

# highlight map of the bright swirl ribbons
lum = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
hl = np.clip((lum - 0.18) / 0.35, 0, 1) ** 1.3

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
CX, CY = 640.0, 600.0                      # heart of the swirl
dx, dy = xx - CX, yy - CY
r = np.sqrt(dx * dx + dy * dy) + 1e-3
th = np.arctan2(dy, dx)

BEAT = 60.0 / 124.0 * 2                    # half-time 124 BPM pulse

def ease(t):
    return t * t * (3 - 2 * t)

def pulse(t):
    p = 0.0
    k = np.floor(t / BEAT)
    for j in (k, k - 1):
        dt = t - j * BEAT
        if dt >= 0:
            p += np.exp(-dt / 0.33)
    return min(p, 1.0)

def scale_about_center(im, s, border):
    M = np.float32([[s, 0, (1 - s) * W / 2], [0, s, (1 - s) * H / 2]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=border)

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                       '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p',
                       '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)

rng = np.random.default_rng(7)
fg3 = fg[..., None]
for i in range(N):
    t = i / FPS
    u = t / DUR
    # 3D-ish swirl: differential twist (inner turns more) + slow global drift
    twist = 0.075 * np.sin(2 * np.pi * t / 6.5) + 0.02 * u
    ang = twist * np.exp(-r / 520.0) + 0.012 * np.sin(2 * np.pi * t / 10.0)
    # flowing ripple along the ribbons, travelling outward
    rip = 5.0 * np.sin(r / 38.0 - 2 * np.pi * t / 2.2 + th * 2)
    nr = r + rip * wmot
    nth = th - ang * wmot
    mapx = (CX + nr * np.cos(nth)).astype(np.float32)
    mapy = (CY + nr * np.sin(nth)).astype(np.float32)
    bg = cv2.remap(plate, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    hlw = cv2.remap(hl, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # light pulses: kick envelope + wave travelling outward through the ribbons
    p = pulse(t)
    band = 0.5 + 0.5 * np.cos(r / 85.0 - 2 * np.pi * t / 1.7)
    breathe = 0.5 + 0.5 * np.sin(2 * np.pi * t / 4.0)
    gain = 1.0 + (0.30 * p + 0.10 * breathe) * hlw * (0.55 + 0.45 * band)
    bg = bg * gain[..., None]
    small = cv2.resize(bg * hlw[..., None], (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    glow = cv2.resize(cv2.GaussianBlur(small, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR)
    bg = bg + glow * (0.18 + 0.30 * p) * np.float32([0.55, 0.75, 1.0])  # warm (BGR) glow
    bg = bg * (0.93 + 0.07 * breathe)

    # slow camera push-in with parallax (subject layer moves more than background)
    e = ease(u)
    bgs = scale_about_center(bg, 1.0 + 0.045 * e, cv2.BORDER_REFLECT)
    s_fg = 1.0 + 0.08 * e
    fgs = scale_about_center(img, s_fg, cv2.BORDER_REFLECT)
    m = scale_about_center(fg, s_fg, cv2.BORDER_CONSTANT)[..., None]
    out = bgs * (1 - m) + fgs * m

    # vignette breathing + subtle grain
    vig = 1 - 0.28 * ((dx / (W * 0.75)) ** 2 + (dy / (H * 0.7)) ** 2) * (0.9 + 0.1 * breathe)
    out = out * vig[..., None]
    grain = rng.normal(0, 0.012, (H // 2, W // 2)).astype(np.float32)
    out = out + cv2.resize(grain, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]

    # fade in / fade out
    fade = min(1.0, t / 0.8, (DUR - t) / 0.6)
    out = np.clip(out * max(fade, 0.0), 0, 1)
    ff.stdin.write((out * 255 + 0.5).astype(np.uint8).tobytes())
    if i % 30 == 0:
        print('frame', i, flush=True)

ff.stdin.close(); ff.wait()
cv2.imwrite(OUT.replace('.mp4', '_fgmask.png'), (fg * 255).astype(np.uint8))
