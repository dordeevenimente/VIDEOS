# -*- coding: utf-8 -*-
"""Montaj reclamă mese Bribón del Puerto · Bogdan DLP (1080×1920, 30 fps, max 20 s).

1. taie fiecare plan din sursă, îl stabilizează ușor, îl accelerează și îl aduce la 1080×1920;
2. aplică același grade pe toate planurile;
3. lipește planurile cap la cap (tăieturi pe ritm) și pune straturile de text (cards/*.png);
4. audio: piesa din MUSIC (dacă există), altfel liniște.

Rulare:  python3 video_bribon/build.py      (cu SRC_DIR = folderul cu .MOV-urile)
"""
import os, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
FF = os.environ.get("FFMPEG", "ffmpeg")
SRC = os.environ.get("SRC_DIR", ".")
MUSIC = os.environ.get("MUSIC", "")           # ex: piesa.mp3
MUSIC_START = float(os.environ.get("MUSIC_START", "0"))
FPS = 30


def src(name):
    hits = glob.glob(os.path.join(SRC, f"*{name}*"))
    if not hits:
        raise SystemExit(f"lipsește sursa {name} în {SRC}")
    return hits[0]


# Piesa: Bogdan DLP – Hazolina, 89.1 BPM (o bătaie = 0.6734 s). Montajul începe pe primul timp al
# refrenului (0:35.36) și fiecare tăietură cade pe o bătaie.
BEAT = 60 / 89.1

# plan: (id, fișier sursă, start în sursă [s], durată în montaj [s], viteză, card text)
SHOTS = [
    ("01_usi",     "IMG_7155", 0.30, 3 * BEAT, 1.10, "hook"),   # ușile cu logo Bribón se deschid
    ("02_afis",    "afis_9x16.png", 0, 4 * BEAT, 1.00, None),   # afișul evenimentului, zoom lent
    ("03_ring",    "IMG_7154", 8.00, 3 * BEAT, 1.00, "gold"),   # de la balcon: ringul cu mesele + DJ
    ("04_masa",    "IMG_7156", 9.00, 3 * BEAT, 1.20, "plat"),   # masă de marmură, prima linie
    ("05_sofa",    "IMG_7154", 0.00, 3 * BEAT, 1.10, "vip"),    # canapeaua roșie de la etaj, lângă geamul spre ring
    ("06_prive",   "4042378073717630682", 12.2, 4 * BEAT, 1.10, "prive"),  # interior Platinum Privé
    ("07_balcon",  "IMG_7154", 6.00, 3 * BEAT, 1.10, "bal"),    # masă la balcon, cu vedere spre ring
    ("08_final",   "IMG_7152", 0.00, 20.0 - 23 * BEAT, 0.80, "end"),  # toate pachetele + rezervare
]

GRADE = (
    "eq=contrast=1.09:saturation=1.08:brightness=-0.01:gamma=0.97,"
    "curves=master='0/0 0.12/0.08 0.5/0.5 0.85/0.9 1/1',"
    "colorbalance=rh=0.03:gh=0.01:bh=-0.03:rm=0.01,"
    "unsharp=5:5:0.45:5:5:0,"
    "vignette=a=PI/7"
)


def cut(shot):
    sid, name, ss, dur, speed, _ = shot
    out = os.path.join(HERE, "seg", sid + ".mp4")
    if name.endswith(".png"):                       # imagine fixă: zoom lent 1.00 → 1.07
        nf = int(round(dur * FPS))
        vf = (f"scale=2160:3840,zoompan=z='1+0.07*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":d={nf}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p")
        subprocess.run([FF, "-y", "-loglevel", "error", "-i", os.path.join(HERE, name), "-vf", vf,
                        "-frames:v", str(nf), "-c:v", "libx264", "-preset", "medium", "-crf", "14", out], check=True)
        return out
    src_len = dur * speed + 0.4
    vf = (
        f"deshake=rx=32:ry=32:edge=mirror,"
        f"setpts=(PTS-STARTPTS)/{speed},fps={FPS},"
        f"scale=1166:2072:flags=lanczos,crop=1080:1920,"   # zoom 8% (ascunde marginile stabilizării)
        f"{GRADE},setsar=1,format=yuv420p"
    )
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(ss), "-t", f"{src_len:.2f}",
                    "-i", src(name), "-an", "-vf", vf, "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "14", out], check=True)
    return out


def main():
    segs = [cut(s) for s in SHOTS]
    total = sum(s[3] for s in SHOTS)

    inputs, parts = [], []
    for p in segs:
        inputs += ["-i", p]
    n = len(segs)
    parts.append("".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[base]")

    # straturi de text: apar cu fade + urcare de 18 px, dispar puțin înainte de tăietură
    t, prev = 0.0, "base"
    for i, s in enumerate(SHOTS):
        sid, _, _, dur, _, card = s
        if card is None:
            t += dur
            continue
        idx = len([x for x in inputs if x == "-i"])
        inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", os.path.join(HERE, "cards", card + ".png")]
        tin = t + 0.12
        tout = t + dur - (0.0 if card == "end" else 0.10)
        fo = "" if card == "end" else f",fade=t=out:st={tout - 0.22:.3f}:d=0.22:alpha=1"
        parts.append(f"[{idx}:v]format=rgba,fade=t=in:st={tin:.3f}:d=0.30:alpha=1{fo}[c{i}]")
        y = f"18*pow(1-clip((t-{tin:.3f})/0.45\\,0\\,1)\\,2)"
        parts.append(f"[{prev}][c{i}]overlay=x=0:y='{y}':eval=frame:enable='between(t\\,{t:.3f}\\,{tout:.3f})'[v{i}]")
        prev = f"v{i}"
        t += dur
    parts.append(f"[{prev}]fade=t=out:st={total - 0.35:.3f}:d=0.35,format=yuv420p[vout]")

    a_idx = len([x for x in inputs if x == "-i"])
    if MUSIC:
        inputs += ["-ss", str(MUSIC_START), "-i", MUSIC]
        parts.append(f"[{a_idx}:a]atrim=0:{total:.3f},afade=t=in:d=0.04,afade=t=out:st={total - 0.8:.3f}:d=0.8[aout]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        parts.append(f"[{a_idx}:a]anull[aout]")

    out = os.path.join(HERE, "out", "bribon_mese_bogdan_dlp_1080x1920.mp4")
    subprocess.run([FF, "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
                    "-t", f"{total:.3f}", "-r", str(FPS),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", out], check=True)
    print(out, f"{total:.2f}s")


if __name__ == "__main__":
    main()
