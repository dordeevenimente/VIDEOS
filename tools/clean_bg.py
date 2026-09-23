# -*- coding: utf-8 -*-
"""Removes the baked-in text from the source IG visuals (cream type on warm bokeh).
Text pixels = bright + low saturation inside the text band; inpainted, then softened."""
import cv2, numpy as np, os, sys
SRC = os.environ.get("IG_SRC", "assets/ig_dor_src")
OUT = os.environ.get("IG_CLEAN", "build/ig_clean")
os.makedirs(OUT, exist_ok=True)
# text band (y0, y1) in source pixels, per visual
BANDS = {1: (360, 690), 2: (230, 630), 3: (300, 710), 4: (240, 610),
         5: (250, 625), 6: (270, 655)}
SPOTS = {4: [(780, 226, 34, 26)]}
for i, (y0, y1) in BANDS.items():
    im = cv2.imread(f"{SRC}/{i}.webp")
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    m = ((hsv[..., 2] > 150) & (hsv[..., 1] < 90)).astype(np.uint8) * 255
    band = np.zeros_like(m); band[y0:y1, 60:1070] = 255
    m = cv2.bitwise_and(m, band)
    m = cv2.dilate(m, np.ones((3, 3), np.uint8), iterations=4)
    for (x, y, w, h) in SPOTS.get(i, []):          # stray artefacts in the source
        m[y:y + h, x:x + w] = 255
    out = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
    # soften the whole text band so no letter ghosts remain (it sits behind new type anyway)
    soft = cv2.GaussianBlur(out, (0, 0), 14)
    w = np.zeros(m.shape, np.float32); w[y0:y1, :] = 1
    w = cv2.GaussianBlur(w, (0, 0), 40)[..., None]
    out = (out * (1 - w) + soft * w).astype(np.uint8)
    cv2.imwrite(f"{OUT}/{i}.png", out)
    cv2.imwrite(f"{OUT}/{i}_mask.png", m)
print("ok")
