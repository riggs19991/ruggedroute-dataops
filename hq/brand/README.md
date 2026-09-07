# Addictive Media Productions — brand source files

Recovered 2026-09-07 from the founder's Gmail ("Amp logos", Sep 2024, sent from
jriggs@ampmediastore.com; "amp logos for engraving", Jun 2026). Originals, untouched.

| File | What |
|---|---|
| `amp_logo_no_background.png` | Full wordmark, transparent, 3840×2160 — master for in-app use |
| `AMP_LOGO_BACKGROUND.png` | Wordmark on black topographic background, 3840×2160 |
| `amp_logo_with_topographical_lines.png` | Variant with white tagline on topo black, 3840×2160 |
| `AMP_FAVICON.png` | "AMP" mark, 130×130 |
| `amp_logo_for_LASER_ENGRAVE.svg` | Single-colour vector for engraving |

## Palette (sampled from the files)

| Token | Hex | Use |
|---|---|---|
| AMP green | `#38F800` | primary, buttons, active nav, good-standing |
| green dim | `#1FA300` | pressed, containers |
| black | `#000000` | app bar, nav, sign-in ground |
| ink | `#0A0A0A` | page background |
| surface | `#141414` | cards, inputs |
| charcoal | `#282828` | borders (the logo's secondary gray) |
| text | `#E8E8E8` / `#9A9A9A` | primary / secondary |
| amber | `#FFAB40` | due soon |
| red | `#FF5252` | overdue, errors |

Display face: **Barlow Condensed** (SemiBold Italic for titles, Bold for labels), OFL-licensed,
bundled in `app/assets/fonts/`. Chosen to echo the wordmark's chunky italic without imitating it.

The app's derived assets (`app/assets/brand/`) are generated from these: `amp_wordmark.png`
(cropped, 1600 px), `amp_topo.jpg` (1920 px backdrop), `amp_mark.png` (nav mark), and the
1024 px launcher-icon sources used by `flutter_launcher_icons`.
