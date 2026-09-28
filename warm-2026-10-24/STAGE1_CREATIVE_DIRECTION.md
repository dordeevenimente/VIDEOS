# WARM × Bribón del Puerto — 24.10.2026
## Stage 1: Research & Creative Direction

Status: **awaiting approval**. No video has been rendered yet.

---

## 0. What was actually analysed (and what was not)

| Input | Status | How |
|---|---|---|
| Reference Reel (`DdEMyA4CPZO`) | **Analysed from the attached MP4** (the savefromins download, 720×1280, 23.976 fps, 22.65 s). I could not open the Instagram link itself because instagram.com is blocked from this environment, so I'm assuming the attached file is that reel. | Frames at 2 fps and 8 fps, full-res stills, scene-cut detection, colour sampling, and the reel's own audio beat-tracked against its cuts |
| Soundtrack `JUST2 - Close Your Eyes` (WAV, 90.88 s, 44.1 kHz stereo) | **Analysed** | Beat tracking, a kick-envelope tempo/phase grid search, and per-beat energy in 5 frequency bands |
| WARM Barcelona (@warmbcn) | **Only partly researched.** instagram.com and warm.productions are blocked here. I have search-result text only, with no posters, logo or colours. | Web search (sources below) |

---

## 1. Reference Reel: analysis

### 1.1 What it actually is
It is **not** a pure motion-graphics piece. It is **live event footage** (DJ booth, crowd, CO2/confetti, haze) under a heavy **magenta/violet grade**, with a typographic layer on top. The footage supplies the atmosphere and the type supplies the identity. This matters for production (see §6, question 1).

### 1.2 Edit and pacing
- Only **5 shots in 22.65 s**. Cuts at 5.26 / 7.26 / 18.81 / 20.73 s.
- The reel's music is about 126 BPM. **Every cut sits on a beat**, 0.1–0.2 s ahead of it, which is the classic "cut into the kick" technique. One shot lasts exactly one bar (5.26 → 7.26). Another holds for about six bars.
- The energy comes from the **type**, not from fast cutting. Long takes plus restless typography reads as confident and premium.

### 1.3 Typography
Four text roles, all set in neo-grotesque or geometric sans, **all caps**:

| Role | Example | Look | Closest identification |
|---|---|---|---|
| **A. Headline** | `MAHMUT ORHAN`, `3H SET`, `SUN. 11 OCT` | Heavy/Black grotesk, tight tracking, 2-line stack, centred, ~9–10 % of frame width per cap | Helvetica Neue 85 Heavy / Neue Haas Grotesk Display Black type |
| **B. Marquee** | `CLOSING PARTY` | Regular weight, very large (cap height ~7 % of frame height), bleeds off both edges | Helvetica / Arial Regular type |
| **C. Info line** | `SILENCIO - TORREMOLINOS` | Bold geometric sans (round O, C, S), small, centred | Montserrat / Gotham Bold type |
| **D. Frame stamp** | `K O K U N` top & bottom | Regular, tiny (~2.3 % of frame height), **extremely wide tracking (~+800)**, at top and bottom like a picture frame | any neutral grotesk |
| End card | `KOKUN®` | Bold grotesk, white, centred, held about 4 s | Helvetica Bold type |

At 720p I can't name the exact commercial fonts with certainty. The random-letter reveal and marquee are also typical of CapCut/After Effects type presets. What *is* certain is the **system**: one heavy grotesk for names, one light/regular grotesk for huge marquee lines, one wide-tracked micro line as a frame.

**Proposed fonts** (free, licence-safe, cover the Spanish glyphs Ó and Í):
- **A / End card:** Inter Display Black (or **Neue Haas Grotesk Display Black** if you or WARM hold a licence; it's the closest to the reference).
- **B:** Inter Display Regular.
- **C / D:** Inter Display SemiBold / Regular, with D at +800 tracking.
- I'd drop the separate geometric face (role C) to keep one family. It is the only element in the reference that looks slightly template-like. If you want it kept 1:1, I'd use Montserrat Bold.

### 1.4 Colour (sampled from frames)
- Footage grade: deep magenta → violet. Background medians range from `#2E0917` (shadows) through `#902E64` (mids) to `#7A1167` (violet). Occasional washed-out, near-white haze frames (`#C2C3BD`) appear at the transitions.
- Type: **mint** `#9CD1C0` (median; the letter cores run brighter, about `#A8F0CF`), plus a **silver → mint metallic gradient** on the marquee, and **white** for the end card only.
- Mint on magenta is the reference's signature complementary contrast.

### 1.5 Motion language
1. **Random-letter decode:** letters of a word pop in individually in random order over about 0.4–0.6 s (`M… MAHMUT… ORHA N`, `3 … ET → 3H SET`). There's no slide or scale; letters are simply switched on.
2. **Opacity flicker:** once set, the headline pulses between full mint and roughly 50 % grey for a few frames, like a strobe echo.
3. **Counter-scrolling marquees:** two copies of `CLOSING PARTY` travel in **opposite directions** (top line left→right, bottom line right→left), crossing the frame in about 2–2.5 s at constant linear speed, partly behind or over the headline.
4. **Exits** are dissolves or letter-off, never slides or wipes.
5. **Transitions** between shots are hard cuts on the beat, plus one **haze whiteout** (footage blown to pale grey) before the end card.
6. No 3D, glitch, glow, particles or neon strokes. It is restrained.

---

## 2. Soundtrack: analysis

**JUST2 – "Close Your Eyes"** (Solid Grooves). Press describes it as a darker, groove-led, late-night cut. The measurements below are from the attached file.

- **Tempo: 127.00 BPM**, locked (grid-search fit on the kick envelope; one beat = 0.4724 s, one bar = 1.8898 s).
  - librosa's default tracker reported 129.2 BPM. That is a known quantisation error; its phase fit is poor, and 127 fits the kicks clearly best.
- **Beat grid:** first kick at **7.062 s**. 8-bar phrases start at 7.06 · 22.18 · 37.30 · 52.42 · 67.54 · 82.65 s.

### Structure of the supplied clip
| Source time | Section | What happens |
|---|---|---|
| 0.00 – 1.39 | Partial intro bar | The cut starts mid-bar |
| 1.39 – 5.17 | Intro, 2 bars | Bass and percussion, no full kick, low level (−7 dB) |
| 5.17 – 6.12 | **Build** | Mids, presence and air all rise (riser/fill) |
| 6.12 – 7.06 | **Suck-out** | Highs vanish (air −10 dB) while the sub swells. Classic tension beat |
| **7.06** | **KICK DROP** | Full groove in. The strongest moment in the clip |
| 7.06 – 81.7 | Groove | Steady kick and bass. A **mid-range stab/riff hits bar 4 of every 4-bar group** (12.73, 20.29, 27.85 …). A new layer enters at 22.18 |
| 81.71 | Kick out | |
| 82.65 – 90.88 | **Breakdown** | Pads/atmosphere only, no kick |

### Recommended section: **source 1.393 s → 24.070 s = 22.68 s = exactly 12 bars**
- It starts on a downbeat and ends on a downbeat (bar 9 of the groove). Tempo, pitch and arrangement are untouched; it is one continuous cut.
- It contains the one real **drop** in the clip, 5.67 s into the video, which is ideal for the lineup reveal.
- It contains two riff accents, at video 11.34 s and 18.90 s, for the full lineup and the final card.
- Instagram loops: the end at a downbeat, going back to the quiet intro, loops seamlessly.
- Only processing: a 1-beat (0.47 s) fade-out at the very end so the loop doesn't click. **Please confirm this is OK.**

Alternative I considered and rejected: 59.98 → 82.65 s (groove into the breakdown). It has no drop, and the kick disappears only 1 bar before the end, so the final card would get too little time.

---

## 3. WARM Barcelona: what I can substantiate

- WARM is a Barcelona promoter of house and techno events. It describes itself as creating "house, techno, and immersive spaces where people and music connect freely" and transforming "unique spaces" into dance experiences. [warm.productions](https://warm.productions/)
- Channels: [Instagram @warmbcn](https://www.instagram.com/warmbcn/) · [Facebook](https://www.facebook.com/warm.barcelona?locale=ka_GE) · listed on [RA Barcelona promoters](https://ra.co/promoters/es/barcelona)
- **I could not see a single WARM poster, logo, colour or font.** Everything below about "WARM identity" is therefore a *conditional* adaptation, and I will not present it as research.

Context:
- **Venue:** Bribón del Puerto is a 3-storey, 2,000 m² leisure complex (restaurants, lounge, nightclub) on the Península de Contradique, Aguadulce marina, opened by Grupo Flavia. [Indisa](https://www.indisa.es/al-dia/bribon-puerto-nuevo-place-to-be-almeria) · [La Voz de Almería](https://www.lavozdealmeria.com/vivir/230425/bribon-vuelve-brillar-puerto-aguadulce.html)
- **Track:** [Undrtone on "Close Your Eyes"](https://www.undrtone.co.uk/post/just2-refines-his-late-night-sound-on-close-your-eyes)

---

## 4. Creative direction (proposal)

### Concept: "CLOSE YOUR EYES" (working title, internal only; it won't appear on screen unless you want it)
The track title suggests the idea: the video **opens nearly dark and hazy, like eyes closing**, and on the kick drop at 5.67 s it **opens into light and names**. The reference's type system becomes a WARM system: the same restraint, the same decode and marquee grammar, and one clear visual signature.

### Visual system
- **Frame stamp (role D):** `W A R M` top and `B R I B Ó N  D E L  P U E R T O` bottom, tiny and wide-tracked, present from frame 1. This is the brand anchor, so the event is recognisable before anything is read. **It is placeholder type, not a logo;** the official WARM logo replaces it in Stage 3.
- **Marquee (role B):** two counter-scrolling lines, `WARM  ·  24 OCTOBER 2026` and `BRIBÓN DEL PUERTO  ·  AGUADULCE`.
- **Names (role A):** heavy grotesk, all four at **identical size, weight and duration**, in the given order, so no hierarchy is implied.
- **Info (role C):** `24 OCTOBER 2026`, `23:00 – 07:00`, `AGUADULCE`.
- **End card:** a WARM placeholder wordmark (white, bold) plus a compact info block.

### Palette: two routes (decide after I've seen WARM's feed)
- **Route 1, "Reference-true":** magenta/violet grade + mint `#A8F0CF` / silver type + white end card. Closest to the reference.
- **Route 2, "WARM":** a warmer grade (deep oxblood → amber highlights, soft haze) with the **same mint/silver type**. That keeps the reference's complementary contrast and gives the red–amber base a reason. **I will only choose this if WARM's actual materials support it.**

### Motion
The reference grammar only: random-letter decode (0.45 s, 1 beat), a 3-frame opacity flicker on accents, linear counter-scrolling marquees (1 screen width per 2 bars), dissolve exits, hard cuts on kicks, and one haze whiteout before the end card. No glitch, neon, particles, 3D or zooms.

### Sync map (video time; 1 bar = 1.89 s)
| Video | Music | Picture / type |
|---|---|---|
| 0.00 – 3.78 | Intro, 2 bars | Dark, hazy footage. Frame stamp decodes in. Marquees drift at 40 % opacity |
| 3.78 – 4.72 | Build | Marquees reach full opacity, micro-flicker every 1/8 note |
| 4.72 – 5.67 | Suck-out | Everything drops out to near-black and haze. Tension |
| **5.67** | **KICK DROP** | Hard cut to peak footage. **JUST2** decodes |
| 7.56 | bar | **Salvi Fernandez** decodes below |
| 9.45 | bar | **CORAL** |
| 11.34 | **riff** | **BITCH**; the stack completes and the full lineup flickers on the stab |
| 13.23 – 18.90 | groove, 3 bars | Cut on the kick. `24 OCTOBER 2026` → `23:00 – 07:00` → `BRIBÓN DEL PUERTO · AGUADULCE` (one per bar, same decode) |
| 18.90 | **riff** | Haze whiteout, then the **end card**: WARM + lineup + date/time + venue |
| 20.79 | New layer enters | End card holds; subtle marquee return |
| 22.68 | Downbeat | Loop point |

Stage 2 will make this second-by-second, with exact frames.

### Format and safe areas (1080 × 1920)
Essential text stays inside **x 90–960, y 260–1480**. That leaves the Instagram/TikTok top bar, the caption/CTA area (bottom ~440 px) and the right-hand button column (~120 px) clear. Marquees may bleed off the edges because they are decorative; all information is repeated in safe static text.

---

## 5. Production plan

Rendering is done in code: a Python frame compositor with ffmpeg/libx264. Output is H.264 High, yuv420p, 1080×1920, 25 or 30 fps, with **your WAV encoded to AAC 320 kbps**, unaltered apart from the trim and the 1-beat tail fade. I can render a real MP4 concept preview in Stage 2.

---

## 6. Decisions I need from you

1. **Footage (blocking).** The reference is built on real event footage, and I won't generate AI crowds or artists. Options:
   - **a)** You send WARM or Bribón del Puerto event footage: crowd, booth, lights, venue, vertical if possible, about 6–10 clips of 3–8 s. **Recommended: this is what makes it look like the reference.**
   - **b)** Type-only version on non-figurative textures made in code (haze, grain, light leaks in the chosen grade). It's cleaner but departs from the reference.
   - **c)** Licensed stock club footage. It's generic, so I don't recommend it.
2. **WARM visuals:** 5–10 screenshots of @warmbcn flyers, reels and lineup posts, so I can choose between palette routes 1 and 2.
3. **Audio section:** approve source 1.393 → 24.070 s (22.68 s) with a 1-beat tail fade.
4. **Lineup treatment:** equal-weight names in the given order, stacked one per bar (proposed), or confirm a different hierarchy.
5. **Weekday:** 24 October 2026 is a Saturday. Show `SAT. 24 OCT` in the reference style, or `24 OCTOBER 2026` only, as given?
6. **Font:** Inter Display (free) or Neue Haas Grotesk Display (if licensed).
