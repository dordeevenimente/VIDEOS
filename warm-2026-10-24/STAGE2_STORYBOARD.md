# WARM × Bribón del Puerto — 24.10.2026
## Stage 2: Storyboard and animation spec

Approved in Stage 1 / footage: reference-magenta palette, Inter Display, equal-weight lineup in the
given order, date as `24 OCTOBER 2026`, audio section 1.393 → 24.070 s of the WAV, DJ-from-behind shot kept.
The video **replaces the poster**, so the last frame is designed as a standalone poster.

### Global specs
- 1080 × 1920, 30 fps, 680 frames = 22.667 s. H.264 High yuv420p (CRF 16) + AAC 320 kbps, 48 kHz.
- Audio: the supplied WAV, trimmed only (`atrim` from 1.392719 s), with a 1-beat (0.472 s) fade on the last beat. No tempo, pitch or edit changes.
- Grid: 127 BPM, 1 beat = 0.4724 s, 1 bar = 1.8898 s (= 56.7 frames). Every cut and every text entrance starts on a grid frame.
- Safe area for information: x 100–980, y 260–1480. Only the decorative marquees bleed off-frame.

### Type system (Inter Display)
| Role | Weight / size | Colour | Motion |
|---|---|---|---|
| Frame stamp | Regular 34 px (`WARM`, +0.9 em) at y 292 / Regular 30 px (`BRIBÓN DEL PUERTO`, +0.6 em) at y 1462 | silver `#CED0D2` @ 90 % | random-letter decode, present until the end card |
| Marquee | Regular 176 px (intro) / 150 px (info section) | silver ↔ mint metallic gradient, drifting | constant-speed scroll, top line L→R, bottom line R→L, 286 / 240 px/s |
| Headline | Black, auto-fitted to 880 px (all 4 names share one size) | mint `#A8F0CF` | random-letter decode over 1 beat; 6-frame flicker on accents |
| Info | Black (date/time), SemiBold 62 / 44 px (venue / town) | mint / warm white `#F6F4F0` | decode over 1 beat |
| End card | `WARM` Black 230 px (**placeholder wordmark**), names Black auto-fitted to 720 px, info SemiBold 50 / 38 px | white / mint | staggered decode, 1/8 note apart |

### Timeline
| Video time | Frames | Music (WAV time) | Picture | Type |
|---|---|---|---|---|
| 0.00 – 3.78 | 0–113 | Intro, 2 bars (1.39–5.17) | Stock 799935911: dark moving heads. Opens at 55 % exposure → 100 % in 0.5 s | Stamps decode in (0.15 s / 0.30 s). Marquees `WARM · 24 OCTOBER 2026` (L→R, y 640) and `BRIBÓN DEL PUERTO · AGUADULCE` (R→L, y 1190) at 72 % from frame 1, as the hook |
| 3.78 | 113 | **Build** starts (5.17) | Hard cut → 518355395 crossed violet beams | Marquees up to 95 % |
| 4.25 – 4.72 | 128–141 | Riser peak | — | Marquees strobe on 1/8 notes (100 % / 50 %) |
| 4.72 | 142 | **Suck-out**: highs vanish (6.12) | Exposure drops to 16 % (eyes closing) | Marquees cut out; stamps alone |
| **5.67** | **170** | **KICK DROP** (7.06) | Hard cut → 767667938 DJ from behind, crowd, magenta | **JUST2** decodes (1 beat), at the top of a 4-line stack centred at y 1080, below the DJ's head |
| 7.56 | 227 | Bar | — | **Salvi Fernandez** decodes (line 2) |
| 9.45 | 283 | Bar | — | **CORAL** decodes (line 3) |
| **11.34** | **340** | **Riff / stab** (12.73) | Hard cut → 517066238 crowd silhouettes, hands up | **BITCH** decodes; the whole stack flickers for 6 frames (35/100/45/100/60/100 %) |
| 13.08 – 13.23 | 392–397 | — | — | Lineup dissolves (0.15 s) |
| 13.23 | 397 | Bar (14.62) | Hard cut → 757067874 hands on the mixer | `24 OCTOBER 2026` decodes (y 880). Marquees return at 38 % (y 560 / 1340) |
| 15.12 | 454 | Bar | — | `23:00 – 07:00` decodes below |
| 17.01 | 510 | Bar | — | `BRIBÓN DEL PUERTO` decodes (y 1180), `AGUADULCE` one beat later (y 1262) |
| **18.90** | **567** | **Riff / stab** (20.29) | Hard cut → 518355395 beams + **haze whiteout** (88 % pale grey, decaying over 0.5 s); plate settles to 58 % | Stamps and info cut. `WARM` wordmark decodes (y 560) |
| 19.37 – 20.31 | 581–609 | — | — | Names decode one per 1/8 note (y 820 → 1142), then date, time, `BRIBÓN DEL PUERTO · AGUADULCE` |
| 20.79 | 624 | New layer enters (22.18) | — | 6-frame flicker on `WARM` |
| 20.79 – 22.67 | 624–679 | Groove | End card holds | **Poster frame**, with every item readable |
| 22.67 | 680 | Downbeat (24.07) | Loop point | Reel loops back to the intro |

### Assets and placeholders
- `WARM` in Inter Display Black is **temporary type**, not the logo. In Stage 3 the official logo replaces the end-card wordmark and the top stamp, at its original proportions. The layout will be adapted to the logo, not the logo to the layout.
- `BRIBÓN DEL PUERTO` is set in type. It can be swapped for the venue logo in the bottom stamp and end card if you supply one.
- No artist imagery. The DJ in 767667938 is anonymous and seen from behind; no name is placed over his head.

### Reproduction
```sh
export STOCK_DIR=…/stock            # Adobe Stock <id>.mov files (see footage/FOOTAGE.md)
export FONT_DIR=…/inter/extras/ttf  # Inter 4.1
python3 tools/bg.py                 # graded background plate -> build/bg.mp4
BG=build/bg.mp4 TRACK=…/JUST2_Close_Your_Eyes.wav OUT=out.mp4 POSTER=poster.png python3 tools/render.py
```

---

## v2: official logos, JUST2 footage, Meta safe zone (28.09.2026)

- **Logos** (in `assets/`, from `assets/source/`), used as supplied, never recoloured or reshaped, only scaled:
  - `warm_logo.png` (red, already transparent, only trimmed): top stamp 150 px wide, end card 560 px.
  - `just2_logo.png` (white): alone at 640 px on the drop, 440 px on top of the full bill and on the end card.
  - `bribon_lettering.png`: **only the lettering** of the Bribón del Puerto logo (emblem and background left out, as requested). Used as the bottom stamp (170 px), in the info section (340 px) and on the end card (250 px).
- **Hierarchy:** JUST2 is the headliner (logo, larger). SALVI FERNANDEZ, CORAL and BITCH follow in the given order, **all caps**, at one smaller size.
- **Meta safe zone:** every piece of information sits between y 270 and 1250 (14 % top / 35 % bottom clear, as for Reels ads). Type is smaller: supports are auto-fitted to 760 px, date/time 96 px, end-card supports 64 px.
- **Footage:** the artist's own video (`assets/source/just2_footage_source.mp4`, 720×900) now carries the drop, the bill and the info section. It is scaled to cover 9:16 with a per-shot horizontal crop, and colour-stripped then tinted into the same magenta as the stock shots. Stock remains for the intro, the build and under the end card.

| Video | Shot |
|---|---|
| 0.00–3.78 | stock 799935911 (dark) |
| 3.78–5.67 | stock 518355395 (beams) |
| 5.67–7.56 | JUST2 front view at the booth, his name lit behind him (src 1.10 s): **JUST2 logo** |
| 7.56–9.45 | JUST2 front view, second take (src 4.40 s) |
| 9.45–11.34 | JUST2 from behind, facing the crowd (src 22.55 s): SALVI FERNANDEZ, then CORAL |
| 11.34–13.23 | full room in haze (src 15.75 s): BITCH plus a flicker on the riff |
| 13.23–17.01 | JUST2 from behind (src 7.35 s): date, time |
| 17.01–18.90 | lasers over the crowd (src 17.95 s): Bribón lettering, AGUADULCE |
| 18.90–22.67 | stock 518355395 + whiteout: end card / poster |

- A soft dark band behind the info block keeps the date and time legible over the hazy shots.

---

## v3: centred, Spanish, simpler story (client feedback 28.09.2026)

Feedback: the layout had no logic and was not centred, the WARM logo should be white and smaller, the copy should be in Spanish, and the Bribón logo should appear only at the end.

- One idea per scene, every block centred on the frame (and still inside y 270–1250):
  1. 0.00–4.72 **WARM** (white, 300 px) + `PRESENTA`, strobing through the riser; black on the suck-out.
  2. 5.67–9.45 **JUST2 logo** alone (620 px) over his front-view footage.
  3. 9.45–13.23 `SALVI FERNANDEZ` → `CORAL` → `BITCH` (white, stacked), flicker on the riff; haze and lasers footage.
  4. 13.23–18.90 `24 OCTUBRE 2026` → `23:00 – 07:00` → `AGUADULCE`; stock mixer, then crowd.
  5. 18.90–22.67 poster: WARM (white, 230 px), JUST2 logo, support acts, date · time, **Bribón lettering (only here)**, AGUADULCE.
- Removed: scrolling marquees, permanent top/bottom stamps.
- The WARM logo is shown in white (the client asked for it); shape and proportions are untouched.

---

## v4: WARM × UNDER THE SUN, light ending (client feedback 28.09.2026)

- Organisers: **WARM × UNDER THE SUN**. The intro is one centred row: WARM (white) · × · Under The Sun lettering (white, lifted from `assets/source/under_the_sun_source.jpg`, a 150 px source, upscaled), then `PRESENTAN`.
- The ending no longer repeats all the information: it shows only the **Bribón del Puerto lettering** + `AGUADULCE`.
- The intro and build play over the violet-beams clip (dark centre), so no stage light sits behind the logos.

---

## v5: back to the reference grammar (client feedback 28.09.2026)

- `PRESENTAN` removed.
- Restored from the reference reel, kept centred and inside the Meta zone:
  - two large regular-weight lines, `24 OCTUBRE 2026 · AGUADULCE`, scrolling in opposite directions behind the headline (y 735 / 1185; 75 % in the intro, 42 % behind the names), off during the suck-out and before the ending;
  - support acts and date/time in heavy mint type with the random-letter reveal, and a flicker on the riff;
  - a small organisers stamp at the top (WARM × UNDER THE SUN, white), in the role KOKUN plays in the reference;
  - the ending: the venue logo alone, white and centred (Bribón lettering + AGUADULCE), as the KOKUN® end card does.

---

## v6: every piece of text once (client feedback 28.09.2026)

The same text was repeating (the date/town in the scrolling lines and again in the centre; the organisers in the intro and again as a stamp). Now each item appears exactly once:

| Video | Text |
|---|---|
| 0.00–4.72 | WARM × UNDER THE SUN |
| 5.67–9.45 | JUST2 logo |
| 9.45–13.23 | SALVI FERNANDEZ · CORAL · BITCH |
| 13.23–18.90 | `24 OCTUBRE 2026` only as the two opposite scrolling lines (reference grammar); `23:00 – 07:00` alone in the centre |
| 18.90–22.67 | Bribón del Puerto + AGUADULCE |

The top stamp and the always-on scrolling lines are removed.

---

## v7: built on the final poster (client, 28.09.2026)

The client supplied the final poster (`assets/source/final_poster.png`). The video now uses its copy and its identity.

- **Copy (from the poster, each item once):** WARM · JUST2 / SOLID GROOVES · SALVI FERNANDEZ, DANI CORRAL, LADY SASHA (the lineup changed from CORAL/BITCH) · SÁB 24 OCTUBRE · 23:00H — 07:00H · BRIBÓN del puerto · PENÍNSULA DE CONTRADIQUE, 04720 / AGUADULCE (ALMERÍA) · INFO & RESERVAS · 679 743 114. Under The Sun is not on the poster, so it is not in the video.
- **Look:** black ground; the poster's orange-to-red topographic rings, generated procedurally, drifting outward and pulsing on every kick after the drop (1/8-note pulse on the riser, near-dark on the suck-out). JUST2's footage is monochrome warmed to orange, shown in a soft central window like the poster's portrait. White type.
- **Type:** Barlow Condensed ExtraBold for the names (poster's condensed bold); Montserrat Light/Bold for `SÁB 24 OCTUBRE`; Montserrat SemiBold/Medium for the hours, address and bookings (fonts from Fontsource via npm).
- **Motion kept from the reference:** random-letter decode, flicker on accents, cuts on the kick.

| Video | Picture | Text |
|---|---|---|
| 0.00–4.72 | rings | WARM (white) |
| 5.67–9.45 | JUST2 front view ×2 | JUST2 logo, `— SOLID GROOVES —` |
| 9.45–13.23 | haze, lasers | SALVI FERNANDEZ → DANI CORRAL → LADY SASHA |
| 13.23–17.01 | rings | SÁB **24 OCTUBRE**, then 23:00H — 07:00H |
| 17.01–22.67 | rings | Bribón del Puerto; at 18.90 the address, then INFO & RESERVAS · 679 743 114 |
