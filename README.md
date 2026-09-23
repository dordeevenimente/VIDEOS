# DOR · BOGDAN DLP — Bribón del Puerto, 9 octombrie

Reclamă verticală (Meta Ads / Instagram Reels / Stories / Facebook Stories) construită
peste materialul live original, fără nicio modificare structurală a imaginii sau a sunetului.

## Livrabil

`out/bogdan_dlp_bribon_9oct_1080x1920.mp4` — master, 1080 × 1920 (9:16), 29.97 fps,
H.264 High, yuv420p, ~10.8 Mbps, audio AAC copiat bit-cu-bit din sursă (48 MB).

`out/bogdan_dlp_bribon_9oct_1080x1920_light.mp4` — aceeași montare, ~5 Mbps (22 MB),
pentru trimis prin WhatsApp / e-mail sau upload rapid. Meta re-encodează oricum la upload.

## Ce s-a păstrat intact

- toate cadrele sursei, în ordinea originală, la viteza originală;
- durata identică cu originalul (36.64 s);
- primul și ultimul frame provin din videoclipul original — fără intro, outro, freeze-frame,
  fade-to-black sau ecran negru;
- coloana sonoră originală, stream-copiată (`-c:a copy`): PCM-ul decodat are exact același
  md5 ca sursa (`5062891a5bd3f3ab4bff915f94b8bd17`), deci audio-ul este intact și sincronizat;
- finalul sursei conține un fade-to-black propriu (ultimele ~2.5 s); a fost păstrat ca atare,
  logo-ul DOR rămâne pe ecran până la ultimul frame.

Verificat după export: 1098 frame-uri sursă → 1098 frame-uri export, aliniere temporală
offset 0 (corelație 0.993), zero cadre duplicate (fără freeze).

## Ce s-a adăugat

**Color grading** — contrast cinematic, S-curve blând, echilibru de culoare cald pe mid-tonuri
(pentru tonuri naturale ale pielii sub lumina de scenă), vibrance moderat, bloom discret pe
highlight-uri, sharpening subtil, vignetă foarte slabă.

**Tipografie** — o singură familie, Inter Display, ierarhie din greutate / corp / tracking.
Text crem `#F8F5F1` (culoarea logo-ului DOR), fără efecte decorative pe litere; doar o umbră
difuză, aproape invizibilă, pentru lizibilitate. Animație: fade + urcare de 12 px cu easing.

**Storytelling** (in/out snapate pe accentele muzicale din piesa originală):

| # | Mesaj | In | Out |
|---|---|---|---|
| 1 | ȚI-A FOST DOR? | 0.50 s | 4.83 s |
| 2 | LIVE CU FORMAȚIA / BOGDAN DLP | 6.50 s | 11.63 s |
| 3 | 9 OCTUBRE · 22:00 | 14.65 s | 18.99 s |
| 4 | BRIBÓN DEL PUERTO / AGUADULCE, ALMERÍA | 21.08 s | 25.43 s |
| 5 | INFORMACIÓN Y RESERVAS / 679 743 114 | 28.31 s | 33.72 s |
| — | logo DOR (sus, discret) | 26.38 s | final |

Toate blocurile sunt centrate pe x și ancorate optic la y ≈ 1300 px: sub fața artistului
(y ≈ 400–650) și deasupra zonei de UI Instagram, în interiorul safe zone-ului
(x 120–960, ferit de coloana de butoane din dreapta).

**Branding** — logo-ul oficial DOR, folosit ca asset blocat: doar decupat de pe fundalul negru
și scalat la 131 × 41 px, cu proporțiile originale (3.196) păstrate.

## Reproducere

```sh
export SRC=source.mp4                 # clipul original, neatins
export INTER_DIR=inter/extras/ttf     # familia Inter Display

python3 tools/prep_logo.py     # logo DOR → PNG transparent
python3 tools/make_cards.py    # straturile tipografice
python3 tools/render.py        # grade + compoziție + export
```

Dependențe: `ffmpeg` (7.x, cu libx264), `Pillow`, `numpy`, familia de fonturi Inter Display.

---

# DOR · Carusel Instagram „Dor de…” (feed 1080 × 1350)

`out/ig_dor/dor_ig_{1..6}_1080x1350.jpg` — cele 6 vizualuri, mesajele originale neschimbate.

- **Text** centrat pe ambele axe (bloc titlu + ornament + subtitlu, centrat optic pe y = 675).
- **Look nostalgic**: negru „mat” ridicat (print decolorat), split-tone chihlimbar/sepia,
  halation pe lumini, vignetă, light leak cald, grain de film, praf și zgârieturi fine,
  ramă subțire crem ca la o fotografie developată; logo DOR discret, jos.
- **Tipografie**: o singură familie, Inter (OFL, `assets/fonts/Inter.ttf`) — titlul
  are „DOR” (brandul) ExtraBold, restul Light; subtitluri Medium, majuscule,
  tracking larg; linie aurie `#C9A048` sub text; culoare crem cald `#F6EAD4`.

```sh
python3 tools/clean_bg.py            # șterge textul vechi din imaginile sursă (assets/ig_dor_src)
python3 tools/make_ig_nostalgic.py   # grade + tipografie → out/ig_dor
```
