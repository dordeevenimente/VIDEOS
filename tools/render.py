# -*- coding: utf-8 -*-
"""Renders the final 1080x1920 cut.
The source video is used frame-for-frame: no cuts, no retiming, no freeze, no
intro/outro. Audio is stream-copied, so it is bit-identical to the original.
Everything added is a grade plus a typographic layer composited on top.
"""
import subprocess, os

FF = os.environ.get("FFMPEG", "ffmpeg")
SRC = os.environ.get("SRC", "source.mp4")   # the untouched original clip
OUT = "bogdan_dlp_bribon_9oct_1080x1920.mp4"
END = 36.637         # exact source length: 1098 frames @ 30000/1001
NFRAMES = 1098       # output is locked to the source frame count

# in / out points snapped to musical onsets in the original soundtrack
CARDS = [
    # file,              t_in,  t_out, fade_in, fade_out, slide_px
    ("card_hook.png",     0.50,  4.83, 0.55, 0.45, 12),
    ("card_artist.png",   6.50, 11.63, 0.55, 0.45, 12),
    ("card_date.png",    14.65, 18.99, 0.50, 0.45, 12),
    ("card_venue.png",   21.08, 25.43, 0.50, 0.45, 12),
    ("card_cta.png",     28.31, 33.72, 0.55, 0.45, 12),
    ("card_logo.png",    26.38, END,   0.80, 0.00,  0),
]

GRADE = (
    "format=gbrp,"
    "eq=contrast=1.07:saturation=1.10:brightness=0.004,"
    "curves=master='0/0 0.10/0.075 0.35/0.35 0.72/0.755 1/1',"
    "colorbalance=rs=-0.012:bs=0.018:rm=0.018:gm=0.004:bm=-0.014:rh=0.008:bh=-0.006,"
    "vibrance=intensity=0.10,"
    "split[bse][blm];"
    "[blm]curves=all='0/0 0.62/0 0.85/0.35 1/1',gblur=sigma=26[bloom];"
    "[bse][bloom]blend=all_mode=screen:all_opacity=0.16,"
    "unsharp=5:5:0.30:5:5:0,"
    "vignette=a=PI/9,"
    "format=gbrp[v0]"
)

parts = [f"[0:v]{GRADE}"]
prev = "v0"
for i, (f, tin, tout, fin, fout, slide) in enumerate(CARDS):
    idx = i + 1
    lbl = f"c{idx}"
    chain = f"[{idx}:v]format=rgba,fade=t=in:st={tin}:d={fin}:alpha=1"
    if fout > 0:
        chain += f",fade=t=out:st={round(tout - fout, 3)}:d={fout}:alpha=1"
    chain += f"[{lbl}]"
    parts.append(chain)
    if slide:
        y = f"{slide}*pow(1-clip((t-{tin})/0.70\\,0\\,1)\\,2)"
    else:
        y = "0"
    nxt = f"v{idx}"
    parts.append(
        f"[{prev}][{lbl}]overlay=x=0:y='{y}':eval=frame:"
        f"enable='between(t\\,{tin}\\,{tout})':format=auto[{nxt}]"
    )
    prev = nxt
parts.append(f"[{prev}]format=yuv420p[vout]")

open("filter.txt", "w").write(";\n".join(parts))

cmd = [FF, "-hide_banner", "-y", "-i", SRC]
for f, tin, tout, fin, fout, slide in CARDS:
    cmd += ["-loop", "1", "-framerate", "30000/1001", "-t", f"{min(tout + 0.3, END):.3f}", "-i", f]
cmd += [
    "-filter_complex_script", "filter.txt",
    "-map", "[vout]", "-map", "0:a",
    "-frames:v", str(NFRAMES),
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p",
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-video_track_timescale", "11988",
    "-c:a", "copy",
    "-movflags", "+faststart",
    OUT,
]
print(" ".join(cmd[:6]), "...")
subprocess.run(cmd, check=True)
# the mp4 muxer drops the final AAC packet when the video stream is frame-limited,
# so the complete original audio track is re-attached verbatim (no video re-encode)
FINAL = "final_" + OUT
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", OUT, "-i", SRC,
                "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
                "-video_track_timescale", "11988", "-movflags", "+faststart", FINAL], check=True)
print("done:", FINAL, os.path.getsize(FINAL) // 1024, "KiB")
