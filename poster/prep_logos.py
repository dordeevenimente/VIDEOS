# Turns the supplied white-on-black logos into white-on-transparent PNGs.
# Artwork is untouched: luminance becomes alpha, fill stays pure white.
from PIL import Image, ImageOps
import os
D = os.path.join(os.path.dirname(__file__), "assets")

def to_alpha(img, black=18, white=235):
    g = ImageOps.grayscale(img)
    a = g.point(lambda v: 0 if v <= black else 255 if v >= white else int((v - black) * 255 / (white - black)))
    out = Image.new("RGBA", img.size, (255, 255, 255, 0))
    out.putalpha(a)
    return out.crop(a.getbbox())

lf = Image.open(f"{D}/lafabrica_source.jpg").convert("RGB")
to_alpha(lf).save(f"{D}/lafabrica.png")

cat = Image.open(f"{D}/catcape_source.jpg").convert("RGB")
cat = cat.resize((cat.width * 4, cat.height * 4), Image.LANCZOS)
to_alpha(cat, black=40, white=200).save(f"{D}/catcape.png")
