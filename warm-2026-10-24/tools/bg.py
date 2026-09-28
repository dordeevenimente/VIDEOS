"""Build the graded background plate from the licensed Adobe Stock clips.

env: STOCK_DIR (folder with <id>.mov), JUST2_SRC (artist footage), FFMPEG (optional),
     OUT_DIR (default build/)
"""
import os
import subprocess

from timeline import FPS, SHOTS, W, H

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
STOCK = os.environ["STOCK_DIR"]
OUT = os.environ.get("OUT_DIR", "build")

# Reference-magenta grade: pull saturation, push R/B against G, lift blacks, soften.
GRADE = (
    "eq=saturation=0.55:contrast=1.05:brightness={br}",
    "colorbalance=rs=0.30:gs=-0.18:bs=0.18:rm=0.25:gm=-0.15:bm=0.12:rh=0.10:gh=-0.02:bh=0.08",
    "curves=all='0/0.04 0.5/0.47 1/0.93'",
    "gblur=sigma=0.8",
)
# The artist footage is lit teal: strip most colour first, then tint into the same magenta.
GRADE_JUST2 = (
    "eq=saturation=0.12:contrast=1.08:brightness={br}",
    "colorbalance=rs=0.38:gs=-0.22:bs=0.22:rm=0.32:gm=-0.2:bm=0.16:rh=0.12:gh=-0.04:bh=0.1",
    "curves=all='0/0.04 0.5/0.47 1/0.93'",
    "gblur=sigma=0.6",
)
# Per-shot exposure trims so the cut sequence reads as one night.
BRIGHT = {"799935911": 0.0, "518355395": -0.01, "767667938": -0.03,
          "517066238": 0.04, "757067874": -0.06}
BRIGHT_JUST2 = {15.75: -0.10, 7.35: -0.08, 17.95: -0.15}


def main():
    os.makedirs(OUT, exist_ok=True)
    parts = []
    for i, (t0, t1, sid, src_in, xoff) in enumerate(SHOTS):
        n = round(t1 * FPS) - round(t0 * FPS)
        if sid == "just2":
            src = os.environ["JUST2_SRC"]
            # cover 9:16 from 4:5, choosing where the crop window sits horizontally
            fit = [f"scale=-2:{H}:flags=lanczos", f"crop={W}:{H}:(iw-{W})*{xoff}:0"]
            grade, br = GRADE_JUST2, 0.0 + BRIGHT_JUST2.get(src_in, 0.0)
        else:
            src = os.path.join(STOCK, f"{sid}.mov")
            fit = [f"scale={W}:{H}:flags=lanczos"]
            grade, br = GRADE, -0.02 + BRIGHT.get(sid, 0.0)
        vf = ",".join([f"fps={FPS}", *fit, *grade]).format(br=br)
        out = os.path.join(OUT, f"shot{i}.mp4")
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                        "-ss", str(src_in), "-i", src,
                        "-vf", vf, "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "8", "-pix_fmt", "yuv420p", out], check=True)
        parts.append(out)
    lst = os.path.join(OUT, "shots.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in parts)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
                    "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(OUT, "bg.mp4")], check=True)


if __name__ == "__main__":
    main()
