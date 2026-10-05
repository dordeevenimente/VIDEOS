"""Invitaciones DOR · BOGDAN DLP — PDFs listos para imprenta.

Por invitado genera:
  invitacion_100x150_<NOMBRE>.pdf   3 páginas (portada, ilustración, carta), 100 × 150 mm,
                                    sangrado 3 mm + marcas de corte, TrimBox/BleedBox definidos
  sobre_DL_220x110_<NOMBRE>.pdf     2 páginas (anverso con nombre, solapa con logo),
                                    sin sangrado: se imprime sobre sobre ya fabricado

Todo en CMYK nativo (sin RGB), fuentes incrustadas, ilustración a >300 ppp.
"""
import os
import subprocess
import unicodedata

import numpy as np
from PIL import Image
from reportlab.lib.colors import CMYKColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
ART = os.path.join(ROOT, "assets", "invitacion")
OUT = os.environ.get("OUT_DIR", os.path.join(ROOT, "print"))

GUESTS = [
    ("DANIEL SALCEDO", 1),
    ("JOSÉ JUAN RUBÍ", 2),
    ("ALEXANDRINA GORDON", 3),
    ("ILIE VÍCTOR GORDON", 4),
]

# ---- colour (CMYK 0..1) ----------------------------------------------------
GOLD_V = (0.18, 0.38, 0.90, 0.12)   # oro impreso en cuatricromía (~RGB 160/120/44)
CREAM_V = (0.00, 0.02, 0.08, 0.00)  # fondo marfil
INK_V = (0.00, 0.00, 0.00, 0.88)    # texto: sólo negro, sin riesgo de registro
GOLD, CREAM, INK = CMYKColor(*GOLD_V), CMYKColor(*CREAM_V), CMYKColor(*INK_V)
REG = CMYKColor(1, 1, 1, 1)         # registro, sólo para marcas de corte

# ---- geometry ---------------------------------------------------------------
BLEED = 3 * mm
MARK_ZONE = 10 * mm                 # zona fuera del sangrado para las marcas
CARD_W, CARD_H = 100 * mm, 150 * mm
FRAME_OUT, FRAME_IN = 5.0 * mm, 6.3 * mm   # marco doble, a >= 5 mm del corte


def font(name, file):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, file)))


font("EB", "EBGaramond-400.ttf")
font("EB-I", "EBGaramond-400i.ttf")
font("EB-M", "EBGaramond-500.ttf")
font("EB-B", "EBGaramond-700.ttf")
font("EB-SB", "EBGaramond-600.ttf")
font("CG-M", "CormorantGaramond-500.ttf")
font("CG-MI", "CormorantGaramond-500i.ttf")
font("CG-SB", "CormorantGaramond-600.ttf")


# ---- drawing helpers (coords: mm from top-left of trim box) ----------------
class Page:
    def __init__(self, c, w, h, ox, oy):
        self.c, self.w, self.h, self.ox, self.oy = c, w, h, ox, oy

    def y(self, top_mm):
        return self.oy + self.h - top_mm * mm

    def x(self, left_mm):
        return self.ox + left_mm * mm

    def text(self, s, top_mm, fnt, size, color=INK, track=0.0, max_w_mm=None):
        """Centred text with optional tracking (em); baseline at top_mm."""
        c = self.c
        width = lambda sz: pdfmetrics.stringWidth(s, fnt, sz) + track * sz * (len(s) - 1)
        if max_w_mm:
            while width(size) > max_w_mm * mm:
                size -= 0.1
        w = width(size)
        t = c.beginText()
        t.setFont(fnt, size)
        t.setCharSpace(track * size)
        t.setFillColor(color)
        t.setTextOrigin(self.ox + (self.w - w) / 2, self.y(top_mm))
        t.textOut(s)
        c.drawText(t)

    def divider(self, top_mm, half_mm=22, gap_mm=2.6, d_mm=1.0):
        c, cx, y = self.c, self.ox + self.w / 2, self.y(top_mm)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.5)
        c.line(cx - half_mm * mm, y, cx - gap_mm * mm, y)
        c.line(cx + gap_mm * mm, y, cx + half_mm * mm, y)
        c.setFillColor(GOLD)
        p = c.beginPath()
        p.moveTo(cx, y + d_mm * 1.35 * mm); p.lineTo(cx + d_mm * mm, y)
        p.lineTo(cx, y - d_mm * 1.35 * mm); p.lineTo(cx - d_mm * mm, y); p.close()
        c.drawPath(p, stroke=0, fill=1)

    def frame(self, out_mm, in_mm):
        c = self.c
        c.setStrokeColor(GOLD)
        for inset, lw in ((out_mm, 0.9), (in_mm, 0.35)):
            c.setLineWidth(lw)
            c.rect(self.ox + inset, self.oy + inset, self.w - 2 * inset, self.h - 2 * inset)

    def logo(self, centre_top_mm, width_mm):
        d = LOGO
        s = width_mm * mm / LOGO_BOX[2]
        h = LOGO_BOX[3] * s
        self.c.saveState()
        self.c.translate(self.ox + self.w / 2 - width_mm * mm / 2 - LOGO_BOX[0] * s,
                         self.y(centre_top_mm) - h / 2 - LOGO_BOX[1] * s)
        self.c.scale(s, s)
        renderPDF.draw(d, self.c, 0, 0)
        self.c.restoreState()


def load_logo():
    d = svg2rlg(os.path.join(ART, "dor_logo.svg"))

    def paint(node):
        for ch in getattr(node, "contents", []):
            paint(ch)
        if hasattr(node, "fillColor"):
            node.fillColor = GOLD
            node.strokeColor = None
    paint(d)
    x0, y0, x1, y1 = d.getBounds()
    return d, (x0, y0, x1 - x0, y1 - y0)


LOGO, LOGO_BOX = load_logo()


def crop_marks(c, ox, oy, w, h):
    c.setStrokeColor(REG)
    c.setLineWidth(0.25)
    off, ln = BLEED + 2 * mm, 5 * mm   # empiezan fuera del sangrado
    for x in (ox, ox + w):
        for y, sgn in ((oy, -1), (oy + h, 1)):
            c.line(x, y + sgn * off, x, y + sgn * (off + ln))
    for y in (oy, oy + h):
        for x, sgn in ((ox, -1), (ox + w, 1)):
            c.line(x + sgn * off, y, x + sgn * (off + ln), y)


# ---- illustration -> CMYK raster (gold ink over cream, exact cream background) -
def illustration_cmyk(idx):
    src = np.asarray(Image.open(os.path.join(ART, f"ilustracion_{idx}.png")).convert("RGB")).astype(np.float32)
    h, w, _ = src.shape
    # paper colour = bright median of the top rows (empty sky)
    bg = np.median(src[: max(4, h // 25)].reshape(-1, 3), axis=0)
    gold_rgb = np.array([160.0, 120.0, 44.0])
    v = bg - gold_rgb
    t = ((bg - src) @ v) / (v @ v)          # cantidad de "tinta oro" por píxel
    t = np.clip(t, 0, 1.35)
    t = np.where(t < 0.05, 0, (t - 0.05) / 0.95 * (1 + 0.05 * (t > 1)))  # fondo limpio = crema exacta
    # suave fundido en el borde superior para que no se note el corte
    fade = np.clip(np.arange(h) / (h * 0.06), 0, 1)[:, None]
    t = t * fade
    cream, gold = np.array(CREAM_V), np.array(GOLD_V)
    base = np.clip(t, 0, 1)[..., None]
    cmyk = cream * (1 - base) + gold * base
    cmyk[..., 3] += np.clip(t - 1, 0, None) * 0.9   # trazos más oscuros que el oro: un poco de K
    cmyk = np.clip(cmyk, 0, 1)
    return Image.fromarray((cmyk * 255 + 0.5).astype(np.uint8), "CMYK")


# ---- pages -------------------------------------------------------------------
def card_page(c, draw, guest, illus, marks=True):
    ox = oy = (MARK_ZONE if marks else 0) + BLEED
    pw, ph = CARD_W + 2 * ox, CARD_H + 2 * oy
    c.setPageSize((pw, ph))
    # TrimBox / BleedBox (PDF/X)
    c.setTrimBox((ox, oy, ox + CARD_W, oy + CARD_H))
    c.setBleedBox((ox - BLEED, oy - BLEED, ox + CARD_W + BLEED, oy + CARD_H + BLEED))
    c.setFillColor(CREAM)
    c.rect(ox - BLEED, oy - BLEED, CARD_W + 2 * BLEED, CARD_H + 2 * BLEED, stroke=0, fill=1)
    p = Page(c, CARD_W, CARD_H, ox, oy)
    draw(p, guest, illus)
    p.frame(FRAME_OUT, FRAME_IN)
    if marks:
        crop_marks(c, ox, oy, CARD_W, CARD_H)
    c.showPage()


def portada(p, guest, illus):
    p.logo(54, 66)
    p.text("INVITACIÓN OFICIAL", 80, "CG-SB", 14.5, track=0.16)
    p.text("PRIMERA EDICIÓN", 88.5, "CG-SB", 8.6, track=0.32)
    p.divider(98)
    p.text("9 OCTUBRE 2026", 110, "EB-M", 11.5, track=0.2)
    p.text("BRIBÓN DEL PUERTO · AGUADULCE", 118.5, "CG-SB", 7.0, track=0.24)


def ilustracion(p, guest, illus):
    c = p.c
    p.text("“Música nuestra.", 37, "CG-MI", 19.5)
    p.text("Nuestra gente.”", 45, "CG-MI", 19.5)
    p.divider(53.5, half_mm=16)
    p.text("Una noche que nos acerca", 62, "CG-MI", 13)
    p.text("un poco más a casa.", 68, "CG-MI", 13)
    inner = FRAME_IN + 0.35  # justo dentro del filete interior
    w = CARD_W - 2 * inner
    iw, ih = illus.size
    h = w * ih / iw
    h = min(h, CARD_H - inner - 76 * mm)          # nunca sube por encima del texto
    c.saveState()
    clip = c.beginPath()
    clip.rect(p.ox + inner, p.oy + inner, w, CARD_H - 2 * inner)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawInlineImage(illus, p.ox + inner, p.oy + inner, w, w * ih / iw)
    c.restoreState()


def carta(p, guest, illus):
    p.text(guest, 19.5, "CG-SB", 15.5, track=0.16, max_w_mm=76)
    p.divider(25.5)
    body = [
        ["Es un honor para DOR invitarle a la primera edición",
         "de nuestro proyecto, una iniciativa creada para acercar",
         "la música, la cultura y la comunidad rumana",
         "residente en España."],
        ["Nos encantaría contar con su presencia en esta noche",
         "especial, que marca el inicio de un nuevo punto de encuentro",
         "para la comunidad rumana de Roquetas de Mar, Aguadulce",
         "y la provincia de Almería."],
    ]
    y, lead = 34.0, 4.25
    for para in body:
        for line in para:
            p.text(line, y, "EB", 8.6)
            y += lead
        y += 2.2
    p.text("DOR presenta", 75.5, "EB-M", 8.8, track=0.12)
    p.text("BOGDAN DLP", 87, "EB-SB", 29, color=GOLD, max_w_mm=72)
    p.text("EN DIRECTO CON SU BANDA", 93, "EB-M", 7.6, color=GOLD, track=0.26)
    p.text("9 de octubre de 2026  ·  23:00 h", 101.5, "EB", 11)
    p.text("Bribón del Puerto  ·  Aguadulce", 107.3, "EB", 11)
    p.divider(114)
    p.text("Será un verdadero placer contar con su presencia", 121.5, "EB", 9)
    p.text("en la primera edición de DOR.", 125.9, "EB", 9)
    p.text("Se ruega confirmación de asistencia.", 132.3, "EB", 9)
    p.text("Equipo DOR", 138.6, "EB", 9)


ENV_W, ENV_H = 220 * mm, 110 * mm


def sobre(c, guest):
    for side in ("anverso", "solapa"):
        c.setPageSize((ENV_W, ENV_H))
        c.setTrimBox((0, 0, ENV_W, ENV_H))
        c.setBleedBox((0, 0, ENV_W, ENV_H))
        p = Page(c, ENV_W, ENV_H, 0, 0)
        if side == "anverso":
            p.frame(9 * mm, 10.3 * mm)
            p.text(guest, 57, "CG-SB", 19, track=0.18, max_w_mm=150)
            p.divider(65, half_mm=26)
        else:
            # logo centrado sobre la solapa en pico (DL, solapa ~ 45 mm)
            p.logo(20, 40)
            p.divider(33, half_mm=13)
        c.showPage()


def finalize(path):
    """Ghostscript prepress: fuentes incrustadas, sin fuentes huérfanas, CMYK intacto, sin recompresión."""
    tmp = path + ".tmp.pdf"
    subprocess.run(["gs", "-q", "-o", tmp, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                    "-dPDFSETTINGS=/prepress", "-sColorConversionStrategy=CMYK",
                    "-dEmbedAllFonts=true", "-dSubsetFonts=true",
                    "-dDownsampleColorImages=false", "-dAutoFilterColorImages=false",
                    "-dColorImageFilter=/FlateEncode", path], check=True)
    os.replace(tmp, path)


def preview(pdf, png, dpi):
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, png[:-4]], check=True)
    pages = sorted(f for f in os.listdir(os.path.dirname(png))
                   if f.startswith(os.path.basename(png)[:-4] + "-"))
    return [os.path.join(os.path.dirname(png), f) for f in pages]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.replace(" ", "_")


def main():
    os.makedirs(OUT, exist_ok=True)
    for n, (guest, idx) in enumerate(GUESTS, 1):
        d = os.path.join(OUT, f"{n:02d}_{slug(guest)}")
        os.makedirs(d, exist_ok=True)
        illus = illustration_cmyk(idx)
        for marks, suffix in ((True, ""), (False, "_sin_marcas")):
            c = canvas.Canvas(os.path.join(d, f"invitacion_100x150_{slug(guest)}{suffix}.pdf"),
                              initialFontName="EB")
            c.setTitle(f"Invitación DOR · {guest}"); c.setAuthor("DOR")
            for draw in (portada, ilustracion, carta):
                card_page(c, draw, guest, illus, marks)
            c.save()
            finalize(c._filename)
        c = canvas.Canvas(os.path.join(d, f"sobre_DL_220x110_{slug(guest)}.pdf"), initialFontName="EB")
        c.setTitle(f"Sobre DOR · {guest}"); c.setAuthor("DOR")
        sobre(c, guest)
        c.save()
        finalize(c._filename)
        # prueba visual (no es para imprenta)
        cards = preview(os.path.join(d, f"invitacion_100x150_{slug(guest)}_sin_marcas.pdf"),
                        os.path.join(d, "_c.png"), 120)
        env = preview(os.path.join(d, f"sobre_DL_220x110_{slug(guest)}.pdf"), os.path.join(d, "_e.png"), 60)
        ims = [Image.open(f).convert("RGB") for f in cards + env]
        gap = 30
        top_w = sum(i.width for i in ims[:3]) + gap * 4
        bot_w = sum(i.width for i in ims[3:]) + gap * 3
        W = max(top_w, bot_w)
        H = ims[0].height + max(i.height for i in ims[3:]) + gap * 3
        sheet = Image.new("RGB", (W, H), (226, 222, 214))
        x = (W - top_w) // 2 + gap
        for im in ims[:3]:
            sheet.paste(im, (x, gap)); x += im.width + gap
        x = (W - bot_w) // 2 + gap
        for im in ims[3:]:
            sheet.paste(im, (x, ims[0].height + 2 * gap)); x += im.width + gap
        sheet.save(os.path.join(d, f"PRUEBA_{slug(guest)}.jpg"), quality=88)
        for f in cards + env:
            os.remove(f)
        print("ok", d)


if __name__ == "__main__":
    main()
