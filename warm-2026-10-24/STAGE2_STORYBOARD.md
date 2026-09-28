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
